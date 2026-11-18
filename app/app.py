"""Dashboard · Violencia armada: conflicto global (UCDP) y homicidios en Colombia (MinDefensa).

Ejecutar (dentro del contenedor `app`, o localmente desde la carpeta app/):
    streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title="Violencia armada · conflicto global y homicidios en Colombia",
                   page_icon="static/favicon.svg", layout="wide", initial_sidebar_state="collapsed")

import tema  # noqa: E402

tema.aplicar()
st.logo("static/marca.png", size="large")

paginas = [
    st.Page("paginas/resumen.py", title="Resumen", url_path="resumen", default=True),
    st.Page("paginas/datos.py", title="Datos", url_path="datos"),
    st.Page("paginas/visualizaciones.py", title="Visualizaciones", url_path="visualizaciones"),
    st.Page("paginas/modelo.py", title="Modelo", url_path="modelo"),
    st.Page("paginas/insights.py", title="Insights y reporte", url_path="insights"),
]
st.navigation(paginas, position="top").run()
