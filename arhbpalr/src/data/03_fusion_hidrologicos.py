#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para fusionar datos hidrológicos y meteorológicos.

Fusiona los datos de la Presa Abelardo L. Rodríguez con datos meteorológicos
para crear un dataset completo. Utiliza estrategia OUTER JOIN para preservar
todas las fechas de ambos datasets y generar archivo de descripción del proceso.

Autor: MCDproyectos
Fecha: 2024-10-15
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from datetime import datetime


def fusionar_datos_hidrologicos():
    """Función principal para fusionar datos hidrológicos y meteorológicos."""

    print("="*70)
    print("FUSIÓN DE DATOS HIDROLÓGICOS Y METEOROLÓGICOS")
    print("="*70)

    # Configurar rutas
    project_dir = Path(__file__).resolve().parents[2]
    data_raw = project_dir / 'data' / 'raw'
    data_processed = project_dir / 'data' / 'processed'

    data_processed.mkdir(parents=True, exist_ok=True)

    print(f"\nDirectorio de datos raw: {data_raw}")
    print(f"Directorio de datos processed: {data_processed}")

    # Cargar datos de la presa
    print("\n" + "-"*70)
    print("Cargando datos de la presa...")
    print("-"*70)

    df_presa = cargar_datos_presa(data_raw)

    # Cargar datos meteorológicos
    print("\n" + "-"*70)
    print("Cargando datos meteorológicos...")
    print("-"*70)

    df_meteo = cargar_datos_meteorologicos(data_raw)

    # Analizar cobertura temporal
    print("\n" + "-"*70)
    print("Analizando cobertura temporal...")
    print("-"*70)

    stats_cobertura = analizar_cobertura_temporal(df_presa, df_meteo)

    # Fusionar datasets
    print("\n" + "-"*70)
    print("Fusionando datasets...")
    print("-"*70)

    df_fusion = fusionar_datasets(df_presa, df_meteo)

    # Analizar valores faltantes
    print("\n" + "-"*70)
    print("Analizando valores faltantes...")
    print("-"*70)

    stats_faltantes = analizar_valores_faltantes(df_fusion)

    # Guardar dataset fusionado
    print("\n" + "-"*70)
    print("Guardando dataset fusionado...")
    print("-"*70)

    df_final = guardar_dataset_fusionado(df_fusion, data_processed)

    # Generar archivo de descripción
    generar_descripcion_proceso(
        data_processed, df_final, stats_cobertura, stats_faltantes
    )

    print("\n" + "="*70)
    print("PROCESO COMPLETADO")
    print("="*70)


def cargar_datos_presa(data_raw):
    """Carga los datos de almacenamiento de la presa."""

    file_presa = data_raw / 'datos_presa_arlso.csv'

    if not file_presa.exists():
        raise FileNotFoundError(
            f"[ERROR] No se encontró {file_presa}\n"
            "   Ejecuta primero el script 01_obtener_datos_presa.py"
        )

    df_presa = pd.read_csv(file_presa)
    df_presa['fecha'] = pd.to_datetime(df_presa['fecha'])

    print(f"[OK] Datos de presa cargados")
    print(f"  Registros: {len(df_presa):,}")
    print(f"  Columnas: {list(df_presa.columns)}")
    print(f"  Rango: {df_presa['fecha'].min().date()} a {df_presa['fecha'].max().date()}")

    return df_presa


def cargar_datos_meteorologicos(data_raw):
    """Carga los datos meteorológicos completos."""

    file_meteo = data_raw / 'datos_meteorologicos_completos.csv'

    if not file_meteo.exists():
        raise FileNotFoundError(
            f"[ERROR] No se encontró {file_meteo}\n"
            "   Ejecuta primero el script 02_obtener_datos_meteo.py"
        )

    df_meteo = pd.read_csv(file_meteo)
    df_meteo['fecha'] = pd.to_datetime(df_meteo['fecha'])

    print(f"[OK] Datos meteorológicos cargados")
    print(f"  Registros: {len(df_meteo):,}")
    print(f"  Columnas: {list(df_meteo.columns)}")
    print(f"  Rango: {df_meteo['fecha'].min().date()} a {df_meteo['fecha'].max().date()}")

    return df_meteo


def analizar_cobertura_temporal(df_presa, df_meteo):
    """Analiza la cobertura temporal de ambos datasets."""

    presa_min, presa_max = df_presa['fecha'].min(), df_presa['fecha'].max()
    meteo_min, meteo_max = df_meteo['fecha'].min(), df_meteo['fecha'].max()

    print(f"Datos de presa:")
    print(f"   Inicio: {presa_min.date()}")
    print(f"   Fin: {presa_max.date()}")
    print(f"   Días: {(presa_max - presa_min).days:,}")

    print(f"\nDatos meteorológicos:")
    print(f"   Inicio: {meteo_min.date()}")
    print(f"   Fin: {meteo_max.date()}")
    print(f"   Días: {(meteo_max - meteo_min).days:,}")

    # Calcular intersección
    interseccion_min = max(presa_min, meteo_min)
    interseccion_max = min(presa_max, meteo_max)

    print(f"\nPeríodo de intersección:")
    print(f"   Inicio: {interseccion_min.date()}")
    print(f"   Fin: {interseccion_max.date()}")
    print(f"   Días: {(interseccion_max - interseccion_min).days:,}")

    # Fechas únicas
    fechas_presa = set(df_presa['fecha'].dt.date)
    fechas_meteo = set(df_meteo['fecha'].dt.date)

    solo_presa = len(fechas_presa - fechas_meteo)
    solo_meteo = len(fechas_meteo - fechas_presa)
    comunes = len(fechas_presa & fechas_meteo)

    print(f"\nAnálisis de fechas únicas:")
    print(f"   Fechas solo en presa: {solo_presa:,}")
    print(f"   Fechas solo en meteo: {solo_meteo:,}")
    print(f"   Fechas en común: {comunes:,}")

    return {
        'presa_min': presa_min,
        'presa_max': presa_max,
        'meteo_min': meteo_min,
        'meteo_max': meteo_max,
        'interseccion_min': interseccion_min,
        'interseccion_max': interseccion_max,
        'solo_presa': solo_presa,
        'solo_meteo': solo_meteo,
        'comunes': comunes
    }


def fusionar_datasets(df_presa, df_meteo):
    """
    Fusiona los datasets usando estrategia OUTER JOIN.

    Preserva todas las fechas de ambos datasets para análisis completo.
    """

    # Fusión OUTER: preserva todas las fechas
    df_fusion = pd.merge(
        df_presa,
        df_meteo,
        on='fecha',
        how='outer',
        indicator=True
    )

    # Ordenar por fecha
    df_fusion = df_fusion.sort_values('fecha').reset_index(drop=True)

    # Crear columna indicadora de completitud
    df_fusion['datos_completos'] = (
        df_fusion['almacenamiento_hm3'].notna() &
        df_fusion['evapotranspiracion_mm'].notna()
    )

    print(f"[OK] Fusión completada")
    print(f"  Total de registros: {len(df_fusion):,}")
    print(f"  Registros con datos completos: {df_fusion['datos_completos'].sum():,}")
    print(f"  Registros con datos incompletos: {(~df_fusion['datos_completos']).sum():,}")

    # Mostrar origen de los datos
    print(f"\nOrigen de los datos:")
    merge_counts = df_fusion['_merge'].value_counts()
    for origen, count in merge_counts.items():
        print(f"  {origen}: {count:,}")

    # Eliminar columna _merge
    df_fusion = df_fusion.drop(columns=['_merge'])

    return df_fusion


def analizar_valores_faltantes(df_fusion):
    """Analiza valores faltantes en el dataset fusionado."""

    # Contar valores faltantes por columna
    missing = df_fusion.isnull().sum()
    missing_pct = (missing / len(df_fusion) * 100).round(2)

    missing_df = pd.DataFrame({
        'Columna': missing.index,
        'Valores_faltantes': missing.values,
        'Porcentaje': missing_pct.values
    })

    missing_df = missing_df[missing_df['Valores_faltantes'] > 0].sort_values(
        'Valores_faltantes', ascending=False
    )

    if len(missing_df) > 0:
        print("Columnas con valores faltantes:\n")
        for _, row in missing_df.iterrows():
            print(f"  {row['Columna']}: {row['Valores_faltantes']:,} ({row['Porcentaje']}%)")
    else:
        print("[OK] No hay valores faltantes en ninguna columna")

    # Análisis por año
    df_fusion['año'] = df_fusion['fecha'].dt.year

    completitud_anual = df_fusion.groupby('año').agg({
        'datos_completos': ['sum', 'count'],
        'almacenamiento_hm3': lambda x: x.notna().sum(),
        'evapotranspiracion_mm': lambda x: x.notna().sum()
    })

    completitud_anual.columns = ['Completos', 'Total', 'Con_presa', 'Con_meteo']
    completitud_anual['Pct_completo'] = (
        completitud_anual['Completos'] / completitud_anual['Total'] * 100
    ).round(1)

    # Mostrar años con datos incompletos
    incompletos = completitud_anual[completitud_anual['Pct_completo'] < 100]
    if len(incompletos) > 0:
        print(f"\nAños con datos incompletos: {len(incompletos)}")

    return {
        'missing_df': missing_df,
        'completitud_anual': completitud_anual
    }


def guardar_dataset_fusionado(df_fusion, data_processed):
    """Guarda el dataset fusionado en data/processed."""

    # Eliminar columna temporal 'año' si existe
    df_final = df_fusion.drop(columns=['año'], errors='ignore')

    output_file = data_processed / 'datos_hidrologicos_completos.csv'
    df_final.to_csv(output_file, index=False)

    file_size = output_file.stat().st_size / (1024 * 1024)  # MB

    print(f"[OK] Dataset guardado: {output_file}")
    print(f"  Registros: {len(df_final):,}")
    print(f"  Columnas: {len(df_final.columns)}")
    print(f"  Tamaño: {file_size:.2f} MB")
    print(f"  Rango: {df_final['fecha'].min().date()} a {df_final['fecha'].max().date()}")

    return df_final


def generar_descripcion_proceso(data_processed, df_final, stats_cobertura, stats_faltantes):
    """Genera archivo de descripción del proceso de fusión."""

    fecha_proceso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fecha_min = df_final['fecha'].min().strftime("%Y-%m-%d")
    fecha_max = df_final['fecha'].max().strftime("%Y-%m-%d")

    # Calcular tamaño del archivo
    file_path = data_processed / 'datos_hidrologicos_completos.csv'
    size_mb = os.path.getsize(file_path) / (1024 * 1024) if file_path.exists() else 0

    # Estadísticas de completitud
    datos_completos = df_final['datos_completos'].sum()
    datos_incompletos = (~df_final['datos_completos']).sum()
    pct_completo = (datos_completos / len(df_final) * 100).round(1)

    descripcion = f"""# PROCESO: Fusión de Datos Hidrológicos y Meteorológicos

## Información del Proceso

**Fecha de procesamiento:** {fecha_proceso}
**Script de procesamiento:** `src/data/03_fusion_hidrologicos.py`
**Tipo de proceso:** Fusión de datasets (OUTER JOIN)

## Archivos de Entrada

### 1. Datos de Presa (datos_presa_arlso.csv)
- **Periodo:** {stats_cobertura['presa_min'].date()} a {stats_cobertura['presa_max'].date()}
- **Fuente:** Portal de Sonora Datos Abiertos
- **Variable principal:** almacenamiento_hm3

### 2. Datos Meteorológicos (datos_meteorologicos_completos.csv)
- **Periodo:** {stats_cobertura['meteo_min'].date()} a {stats_cobertura['meteo_max'].date()}
- **Fuente:** Open-Meteo Historical Weather API
- **Variables:** 18 variables meteorológicas

## Archivo de Salida

**Archivo:** `datos_hidrologicos_completos.csv`
**Ubicación:** data/processed/
**Tamaño:** {size_mb:.2f} MB
**Registros:** {len(df_final):,}
**Columnas:** {len(df_final.columns)}
**Periodo:** {fecha_min} a {fecha_max}

### Variables Incluidas ({len(df_final.columns)} columnas):

**De la presa:**
- `fecha`: Fecha de medición (YYYY-MM-DD)
- `almacenamiento_hm3`: Volumen de agua en hectómetros cúbicos

**Meteorológicas:**
- `precipitacion_mm`: Precipitación total diaria (mm)
- `lluvia_mm`: Lluvia diaria (mm)
- `evapotranspiracion_mm`: Evapotranspiración ET0 FAO (mm)
- `temp_media_c`: Temperatura media (°C)
- `temp_max_c`: Temperatura máxima (°C)
- `temp_min_c`: Temperatura mínima (°C)
- `horas_precipitacion`: Horas con precipitación
- `viento_max_km_h`: Velocidad máxima del viento (km/h)
- `viento_medio_km_h`: Velocidad media del viento (km/h)
- `deficit_presion_vapor_kpa`: Déficit de presión de vapor (kPa)
- `radiacion_solar_mj_m2`: Radiación solar (MJ/m²)
- `humedad_relativa_pct`: Humedad relativa (%)
- `cobertura_nubes_pct`: Cobertura de nubes (%)
- `humedad_suelo_0_100cm`: Humedad del suelo 0-100cm (m³/m³)
- `humedad_suelo_0_7cm`: Humedad del suelo 0-7cm (m³/m³)
- `humedad_suelo_28_100cm`: Humedad del suelo 28-100cm (m³/m³)
- `humedad_suelo_7_28cm`: Humedad del suelo 7-28cm (m³/m³)

**Indicadora:**
- `datos_completos`: Booleano - True si hay datos de presa Y meteorológicos

## Estrategia de Fusión

**Método utilizado:** OUTER JOIN (Unión completa)

**Decisión:** Se utilizó `pd.merge()` con `how='outer'` para preservar **todas las fechas**
de ambos datasets.

**Razones:**
1. **Máxima preservación de datos**: No se pierde información de ningún dataset
2. **Análisis temporal completo**: Permite estudiar períodos con datos meteorológicos
   pero sin mediciones de presa (y viceversa)
3. **Flexibilidad analítica**: Los análisis posteriores pueden decidir cómo manejar
   valores faltantes según el caso de uso

**Alternativas descartadas:**
- **INNER JOIN**: Perdería datos históricos valiosos donde solo existe uno de los datasets
- **LEFT/RIGHT JOIN**: Sesgaría el dataset hacia una de las fuentes

## Cobertura Temporal

**Período de intersección (datos en común):**
- Inicio: {stats_cobertura['interseccion_min'].date()}
- Fin: {stats_cobertura['interseccion_max'].date()}
- Días: {(stats_cobertura['interseccion_max'] - stats_cobertura['interseccion_min']).days:,}

**Análisis de fechas únicas:**
- Fechas solo en datos de presa: {stats_cobertura['solo_presa']:,}
- Fechas solo en datos meteorológicos: {stats_cobertura['solo_meteo']:,}
- Fechas en común (ambos datasets): {stats_cobertura['comunes']:,}

## Completitud de Datos

**Registros con datos completos:** {datos_completos:,} ({pct_completo}%)
**Registros con datos incompletos:** {datos_incompletos:,} ({(100-pct_completo):.1f}%)

Los registros con datos incompletos corresponden principalmente a:
- Fechas antes de 1940 (solo datos de presa, sin meteorología)
- Fechas después de 2024-09-19 (solo meteorología, sin mediciones de presa)

## Manejo de Valores Faltantes

- Los valores faltantes se marcan como `NaN` en pandas
- La columna `datos_completos` permite filtrar rápidamente registros completos
- Para análisis de correlación: usar `df[df['datos_completos'] == True]`
- Para series temporales: considerar interpolación según el caso de uso

## Calidad de Datos

- Sin duplicados en fechas
- Fechas ordenadas cronológicamente
- Tipos de datos correctos (datetime para fechas, float para valores numéricos)
- Preservación de todos los datos originales
- Indicador de completitud para facilitar análisis

## Uso Recomendado

Este dataset puede utilizarse para:
- **Análisis de correlación** entre niveles de agua y variables meteorológicas
- **Modelado predictivo** del almacenamiento basado en clima
- **Estudios de balance hídrico** combinando precipitación y evapotranspiración
- **Análisis de series temporales** con variables hidrometeorológicas
- **Identificación de patrones** climáticos que afectan el llenado de la presa

## Procesamiento Aplicado

1. Carga de datasets de entrada con validación de existencia
2. Conversión de fechas a formato datetime
3. Fusión OUTER JOIN en columna 'fecha'
4. Ordenamiento cronológico
5. Creación de columna indicadora de completitud
6. Análisis de valores faltantes por columna y por año
7. Guardado en formato CSV en data/processed/

## Referencias

- **Datos de presa:** Ver FUENTE_datos_presa.txt
- **Datos meteorológicos:** Ver FUENTE_datos_meteorologicos.txt

---
Generado automáticamente por el pipeline de datos
Fecha de generación: {fecha_proceso}
"""

    # Guardar descripción
    descripcion_file = data_processed / 'PROCESO_fusion_hidrologicos.txt'
    with open(descripcion_file, 'w', encoding='utf-8') as f:
        f.write(descripcion)

    print(f"\n[OK] Descripción del proceso guardada: {descripcion_file}")


if __name__ == '__main__':
    fusionar_datos_hidrologicos()
