#!/usr/bin/env python
# coding: utf-8

# # **OBTENCIÓN DE DATOS DE LA PRESA ABELARDO L. RODRÍGUEZ**
# 
# Este notebook obtiene los datos históricos de la capacidad hídrica de la Presa Abelardo L. Rodríguez desde el portal de Sonora Datos Abiertos mediante web scraping.
# 
# **Salida:** `../data/raw/datos_presa_arlso.csv`

# ## 1. Importar librerías

# In[1]:


import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path

# Definir rutas del proyecto siguiendo estructura Cookiecutter
project_dir = Path.cwd().parent
data_dir = project_dir / 'data' / 'raw'

print(f"Directorio de datos: {data_dir}")


# ## 2. Diccionario de presas de Sonora
# 
# Contiene las claves y nombres de todas las presas monitoreadas en Sonora.

# In[2]:


# Diccionario de claves de presas en Sonora
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


# ## 3. Web Scraping: obtener enlaces de datos
# 
# Extraemos los enlaces de los archivos XLSX desde el portal de Sonora Datos Abiertos.

# In[3]:


resp = requests.get('https://datos.sonora.gob.mx/dataset/Recursos%20H%C3%ADdricos')
soup = BeautifulSoup(resp.text, 'html.parser')
links_datasets = soup.find('section', id='dataset-resources').find_all('ul')

# Extraer enlaces de capacidad hídrica
links_cap = []
for link in links_datasets[0].find_all('a', attrs={'target': "_blank"}):
    if link.get('href') != '':
        links_cap.append(link.get('href'))

print(f"Enlaces encontrados: {len(links_cap)}")
for i, link in enumerate(links_cap, 1):
    print(f"{i}. {link.split('/')[-1]}")


# ## 4. Descargar y convertir archivos XLSX a CSV
# 
# Descargamos los archivos Excel y los convertimos a formato CSV temporal para procesamiento.

# In[4]:


# Crear directorio temporal para archivos CSV si no existe
temp_dir = 'temp_csv'
os.makedirs(temp_dir, exist_ok=True)

# Crear archivos CSV para cada uno
paths = []
for link in links_cap:
    # Extraer el nombre del archivo del link y cambiar la extensión a .csv
    file_name = link.split("/")[-1].replace(".xlsx", ".csv")
    file_path = os.path.join(temp_dir, file_name)

    # Leer el archivo Excel desde el link y guardarlo como CSV
    try:
        df = pd.read_excel(link)
        df.to_csv(file_path, index=False)
        paths.append(file_path)
        print(f"✓ Archivo creado: {file_name}")
    except Exception as e:
        print(f"✗ No se pudo procesar el link {link}: {e}")

print(f"\nTotal de archivos procesados: {len(paths)}")


# ## 5. Consolidar todos los datos en un DataFrame
# 
# Leemos todos los archivos CSV y los concatenamos en un solo DataFrame.

# In[5]:


# Consolidar todos los datos
df_cap = pd.DataFrame()
for path in paths:
    df = pd.read_csv(path, names=["clave", "fecha", "almacenamiento_hm3"], skiprows=1, header=None)
    df_cap = pd.concat([df_cap, df], ignore_index=True)
    print(f"Agregado: {os.path.basename(path)}")

print(f"\nDimensiones totales: {df_cap.shape}")
print(f"Presas únicas encontradas: {df_cap['clave'].unique()}")


# ## 6. Filtrar datos de la Presa Abelardo L. Rodríguez (ARLSO)
# 
# Extraemos únicamente los registros correspondientes a la presa de interés.

# In[6]:


# Filtrar datos de ARLSO
df_arlso = df_cap[df_cap["clave"] == "ARLSO"].copy()

# Limpiar y convertir tipos de datos
# Reemplazar guiones o valores vacíos por NaN
df_arlso.loc[:, "almacenamiento_hm3"] = pd.to_numeric(df_arlso["almacenamiento_hm3"], errors='coerce')
df_arlso.loc[:, "fecha"] = pd.to_datetime(df_arlso["fecha"], format="mixed", errors='coerce')

# Eliminar filas con fechas o almacenamiento nulos
df_arlso = df_arlso.dropna(subset=['fecha', 'almacenamiento_hm3'])

# Ordenar por fecha
df_arlso = df_arlso.sort_values('fecha').reset_index(drop=True)

#Eliminar la columna clave (todos los valores son iguales)
df_arlso.drop("clave", axis=1, inplace=True)

print(f"Registros de la Presa ARLSO: {len(df_arlso)}")
print(f"Rango de fechas: {df_arlso['fecha'].min()} a {df_arlso['fecha'].max()}")
print(f"\nPrimeros registros:")
display(df_arlso.head(10))


# ## 7. Estadísticas descriptivas

# In[7]:


print("Estadísticas descriptivas del almacenamiento (hm³):")
print(df_arlso['almacenamiento_hm3'].describe())


# ## 8. Guardar datos en CSV
# 
# Exportamos los datos limpios de la presa a un archivo CSV para uso posterior.

# In[8]:


# Guardar el DataFrame en CSV en la carpeta data/raw según estándares Cookiecutter
output_file = data_dir / 'datos_presa_arlso.csv'
df_arlso.to_csv(output_file, index=False)

print(f"✓ Archivo guardado exitosamente: {output_file}")
print(f"  - Registros: {len(df_arlso)}")
print(f"  - Columnas: {list(df_arlso.columns)}")
print(f"  - Tamaño: {os.path.getsize(output_file) / 1024:.2f} KB")


# ## 9. Limpieza: eliminar archivos temporales
# 
# Removemos los archivos CSV temporales creados durante el proceso.

# In[9]:


# Eliminar archivos temporales
import shutil

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
    print(f"✓ Directorio temporal '{temp_dir}' eliminado")

print("\n" + "="*50)
print("PROCESO COMPLETADO")
print("="*50)


# In[ ]:




