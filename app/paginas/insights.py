"""Insights y reporte: hallazgos y recomendaciones leídos de MongoDB, y descarga del PDF."""

import streamlit as st

import datos
import tema

st.title("Insights y reporte")
documento, error = datos.documento_analisis()
if error:
    st.markdown(f'<div class="vacio">{error}</div>', unsafe_allow_html=True)
    st.stop()

meta = documento["metadata"]
st.markdown(f'<p class="entrada">{meta["pregunta_negocio"]}</p>', unsafe_allow_html=True)
tema.cifras([(str(len(documento["insights"])), "hallazgos calculados con los datos"),
             (str(len(documento["recomendaciones"])), "recomendaciones"),
             (tema.miles(meta["dataset"]["registros"]), "registros analizados"),
             (meta["fecha_analisis"][:10], "fecha del análisis")])

st.header("Hallazgos")
temas = sorted({x["tema"] for x in documento["insights"]})
elegidos = st.pills("Tema", temas, selection_mode="multi", label_visibility="collapsed")
visibles = [x for x in documento["insights"] if not elegidos or x["tema"] in elegidos]
elementos = "".join(f'<li style="animation-delay:{i * 0.06:.2f}s"><b>{x["titulo"]}</b><span>{x["detalle"]}</span><em>{x["tema"]}</em></li>'
                    for i, x in enumerate(visibles))
st.markdown(f'<ul class="lista-diagonal">{elementos}</ul>', unsafe_allow_html=True)

st.header("Recomendaciones")
recs = "".join(f'<li style="animation-delay:{i * 0.06:.2f}s"><b>{r["titulo"]}</b><span>{r["detalle"]}</span>'
               f'<em>Prioridad {r["prioridad"].lower()} · {r["sustento"]}</em></li>' for i, r in enumerate(documento["recomendaciones"]))
st.markdown(f'<ul class="lista-diagonal">{recs}</ul>', unsafe_allow_html=True)

st.header("Reporte PDF")
pdf = datos.REPORTES / "reporte_violencia_armada.pdf"
c1, c2 = st.columns([2, 3])
with c1:
    if pdf.exists():
        st.markdown('<p class="entrada">Generado automáticamente desde este mismo documento de MongoDB: datos, calidad, '
                    'agregaciones, gráficas, modelo, hallazgos y recomendaciones.</p>', unsafe_allow_html=True)
        st.download_button("Descargar el reporte PDF", pdf.read_bytes(), file_name="reporte_violencia_armada.pdf",
                           mime="application/pdf")
    else:
        st.markdown('<div class="vacio">El reporte todavía no existe. Ejecute el notebook o '
                    '<code>python src/generar_reporte.py</code> en el contenedor de procesamiento.</div>', unsafe_allow_html=True)
with c2:
    # Páginas para consultar cada fuente en la web (no los archivos de descarga)
    paginas_web = {"ucdp_ged": "https://ucdp.uu.se/downloads/", "ucdp_candidate": "https://ucdp.uu.se/downloads/",
                   "homicidios_col": "https://www.datos.gov.co/d/m8fd-ahd9"}
    fuentes = "".join(f'<li><b>{f["nombre"]}</b><span>{tema.miles(f["registros"])} registros · {f["periodo"]} · '
                      f'<a href="{paginas_web.get(f["clave"], f["url"])}" target="_blank" rel="noopener">ver la fuente</a></span></li>'
                      for f in meta["dataset"]["fuentes"])
    st.markdown(f'<ul class="lista-diagonal">{fuentes}</ul>', unsafe_allow_html=True)
