# Reglas de Calidad de Datos

## Información General

**Proyecto:** Análisis del Rol Hidrológico y Biológico de la Presa Abelardo L. Rodríguez
**Versión:** 1.0
**Fecha:** 2024-10-15
**Responsable:** MCDproyectos

## Objetivo

Este documento describe las reglas de calidad de datos implementadas en los scripts del proyecto, documentando las transformaciones y validaciones aplicadas durante la obtención y procesamiento de datos.

---

## 1. Reglas Generales

### 1.1 Codificación de Caracteres
- Todos los archivos CSV se guardan con codificación UTF-8
- `encoding='utf-8'` en todas las operaciones de escritura

### 1.2 Formato de Fechas
- Conversión a datetime con formato mixto
- `pd.to_datetime(df['fecha'], format='mixed', errors='coerce')`
- Valores inválidos se convierten a NaT (Not a Time)

### 1.3 Separador de Columnas
- Coma como separador, punto como decimal
- Configuración por defecto de pandas

### 1.4 Nombres de Columnas
- Lowercase snake_case (minúsculas con guiones bajos)
- Ejemplos: `almacenamiento_hm3`, `temp_media_c`, `nombre_cientifico`

---

## 2. Reglas por Dataset

### 2.1 Datos de Presa (datos_presa_arlso.csv)

**Script:** `src/data/01_obtener_datos_presa.py`

**Conversión de tipos:**
```python
df["almacenamiento_hm3"] = pd.to_numeric(df["almacenamiento_hm3"], errors='coerce')
df["fecha"] = pd.to_datetime(df["fecha"], format="mixed", errors='coerce')
```

**Eliminación de valores faltantes:**
```python
df = df.dropna(subset=['fecha', 'almacenamiento_hm3'])
```

**Ordenamiento cronológico:**
```python
df = df.sort_values('fecha').reset_index(drop=True)
```

**Eliminación de columna temporal:**
```python
df.drop("clave", axis=1, inplace=True)
```

---

### 2.2 Datos Meteorológicos (datos_meteorologicos_completos.csv)

**Script:** `src/data/02_obtener_datos_meteo.py`

**Renombrado de columnas:**
```python
df.columns = [
    'fecha', 'precipitacion_mm', 'lluvia_mm', 'evapotranspiracion_mm',
    'temp_media_c', 'temp_max_c', 'temp_min_c', 'horas_precipitacion',
    'viento_max_km_h', 'viento_medio_km_h', 'deficit_presion_vapor_kpa',
    'radiacion_solar_mj_m2', 'humedad_relativa_pct', 'cobertura_nubes_pct',
    'humedad_suelo_0_100cm', 'humedad_suelo_0_7cm',
    'humedad_suelo_28_100cm', 'humedad_suelo_7_28cm'
]
```

**Conversión de fecha:**
```python
df['time'] = pd.to_datetime(df['time'])
```

---

### 2.3 Datos de Avifauna (avistamientos_aves_presa.csv)

**Script:** `src/data/04_obtener_datos_aves.py`

**Conversión de fecha (formato mixto):**
```python
df['fecha'] = pd.to_datetime(df['fecha'], format='mixed')
```

**Conversión de cantidad:**
```python
df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(1).astype(int)
```

**Flag de especie exótica:**
```python
df['es_exotica'] = df['es_exotica'].notna()
```

**Eliminación de registros sin nombre científico:**
```python
len_antes = len(df)
df = df[df['nombre_cientifico'].notna()]
len_despues = len(df)
print(f"✓ Eliminados {len_antes - len_despues:,} registros sin nombre científico")
```

**Ordenamiento cronológico:**
```python
df = df.sort_values('fecha').reset_index(drop=True)
```

**Selección de columnas finales:**
```python
columnas_finales = [
    'fecha', 'nombre_comun', 'nombre_cientifico',
    'codigo_especie', 'cantidad', 'es_exotica'
]
df_final = df[columnas_finales].copy()
```

---

### 2.4 Datos Fusionados (datos_hidrologicos_completos.csv)

**Script:** `src/data/03_fusion_hidrologicos.py`

**Fusión OUTER JOIN:**
```python
df_fusion = pd.merge(
    df_presa, df_meteo,
    on='fecha',
    how='outer',
    indicator=True
)
```

**Ordenamiento:**
```python
df_fusion = df_fusion.sort_values('fecha').reset_index(drop=True)
```

**Indicador de completitud:**
```python
df_fusion['datos_completos'] = (
    df_fusion['almacenamiento_hm3'].notna() &
    df_fusion['evapotranspiracion_mm'].notna()
)
```

**Eliminación de columna temporal:**
```python
df_fusion = df_fusion.drop(columns=['_merge'])
```

---

## 3. Manejo de Valores Faltantes

### Estrategia por Dataset

| Dataset | Columna | Acción |
|---------|---------|--------|
| **Presa** | fecha | Eliminar registro |
| **Presa** | almacenamiento_hm3 | Eliminar registro |
| **Meteo** | todas | Mantener como está |
| **Aves** | fecha | Mantener (conversión con format='mixed') |
| **Aves** | nombre_cientifico | Eliminar registro |
| **Aves** | nombre_comun | Mantener NaN |
| **Aves** | codigo_especie | Mantener NaN |
| **Aves** | cantidad | Reemplazar por 1 |
| **Aves** | es_exotica | Convertir a False |
| **Fusionado** | todas | Mantener NaN, usar columna datos_completos |

---

## 4. Documentación de Transformaciones

### Logging en Consola

Todos los scripts imprimen información de progreso:

```python
print(f"✓ Datos cargados")
print(f"  Registros: {len(df):,}")
print(f"  Columnas: {list(df.columns)}")
print(f"  Rango: {df['fecha'].min().date()} a {df['fecha'].max().date()}")
```

### Archivos de Descripción Automáticos

Cada script genera archivo de texto con metadata:
- `FUENTE_datos_presa.txt`
- `FUENTE_datos_meteorologicos.txt`
- `FUENTE_datos_avifauna.txt`
- `PROCESO_fusion_hidrologicos.txt`

---

## 5. Verificación de Salida

**Verificación de guardado exitoso:**
```python
output_file = data_dir / 'archivo.csv'
df.to_csv(output_file, index=False)

# Verificar tamaño
file_size = output_file.stat().st_size / 1024
print(f"  Tamaño: {file_size:.2f} KB")
```

**Verificación de registros:**
```python
print(f"✓ Archivo guardado: {output_file}")
print(f"  - Registros: {len(df):,}")
print(f"  - Columnas: {len(df.columns)}")
```

---

## 6. Gestión de Archivos Temporales

**Script 01 (Presa):**
```python
temp_dir = 'temp_csv'
# ... procesamiento ...
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
```

**Script 04 (Aves) - Checkpoints:**
```python
checkpoint_file = data_raw / 'checkpoint_avistamientos.json'
checkpoint_data_file = data_raw / 'avistamientos_checkpoint.csv'

# Después de completar
if checkpoint_file.exists():
    checkpoint_file.unlink()
if checkpoint_data_file.exists():
    checkpoint_data_file.unlink()
```

### Sistema de Checkpoints (Script 04)

```python
# Guardar progreso cada 100 requests
if (idx + 1) % CHECKPOINT_INTERVAL == 0:
    checkpoint_data = {
        'fechas_procesadas': list(fechas_procesadas),
        'ultima_actualizacion': datetime.now().isoformat(),
        'stats': {...}
    }
    with open(checkpoint_file, 'w') as f:
        json.dump(checkpoint_data, f)
```

---

## 7. Validación de Existencia de Archivos

```python
if not file_path.exists():
    raise FileNotFoundError(f"❌ No se encontró {file_path}")
```

---

## 8. Resumen de Transformaciones por Script

| Transformación | Script 01 | Script 02 | Script 03 | Script 04 |
|----------------|-----------|-----------|-----------|-----------|
| Conversión de tipos con errors='coerce' | ✓ | ✓ | - | ✓ |
| Formato mixto para fechas | ✓ | ✓ | - | ✓ |
| Eliminación de valores faltantes | ✓ | - | - | ✓ |
| Ordenamiento cronológico | ✓ | ✓ | ✓ | ✓ |
| Renombrado a snake_case | ✓ | ✓ | - | ✓ |
| Codificación UTF-8 | ✓ | ✓ | ✓ | ✓ |
| Generación de archivos de descripción | ✓ | ✓ | ✓ | ✓ |
| Logging de transformaciones | ✓ | ✓ | ✓ | ✓ |
| Limpieza de archivos temporales | ✓ | - | - | ✓ |

---

**Última actualización:** 2024-10-15
**Versión:** 1.0
