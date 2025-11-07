# Diccionario de Datos: Presa Abelardo L. Rodríguez

## Información General

**Archivo:** `datos_presa_arlso.csv`
**Ubicación:** `data/raw/`
**Fuente:** Portal de Sonora Datos Abiertos
**Frecuencia temporal:** Diaria
**Periodo:** 1947-04-14 a 2024-09-19
**Número de registros:** ~24,631 días

## Descripción

Dataset de almacenamiento diario de agua en la Presa Abelardo L. Rodríguez, ubicada en Hermosillo, Sonora. Contiene mediciones históricas del volumen de agua almacenado en hectómetros cúbicos.

## Variables

| Columna | Tipo | Unidad | Descripción | Valores permitidos | Valores faltantes |
|---------|------|--------|-------------|-------------------|-------------------|
| `fecha` | datetime | - | Fecha de la medición | 1947-04-14 a 2024-09-19 | No permitidos |
| `almacenamiento_hm3` | float | hm³ | Volumen de agua almacenado en hectómetros cúbicos | ≥ 0.0 | No en registros reportados |

## Descripción Detallada de Variables

### fecha
- **Formato:** YYYY-MM-DD
- **Tipo de datos:** datetime64[ns] en pandas
- **Descripción:** Fecha en la que se realizó la medición del nivel de almacenamiento de la presa
- **Notas:**
  - No todos los días del periodo tienen mediciones
  - Los datos más antiguos pueden tener frecuencia irregular
  - Datos más recientes (2000+) tienen mayor consistencia temporal

### almacenamiento_hm3
- **Formato:** Numérico decimal (float)
- **Unidad:** Hectómetros cúbicos (hm³)
- **Descripción:** Volumen total de agua almacenado en la presa
- **Rango esperado:** 0.0 a capacidad máxima de diseño (~200 hm³)
- **Valores típicos:**
  - Mínimo histórico: Cercano a 0 en periodos de sequía extrema
  - Máximo histórico: Varía según capacidad de azolve
- **Notas:**
  - 1 hm³ = 1,000,000 m³
  - La capacidad ha disminuido con el tiempo debido al azolve
  - Valores de 0 o cercanos a 0 indican sequía severa

## Notas sobre Calidad de Datos

- **Valores faltantes:** No hay valores faltantes en las fechas reportadas, pero existen brechas temporales donde no se reportaron mediciones
- **Duplicados:** No se encontraron fechas duplicadas
- **Consistencia:** Los valores son consistentes con la capacidad conocida de la presa
- **Validación:** Todos los valores numéricos fueron validados durante la limpieza

## Uso y Contexto

### Casos de Uso Recomendados
- Análisis de tendencias históricas del almacenamiento
- Estudios de disponibilidad hídrica en Hermosillo
- Correlación con variables climáticas (precipitación, evapotranspiración)
- Evaluación del impacto de sequías
- Modelado predictivo de niveles de agua

### Limitaciones
- La capacidad de almacenamiento ha cambiado debido al azolve
- Frecuencia de mediciones puede variar en datos históricos antiguos
- No incluye información sobre entradas/salidas de agua

## Conversiones Útiles

- 1 hm³ = 1,000,000 m³
- 1 hm³ = 1,000,000,000 litros
- 1 hm³ = 810.71 acre-feet

## Referencias

- **Script de obtención:** `src/data/01_obtener_datos_presa.py`
- **Descripción de fuente:** `data/raw/FUENTE_datos_presa.txt`
- **Portal de datos:** https://datos.sonora.gob.mx/

---
**Última actualización:** 2024-10-15
**Versión:** 1.0
