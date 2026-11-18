"""Pipeline completo del proyecto, para que `docker compose up --build` deje todo listo con un solo comando.

Lo ejecuta el servicio `pipeline` del docker-compose.yml antes de que arranque el dashboard:
  1. Descarga los datos crudos en data/raw/ (los archivos que ya existen no se vuelven a descargar).
  2. Ejecuta el notebook de principio a fin en un kernel limpio (ETL, OLAP, ML, MongoDB y reporte PDF).
  3. Prepara data/processed/mapa_mundo.json para el mapamundi del dashboard.

Cada paso se salta si sus resultados ya existen, así que levantar el proyecto por segunda vez tarda segundos.
Para rehacer todo:  PIPELINE_FORZAR=1 docker compose up --build   (o `python src/pipeline.py --forzar`).
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
NOTEBOOK = RAIZ / "notebooks" / "Almanza_Diego_BigData_ProyectoFinal.ipynb"
PROCESADOS = RAIZ / "data" / "processed"

# Lo que deja el notebook: si falta cualquiera, se vuelve a ejecutar
SALIDAS_NOTEBOOK = [
    PROCESADOS / "homicidios_limpio.parquet",
    PROCESADOS / "ucdp_eventos.parquet",
    PROCESADOS / "cubo_homicidios.parquet",
    PROCESADOS / "cubo_ucdp.parquet",
    PROCESADOS / "panel_ucdp_colombia.parquet",
    RAIZ / "models" / "modelo_categoria_violencia.joblib",
    RAIZ / "models" / "metadatos_modelo.json",
    RAIZ / "reports" / "reporte_violencia_armada.pdf",
]


def paso(titulo):
    print(f"\n[pipeline] {titulo}", flush=True)


def correr(comando):
    inicio = time.time()
    subprocess.run(comando, cwd=RAIZ, check=True)
    print(f"[pipeline]   listo en {time.time() - inicio:,.0f} s", flush=True)


def documento_en_mongo():
    """El volumen de Mongo puede estar vacío aunque existan los Parquet (p. ej. tras `docker compose down -v`)."""
    from pymongo import MongoClient
    try:
        cliente = MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=8000)
        bd = cliente[os.environ.get("MONGO_BD", "violencia_armada")]
        return bd["analisis"].count_documents({"metadata.proyecto": "violencia-armada"}) > 0
    except Exception as error:  # sin Mongo no se puede decidir: se ejecuta el notebook, que sí lo exige
        print(f"[pipeline]   no se pudo consultar MongoDB ({error})", flush=True)
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--forzar", action="store_true", help="rehace el notebook y el mapa aunque existan sus resultados")
    args = parser.parse_args()
    forzar = args.forzar or os.environ.get("PIPELINE_FORZAR", "0") == "1"

    paso("1/3 Datos crudos en data/raw/")
    correr([sys.executable, "src/descargar_datos.py"])

    paso("2/3 Notebook: ETL, OLAP, modelo, MongoDB y reporte PDF")
    faltan = [str(p.relative_to(RAIZ)) for p in SALIDAS_NOTEBOOK if not p.exists()]
    if not documento_en_mongo():
        faltan.append("documento de análisis en MongoDB")
    if forzar or faltan:
        print(f"[pipeline]   se ejecuta ({'forzado' if forzar else 'faltan: ' + ', '.join(faltan)}); puede tardar varios minutos",
              flush=True)
        # Restart & Run All en un kernel limpio; las salidas quedan guardadas en el mismo notebook
        correr([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                "--ExecutePreprocessor.kernel_name=python3", "--ExecutePreprocessor.timeout=-1", str(NOTEBOOK)])
    else:
        print("[pipeline]   resultados vigentes: se omite", flush=True)

    paso("3/3 Datos del mapamundi del dashboard")
    if forzar or not (PROCESADOS / "mapa_mundo.json").exists():
        correr([sys.executable, "src/mapa_mundo.py"])
    else:
        print("[pipeline]   data/processed/mapa_mundo.json vigente: se omite", flush=True)

    print("\n[pipeline] Todo listo. Dashboard: http://localhost:" + os.environ.get("APP_PUERTO_HOST", "8501"), flush=True)


if __name__ == "__main__":
    main()
