"""Copia el documento de análisis del MongoDB local (Docker) a MongoDB Atlas, para la versión publicada del dashboard.

La versión en la nube (Streamlit Community Cloud) no tiene acceso al MongoDB del contenedor, así que lee
los insights desde un clúster gratuito de Atlas. El documento es el mismo que generó el notebook.

Uso (con la cadena de conexión de Atlas en ATLAS_URI dentro del .env, que nunca se sube a GitHub):
    docker compose up -d procesamiento
    docker compose exec procesamiento python src/subir_a_atlas.py
"""

import os
import sys

from pymongo import MongoClient

FILTRO = {"metadata.proyecto": "violencia-armada"}


def main():
    origen_uri, destino_uri = os.environ.get("MONGO_URI"), os.environ.get("ATLAS_URI")
    base = os.environ.get("MONGO_BD", "violencia_armada")
    if not destino_uri:
        sys.exit("Falta ATLAS_URI en el .env (la cadena mongodb+srv://... que da Atlas en Connect > Drivers).")
    if not origen_uri:
        sys.exit("Falta MONGO_URI: ejecute este script dentro del contenedor procesamiento.")

    with MongoClient(origen_uri, serverSelectionTimeoutMS=8000) as origen:
        documento = origen[base]["analisis"].find_one(FILTRO, sort=[("metadata.fecha_analisis", -1)])
    if documento is None:
        sys.exit("El MongoDB local no tiene el documento de análisis: ejecute primero docker compose up --build.")
    print(f"Documento local: {len(documento.get('insights', []))} insights, "
          f"{len(documento.get('recomendaciones', []))} recomendaciones, fecha {documento['metadata'].get('fecha_analisis')}")

    with MongoClient(destino_uri, serverSelectionTimeoutMS=15000) as destino:
        coleccion = destino[base]["analisis"]
        borrados = coleccion.delete_many(FILTRO).deleted_count  # se reemplaza la versión anterior, sin duplicar
        coleccion.insert_one(documento)
        total = coleccion.count_documents(FILTRO)
    print(f"Atlas: {borrados} documento(s) anterior(es) reemplazado(s); ahora hay {total} en {base}.analisis")


if __name__ == "__main__":
    main()
