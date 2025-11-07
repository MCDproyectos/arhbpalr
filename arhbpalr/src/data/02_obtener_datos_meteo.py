#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para obtener datos meteorológicos históricos.

Obtiene datos meteorológicos históricos desde Open-Meteo API para la ubicación
de la Presa Abelardo L. Rodríguez y genera archivo de descripción de fuentes.

Autor: MCDproyectos
Fecha: 2024-10-15
"""

import pandas as pd
import requests
import os
from datetime import datetime
from pathlib import Path


# Configuración
LATITUD = 29.067999
LONGITUD = -110.910734
FECHA_INICIO = '1940-01-01'
FECHA_FIN = '2024-12-31'


def obtener_datos_meteorologicos():
    """Función principal para obtener datos meteorológicos."""

    print("="*70)
    print("OBTENCIÓN DE DATOS METEOROLÓGICOS")
    print("="*70)

    # Configurar rutas
    project_dir = Path(__file__).resolve().parents[2]
    data_dir = project_dir / 'data' / 'raw'
    data_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nDirectorio de datos: {data_dir}")
    print(f"Coordenadas: ({LATITUD}, {LONGITUD})")
    print(f"Rango de fechas: {FECHA_INICIO} a {FECHA_FIN}")

    # Obtener datos básicos (evapotranspiración)
    print("\n" + "-"*70)
    print("1. Obteniendo datos básicos (evapotranspiración)...")
    print("-"*70)

    df_basico = obtener_datos_basicos(data_dir)

    # Obtener datos completos
    print("\n" + "-"*70)
    print("2. Obteniendo datos meteorológicos completos...")
    print("-"*70)

    df_completo = obtener_datos_completos(data_dir)

    # Generar archivo de descripción
    generar_descripcion_fuente(data_dir, df_basico, df_completo)

    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN DE ARCHIVOS GENERADOS")
    print("="*70)

    archivos_generados = []
    file_basico = data_dir / 'datos_meteorologicos_basicos.csv'
    file_completo = data_dir / 'datos_meteorologicos_completos.csv'

    if file_basico.exists():
        archivos_generados.append(file_basico.name)
        print(f"\n[OK] {file_basico.name}")
        print(f"  Tamaño: {os.path.getsize(file_basico) / 1024:.2f} KB")

    if file_completo.exists():
        archivos_generados.append(file_completo.name)
        print(f"\n[OK] {file_completo.name}")
        print(f"  Tamaño: {os.path.getsize(file_completo) / 1024:.2f} KB")

    print(f"\n{len(archivos_generados)} archivo(s) generado(s) exitosamente")
    print("\n" + "="*70)
    print("PROCESO COMPLETADO")
    print("="*70)


def obtener_datos_basicos(data_dir):
    """Obtiene datos básicos de evapotranspiración."""

    api_url = (
        f'https://archive-api.open-meteo.com/v1/archive?'
        f'latitude={LATITUD}&longitude={LONGITUD}&'
        f'start_date={FECHA_INICIO}&end_date={FECHA_FIN}&'
        f'daily=et0_fao_evapotranspiration&'
        f'timezone=America/Los_Angeles'
    )

    try:
        response = requests.get(api_url, timeout=60)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data['daily'])
            df["time"] = pd.to_datetime(df["time"])
            df.columns = ['fecha', 'evapotranspiracion_mm_dia']

            # Guardar
            output_file = data_dir / 'datos_meteorologicos_basicos.csv'
            df.to_csv(output_file, index=False)

            print(f"[OK] Datos básicos obtenidos")
            print(f"  Registros: {len(df):,}")
            print(f"  Rango: {df['fecha'].min().date()} a {df['fecha'].max().date()}")

            return df

        else:
            print(f"[ERROR] Error HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None


def obtener_datos_completos(data_dir):
    """Obtiene datos meteorológicos completos."""

    api_url = (
        "https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={LATITUD}&longitude={LONGITUD}&"
        f"start_date={FECHA_INICIO}&end_date={FECHA_FIN}&"
        "daily=precipitation_sum,rain_sum,et0_fao_evapotranspiration,"
        "temperature_2m_mean,temperature_2m_max,temperature_2m_min,"
        "precipitation_hours,wind_speed_10m_max,wind_speed_10m_mean,"
        "vapour_pressure_deficit_max,shortwave_radiation_sum,"
        "relative_humidity_2m_mean,cloud_cover_mean,"
        "soil_moisture_0_to_100cm_mean,soil_moisture_0_to_7cm_mean,"
        "soil_moisture_28_to_100cm_mean,soil_moisture_7_to_28cm_mean&"
        "timezone=auto"
    )

    print("  (Esto puede tardar 10-30 segundos)")

    try:
        response = requests.get(api_url, timeout=60)

        if response.status_code == 200:
            data = response.json()

            if 'daily' in data:
                df = pd.DataFrame(data['daily'])
                df['time'] = pd.to_datetime(df['time'])

                # Renombrar columnas
                df.columns = [
                    'fecha', 'precipitacion_mm', 'lluvia_mm', 'evapotranspiracion_mm',
                    'temp_media_c', 'temp_max_c', 'temp_min_c', 'horas_precipitacion',
                    'viento_max_km_h', 'viento_medio_km_h', 'deficit_presion_vapor_kpa',
                    'radiacion_solar_mj_m2', 'humedad_relativa_pct', 'cobertura_nubes_pct',
                    'humedad_suelo_0_100cm', 'humedad_suelo_0_7cm',
                    'humedad_suelo_28_100cm', 'humedad_suelo_7_28cm'
                ]

                # Guardar
                output_file = data_dir / 'datos_meteorologicos_completos.csv'
                df.to_csv(output_file, index=False)

                print(f"[OK] Datos completos obtenidos")
                print(f"  Registros: {len(df):,}")
                print(f"  Variables: {len(df.columns)}")
                print(f"  Rango: {df['fecha'].min().date()} a {df['fecha'].max().date()}")

                return df

            else:
                print("[ERROR] Error: Respuesta no contiene datos 'daily'")
                return None

        elif response.status_code == 429:
            print("[ERROR] Error 429: Límite de peticiones alcanzado")
            print("  Espera 1 hora e intenta nuevamente")
            return None

        else:
            print(f"[ERROR] Error HTTP {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("[ERROR] Timeout: La solicitud tardó más de 60 segundos")
        return None

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None


def generar_descripcion_fuente(data_dir, df_basico, df_completo):
    """Genera archivo de descripción de la fuente de datos."""

    fecha_descarga = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Información del archivo básico
    info_basico = ""
    if df_basico is not None:
        fecha_min_b = df_basico['fecha'].min().strftime("%Y-%m-%d")
        fecha_max_b = df_basico['fecha'].max().strftime("%Y-%m-%d")
        file_basico = data_dir / 'datos_meteorologicos_basicos.csv'
        size_basico = os.path.getsize(file_basico) / 1024 if file_basico.exists() else 0

        info_basico = f"""
### Archivo 1: Datos Básicos

**Archivo:** `datos_meteorologicos_basicos.csv`
**Tamaño:** {size_basico:.2f} KB
**Registros:** {len(df_basico):,}
**Periodo:** {fecha_min_b} a {fecha_max_b}

**Variables:**
- `fecha`: Fecha de la medición
- `evapotranspiracion_mm_dia`: Evapotranspiración de referencia ET0 (FAO) en mm/día
"""

    # Información del archivo completo
    info_completo = ""
    if df_completo is not None:
        fecha_min_c = df_completo['fecha'].min().strftime("%Y-%m-%d")
        fecha_max_c = df_completo['fecha'].max().strftime("%Y-%m-%d")
        file_completo = data_dir / 'datos_meteorologicos_completos.csv'
        size_completo = os.path.getsize(file_completo) / 1024 if file_completo.exists() else 0

        info_completo = f"""
### Archivo 2: Datos Completos

**Archivo:** `datos_meteorologicos_completos.csv`
**Tamaño:** {size_completo:.2f} KB
**Registros:** {len(df_completo):,}
**Periodo:** {fecha_min_c} a {fecha_max_c}

**Variables (18 columnas):**
1. `fecha`: Fecha de medición
2. `precipitacion_mm`: Precipitación total diaria (mm)
3. `lluvia_mm`: Lluvia diaria (mm)
4. `evapotranspiracion_mm`: Evapotranspiración ET0 FAO (mm)
5. `temp_media_c`: Temperatura media (°C)
6. `temp_max_c`: Temperatura máxima (°C)
7. `temp_min_c`: Temperatura mínima (°C)
8. `horas_precipitacion`: Horas con precipitación
9. `viento_max_km_h`: Velocidad máxima del viento (km/h)
10. `viento_medio_km_h`: Velocidad media del viento (km/h)
11. `deficit_presion_vapor_kpa`: Déficit de presión de vapor (kPa)
12. `radiacion_solar_mj_m2`: Radiación solar (MJ/m²)
13. `humedad_relativa_pct`: Humedad relativa (%)
14. `cobertura_nubes_pct`: Cobertura de nubes (%)
15. `humedad_suelo_0_100cm`: Humedad del suelo 0-100cm (m³/m³)
16. `humedad_suelo_0_7cm`: Humedad del suelo 0-7cm (m³/m³)
17. `humedad_suelo_28_100cm`: Humedad del suelo 28-100cm (m³/m³)
18. `humedad_suelo_7_28cm`: Humedad del suelo 7-28cm (m³/m³)
"""

    descripcion = f"""# FUENTE DE DATOS: Datos Meteorológicos Históricos

## Información de la Fuente

**Nombre de la fuente:** Open-Meteo Historical Weather API
**URL:** https://open-meteo.com/
**Documentación:** https://open-meteo.com/en/docs/historical-weather-api
**Tipo de fuente:** API REST pública
**Fecha de descarga:** {fecha_descarga}
**Método de obtención:** HTTP GET requests a la API

## Ubicación

**Coordenadas:** Lat: {LATITUD}, Lon: {LONGITUD}
**Localización:** Presa Abelardo L. Rodríguez, Hermosillo, Sonora, México

## Descripción de los Datos
{info_basico}{info_completo}

## Naturaleza de los Datos

Open-Meteo combina múltiples fuentes de reanálisis meteorológico (ERA5, NCEP, etc.)
para proporcionar datos históricos consistentes y de alta calidad. Estos datos son
esenciales para entender las condiciones climáticas que afectan el llenado y
vaciado de la presa.

Las variables meteorológicas incluyen tanto datos básicos (evapotranspiración)
como un conjunto completo de variables para análisis hidrológico detallado.

## Calidad de Datos

- No hay valores faltantes significativos
- Datos validados por Open-Meteo
- Cobertura temporal completa para el periodo especificado
- Resolución diaria
- Zona horaria: America/Los_Angeles (ajustada automáticamente)

## Uso Recomendado

Estos datos pueden utilizarse para:
- Análisis de balance hídrico
- Estudios de evapotranspiración
- Correlación con niveles de almacenamiento de la presa
- Análisis de patrones climáticos históricos
- Modelado hidrológico

## Limitaciones y Consideraciones

- Los datos de reanálisis pueden tener incertidumbre en zonas con pocas estaciones
- La evapotranspiración ET0 es un valor de referencia (FAO Penman-Monteith)
- La humedad del suelo es modelada, no medida directamente
- API gratuita con límites: 600 req/min, 5,000 req/hora, 10,000 req/día

## Contacto y Licencia

**Proveedor:** Open-Meteo
**Licencia:** Attribution 4.0 International (CC BY 4.0)
**Atribución requerida:** "Data provided by Open-Meteo.com"
**Script de obtención:** `src/data/02_obtener_datos_meteo.py`

---
Generado automáticamente por el pipeline de datos
Fecha de generación: {fecha_descarga}
"""

    # Guardar descripción
    descripcion_file = data_dir / 'FUENTE_datos_meteorologicos.txt'
    with open(descripcion_file, 'w', encoding='utf-8') as f:
        f.write(descripcion)

    print(f"\n[OK] Descripción de fuente guardada: {descripcion_file}")


if __name__ == '__main__':
    obtener_datos_meteorologicos()
