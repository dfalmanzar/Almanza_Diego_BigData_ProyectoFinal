"""Carga de los resultados ya procesados (Parquet, modelo, MongoDB y mapa).

La app nunca repite el ETL ni reentrena: solo lee lo que dejó el notebook.
Todo se cachea para que la navegación entre secciones sea inmediata.
"""

import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st
from pymongo import MongoClient

RAIZ = Path(__file__).resolve().parent.parent
PROCESADOS = RAIZ / "data" / "processed"
MODELOS = RAIZ / "models"
REPORTES = RAIZ / "reports"
COMPONENTES = Path(__file__).resolve().parent / "componentes"
FUENTES = Path(__file__).resolve().parent / "static" / "fuentes"
sys.path.insert(0, str(RAIZ / "src"))

import modelo as mdl  # noqa: E402  (módulo compartido con el notebook)
import olap  # noqa: E402
import tema  # noqa: E402

REGIONES_ES = {"Africa": "África", "Americas": "América", "Asia": "Asia", "Europe": "Europa", "Middle East": "Medio Oriente"}


@st.cache_data(show_spinner=False)
def homicidios():
    return pd.read_parquet(PROCESADOS / "homicidios_limpio.parquet")


@st.cache_data(show_spinner=False)
def eventos_ucdp():
    columnas = ["id", "anio", "date_start", "tipo_violencia", "country", "region", "adm_1", "conflict_name",
                "side_a", "side_b", "best", "deaths_civilians", "latitude", "longitude", "version_ucdp"]
    tabla = pd.read_parquet(PROCESADOS / "ucdp_eventos.parquet", columns=columnas)
    tabla["region"] = tabla["region"].astype(str).map(REGIONES_ES).astype("category")
    return tabla


@st.cache_data(show_spinner=False)
def cubo_homicidios():
    return pd.read_parquet(PROCESADOS / "cubo_homicidios.parquet")


@st.cache_data(show_spinner=False)
def cubo_ucdp():
    tabla = pd.read_parquet(PROCESADOS / "cubo_ucdp.parquet")
    tabla["region"] = tabla["region"].astype(str).map(REGIONES_ES)
    return tabla


@st.cache_data(show_spinner=False)
def mapa_mundo():
    return json.loads((PROCESADOS / "mapa_mundo.json").read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def metadatos_modelo():
    return json.loads((MODELOS / "metadatos_modelo.json").read_text(encoding="utf-8"))


def configuracion(nombre, defecto=None):
    """Lee un valor de las variables de entorno (Docker) o de los secrets de Streamlit Community Cloud."""
    valor = os.environ.get(nombre)
    if valor:
        return valor
    try:
        return st.secrets.get(nombre, defecto)
    except Exception:  # sin archivo de secrets (p. ej. dentro de Docker)
        return defecto


@st.cache_resource(show_spinner="Descargando el modelo entrenado (solo la primera vez)…")
def modelo_entrenado():
    """Modelo guardado por el notebook. En la nube no está en el repositorio (76 MB): se descarga una vez del
    Release de GitHub indicado en MODELO_URL. Es el mismo archivo, así que las métricas no cambian."""
    ruta = MODELOS / "modelo_categoria_violencia.joblib"
    url = configuracion("MODELO_URL")
    if not ruta.exists() and url:
        temporal = ruta.with_suffix(".descarga")
        urllib.request.urlretrieve(url, temporal)
        temporal.replace(ruta)
    return joblib.load(ruta)


@st.cache_data(show_spinner=False)
def panel_ucdp():
    return pd.read_parquet(PROCESADOS / "panel_ucdp_colombia.parquet")


@st.cache_data(ttl=300, show_spinner=False)
def documento_analisis():
    """Último documento de análisis guardado en MongoDB. Devuelve (documento, error)."""
    uri = configuracion("MONGO_URI")
    if not uri:
        return None, "La app no tiene la variable MONGO_URI. Ejecútela con docker compose para conectarse a MongoDB."
    try:
        with MongoClient(uri, serverSelectionTimeoutMS=4000) as cliente:
            doc = cliente[configuracion("MONGO_BD", "violencia_armada")]["analisis"].find_one(
                {"metadata.proyecto": "violencia-armada"}, sort=[("metadata.fecha_analisis", -1)])
    except Exception as error:  # se muestra al visitante con la forma de recuperarse
        return None, f"No fue posible conectarse a MongoDB ({type(error).__name__}). Verifique que el servicio mongo esté activo."
    if doc is None:
        return None, "MongoDB no tiene todavía el documento de análisis. Ejecute el notebook para generarlo."
    doc["_id"] = str(doc["_id"])
    return doc, None


def _fuente_b64(nombre):
    return base64.b64encode((FUENTES / nombre).read_bytes()).decode()


@st.cache_data(show_spinner=False)
def html_mapa_hero(desde=2016, hasta=2025, url_datos="/datos"):
    """Componente del mapa con los datos y las fuentes incrustados (el iframe no comparte las fuentes de la app)."""
    plantilla = (COMPONENTES / "mapa_hero.html").read_text(encoding="utf-8")
    datos = {"mapa": mapa_mundo(), "periodo": [desde, hasta]}
    return (plantilla
            .replace("__FUENTE_CHAKRA_600__", _fuente_b64("ChakraPetch-SemiBold.ttf"))
            .replace("__FUENTE_CHAKRA_700__", _fuente_b64("ChakraPetch-Bold.ttf"))
            .replace("__FUENTE_BARLOW_400__", _fuente_b64("Barlow-Regular.ttf"))
            .replace("__FUENTE_BARLOW_600__", _fuente_b64("Barlow-SemiBold.ttf"))
            .replace("__FUENTE_MARTIAN__", _fuente_b64("MartianMono-Variable.ttf"))
            .replace("__TOKENS__", tema.tokens_css())
            .replace("__URL_DATOS__", url_datos)
            .replace("__DATOS__", json.dumps(datos, ensure_ascii=False, separators=(",", ":"))))
