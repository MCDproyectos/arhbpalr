# ***Análisis del Rol Hidrológico y Biológico de la Presa Abelardo L. Rodríguez***

<img width="1610" height="554" alt="image" src="https://github.com/user-attachments/assets/a1b7d23f-94ed-460a-a739-f86dea750477" />


============================================================================================

Este proyecto utiliza técnicas de ciencia de datos e ingeniería de características para evaluar la importancia actual de la presa Abelardo L. Rodríguez en Hermosillo, Sonora, como un sistema socio-ecológico vital. A través del análisis de datos hidrológicos, climáticos y de biodiversidad, buscamos cuantificar su rol en la recarga de acuíferos y como soporte de un ecosistema clave, con un enfoque especial en la avifauna.

## Guía de inicio rápido

### 1. Requisitos previos

- Python 3.8 o superior
- Make (para Windows: instalar con `choco install make` o usar Git Bash)
- Conexión a Internet estable

### 2. Instalación del entorno

**Windows:**
```powershell
# Navegar al directorio del proyecto
cd arhbpalr

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
# Navegar al directorio del proyecto
cd arhbpalr

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Obtención de datos

#### Opción A: Pipeline automatizado (recomendado) ⭐

**Ejecutar con Make:**
```bash
cd arhbpalr
make pipeline
```

**Ejecutar con Python (alternativa si Make no está disponible):**
```bash
cd arhbpalr
python src/data/run_pipeline.py
```

**¿Qué hace el pipeline?**
- Ejecuta automáticamente los 4 scripts de Python en secuencia
- Verifica que todos los archivos de salida se generen correctamente
- Muestra progreso detallado con timestamps
- Maneja errores y reporta problemas
- **Tiempo estimado total: 4-5 horas**

**Salida esperada:**
```
======================================================================
INICIANDO PIPELINE DE OBTENCIÓN DE DATOS
======================================================================
Scripts a ejecutar: 4
  1. 01_obtener_datos_presa.py
  2. 02_obtener_datos_meteo.py
  3. 03_fusion_hidrologicos.py
  4. 04_obtener_datos_aves.py
...
✅ Pipeline completado exitosamente!
```

#### Opción B: Ejecución manual de scripts

Los datos se obtienen mediante cuatro scripts de Python ejecutados en secuencia:

1. **`src/data/01_obtener_datos_presa.py`**
   - Obtiene datos históricos de almacenamiento de la presa mediante web scraping
   - Fuente: Portal de Sonora Datos Abiertos
   - Salida: `data/raw/datos_presa_arlso.csv`
   - Genera: `data/raw/FUENTE_datos_presa.txt`

2. **`src/data/02_obtener_datos_meteo.py`**
   - Obtiene datos meteorológicos históricos desde Open-Meteo API
   - Variables: precipitación, temperatura, evapotranspiración, viento, humedad, etc.
   - Salidas:
     - `data/raw/datos_meteorologicos_basicos.csv`
     - `data/raw/datos_meteorologicos_completos.csv`
   - Genera: `data/raw/FUENTE_datos_meteorologicos.txt`

3. **`src/data/03_fusion_hidrologicos.py`**
   - Fusiona datos de presa con datos meteorológicos
   - Estrategia: OUTER JOIN para preservar todos los registros históricos
   - Salida: `data/processed/datos_hidrologicos_completos.csv`
   - Genera: `data/processed/PROCESO_fusion_hidrologicos.txt`

4. **`src/data/04_obtener_datos_aves.py`**
   - Obtiene datos históricos de avistamientos de aves desde eBird API
   - Rango temporal: 1947-2025 (alineado con datos de presa)
   - Localización: Presa Abelardo L. Rodríguez (L506196)
   - Sistema robusto con reintentos, manejo de rate limits y checkpoints
   - Salidas:
     - `data/raw/avistamientos_ebird_raw.csv`
     - `data/processed/avistamientos_aves_presa.csv`
   - Genera: `data/raw/FUENTE_datos_avifauna.txt`
   - Tiempo estimado de ejecución: ~4 horas

**Ejecutar manualmente:**
```bash
cd arhbpalr
python src/data/01_obtener_datos_presa.py
python src/data/02_obtener_datos_meteo.py
python src/data/03_fusion_hidrologicos.py
python src/data/04_obtener_datos_aves.py
```

### 4. Análisis

Una vez obtenidos los datos fusionados y de avifauna, los datasets están listos para análisis que integren:
- Correlaciones entre niveles de agua y biodiversidad de aves
- Patrones estacionales de avifauna
- Impacto del ecosistema de la presa en especies migratorias y residentes
- Análisis exploratorio, modelado y visualizaciones

---

## Comandos Make disponibles

El proyecto incluye un Makefile con comandos útiles para gestionar el proyecto:

| Comando | Descripción | Tiempo estimado |
|---------|-------------|-----------------|
| `make help` | Muestra todos los comandos disponibles | Instantáneo |
| `make requirements` | Instala todas las dependencias de Python | 2-3 minutos |
| `make pipeline` | **Ejecuta el pipeline completo de obtención de datos** | **4-5 horas** |
| `make clean` | Elimina archivos compilados de Python | Instantáneo |
| `make lint` | Ejecuta flake8 para verificar calidad del código | 1 minuto |

### Ejemplo de uso completo:

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/arhbpalr.git
cd arhbpalr/arhbpalr

# 2. Crear entorno virtual e instalar dependencias
python -m venv .venv
.\.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Ejecutar pipeline completo
make pipeline

# 4. Los datos estarán listos en:
#    - data/raw/*.csv
#    - data/processed/*.csv
```

---

## Troubleshooting (Solución de problemas)

### Problema: "jupyter nbconvert no encontrado"
**Solución:**
```bash
pip install jupyter nbconvert
```

### Problema: "make: command not found" (Windows)
**Solución 1 - Usar Python directamente:**
```bash
python src/data/run_pipeline.py
```

**Solución 2 - Instalar Make:**
```powershell
# Con Chocolatey
choco install make

# O usar Git Bash que incluye make
```

### Problema: "python3: command not found" (Windows)
**Solución:** El Makefile ya está configurado para usar `python` en lugar de `python3`.

### Problema: Pipeline se interrumpe en script 04
**Solución:** El script 04 tiene sistema de checkpoints. Si se interrumpe:
1. Ejecuta manualmente: `python src/data/04_obtener_datos_aves.py`
2. O vuelve a ejecutar `make pipeline` (continuará desde el checkpoint)

### Problema: "Rate limit" en eBird API
**Solución:** El script 04 ya tiene manejo automático de rate limits. Simplemente espera, el script reintentará automáticamente.

---

## Archivos de salida generados

Después de ejecutar el pipeline exitosamente, encontrarás:

**data/raw/** (datos crudos de las APIs):
- `datos_presa_arlso.csv` (~640 KB) - Datos de almacenamiento de la presa
- `datos_meteorologicos_basicos.csv` (~500 KB) - Datos meteorológicos básicos
- `datos_meteorologicos_completos.csv` (~2.8 MB) - Datos meteorológicos completos
- `avistamientos_ebird_raw.csv` (~300 KB) - Avistamientos crudos de eBird

**data/processed/** (datos procesados y limpios):
- `datos_hidrologicos_completos.csv` (~3.1 MB) - Fusión de datos de presa y meteorológicos
- `avistamientos_aves_presa.csv` (~330 KB) - Avistamientos de aves procesados

---

## Documentación de Datos

### Archivos de Descripción de Fuentes

Cada script de obtención de datos genera automáticamente un archivo de texto con información detallada sobre la fuente:

**data/raw/**:
- `FUENTE_datos_presa.txt` - Descripción de datos de almacenamiento de la presa
- `FUENTE_datos_meteorologicos.txt` - Descripción de datos meteorológicos de Open-Meteo
- `FUENTE_datos_avifauna.txt` - Descripción de datos de avistamientos de eBird

**data/processed/**:
- `PROCESO_fusion_hidrologicos.txt` - Descripción del proceso de fusión de datos

Estos archivos incluyen:
- Información de la fuente (URL, tipo, método de obtención)
- Fecha de descarga/procesamiento
- Descripción de variables
- Estadísticas de cobertura temporal
- Notas sobre calidad de datos
- Uso recomendado y limitaciones

### Diccionarios de Datos

Los diccionarios de datos detallados se encuentran en `references/`:

- `diccionario_datos_presa.md` - Dataset de almacenamiento de la presa
- `diccionario_datos_meteorologicos.md` - Dataset meteorológico completo (18 variables)
- `diccionario_datos_avifauna.md` - Dataset de avistamientos de aves
- `diccionario_datos_hidrologicos_completos.md` - Dataset fusionado (20 columnas)

Cada diccionario incluye:
- Descripción de cada variable (tipo, unidad, rango válido)
- Contexto y uso recomendado
- Notas sobre calidad de datos
- Ejemplos de análisis y visualizaciones
- Conversiones útiles y fórmulas

### Reglas de Calidad de Datos

El documento `references/reglas_calidad_datos.md` especifica:
- Reglas de validación aplicadas a cada dataset
- Manejo de valores faltantes y atípicos
- Verificaciones de consistencia
- Transformaciones aplicadas
- Checklist de calidad pre/post-guardado

### Archivo Central de Fuentes

El archivo `data/raw/FUENTES_DATOS.md` proporciona una visión consolidada de todas las fuentes de datos del proyecto, incluyendo fechas de descarga y métodos de obtención.

---

## Hipótesis
A pesar de la disminución de su capacidad de almacenamiento por el azolve, el embalse de la presa Abelardo L. Rodríguez sigue funcionando como un regulador hídrico crucial para la recarga de acuíferos y sostiene un ecosistema de alta biodiversidad, especialmente de avifauna, cuya pérdida no se ha considerado en la propuesta de su clausura.

## Objetivo
Cuantificar el rol hidrológico y biológico actual del sistema de la presa Abelardo L. Rodríguez para generar una evaluación basada en evidencia sobre los impactos ambientales y de gestión de agua que tendría su clausura.



Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
