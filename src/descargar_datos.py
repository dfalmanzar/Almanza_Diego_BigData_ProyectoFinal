"""Descarga los datasets crudos del proyecto en data/raw/.

Fuentes (todas públicas, sin registro):
  1. UCDP GED 26.1 (Uppsala Conflict Data Program): violencia organizada global, 1989-2025.
  2. UCDP Candidate Events 26.01.26.09: eventos preliminares enero-septiembre 2026.
  3. Homicidios - Ministerio de Defensa Nacional (datos.gov.co, id m8fd-ahd9), 2003-2026.
  4. (Opcional, --incluir-lesiones) Lesiones personales - Policía Nacional (datos.gov.co, id 72sg-cybi).

Uso (desde la raíz del proyecto o desde el contenedor):
    python src/descargar_datos.py
    python src/descargar_datos.py --incluir-lesiones
    python src/descargar_datos.py --forzar          # vuelve a descargar aunque el archivo exista

Cada descarga queda registrada en data/raw/descargas.json (URL, fecha de descarga y peso),
que el notebook usa para documentar el origen de los datos.
"""

import argparse
import json
import shutil
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_RAW = RAIZ_PROYECTO / "data" / "raw"
REGISTRO = CARPETA_RAW / "descargas.json"

DATASETS = {
    "ucdp_ged": {
        "descripcion": "UCDP Georeferenced Event Dataset (GED) Global v26.1, 1989-2025",
        "url": "https://ucdp.uu.se/downloads/ged/ged261-csv.zip",
        "archivo": "ucdp_ged_261.zip",
        "descomprimir": True,
    },
    "ucdp_candidate": {
        "descripcion": "UCDP Candidate Events Dataset v26.01.26.09, enero-septiembre 2026",
        "url": "https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_01_26_09.csv",
        "archivo": "ucdp_candidate_2026.csv",
        "descomprimir": False,
    },
    "homicidios_col": {
        "descripcion": "Homicidios en Colombia - Ministerio de Defensa Nacional (datos.gov.co m8fd-ahd9)",
        "url": "https://www.datos.gov.co/api/views/m8fd-ahd9/rows.csv?accessType=DOWNLOAD",
        "archivo": "homicidios_mindefensa.csv",
        "descomprimir": False,
    },
    "paises_geo": {
        "descripcion": "Límites de países Natural Earth 1:50m v5.1.2 (dominio público), para el mapa del dashboard",
        "url": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_50m_admin_0_countries.geojson",
        "archivo": "ne_50m_admin_0_countries.geojson",
        "descomprimir": False,
    },
    "lesiones_col": {
        "descripcion": "Lesiones personales - Policía Nacional (datos.gov.co 72sg-cybi)",
        "url": "https://www.datos.gov.co/api/views/72sg-cybi/rows.csv?accessType=DOWNLOAD",
        "archivo": "lesiones_policia.csv",
        "descomprimir": False,
        "opcional": True,
    },
}


def descargar(url: str, destino: Path) -> None:
    """Descarga `url` en `destino` mostrando el avance en MB."""
    temporal = destino.with_suffix(destino.suffix + ".part")
    peticion = urllib.request.Request(url, headers={"User-Agent": "proyecto-final-bigdata/1.0"})
    with urllib.request.urlopen(peticion, timeout=120) as respuesta, open(temporal, "wb") as salida:
        descargado = 0
        while bloque := respuesta.read(1024 * 1024):
            salida.write(bloque)
            descargado += len(bloque)
            print(f"\r    {descargado / 1e6:,.1f} MB", end="", flush=True)
    print()
    temporal.replace(destino)  # solo se renombra si la descarga terminó completa


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--incluir-lesiones", action="store_true", help="descarga también lesiones personales")
    parser.add_argument("--forzar", action="store_true", help="vuelve a descargar aunque exista el archivo")
    args = parser.parse_args()

    CARPETA_RAW.mkdir(parents=True, exist_ok=True)
    registro = json.loads(REGISTRO.read_text(encoding="utf-8")) if REGISTRO.exists() else {}

    for clave, info in DATASETS.items():
        if info.get("opcional") and not args.incluir_lesiones:
            continue
        destino = CARPETA_RAW / info["archivo"]
        print(f"[{clave}] {info['descripcion']}")
        if destino.exists() and not args.forzar:
            print(f"    ya existe ({destino.stat().st_size / 1e6:,.1f} MB), se omite")
        else:
            try:
                descargar(info["url"], destino)
            except Exception as error:  # se informa y se sigue con los demás
                print(f"    ERROR al descargar: {error}")
                continue
            registro[clave] = {
                "descripcion": info["descripcion"],
                "url": info["url"],
                "archivo": info["archivo"],
                "fecha_descarga": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "peso_mb": round(destino.stat().st_size / 1e6, 2),
            }

        csv_previo = CARPETA_RAW / "ucdp_ged_261.csv"
        if info["descomprimir"] and csv_previo.exists() and csv_previo.stat().st_mtime >= destino.stat().st_mtime and not args.forzar:
            print(f"    ya descomprimido -> {csv_previo.name}")
        elif info["descomprimir"]:
            with zipfile.ZipFile(destino) as zip_ged:
                for nombre in zip_ged.namelist():
                    if nombre.lower().endswith(".csv"):
                        csv_destino = CARPETA_RAW / "ucdp_ged_261.csv"
                        with zip_ged.open(nombre) as origen, open(csv_destino, "wb") as salida:
                            shutil.copyfileobj(origen, salida)
                        registro.setdefault(clave, {})["archivo_csv"] = csv_destino.name
                        print(f"    descomprimido -> {csv_destino.name}")

    REGISTRO.write_text(json.dumps(registro, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nRegistro de descargas: {REGISTRO.relative_to(RAIZ_PROYECTO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
