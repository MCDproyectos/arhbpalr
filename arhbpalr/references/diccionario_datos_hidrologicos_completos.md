# Diccionario de Datos: Datos Hidrológicos Completos (Fusionado)

## Información General

**Archivo:** `datos_hidrologicos_completos.csv`
**Ubicación:** `data/processed/`
**Tipo:** Dataset fusionado (presa + meteorología)
**Frecuencia temporal:** Diaria
**Periodo:** 1940-01-01 a 2024-12-31
**Número de registros:** ~31,066 días
**Método de fusión:** OUTER JOIN (preserva todas las fechas de ambos datasets)

## Descripción

Dataset integrado que combina datos de almacenamiento de la Presa Abelardo L. Rodríguez con variables meteorológicas. Permite análisis hidrológico completo incluyendo correlaciones entre niveles de agua y condiciones climáticas.

La fusión utiliza estrategia OUTER JOIN para preservar todos los registros históricos, lo que resulta en algunos valores faltantes cuando solo existe información de una de las fuentes.

## Variables

Total de **20 columnas**: 1 fecha + 1 almacenamiento + 17 meteorológicas + 1 indicadora

| Columna | Tipo | Unidad | Fuente | Descripción |
|---------|------|--------|--------|-------------|
| `fecha` | datetime | - | Ambas | Fecha de medición |
| `almacenamiento_hm3` | float | hm³ | Presa | Volumen de agua en la presa |
| `precipitacion_mm` | float | mm | Meteo | Precipitación total diaria |
| `lluvia_mm` | float | mm | Meteo | Lluvia diaria |
| `evapotranspiracion_mm` | float | mm | Meteo | Evapotranspiración ET0 FAO |
| `temp_media_c` | float | °C | Meteo | Temperatura media |
| `temp_max_c` | float | °C | Meteo | Temperatura máxima |
| `temp_min_c` | float | °C | Meteo | Temperatura mínima |
| `horas_precipitacion` | float | horas | Meteo | Horas con precipitación |
| `viento_max_km_h` | float | km/h | Meteo | Velocidad máxima del viento |
| `viento_medio_km_h` | float | km/h | Meteo | Velocidad media del viento |
| `deficit_presion_vapor_kpa` | float | kPa | Meteo | Déficit de presión de vapor |
| `radiacion_solar_mj_m2` | float | MJ/m² | Meteo | Radiación solar |
| `humedad_relativa_pct` | float | % | Meteo | Humedad relativa |
| `cobertura_nubes_pct` | float | % | Meteo | Cobertura de nubes |
| `humedad_suelo_0_100cm` | float | m³/m³ | Meteo | Humedad del suelo 0-100cm |
| `humedad_suelo_0_7cm` | float | m³/m³ | Meteo | Humedad del suelo 0-7cm |
| `humedad_suelo_28_100cm` | float | m³/m³ | Meteo | Humedad del suelo 28-100cm |
| `humedad_suelo_7_28cm` | float | m³/m³ | Meteo | Humedad del suelo 7-28cm |
| `datos_completos` | boolean | - | Calculada | True si hay datos de ambas fuentes |

## Variables por Categoría

### 1. Identificación Temporal
- `fecha`: Variable de fusión y análisis temporal

### 2. Hidrología (1 variable)
- `almacenamiento_hm3`: Variable objetivo principal para muchos análisis

### 3. Precipitación y Evapotranspiración (3 variables)
- `precipitacion_mm`: Input principal al balance hídrico
- `lluvia_mm`: Precipitación líquida
- `evapotranspiracion_mm`: Output del balance hídrico

### 4. Temperatura (3 variables)
- `temp_media_c`, `temp_max_c`, `temp_min_c`: Afectan evaporación

### 5. Viento (2 variables)
- `viento_max_km_h`, `viento_medio_km_h`: Afectan evaporación del embalse

### 6. Humedad y Presión (2 variables)
- `deficit_presion_vapor_kpa`: Demanda evaporativa
- `humedad_relativa_pct`: Condiciones atmosféricas

### 7. Radiación y Nubosidad (2 variables)
- `radiacion_solar_mj_m2`: Energía para evaporación
- `cobertura_nubes_pct`: Modula radiación

### 8. Humedad del Suelo (4 variables)
- `humedad_suelo_*`: Indicadores de recarga de acuíferos

### 9. Calidad de Datos (1 variable)
- `datos_completos`: Facilita filtrado para análisis

## Descripción Detallada de Variables Clave

### datos_completos
- **Tipo:** boolean (True/False)
- **Descripción:** Indica si el registro tiene datos tanto de presa como meteorológicos
- **Cálculo:** `(almacenamiento_hm3 is not null) AND (evapotranspiracion_mm is not null)`
- **Uso:**
  ```python
  # Filtrar solo registros completos
  df_completo = df[df['datos_completos'] == True]
  ```
- **Estadísticas:**
  - Registros completos: ~24,000 días (~77%)
  - Registros incompletos: ~7,000 días (~23%)

### Periodos de Datos Incompletos

**Solo datos meteorológicos (sin presa):**
- Antes de 1947-04-14
- Después de 2024-09-19

**Solo datos de presa (sin meteorología):**
- Antes de 1940-01-01 (no aplicable, la presa es más reciente)

## Cobertura Temporal

| Periodo | Presa | Meteorología | Completo |
|---------|-------|--------------|----------|
| 1940-01-01 a 1947-04-13 | ❌ | ✅ | ❌ |
| 1947-04-14 a 2024-09-19 | ✅ | ✅ | ✅ |
| 2024-09-20 a 2024-12-31 | ❌ | ✅ | ❌ |

## Valores Faltantes

Los valores faltantes (NaN) aparecen principalmente en:
- `almacenamiento_hm3`: ~22% (fechas antes de la presa o después del último reporte)
- Variables meteorológicas: ~21% (fechas después de los reportes de presa)

**Recomendación:** Usar la columna `datos_completos` para filtrar según necesidades del análisis.

## Casos de Uso por Tipo de Análisis

### 1. Análisis de Correlación
```python
# Usar solo datos completos
df_analisis = df[df['datos_completos'] == True]
correlacion = df_analisis[['almacenamiento_hm3', 'precipitacion_mm']].corr()
```

### 2. Balance Hídrico
**Variables clave:**
- Input: `precipitacion_mm`
- Output: `evapotranspiracion_mm`
- Storage: `almacenamiento_hm3`

**Cálculo simplificado:**
```python
df['balance_simple'] = df['precipitacion_mm'] - df['evapotranspiracion_mm']
```

### 3. Análisis de Sequía
**Indicadores:**
- Precipitación acumulada mensual/anual
- Persistencia de niveles bajos de almacenamiento
- Índices de evaporación vs precipitación

### 4. Modelado Predictivo
**Variables predictoras (X):**
- Todas las meteorológicas
- Lags de almacenamiento previo

**Variable objetivo (y):**
- `almacenamiento_hm3`

### 5. Series Temporales
```python
# Análisis de tendencias
df_ts = df[df['datos_completos'] == True].set_index('fecha')
df_ts['almacenamiento_hm3'].resample('M').mean()
```

## Agregaciones Temporales Recomendadas

### Mensual
```python
# Agregación mensual
df_monthly = df.groupby(df['fecha'].dt.to_period('M')).agg({
    'almacenamiento_hm3': 'mean',
    'precipitacion_mm': 'sum',
    'evapotranspiracion_mm': 'sum',
    'temp_media_c': 'mean'
})
```

### Anual
```python
# Agregación anual
df_yearly = df.groupby(df['fecha'].dt.year).agg({
    'almacenamiento_hm3': ['mean', 'min', 'max'],
    'precipitacion_mm': 'sum',
    'evapotranspiracion_mm': 'sum'
})
```

### Por Estación
```python
# Clasificar por estación
def get_season(month):
    if month in [12, 1, 2]: return 'Invierno'
    elif month in [3, 4, 5]: return 'Primavera'
    elif month in [6, 7, 8]: return 'Verano'
    else: return 'Otoño'

df['estacion'] = df['fecha'].dt.month.apply(get_season)
```

## Fórmulas y Cálculos Útiles

### Balance Hídrico Simplificado
```
ΔS ≈ P - ET - O
```
Donde:
- ΔS = Cambio en almacenamiento
- P = Precipitación
- ET = Evapotranspiración
- O = Otras salidas (no capturadas en este dataset)

### Evaporación del Embalse
La evaporación del embalse puede aproximarse usando:
- Temperatura
- Humedad relativa
- Velocidad del viento
- Radiación solar

### Índice de Aridez
```
IA = Precipitación / Evapotranspiración
```
- IA < 0.5: Árido
- 0.5 < IA < 0.75: Semiárido
- IA > 0.75: Subhúmedo

## Calidad de Datos

### Fortalezas
- ✅ Cobertura temporal extensa (>80 años)
- ✅ Variables validadas de fuentes oficiales
- ✅ Fusión preserva todos los datos históricos
- ✅ Indicador de completitud facilita análisis

### Limitaciones
- ⚠️ ~23% de registros incompletos
- ⚠️ Datos meteorológicos son de reanálisis (no mediciones directas)
- ⚠️ No incluye datos de entradas/salidas de agua de la presa
- ⚠️ Capacidad de la presa ha cambiado por azolve

## Integración con Otros Datos

### Datos de Avifauna
```python
# Fusionar con avistamientos de aves
df_merged = pd.merge(
    df_hidro,
    df_aves,
    on='fecha',
    how='left'
)
```

### Datos de Calidad de Agua
Si se obtienen datos de calidad de agua, pueden fusionarse usando `fecha` como key.

## Referencias Cruzadas

- **Datos de presa:** Ver `diccionario_datos_presa.md`
- **Datos meteorológicos:** Ver `diccionario_datos_meteorologicos.md`
- **Proceso de fusión:** Ver `data/processed/PROCESO_fusion_hidrologicos.txt`
- **Script de fusión:** `src/data/03_fusion_hidrologicos.py`

## Visualizaciones Recomendadas

1. **Serie temporal de almacenamiento** con precipitación como barras
2. **Scatter plot** de precipitación vs cambio en almacenamiento
3. **Heatmap** de correlaciones entre variables
4. **Box plots** de almacenamiento por estación del año
5. **Gráficos de balance hídrico** mensual/anual

---
**Última actualización:** 2024-10-15
**Versión:** 1.0
