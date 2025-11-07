# -*- coding: utf-8 -*-
"""
Script para ejecutar el pipeline completo de obtención de datos.

Este script ejecuta todos los scripts de obtención de datos en secuencia:
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


def ejecutar_script(script_path: Path) -> bool:
    """
    Ejecuta un script de Python.

    Args:
        script_path: Ruta al script a ejecutar

    Returns:
        True si el script se ejecutó exitosamente, False en caso contrario
    """
    logger.info(f"Ejecutando script: {script_path.name}")
    logger.info("=" * 70)

    try:
        # Ejecutar script de Python
        resultado = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True
        )

        # Mostrar salida del script
        if resultado.stdout:
            print(resultado.stdout)

        logger.info(f"[OK] Script {script_path.name} ejecutado exitosamente")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"[ERROR] Error al ejecutar {script_path.name}")
        logger.error(f"Código de salida: {e.returncode}")
        if e.stdout:
            logger.error(f"STDOUT: {e.stdout}")
        if e.stderr:
            logger.error(f"STDERR: {e.stderr}")
        return False

    except FileNotFoundError:
        logger.error(f"[ERROR] Script no encontrado: {script_path}")
        return False

    except Exception as e:
        logger.error(f"[ERROR] Error inesperado: {e}")
        return False


def main():
    """Ejecuta el pipeline completo de obtención de datos."""

    inicio = datetime.now()
    logger.info("=" * 70)
    logger.info("INICIANDO PIPELINE DE OBTENCIÓN DE DATOS")
    logger.info("=" * 70)

    # Obtener directorio del proyecto
    project_dir = Path(__file__).resolve().parents[2]
    scripts_dir = project_dir / 'src' / 'data'

    logger.info(f"Directorio del proyecto: {project_dir}")
    logger.info(f"Directorio de scripts: {scripts_dir}")

    # Verificar que el directorio de scripts existe
    if not scripts_dir.exists():
        logger.error(f"[ERROR] Directorio de scripts no encontrado: {scripts_dir}")
        sys.exit(1)

    # Definir scripts a ejecutar en orden
    scripts = [
        '01_obtener_datos_presa.py',
        '02_obtener_datos_meteo.py',
        '03_fusion_hidrologicos.py',
        '04_obtener_datos_aves.py'
    ]

    logger.info(f"\nScripts a ejecutar: {len(scripts)}")
    for i, script in enumerate(scripts, 1):
        logger.info(f"  {i}. {script}")

    logger.info("\n" + "=" * 70 + "\n")

    # Ejecutar cada script en secuencia
    resultados = {}

    for script_name in scripts:
        script_path = scripts_dir / script_name

        # Verificar que el script existe
        if not script_path.exists():
            logger.error(f"[ERROR] Script no encontrado: {script_path}")
            resultados[script_name] = False
            logger.error("Abortando pipeline...")
            break

        # Ejecutar script
        exito = ejecutar_script(script_path)
        resultados[script_name] = exito

        if not exito:
            logger.error(f"\n[ERROR] Pipeline abortado debido a error en {script_name}")
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
    no_ejecutados = len(scripts) - len(resultados)

    logger.info(f"\nScripts ejecutados exitosamente: {exitosos}/{len(scripts)}")
    logger.info(f"Scripts fallidos: {fallidos}")
    logger.info(f"Scripts no ejecutados: {no_ejecutados}")

    logger.info("\nDetalle:")
    for script, resultado in resultados.items():
        estado = "[OK] EXITO" if resultado else "[ERROR] FALLO"
        logger.info(f"  {estado}: {script}")

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
                logger.info(f"    [OK] {archivo} ({tamano:.2f} MB)")
            else:
                logger.warning(f"    [WARNING] {archivo} - NO ENCONTRADO")
                todos_presentes = False

    # Código de salida
    if exitosos == len(scripts) and todos_presentes:
        logger.info("\n[OK] Pipeline completado exitosamente!")
        logger.info("Todos los datos han sido obtenidos y procesados correctamente.")
        sys.exit(0)
    else:
        logger.error("\n[ERROR] Pipeline completado con errores.")
        sys.exit(1)


if __name__ == '__main__':
    main()
