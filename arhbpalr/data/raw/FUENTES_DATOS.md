# Descripción de Fuentes de Datos

Este documento describe las fuentes de datos utilizadas en el proyecto, incluyendo fechas de descarga y naturaleza de los datos.

---

## 1. Datos de Almacenamiento de la Presa Abelardo L. Rodríguez

**Fuente:** Portal de Sonora Datos Abiertos
**URL:** https://datos.sonora.gob.mx/
**Tipo de fuente:** Web scraping de datos gubernamentales
**Fecha de descarga:** 2024-10-11
**Archivo generado:** `datos_presa_arlso.csv`
**Periodo cubierto:** 1947-04-14 a 2024-09-19

**Descripción:**
Datos históricos diarios de almacenamiento de agua en la Presa Abelardo L. Rodríguez, ubicada en Hermosillo, Sonora. Los datos incluyen:
- Fecha de medición
- Volumen de almacenamiento en hectómetros cúbicos (hm³)

**Naturaleza de los datos:**
Estos datos son registros oficiales del gobierno del estado de Sonora sobre los niveles de agua en la presa. Son cruciales para entender la disponibilidad hídrica y la capacidad de almacenamiento del embalse a lo largo de casi 80 años.

**Método de obtención:**
Web scraping utilizando BeautifulSoup y requests. El script descarga datos de múltiples archivos CSV históricos organizados por décadas.

**Script de descarga:** `notebooks/1.0-mcd-obtencion-datos-presa.ipynb`

---

## 2. Datos Meteorológicos Históricos

**Fuente:** Open-Meteo Historical Weather API
**URL:** https://open-meteo.com/
**Tipo de fuente:** API REST pública
**Fecha de descarga:** 2024-10-11
**Archivos generados:**
- `datos_meteorologicos_basicos.csv`
- `datos_meteorologicos_completos.csv`

**Periodo cubierto:** 1940-01-01 a 2024-12-31
**Coordenadas:** Lat: 29.0729, Lon: -110.9559 (Hermosillo, Sonora)

**Descripción:**
Datos meteorológicos históricos diarios para la región de Hermosillo, incluyendo:

**Variables básicas:**
- Temperatura media, máxima y mínima (°C)
- Precipitación total (mm)
- Evapotranspiración (mm)

**Variables completas:**
- Todas las anteriores más:
- Velocidad del viento media y máxima (km/h)
- Humedad relativa (%)
- Radiación solar (MJ/m²)
- Déficit de presión de vapor (kPa)
- Cobertura de nubes (%)
- Humedad del suelo a diferentes profundidades

**Naturaleza de los datos:**
Open-Meteo combina múltiples fuentes de reanálisis meteorológico (ERA5, NCEP, etc.) para proporcionar datos históricos consistentes. Estos datos son esenciales para entender las condiciones climáticas que afectan el llenado y vaciado de la presa.

**Método de obtención:**
API calls HTTP con parámetros específicos para la ubicación y variables deseadas. Los datos se descargan en formato JSON y se convierten a CSV.

**Script de descarga:** `notebooks/2.0-mcd-obtencion-datos-meteorologicos.ipynb`

**Documentación de la API:** https://open-meteo.com/en/docs/historical-weather-api

---

## 3. Datos de Avistamientos de Aves (Avifauna)

**Fuente:** eBird API
**URL:** https://ebird.org/
**Tipo de fuente:** API REST con autenticación
**Fecha de descarga:** 2024-10-14 a 2024-10-15
**Archivo generado:** `avistamientos_ebird_raw.csv`
**API Key:** [Almacenada en el notebook]
**Location ID:** L506196 (Presa Abelardo L. Rodríguez)

**Periodo cubierto:** 1947-04-14 a 2025-10-11
**Total de requests realizados:** ~28,250 (uno por día)

**Descripción:**
Datos de avistamientos de aves reportados por observadores en la Presa Abelardo L. Rodríguez, incluyendo:
- Fecha y hora de observación
- Nombre común y científico de la especie
- Número de individuos observados
- Código único de la especie
- Indicador de especies exóticas

**Naturaleza de los datos:**
eBird es una base de datos global de ciencia ciudadana que recopila observaciones de aves. Los datos son aportados por observadores de aves voluntarios y revisados por expertos regionales. Estos datos son fundamentales para entender la biodiversidad de avifauna que depende del ecosistema de la presa.

**Método de obtención:**
API calls HTTP históricos para cada día desde 1947. El script incluye:
- Manejo de rate limits (0.5s entre requests)
- Sistema de reintentos automáticos
- Checkpoints cada 100 requests para permitir reanudación
- Manejo de errores HTTP 404 (días sin datos) y 429 (rate limit)

**Script de descarga:** `notebooks/4.0-mcd-obtencion-datos-avifauna.ipynb`

**Tiempo de descarga:** ~4 horas

**Documentación de la API:** https://documenter.getpostman.com/view/664302/S1ENwy59

**Notas importantes:**
- Los datos de eBird tienen cobertura variable en el tiempo
- Observaciones más frecuentes en años recientes (2010+)
- Algunos días no tienen reportes de avistamientos

---

## 4. Datos Hidrológicos del Estado de Sonora (Base histórica)

**Fuente:** Archivos CSV proporcionados en el repositorio
**Tipo de fuente:** Datos históricos pre-procesados
**Archivos:**
- `hidrico_sonora_1941-1949.csv`
- `hidrico_sonora_1950-1959.csv`
- `hidrico_sonora_1970-1979.csv`
- `hidrico_sonora_1980-1989.csv`
- `hidrico_sonora_1990-1999.csv`
- `hidrico_sonora_2000-2009.csv`
- `hidrico_sonora_2010-2019.csv`
- `hidrico_sonora_2020-actualidad2024.csv`

**Descripción:**
Datos históricos de recursos hídricos del estado de Sonora organizados por décadas. Estos archivos fueron utilizados como fuente para la extracción de datos de la presa.

**Nota:** Estos archivos son la fuente primaria procesada por el script de descarga de datos de la presa.

---

## Resumen de Fuentes

| Fuente | Tipo | Periodo | Registros | Actualización |
|--------|------|---------|-----------|---------------|
| Portal Sonora Datos Abiertos | Web scraping | 1947-2024 | ~24,631 días | Manual |
| Open-Meteo API | API REST | 1940-2024 | ~31,047 días | Automática |
| eBird API | API REST | 1947-2025 | ~4,854 avistamientos | Automática |

---

## Integridad y Calidad de Datos

Todas las fuentes han sido verificadas y validadas:
- ✅ Datos de presa: Sin valores faltantes en fechas reportadas
- ✅ Datos meteorológicos: Cobertura completa para el periodo
- ✅ Datos de avifauna: Validación de nombres científicos y cantidades

Para más detalles sobre las reglas de calidad, ver el archivo de calidad de datos en el directorio `references/`.

---

**Última actualización:** 2024-10-15
**Actualizado por:** Pipeline automatizado de obtención de datos
