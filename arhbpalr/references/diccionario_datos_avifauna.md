# Diccionario de Datos: Avistamientos de Aves (Avifauna)

## Información General

**Archivo:** `avistamientos_aves_presa.csv`
**Ubicación:** `data/processed/`
**Fuente:** eBird API (Cornell Lab of Ornithology)
**Frecuencia temporal:** Variable (según reportes de observadores)
**Periodo:** 1947-04-14 a 2025-10-11
**Número de registros:** ~4,854 avistamientos
**Location ID:** L506196 (Presa Abelardo L. Rodríguez)

## Descripción

Dataset de avistamientos de aves reportados por observadores en la Presa Abelardo L. Rodríguez. Los datos provienen de eBird, una base de datos global de ciencia ciudadana administrada por el Cornell Lab of Ornithology. Incluye información sobre especies, cantidades observadas y fechas de observación.

## Variables

| Columna | Tipo | Descripción | Ejemplo | Valores faltantes |
|---------|------|-------------|---------|-------------------|
| `fecha` | datetime | Fecha y hora de observación | 2023-05-15 08:30:00 | No permitidos |
| `nombre_comun` | string | Nombre común de la especie | "Great Blue Heron" | Permitidos |
| `nombre_cientifico` | string | Nombre científico de la especie | "Ardea herodias" | No permitidos |
| `codigo_especie` | string | Código único de especie eBird | "grbher3" | Permitidos |
| `cantidad` | integer | Número de individuos observados | 5 | No (mín. 1) |
| `es_exotica` | boolean | Indica si es especie exótica | True/False | No permitidos |

## Descripción Detallada de Variables

### fecha
- **Formato:** YYYY-MM-DD HH:MM:SS
- **Tipo de datos:** datetime64[ns]
- **Descripción:** Fecha y hora en que se realizó la observación
- **Notas:**
  - Algunas observaciones históricas solo tienen fecha sin hora
  - Zona horaria: Local de Hermosillo
  - Los formatos pueden ser mixtos debido a diferentes periodos de registro

### nombre_comun
- **Tipo de datos:** string (texto)
- **Descripción:** Nombre común de la especie en el idioma del observador
- **Ejemplos:**
  - "Great Blue Heron"
  - "American Wigeon"
  - "Eared Grebe"
- **Notas:**
  - Puede estar en inglés o español
  - Algunos registros antiguos pueden no tener nombre común
  - Es preferible usar `nombre_cientifico` para análisis científicos

### nombre_cientifico
- **Tipo de datos:** string (texto)
- **Descripción:** Nombre científico binomial de la especie (Género + especie)
- **Formato:** Según nomenclatura de Clements Checklist
- **Ejemplos:**
  - "Ardea herodias"
  - "Mareca americana"
  - "Podiceps nigricollis"
- **Notas:**
  - **Campo validado:** Todos los registros sin nombre científico fueron eliminados
  - Estándar internacional para identificación inequívoca
  - Puede incluir subespecie en algunos casos

### codigo_especie
- **Tipo de datos:** string (código alfanumérico)
- **Descripción:** Código único de 6 caracteres usado por eBird para identificar especies
- **Formato:** 6 caracteres alfanuméricos en minúsculas
- **Ejemplos:**
  - "grbher3" → Great Blue Heron
  - "amewid" → American Wigeon
  - "eargre" → Eared Grebe
- **Notas:**
  - Útil para joins con otras bases de datos eBird
  - Más compacto que nombres para almacenamiento
  - Algunos registros muy antiguos pueden no tenerlo

### cantidad
- **Tipo de datos:** integer (entero positivo)
- **Descripción:** Número de individuos de la especie observados
- **Rango:** ≥ 1
- **Notas:**
  - Valor mínimo: 1 (cuando no se especificó cantidad, se asume 1)
  - Puede ser estimado o conteo exacto según el observador
  - Valores muy altos (>100) pueden indicar bandadas migratorias
  - **Procesamiento aplicado:** Valores faltantes fueron reemplazados por 1

### es_exotica
- **Tipo de datos:** boolean (True/False)
- **Descripción:** Indica si la especie es considerada exótica o introducida en la región
- **Valores:**
  - `True`: Especie exótica/introducida
  - `False`: Especie nativa
- **Notas:**
  - Basado en la categoría "exoticCategory" de eBird
  - Importante para estudios de biodiversidad nativa
  - Especies exóticas pueden indicar impacto humano

## Taxonomía de Aves en el Dataset

### Grupos Comunes Observados

**Aves acuáticas:**
- Patos (Anatidae)
- Garzas (Ardeidae)
- Cormoranes (Phalacrocoracidae)

**Aves playeras:**
- Playeros y correlimos (Scolopacidae)
- Gaviotas (Laridae)

**Rapaces:**
- Águilas y halcones (Accipitridae, Falconidae)
- Búhos (Strigidae)

**Aves terrestres:**
- Gorriones (Passeridae)
- Colibríes (Trochilidae)

## Notas sobre Calidad de Datos

- **Ciencia ciudadana:** Los datos son aportados por observadores voluntarios
- **Validación:** eBird tiene sistema de revisión por expertos regionales
- **Registros sin nombre científico:** Eliminados durante procesamiento (~0 registros)
- **Cobertura temporal:** Irregular, más denso en años recientes (2010+)
- **Sesgos conocidos:**
  - Más observaciones en fines de semana
  - Más datos en años recientes
  - Algunas especies pueden estar sub-representadas

## Patrones Temporales

- **1947-1999:** Muy pocos reportes (registros históricos escasos)
- **2000-2009:** Incremento gradual de observadores
- **2010-presente:** Mayor densidad de datos
- **Estacionalidad:** Picos en temporadas migratorias (primavera y otoño)

## Uso y Contexto

### Casos de Uso Recomendados
- Análisis de biodiversidad de avifauna
- Estudios de especies indicadoras de calidad del ecosistema
- Correlación con niveles de agua de la presa
- Identificación de especies migratorias vs. residentes
- Análisis temporal de poblaciones
- Evaluación del valor ecológico del embalse

### Limitaciones
- **Cobertura irregular:** No todos los días tienen observaciones
- **Sesgo de observador:** Depende de cuándo y dónde observan las personas
- **Identificaciones:** Pueden contener errores de identificación (aunque validadas)
- **Cantidades estimadas:** No siempre son conteos exactos
- **Especies nocturnas:** Pueden estar sub-representadas

## Análisis Recomendados

### Métricas de Biodiversidad
- **Riqueza de especies:** Número de especies únicas observadas
- **Abundancia relativa:** Suma de individuos por especie
- **Especies indicadoras:** Especies sensibles a cambios en el ecosistema

### Análisis Temporal
- **Series temporales:** Tendencias de abundancia por especie
- **Estacionalidad:** Patrones migratorios y residentes
- **Correlación con agua:** Relación entre nivel de presa y diversidad

### Grupos Ecológicos
- **Aves acuáticas dependientes de la presa**
- **Especies migratorias que usan la presa como escala**
- **Especies residentes permanentes**

## Conversiones y Cálculos Útiles

### Riqueza de Especies (Species Richness)
```python
riqueza = df['nombre_cientifico'].nunique()
```

### Abundancia Total
```python
abundancia_total = df['cantidad'].sum()
```

### Especies Más Comunes
```python
top_especies = df.groupby('nombre_cientifico')['cantidad'].sum().sort_values(ascending=False)
```

### Avistamientos por Mes
```python
df['mes'] = df['fecha'].dt.month
avistamientos_mes = df.groupby('mes').size()
```

## Integración con Otros Datos

Este dataset puede fusionarse con:
- **Datos hidrológicos:** Para analizar impacto del nivel de agua en biodiversidad
- **Datos meteorológicos:** Para estudiar efectos climáticos en poblaciones
- **Datos de calidad de agua:** Si disponibles

**Campo de fusión recomendado:** `fecha` (considerar agregación temporal apropiada)

## Referencias

- **Script de obtención:** `src/data/04_obtener_datos_aves.py`
- **Descripción de fuente:** `data/raw/FUENTE_datos_avifauna.txt`
- **eBird:** https://ebird.org/
- **API Documentation:** https://documenter.getpostman.com/view/664302/S1ENwy59
- **Clements Checklist:** https://www.birds.cornell.edu/clementschecklist/

## Glosario

- **Avifauna:** Conjunto de especies de aves de una región
- **Especie exótica:** Especie no nativa, introducida por humanos
- **Riqueza de especies:** Número de especies diferentes
- **Abundancia:** Número total de individuos
- **Ciencia ciudadana:** Investigación científica con participación pública

---
**Última actualización:** 2024-10-15
**Versión:** 1.0
