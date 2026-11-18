"""Resumen: el mapamundi de áreas reales y los indicadores clave del mundo, de Colombia y del modelo."""

import streamlit as st
import streamlit.components.v1 as components

import datos
import tema

st.title("¿Dónde es más densa la violencia armada?")
st.markdown('<p class="entrada">Cada país con su superficie real; su rojo mide las muertes en hechos de '
            'violencia organizada por cada 1.000 km² (UCDP, Uppsala University).</p>', unsafe_allow_html=True)

components.html(datos.html_mapa_hero(), height=1010, scrolling=False)

st.header("Del mundo a Colombia")
st.markdown('<p class="entrada">En Colombia el homicidio con arma de fuego cambió de forma después del Acuerdo de Paz: el sicariato '
            'y el crimen organizado pasaron a ser la mayoría, mientras el conflicto armado vuelve a crecer en 2026.</p>',
            unsafe_allow_html=True)

hom = datos.homicidios()
ultimo = int(hom["anio"].max())
completo = ultimo - 1
victimas = int(hom["cantidad"].sum())
pct_fuego = hom.loc[hom["es_arma_fuego"], "cantidad"].sum() / victimas * 100
por_anio = hom.pivot_table(index="anio", columns="categoria_violencia", values="cantidad", aggfunc="sum", observed=True).fillna(0)
participacion = por_anio.div(por_anio.sum(axis=1), axis=0) * 100

tema.cifras([
    (tema.miles(victimas), f"víctimas de homicidio en Colombia entre 2003 y {ultimo}"),
    (f"{tema.decimal(pct_fuego)} %", "murieron por arma de fuego"),
    (f"{tema.decimal(participacion.loc[completo, 'Crimen organizado y sicariato'], 0)} %",
     f"de los homicidios de {completo} fueron por crimen organizado y sicariato"),
    (f"{tema.decimal(participacion.loc[ultimo, 'Conflicto armado'])} %",
     f"de los homicidios de {ultimo} (parcial) se atribuyen al conflicto armado, frente a "
     f"{tema.decimal(participacion.loc[2016, 'Conflicto armado'])} % en 2016"),
], roja=3)

st.subheader(f"Composición de los homicidios en {completo}")
orden = list(tema.CATEGORIAS)
partes = "".join(f'<i style="width:{participacion.loc[completo, c]:.2f}%;color:{tema.CATEGORIAS[c]};animation-delay:{k * 0.12:.2f}s" '
                 f'title="{c}: {tema.decimal(participacion.loc[completo, c])} %"></i>'
                 for k, c in enumerate(orden) if c in participacion.columns and participacion.loc[completo, c] > 0)
leyenda = "".join(f'<span style="--c:{tema.CATEGORIAS[c]}">{c} · {tema.decimal(participacion.loc[completo, c])} %</span>'
                  for c in orden if c in participacion.columns)
st.markdown(f'<div class="composicion">{partes}</div><div class="leyenda-c">{leyenda}</div>', unsafe_allow_html=True)

# Indicadores clave del modelo (la guía pide KPIs del dataset y del modelo en el Resumen)
meta = datos.metadatos_modelo()
m, base = meta["metricas_prueba"], meta["linea_base"]
st.header("Qué tan bien clasifica el modelo")
st.markdown(f'<p class="entrada">Un {meta["algoritmo"]} estima a cuál de cuatro tipos de violencia pertenece un homicidio. '
            f'Se entrenó con {meta["periodo_entrenamiento"]} y se evaluó con homicidios que nunca vio ({meta["periodo_prueba"]}).</p>',
            unsafe_allow_html=True)
tema.cifras([
    (tema.decimal(m["f1_macro"], 2), f"F1 macro, frente a {tema.decimal(base['f1_macro'], 2)} de la línea base"),
    (f"+{tema.decimal(m['f1_macro'] - base['f1_macro'], 2)}", "de mejora sobre la línea base (meta: +0,10, se cumple)"),
    (f"{tema.decimal(m['accuracy'] * 100, 0)} %", "de aciertos totales en la prueba"),
    (tema.decimal(m["recall · Conflicto armado"], 2), "de los homicidios del conflicto armado que reconoce (meta: 0,50, no se cumple)"),
], roja=3)
st.page_link("paginas/modelo.py", label="Ver la comparación de modelos y probar una predicción")

st.header("Lo que muestran los datos")
documento, error = datos.documento_analisis()
if error:
    st.markdown(f'<div class="vacio">{error}</div>', unsafe_allow_html=True)
else:
    elementos = "".join(f'<li style="animation-delay:{i * 0.07:.2f}s"><b>{x["titulo"]}</b><span>{x["detalle"]}</span><em>{x["tema"]}</em></li>'
                        for i, x in enumerate(documento["insights"][:4]))
    st.markdown(f'<ul class="lista-diagonal">{elementos}</ul>', unsafe_allow_html=True)
    st.page_link("paginas/insights.py", label="Ver los 9 hallazgos, las recomendaciones y el reporte PDF")
