# ***Análisis del Rol Hidrológico y Biológico de la Presa Abelardo L. Rodríguez***

<img width="1610" height="554" alt="image" src="https://github.com/user-attachments/assets/a1b7d23f-94ed-460a-a739-f86dea750477" />


============================================================================================

Este proyecto utiliza técnicas de ciencia de datos e ingeniería de características para evaluar la importancia actual de la presa Abelardo L. Rodríguez en Hermosillo, Sonora, como un sistema socio-ecológico vital. A través del análisis de datos hidrológicos, climáticos y de biodiversidad, buscamos cuantificar su rol en la recarga de acuíferos y como soporte de un ecosistema clave, con un enfoque especial en la avifauna.

## Guía de inicio rápido

### 1. Instalación del entorno

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.venv\Scripts\activate

# Activar entorno (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Obtención de datos

Los datos se obtienen mediante tres notebooks ejecutados en secuencia:

1. **`1.0-mcd-obtencion-datos-presa.ipynb`**
   - Obtiene datos históricos de almacenamiento de la presa mediante web scraping
   - Fuente: Portal de Sonora Datos Abiertos
   - Salida: `data/raw/datos_presa_arlso.csv`

2. **`2.0-mcd-obtencion-datos-meteorologicos.ipynb`**
   - Obtiene datos meteorológicos históricos desde Open-Meteo API
   - Variables: precipitación, temperatura, evapotranspiración, viento, humedad, etc.
   - Salidas:
     - `data/raw/datos_meteorologicos_basicos.csv`
     - `data/raw/datos_meteorologicos_completos.csv`

3. **`3.0-mcd-fusion-datos-hidrologicos.ipynb`**
   - Fusiona datos de presa con datos meteorológicos
   - Estrategia: OUTER JOIN para preservar todos los registros históricos
   - Salida: `data/processed/datos_hidrologicos_completos.csv`

### 3. Análisis

Una vez obtenidos los datos fusionados, el dataset `datos_hidrologicos_completos.csv` está listo para análisis exploratorio, modelado y visualizaciones.


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
