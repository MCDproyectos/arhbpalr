#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para obtener datos históricos de avistamientos de aves en la Presa Abelardo L. Rodríguez.

Obtiene datos de avistamientos de aves desde la API de eBird para el rango temporal
de los datos de la presa (1947-2025). Implementa sistema de checkpoints para
permitir reanudación en caso de interrupción.

Autor: MCDproyectos
Fecha: 2024-10-15
"""

import pandas as pd
import requests
import time
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')


# Configuración
EBIRD_API_KEY = "se6b2m6ll8ca"
LOC_ID = "L506196"  # Presa Abelardo L. Rodríguez
API_BASE_URL = "https://api.ebird.org/v2/data/obs"

# Headers requeridos por la API
HEADERS = {
    "X-eBirdApiToken": EBIRD_API_KEY
}

# Configuración de throttling y reintentos
SLEEP_BETWEEN_REQUESTS = 0.5  # segundos
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # exponencial
RATE_LIMIT_WAIT = 60  # segundos para esperar si hay rate limit
CHECKPOINT_INTERVAL = 100  # Guardar progreso cada N requests


def obtener_datos_avifauna():
    """Función principal para obtener datos de avifauna."""

    print("="*70)
    print("OBTENCIÓN DE DATOS DE AVIFAUNA - eBird API")
    print("="*70)

    # Configurar rutas
    project_dir = Path(__file__).resolve().parents[2]
    data_raw = project_dir / 'data' / 'raw'
    data_processed = project_dir / 'data' / 'processed'

    data_raw.mkdir(parents=True, exist_ok=True)
    data_processed.mkdir(parents=True, exist_ok=True)

    print(f"\nDirectorio de datos raw: {data_raw}")
    print(f"Directorio de datos processed: {data_processed}")

    # Determinar rango de fechas
    print("\n" + "-"*70)
    print("Determinando rango de fechas a consultar...")
    print("-"*70)

    fechas_a_consultar = obtener_rango_fechas(data_processed)

    print(f"\nTotal de días a consultar: {len(fechas_a_consultar):,}")
    print(f"Tiempo estimado (con sleep de {SLEEP_BETWEEN_REQUESTS}s): "
          f"{len(fechas_a_consultar) * SLEEP_BETWEEN_REQUESTS / 3600:.2f} horas")

    # Verificar checkpoint
    checkpoint_file = data_raw / 'checkpoint_avistamientos.json'
    checkpoint_data_file = data_raw / 'avistamientos_checkpoint.csv'

    fechas_a_consultar, avistamientos_previos = cargar_checkpoint(
        checkpoint_file, checkpoint_data_file, fechas_a_consultar
    )

    # Obtener datos de la API
    print("\n" + "-"*70)
    print("Obteniendo datos de eBird API...")
    print("-"*70)
    print(f"Fechas a procesar: {len(fechas_a_consultar):,}")
    print(f"Checkpoint cada: {CHECKPOINT_INTERVAL} requests\n")

    todos_avistamientos, stats = obtener_avistamientos_ebird(
        fechas_a_consultar, avistamientos_previos, data_raw,
        checkpoint_file, checkpoint_data_file
    )

    # Guardar datos crudos
    print("\n" + "-"*70)
    print("Guardando datos crudos...")
    print("-"*70)

    df_raw = guardar_datos_crudos(todos_avistamientos, data_raw,
                                   checkpoint_file, checkpoint_data_file)

    # Procesar y limpiar datos
    print("\n" + "-"*70)
    print("Procesando y limpiando datos...")
    print("-"*70)

    df_final = procesar_y_limpiar_datos(df_raw, data_processed)

    # Generar archivo de descripción
    generar_descripcion_fuente(data_raw, df_raw, df_final, stats)

    print("\n" + "="*70)
    print("PROCESO COMPLETADO")
    print("="*70)


def obtener_rango_fechas(data_processed):
    """Determina el rango de fechas a consultar basado en datos hidrológicos."""

    file_hidro = data_processed / 'datos_hidrologicos_completos.csv'

    if not file_hidro.exists():
        raise FileNotFoundError(
            f"[ERROR] No se encontró {file_hidro}\n"
            "   Ejecuta primero el script 03_fusion_datos_hidrologicos.py"
        )

    df_hidro = pd.read_csv(file_hidro)
    df_hidro['fecha'] = pd.to_datetime(df_hidro['fecha'])

    # Filtrar fechas donde hay datos de presa
    df_con_presa = df_hidro[df_hidro['almacenamiento_hm3'].notna()]

    fecha_minima = df_con_presa['fecha'].min().date()
    fecha_maxima = datetime(2025, 10, 11).date()

    print(f"Fecha más antigua (datos de presa): {fecha_minima}")
    print(f"Fecha más reciente: {fecha_maxima}")

    # Generar lista de fechas
    fechas_a_consultar = []
    fecha_actual = fecha_maxima
    while fecha_actual >= fecha_minima:
        fechas_a_consultar.append(fecha_actual)
        fecha_actual -= timedelta(days=1)

    return fechas_a_consultar


def cargar_checkpoint(checkpoint_file, checkpoint_data_file, fechas_a_consultar):
    """Carga progreso previo si existe checkpoint."""

    fechas_ya_procesadas = set()
    avistamientos_previos = []

    if checkpoint_file.exists() and checkpoint_data_file.exists():
        print("\n[CHECKPOINT] Checkpoint encontrado. Cargando progreso previo...")

        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)

        fechas_ya_procesadas = set(checkpoint.get('fechas_procesadas', []))

        df_previo = pd.read_csv(checkpoint_data_file)
        avistamientos_previos = df_previo.to_dict('records')

        print(f"[OK] Cargadas {len(fechas_ya_procesadas):,} fechas procesadas previamente")
        print(f"[OK] Cargados {len(avistamientos_previos):,} avistamientos previos")

        fechas_a_consultar = [
            f for f in fechas_a_consultar
            if f.isoformat() not in fechas_ya_procesadas
        ]

        print(f"[OK] Quedan {len(fechas_a_consultar):,} fechas por procesar")
    else:
        print("\n[CHECKPOINT] No se encontró checkpoint previo. Iniciando desde cero.")

    return fechas_a_consultar, avistamientos_previos


def hacer_request_ebird(fecha, max_retries=MAX_RETRIES):
    """
    Hace un request a la API de eBird para obtener avistamientos históricos.

    Args:
        fecha: Fecha a consultar
        max_retries: Número máximo de reintentos

    Returns:
        Lista de avistamientos o None si hay error
    """
    url = f"{API_BASE_URL}/{LOC_ID}/historic/{fecha.year}/{fecha.month}/{fecha.day}"

    for intento in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return []  # No hay avistamientos para esta fecha
            elif response.status_code == 429:
                print(f"\n[WARNING] Rate limit alcanzado. Esperando {RATE_LIMIT_WAIT}s...")
                time.sleep(RATE_LIMIT_WAIT)
                continue
            else:
                print(f"\n[WARNING] Error HTTP {response.status_code} para {fecha}")
                if intento < max_retries - 1:
                    wait_time = RETRY_BACKOFF ** intento
                    time.sleep(wait_time)
                    continue
                return None

        except requests.exceptions.Timeout:
            print(f"\n[WARNING] Timeout para {fecha}. Reintento {intento + 1}/{max_retries}")
            if intento < max_retries - 1:
                time.sleep(RETRY_BACKOFF ** intento)
                continue
            return None

        except requests.exceptions.RequestException as e:
            print(f"\n[ERROR] Error de red para {fecha}: {e}")
            if intento < max_retries - 1:
                time.sleep(RETRY_BACKOFF ** intento)
                continue
            return None

    return None


def extraer_campos_relevantes(avistamiento):
    """Extrae solo los campos relevantes de un avistamiento."""
    return {
        'fecha': avistamiento.get('obsDt'),
        'nombre_comun': avistamiento.get('comName'),
        'nombre_cientifico': avistamiento.get('sciName'),
        'cantidad': avistamiento.get('howMany'),
        'codigo_especie': avistamiento.get('speciesCode'),
        'es_exotica': avistamiento.get('exoticCategory', None)
    }


def obtener_avistamientos_ebird(fechas_a_consultar, avistamientos_previos,
                                  data_raw, checkpoint_file, checkpoint_data_file):
    """Loop principal para obtener datos de la API."""

    todos_avistamientos = avistamientos_previos.copy()
    fechas_procesadas = set()

    stats = {
        'exitosos': 0,
        'sin_datos': 0,
        'errores': 0,
        'especies_unicas': set()
    }

    total = len(fechas_a_consultar)
    for idx, fecha in enumerate(fechas_a_consultar):

        # Mostrar progreso cada 50 requests
        if idx % 50 == 0:
            print(f"Progreso: {idx}/{total} ({idx/total*100:.1f}%)")

        avistamientos = hacer_request_ebird(fecha)

        if avistamientos is None:
            stats['errores'] += 1
        elif len(avistamientos) == 0:
            stats['sin_datos'] += 1
        else:
            stats['exitosos'] += 1

            for avistamiento in avistamientos:
                dato_limpio = extraer_campos_relevantes(avistamiento)
                todos_avistamientos.append(dato_limpio)

                if dato_limpio['codigo_especie']:
                    stats['especies_unicas'].add(dato_limpio['codigo_especie'])

        fechas_procesadas.add(fecha.isoformat())

        # Guardar checkpoint periódicamente
        if (idx + 1) % CHECKPOINT_INTERVAL == 0:
            checkpoint_data = {
                'fechas_procesadas': list(fechas_procesadas),
                'ultima_actualizacion': datetime.now().isoformat(),
                'stats': {
                    'exitosos': stats['exitosos'],
                    'sin_datos': stats['sin_datos'],
                    'errores': stats['errores'],
                    'total_avistamientos': len(todos_avistamientos),
                    'especies_unicas': len(stats['especies_unicas'])
                }
            }

            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f)

            df_checkpoint = pd.DataFrame(todos_avistamientos)
            df_checkpoint.to_csv(checkpoint_data_file, index=False)

            print(f"\n[CHECKPOINT] Checkpoint guardado en request {idx + 1}")
            print(f"   Avistamientos totales: {len(todos_avistamientos):,}")
            print(f"   Especies únicas: {len(stats['especies_unicas'])}")

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    print("\n[OK] Obtención completada")
    print(f"  Requests exitosos: {stats['exitosos']:,}")
    print(f"  Requests sin datos: {stats['sin_datos']:,}")
    print(f"  Requests con error: {stats['errores']:,}")
    print(f"\nTotal de avistamientos: {len(todos_avistamientos):,}")
    print(f"Especies únicas: {len(stats['especies_unicas'])}")

    return todos_avistamientos, stats


def guardar_datos_crudos(todos_avistamientos, data_raw,
                          checkpoint_file, checkpoint_data_file):
    """Guarda los datos crudos y limpia archivos de checkpoint."""

    df_raw = pd.DataFrame(todos_avistamientos)

    output_raw = data_raw / 'avistamientos_ebird_raw.csv'
    df_raw.to_csv(output_raw, index=False)

    file_size = output_raw.stat().st_size / 1024

    print(f"[OK] Datos crudos guardados: {output_raw}")
    print(f"  Registros: {len(df_raw):,}")
    print(f"  Tamaño: {file_size:.2f} KB")

    # Limpiar archivos de checkpoint
    if checkpoint_file.exists():
        checkpoint_file.unlink()
    if checkpoint_data_file.exists():
        checkpoint_data_file.unlink()

    print("[OK] Archivos de checkpoint eliminados")

    return df_raw


def procesar_y_limpiar_datos(df_raw, data_processed):
    """Limpia y procesa los datos crudos."""

    df_processed = df_raw.copy()

    # Convertir fecha a datetime
    df_processed['fecha'] = pd.to_datetime(df_processed['fecha'], format='mixed')
    print("[OK] Fechas convertidas a datetime")

    # Convertir cantidad a numérico
    df_processed['cantidad'] = pd.to_numeric(
        df_processed['cantidad'], errors='coerce'
    ).fillna(1).astype(int)
    print("[OK] Cantidades convertidas a numérico")

    # Crear flag para especies exóticas
    df_processed['es_exotica'] = df_processed['es_exotica'].notna()
    print("[OK] Flag de especies exóticas creado")

    # Eliminar registros sin nombre científico
    len_antes = len(df_processed)
    df_processed = df_processed[df_processed['nombre_cientifico'].notna()]
    len_despues = len(df_processed)
    print(f"[OK] Eliminados {len_antes - len_despues:,} registros sin nombre científico")

    # Ordenar por fecha
    df_processed = df_processed.sort_values('fecha').reset_index(drop=True)

    # Seleccionar columnas finales
    columnas_finales = [
        'fecha',
        'nombre_comun',
        'nombre_cientifico',
        'codigo_especie',
        'cantidad',
        'es_exotica'
    ]

    df_final = df_processed[columnas_finales].copy()

    # Guardar datos procesados
    output_processed = data_processed / 'avistamientos_aves_presa.csv'
    df_final.to_csv(output_processed, index=False)

    file_size = output_processed.stat().st_size / 1024

    print(f"\n[OK] Datos procesados guardados: {output_processed}")
    print(f"  Registros: {len(df_final):,}")
    print(f"  Columnas: {len(df_final.columns)}")
    print(f"  Tamaño: {file_size:.2f} KB")
    print(f"  Rango: {df_final['fecha'].min().date()} a {df_final['fecha'].max().date()}")

    return df_final


def generar_descripcion_fuente(data_raw, df_raw, df_final, stats):
    """Genera archivo de descripción de la fuente de datos."""

    fecha_descarga = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fecha_min = df_final['fecha'].min().strftime("%Y-%m-%d")
    fecha_max = df_final['fecha'].max().strftime("%Y-%m-%d")

    # Calcular tamaños de archivos
    file_raw = data_raw.parent / 'raw' / 'avistamientos_ebird_raw.csv'
    file_processed = data_raw.parent / 'processed' / 'avistamientos_aves_presa.csv'

    size_raw = os.path.getsize(file_raw) / 1024 if file_raw.exists() else 0
    size_processed = os.path.getsize(file_processed) / 1024 if file_processed.exists() else 0

    descripcion = f"""# FUENTE DE DATOS: Avistamientos de Aves (Avifauna)

## Información de la Fuente

**Nombre de la fuente:** eBird API
**URL:** https://ebird.org/
**Documentación:** https://documenter.getpostman.com/view/664302/S1ENwy59
**Tipo de fuente:** API REST con autenticación
**Fecha de descarga:** {fecha_descarga}
**Método de obtención:** HTTP GET requests históricos (día por día)

## Ubicación

**Location ID:** L506196
**Localización:** Presa Abelardo L. Rodríguez, Hermosillo, Sonora, México

## Descripción de los Datos

### Archivo 1: Datos Crudos

**Archivo:** `avistamientos_ebird_raw.csv`
**Tamaño:** {size_raw:.2f} KB
**Registros:** {len(df_raw):,}
**Periodo:** {fecha_min} a {fecha_max}

**Variables:**
- `fecha`: Fecha y hora de la observación
- `nombre_comun`: Nombre común de la especie
- `nombre_cientifico`: Nombre científico de la especie
- `cantidad`: Número de individuos observados
- `codigo_especie`: Código único de la especie en eBird
- `es_exotica`: Indicador si la especie es exótica

### Archivo 2: Datos Procesados

**Archivo:** `avistamientos_aves_presa.csv`
**Tamaño:** {size_processed:.2f} KB
**Registros:** {len(df_final):,}
**Periodo:** {fecha_min} a {fecha_max}

**Variables (6 columnas):**
1. `fecha`: Fecha de observación (formato datetime)
2. `nombre_comun`: Nombre común de la especie
3. `nombre_cientifico`: Nombre científico (validado, sin nulos)
4. `codigo_especie`: Código de especie eBird
5. `cantidad`: Número de individuos (entero, mínimo 1)
6. `es_exotica`: Booleano indicando si es especie exótica

## Naturaleza de los Datos

eBird es una base de datos global de ciencia ciudadana que recopila observaciones
de aves. Los datos son aportados por observadores de aves voluntarios y revisados
por expertos regionales. Estos datos son fundamentales para entender la biodiversidad
de avifauna que depende del ecosistema de la presa.

La obtención de datos se realizó mediante requests históricos día por día desde
{fecha_min} hasta {fecha_max}, totalizando aproximadamente 28,250 requests.

## Estadísticas de Obtención

- **Requests exitosos (con datos):** {stats['exitosos']:,}
- **Requests sin datos (días sin reportes):** {stats['sin_datos']:,}
- **Requests con error:** {stats['errores']:,}
- **Especies únicas identificadas:** {len(stats['especies_unicas'])}

## Calidad de Datos

- Registros sin nombre científico eliminados durante procesamiento
- Cantidades convertidas a enteros (valores faltantes = 1)
- Fechas validadas y convertidas a datetime con formato mixto
- Especies exóticas marcadas con flag booleano
- Datos ordenados cronológicamente

## Uso Recomendado

Estos datos pueden utilizarse para:
- Análisis de biodiversidad de avifauna
- Correlación con niveles de almacenamiento de la presa
- Estudios de especies migratorias vs. residentes
- Evaluación del impacto del ecosistema acuático en poblaciones de aves
- Análisis temporal de avistamientos
- Identificación de especies indicadoras de salud del ecosistema

## Limitaciones y Consideraciones

- Datos de ciencia ciudadana: cobertura variable en el tiempo
- Observaciones más frecuentes en años recientes (2010+)
- Algunos días/periodos sin reportes de avistamientos
- Cantidad de individuos puede ser estimada o exacta según el observador
- No todos los avistamientos están necesariamente registrados
- Sistema de checkpoints usado para manejar interrupciones durante descarga

## Contacto y Licencia

**Proveedor:** Cornell Lab of Ornithology (eBird)
**Licencia:** Uso conforme a términos de eBird API
**API Key utilizada:** se6b2m6ll8ca
**Script de obtención:** `src/data/04_obtener_datos_aves.py`

---
Generado automáticamente por el pipeline de datos
Fecha de generación: {fecha_descarga}
"""

    # Guardar descripción
    descripcion_file = data_raw / 'FUENTE_datos_avifauna.txt'
    with open(descripcion_file, 'w', encoding='utf-8') as f:
        f.write(descripcion)

    print(f"\n[OK] Descripción de fuente guardada: {descripcion_file}")


if __name__ == '__main__':
    obtener_datos_avifauna()
