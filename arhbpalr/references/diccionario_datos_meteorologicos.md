# Diccionario de Datos: Datos Meteorológicos Completos

## Información General

**Archivo:** `datos_meteorologicos_completos.csv`
**Ubicación:** `data/raw/`
**Fuente:** Open-Meteo Historical Weather API
**Frecuencia temporal:** Diaria
**Periodo:** 1940-01-01 a 2024-12-31
**Número de registros:** ~31,047 días
**Coordenadas:** Lat: 29.067999, Lon: -110.910734 (Hermosillo, Sonora)

## Descripción

Dataset meteorológico histórico diario para la región de Hermosillo, Sonora. Combina datos de reanálisis de múltiples fuentes (ERA5, NCEP) proporcionados por Open-Meteo API. Incluye 18 variables meteorológicas esenciales para análisis hidrológico.

## Variables

| Columna | Tipo | Unidad | Descripción | Rango típico |
|---------|------|--------|-------------|--------------|
| `fecha` | datetime | - | Fecha de la medición | 1940-01-01 a 2024-12-31 |
| `precipitacion_mm` | float | mm | Precipitación total diaria | 0 - 150 |
| `lluvia_mm` | float | mm | Lluvia diaria (excluye nieve) | 0 - 150 |
| `evapotranspiracion_mm` | float | mm | Evapotranspiración ET0 FAO | 0 - 15 |
| `temp_media_c` | float | °C | Temperatura media del aire a 2m | -5 - 45 |
| `temp_max_c` | float | °C | Temperatura máxima diaria a 2m | 0 - 50 |
| `temp_min_c` | float | °C | Temperatura mínima diaria a 2m | -10 - 30 |
| `horas_precipitacion` | float | horas | Horas con precipitación | 0 - 24 |
| `viento_max_km_h` | float | km/h | Velocidad máxima del viento a 10m | 0 - 100 |
| `viento_medio_km_h` | float | km/h | Velocidad media del viento a 10m | 0 - 50 |
| `deficit_presion_vapor_kpa` | float | kPa | Déficit de presión de vapor máximo | 0 - 8 |
| `radiacion_solar_mj_m2` | float | MJ/m² | Radiación solar de onda corta | 0 - 35 |
| `humedad_relativa_pct` | float | % | Humedad relativa media | 0 - 100 |
| `cobertura_nubes_pct` | float | % | Cobertura de nubes media | 0 - 100 |
| `humedad_suelo_0_100cm` | float | m³/m³ | Humedad del suelo 0-100cm | 0 - 0.5 |
| `humedad_suelo_0_7cm` | float | m³/m³ | Humedad del suelo 0-7cm | 0 - 0.5 |
| `humedad_suelo_28_100cm` | float | m³/m³ | Humedad del suelo 28-100cm | 0 - 0.5 |
| `humedad_suelo_7_28cm` | float | m³/m³ | Humedad del suelo 7-28cm | 0 - 0.5 |

## Descripción Detallada de Variables

### fecha
- **Formato:** YYYY-MM-DD
- **Tipo de datos:** datetime64[ns]
- **Descripción:** Fecha de la medición meteorológica
- **Cobertura:** Completa sin brechas para el periodo especificado

### precipitacion_mm
- **Descripción:** Suma de precipitación total diaria (incluye lluvia, nieve derretida, granizo)
- **Método de cálculo:** Acumulación diaria de todos los tipos de precipitación
- **Notas:** En Hermosillo es principalmente lluvia, nieve es extremadamente rara

### lluvia_mm
- **Descripción:** Precipitación líquida únicamente
- **Diferencia con precipitacion_mm:** Excluye nieve y otros tipos de precipitación sólida
- **Notas:** En clima de Sonora, generalmente igual a precipitacion_mm

### evapotranspiracion_mm
- **Descripción:** Evapotranspiración de referencia calculada con método FAO Penman-Monteith
- **Uso:** Estándar para cálculos de balance hídrico y necesidades de riego
- **Notas:**
  - Valor de referencia para pasto
  - Factores: temperatura, humedad, viento, radiación solar

### Temperaturas (temp_media_c, temp_max_c, temp_min_c)
- **Altura de medición:** 2 metros sobre el suelo
- **temp_media_c:** Promedio de temperaturas durante el día
- **temp_max_c:** Temperatura máxima alcanzada en el día
- **temp_min_c:** Temperatura mínima alcanzada en el día
- **Contexto Hermosillo:** Clima cálido-seco con veranos muy calurosos (>40°C)

### horas_precipitacion
- **Descripción:** Número de horas en el día con precipitación detectada
- **Rango:** 0 a 24 horas
- **Notas:** Útil para distinguir entre lluvias intensas cortas y lluvias ligeras prolongadas

### Viento (viento_max_km_h, viento_medio_km_h)
- **Altura de medición:** 10 metros sobre el suelo
- **viento_max_km_h:** Ráfaga máxima registrada en el día
- **viento_medio_km_h:** Velocidad promedio del viento
- **Importancia:** Afecta evapotranspiración y evaporación del embalse

### deficit_presion_vapor_kpa
- **Descripción:** Diferencia entre presión de vapor de saturación y presión de vapor real
- **Unidad:** Kilopascales (kPa)
- **Importancia:** Indicador de demanda evaporativa de la atmósfera
- **Valores altos:** Mayor evaporación potencial

### radiacion_solar_mj_m2
- **Descripción:** Radiación solar de onda corta acumulada diaria
- **Unidad:** Megajulios por metro cuadrado
- **Importancia:** Factor clave en evapotranspiración y balance energético

### humedad_relativa_pct
- **Descripción:** Humedad relativa media del aire
- **Unidad:** Porcentaje (%)
- **Rango:** 0-100%
- **Contexto:** Hermosillo tiene humedad típicamente baja (20-40%) excepto en temporada de lluvias

### cobertura_nubes_pct
- **Descripción:** Porcentaje promedio del cielo cubierto por nubes
- **Unidad:** Porcentaje (%)
- **Notas:** Afecta radiación solar y temperaturas

### Humedad del Suelo (4 variables)
- **Unidad:** m³/m³ (contenido volumétrico de agua)
- **Método:** Modelado, no medido directamente
- **Profundidades:**
  - `0-7cm`: Capa superficial
  - `7-28cm`: Zona de raíces superficiales
  - `28-100cm`: Zona de raíces profundas
  - `0-100cm`: Promedio de perfil completo
- **Notas:** Útil para análisis de recarga de acuíferos y vegetación

## Notas sobre Calidad de Datos

- **Valores faltantes:** No hay valores faltantes significativos
- **Fuente:** Datos de reanálisis validados por Open-Meteo
- **Cobertura temporal:** Completa para el periodo especificado
- **Resolución:** Diaria
- **Zona horaria:** America/Los_Angeles (ajustada automáticamente)

## Uso y Contexto

### Casos de Uso Recomendados
- Balance hídrico de la presa
- Correlación con niveles de almacenamiento
- Análisis de patrones climáticos históricos
- Modelado hidrológico
- Estudios de evaporación del embalse
- Análisis de sequías

### Limitaciones
- Datos de reanálisis pueden tener incertidumbre en zonas con pocas estaciones
- Humedad del suelo es modelada, no medida directamente
- Los valores representan promedios de área, no puntos exactos

## Conversiones Útiles

### Evapotranspiración y Precipitación
- 1 mm de agua = 1 litro/m²
- Para calcular volumen en la presa: mm × área_embalse_m²

### Temperatura
- °F = (°C × 9/5) + 32
- K = °C + 273.15

### Radiación Solar
- 1 MJ/m² ≈ 0.0864 kWh/m²

## Referencias

- **Script de obtención:** `src/data/02_obtener_datos_meteo.py`
- **Descripción de fuente:** `data/raw/FUENTE_datos_meteorologicos.txt`
- **API:** https://open-meteo.com/
- **Documentación:** https://open-meteo.com/en/docs/historical-weather-api

---
**Última actualización:** 2024-10-15
**Versión:** 1.0
