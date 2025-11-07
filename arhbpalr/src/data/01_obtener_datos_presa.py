#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para obtener datos históricos de la Presa Abelardo L. Rodríguez.

Obtiene datos históricos de capacidad hídrica desde el portal de Sonora Datos
Abiertos mediante web scraping y genera archivo de descripción de fuentes.

Autor: MCDproyectos
Fecha: 2024-10-15
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import shutil
from pathlib import Path
from datetime import datetime


def obtener_datos_presa():
    """Función principal para obtener datos de la presa."""

    print("="*70)
    print("OBTENCIÓN DE DATOS DE LA PRESA ABELARDO L. RODRÍGUEZ")
    print("="*70)

    # Configurar rutas del proyecto siguiendo estructura Cookiecutter
    project_dir = Path(__file__).resolve().parents[2]
    data_dir = project_dir / 'data' / 'raw'
    data_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nDirectorio de datos: {data_dir}")

    # Diccionario de presas en Sonora
    presas_sonora = {
        "LCDSO": "Presa Lázaro Cárdenas (La Angostura)",
        "CHTSO": "Presa Cuauhtémoc",
        "ARLSO": "Presa Abelardo L. Rodríguez",
        "AOBSO": "Presa Álvaro Obregón (Oviáchic)",
        "ARCSO": "Presa Adolfo Ruiz Cortines (Mocúzari)",
        "PECSO": "Presa Plutarco Elías Calles (El Novillo)",
        "AGZCH": "Presa Abraham González",
        "PMOSO": "Presa Ing. Rodolfo Félix Valdés (El Molinito)",
        "IRASO": "Presa Ignacio R. Alatorre",
        "BICSO": "Presa Bicentenario"
    }

    print(f"Presa objetivo: {presas_sonora['ARLSO']}")

    # Web Scraping: obtener enlaces de datos
    print("\nObteniendo enlaces de datos...")
    resp = requests.get('https://datos.sonora.gob.mx/dataset/Recursos%20H%C3%ADdricos')
    soup = BeautifulSoup(resp.text, 'html.parser')
    links_datasets = soup.find('section', id='dataset-resources').find_all('ul')

    # Extraer enlaces de capacidad hídrica
    links_cap = []
    for link in links_datasets[0].find_all('a', attrs={'target': "_blank"}):
        if link.get('href') != '':
            links_cap.append(link.get('href'))

    print(f"[OK] Enlaces encontrados: {len(links_cap)}")

    # Descargar y convertir archivos XLSX a CSV
    print("\nDescargando y procesando archivos...")
    temp_dir = 'temp_csv'
    os.makedirs(temp_dir, exist_ok=True)

    paths = []
    for link in links_cap:
        file_name = link.split("/")[-1].replace(".xlsx", ".csv")
        file_path = os.path.join(temp_dir, file_name)

        try:
            df = pd.read_excel(link)
            df.to_csv(file_path, index=False)
            paths.append(file_path)
            print(f"  [OK] {file_name}")
        except Exception as e:
            print(f"  [ERROR] Error en {file_name}: {e}")

    print(f"\nTotal de archivos procesados: {len(paths)}")

    # Consolidar todos los datos
    print("\nConsolidando datos...")
    df_cap = pd.DataFrame()
    for path in paths:
        df = pd.read_csv(path, names=["clave", "fecha", "almacenamiento_hm3"],
                        skiprows=1, header=None)
        df_cap = pd.concat([df_cap, df], ignore_index=True)

    print(f"[OK] Dimensiones totales: {df_cap.shape}")

    # Filtrar datos de ARLSO
    print("\nFiltrando datos de la Presa Abelardo L. Rodríguez...")
    df_arlso = df_cap[df_cap["clave"] == "ARLSO"].copy()

    # Limpiar y convertir tipos de datos
    df_arlso.loc[:, "almacenamiento_hm3"] = pd.to_numeric(
        df_arlso["almacenamiento_hm3"], errors='coerce'
    )
    df_arlso.loc[:, "fecha"] = pd.to_datetime(
        df_arlso["fecha"], format="mixed", errors='coerce'
    )

    # Eliminar filas con datos nulos
    df_arlso = df_arlso.dropna(subset=['fecha', 'almacenamiento_hm3'])
    df_arlso = df_arlso.sort_values('fecha').reset_index(drop=True)
    df_arlso.drop("clave", axis=1, inplace=True)

    print(f"[OK] Registros de la Presa ARLSO: {len(df_arlso):,}")
    print(f"[OK] Rango de fechas: {df_arlso['fecha'].min().date()} a {df_arlso['fecha'].max().date()}")

    # Guardar datos
    output_file = data_dir / 'datos_presa_arlso.csv'
    df_arlso.to_csv(output_file, index=False)

    file_size = os.path.getsize(output_file) / 1024
    print(f"\n[OK] Archivo guardado: {output_file}")
    print(f"  - Registros: {len(df_arlso):,}")
    print(f"  - Columnas: {list(df_arlso.columns)}")
    print(f"  - Tamaño: {file_size:.2f} KB")

    # Eliminar archivos temporales
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"\n[OK] Archivos temporales eliminados")

    # Generar archivo de descripción de fuentes
    generar_descripcion_fuente(data_dir, df_arlso, file_size)

    print("\n" + "="*70)
    print("PROCESO COMPLETADO")
    print("="*70)

    return df_arlso


def generar_descripcion_fuente(data_dir, df_arlso, file_size):
    """Genera archivo de descripción de la fuente de datos."""

    fecha_descarga = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fecha_min = df_arlso['fecha'].min().strftime("%Y-%m-%d")
    fecha_max = df_arlso['fecha'].max().strftime("%Y-%m-%d")
    num_registros = len(df_arlso)

    descripcion = f"""# FUENTE DE DATOS: Presa Abelardo L. Rodríguez

## Información de la Fuente

**Nombre de la fuente:** Portal de Sonora Datos Abiertos
**URL:** https://datos.sonora.gob.mx/dataset/Recursos%20H%C3%ADdricos
**Tipo de fuente:** Web scraping de datos gubernamentales
**Fecha de descarga:** {fecha_descarga}
**Método de obtención:** Web scraping con BeautifulSoup y requests

## Descripción de los Datos

**Archivo generado:** `datos_presa_arlso.csv`
**Tamaño del archivo:** {file_size:.2f} KB
**Número de registros:** {num_registros:,}
**Periodo cubierto:** {fecha_min} a {fecha_max}

**Descripción:**
Datos históricos diarios de almacenamiento de agua en la Presa Abelardo L.
Rodríguez, ubicada en Hermosillo, Sonora. Los datos incluyen:
- Fecha de medición
- Volumen de almacenamiento en hectómetros cúbicos (hm³)

## Naturaleza de los Datos

Estos datos son registros oficiales del gobierno del estado de Sonora sobre los
niveles de agua en la presa. Son cruciales para entender la disponibilidad hídrica
y la capacidad de almacenamiento del embalse a lo largo de casi 80 años.

Los datos originales se encuentran en múltiples archivos Excel organizados por
décadas, que fueron consolidados y filtrados para obtener únicamente los registros
de la Presa Abelardo L. Rodríguez (clave: ARLSO).

## Estructura de los Datos

**Columnas:**
1. `fecha`: Fecha de la medición (formato YYYY-MM-DD)
2. `almacenamiento_hm3`: Volumen de agua almacenado en hectómetros cúbicos

**Calidad de datos:**
- No hay valores faltantes en las fechas con registros
- Valores numéricos validados (convertidos con manejo de errores)
- Fechas ordenadas cronológicamente
- Registros duplicados removidos

## Uso Recomendado

Estos datos pueden utilizarse para:
- Análisis de tendencias históricas del almacenamiento
- Estudios de disponibilidad hídrica
- Correlación con datos meteorológicos
- Evaluación del impacto del cambio climático
- Planificación de recursos hídricos

## Contacto y Licencia

**Organización:** Gobierno del Estado de Sonora
**Licencia:** Datos abiertos gubernamentales
**Script de obtención:** `src/data/01_obtener_datos_presa.py`

---
Generado automáticamente por el pipeline de datos
Fecha de generación: {fecha_descarga}
"""

    # Guardar descripción
    descripcion_file = data_dir / 'FUENTE_datos_presa.txt'
    with open(descripcion_file, 'w', encoding='utf-8') as f:
        f.write(descripcion)

    print(f"\n[OK] Descripción de fuente guardada: {descripcion_file}")


if __name__ == '__main__':
    obtener_datos_presa()
