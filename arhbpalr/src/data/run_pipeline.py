# -*- coding: utf-8 -*-
"""
Script para ejecutar el pipeline completo de obtención de datos.

Este script ejecuta todos los notebooks de obtención de datos en secuencia:
1. Obtención de datos de la presa
2. Obtención de datos meteorológicos
3. Fusión de datos hidrológicos
4. Obtención de datos de avifauna (eBird)

Uso:
    python src/data/run_pipeline.py
"""
import logging
import sys
import subprocess
from pathlib import Path
from datetime import datetime


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ejecutar_notebook(notebook_path: Path) -> bool:
    """
    Ejecuta un notebook de Jupyter usando nbconvert.

    Args:
        notebook_path: Ruta al notebook a ejecutar

    Returns:
        True si el notebook se ejecutó exitosamente, False en caso contrario
    """
    logger.info(f"Ejecutando notebook: {notebook_path.name}")
    logger.info("=" * 70)

    try:
        # Ejecutar notebook usando jupyter nbconvert
        resultado = subprocess.run(
            [
                'jupyter', 'nbconvert',
                '--to', 'notebook',
                '--execute',
                '--inplace',
                '--ExecutePreprocessor.timeout=None',  # Sin timeout para notebooks largos
                str(notebook_path)
            ],
            capture_output=True,
            text=True,
            check=True
        )

        logger.info(f"✓ Notebook {notebook_path.name} ejecutado exitosamente")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error al ejecutar {notebook_path.name}")
        logger.error(f"Código de salida: {e.returncode}")
        logger.error(f"STDOUT: {e.stdout}")
        logger.error(f"STDERR: {e.stderr}")
        return False

    except FileNotFoundError:
        logger.error(
            "❌ jupyter nbconvert no encontrado. "
            "Instala con: pip install jupyter nbconvert"
        )
        return False

    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        return False


def main():
    """Ejecuta el pipeline completo de obtención de datos."""

    inicio = datetime.now()
    logger.info("=" * 70)
    logger.info("INICIANDO PIPELINE DE OBTENCIÓN DE DATOS")
    logger.info("=" * 70)

    # Obtener directorio del proyecto
    project_dir = Path(__file__).resolve().parents[2]
    notebooks_dir = project_dir / 'notebooks'

    logger.info(f"Directorio del proyecto: {project_dir}")
    logger.info(f"Directorio de notebooks: {notebooks_dir}")

    # Verificar que el directorio de notebooks existe
    if not notebooks_dir.exists():
        logger.error(f"❌ Directorio de notebooks no encontrado: {notebooks_dir}")
        sys.exit(1)

    # Definir notebooks a ejecutar en orden
    notebooks = [
        '1.0-mcd-obtencion-datos-presa.ipynb',
        '2.0-mcd-obtencion-datos-meteorologicos.ipynb',
        '3.0-mcd-fusion-datos-hidrologicos.ipynb',
        '4.0-mcd-obtencion-datos-avifauna.ipynb'
    ]

    logger.info(f"\nNotebooks a ejecutar: {len(notebooks)}")
    for i, nb in enumerate(notebooks, 1):
        logger.info(f"  {i}. {nb}")

    logger.info("\n" + "=" * 70 + "\n")

    # Ejecutar cada notebook en secuencia
    resultados = {}

    for notebook_name in notebooks:
        notebook_path = notebooks_dir / notebook_name

        # Verificar que el notebook existe
        if not notebook_path.exists():
            logger.error(f"❌ Notebook no encontrado: {notebook_path}")
            resultados[notebook_name] = False
            logger.error("Abortando pipeline...")
            break

        # Ejecutar notebook
        exito = ejecutar_notebook(notebook_path)
        resultados[notebook_name] = exito

        if not exito:
            logger.error(f"\n❌ Pipeline abortado debido a error en {notebook_name}")
            break

        logger.info("\n" + "-" * 70 + "\n")

    # Resumen final
    fin = datetime.now()
    duracion = fin - inicio

    logger.info("\n" + "=" * 70)
    logger.info("RESUMEN DEL PIPELINE")
    logger.info("=" * 70)

    exitosos = sum(1 for v in resultados.values() if v)
    fallidos = sum(1 for v in resultados.values() if not v)
    no_ejecutados = len(notebooks) - len(resultados)

    logger.info(f"\nNotebooks ejecutados exitosamente: {exitosos}/{len(notebooks)}")
    logger.info(f"Notebooks fallidos: {fallidos}")
    logger.info(f"Notebooks no ejecutados: {no_ejecutados}")

    logger.info("\nDetalle:")
    for notebook, resultado in resultados.items():
        estado = "✓ ÉXITO" if resultado else "❌ FALLO"
        logger.info(f"  {estado}: {notebook}")

    logger.info(f"\nTiempo total: {duracion}")
    logger.info("=" * 70)

    # Verificar archivos de salida esperados
    logger.info("\nVerificando archivos de salida...")

    data_dir = project_dir / 'data'
    archivos_esperados = {
        'raw': [
            'datos_presa_arlso.csv',
            'datos_meteorologicos_basicos.csv',
            'datos_meteorologicos_completos.csv',
            'avistamientos_ebird_raw.csv'
        ],
        'processed': [
            'datos_hidrologicos_completos.csv',
            'avistamientos_aves_presa.csv'
        ]
    }

    todos_presentes = True
    for tipo, archivos in archivos_esperados.items():
        logger.info(f"\n  {tipo.upper()}:")
        for archivo in archivos:
            ruta = data_dir / tipo / archivo
            if ruta.exists():
                tamano = ruta.stat().st_size / (1024 * 1024)  # MB
                logger.info(f"    ✓ {archivo} ({tamano:.2f} MB)")
            else:
                logger.warning(f"    ⚠️  {archivo} - NO ENCONTRADO")
                todos_presentes = False

    # Código de salida
    if exitosos == len(notebooks) and todos_presentes:
        logger.info("\n✅ Pipeline completado exitosamente!")
        logger.info("Todos los datos han sido obtenidos y procesados correctamente.")
        sys.exit(0)
    else:
        logger.error("\n❌ Pipeline completado con errores.")
        sys.exit(1)


if __name__ == '__main__':
    main()
