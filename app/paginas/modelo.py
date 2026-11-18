"""Modelo: métricas, comparación con la línea base, interpretación y formulario de predicción."""

from datetime import date

import numpy as np
import plotly.graph_objects as go
import streamlit as st

import datos
import tema

CONFIG = tema.CONFIG_GRAFICA
meta = datos.metadatos_modelo()
mdl = datos.mdl
m, base = meta["metricas_prueba"], meta["linea_base"]

st.title("Modelo")
st.markdown('<p class="entrada">Un clasificador que, a partir de dónde, cuándo y con qué arma ocurrió un homicidio en Colombia, '
            'estima a cuál de cuatro tipos de violencia pertenece. Se evaluó con homicidios que nunca vio (2023 en adelante).</p>',
            unsafe_allow_html=True)

recall_conf = m["recall · Conflicto armado"]
tema.cifras([
    (tema.decimal(m["f1_macro"], 2), f"F1 macro del modelo, frente a {tema.decimal(base['f1_macro'], 2)} de la línea base"),
    (f"+{tema.decimal(m['f1_macro'] - base['f1_macro'], 2)}", "mejora sobre la línea base (meta: +0,10)"),
    (tema.decimal(recall_conf, 2), "de los homicidios del conflicto armado que reconoce (meta: 0,50, no se cumple)"),
    (f"{tema.decimal(m['accuracy'] * 100, 0)} %", "de aciertos totales en la prueba"),
], roja=2)
st.markdown('<p class="entrada">Cumple el primer criterio de éxito y no el segundo: en 2023–2026 el conflicto armado casi duplicó su peso '
            'frente a los años de entrenamiento, y el modelo lo confunde con el sicariato porque ambos se cometen con arma de fuego.</p>',
            unsafe_allow_html=True)

st.header("Comparación de modelos")
comp = meta["comparacion_modelos"]
nombres = sorted(comp, key=lambda n: comp[n]["f1_macro"])
fig = go.Figure()
fig.add_bar(y=nombres, x=[comp[n]["f1_macro"] for n in nombres], name="F1 macro", orientation="h",
            marker=tema.celdas([tema.BLANCO if n == meta["algoritmo"] else tema.GRIS_1 for n in nombres]),
            text=[tema.decimal(comp[n]["f1_macro"], 2) for n in nombres], textposition="outside")
fig.add_bar(y=nombres, x=[comp[n]["recall · Conflicto armado"] for n in nombres], name="Recall de conflicto armado", orientation="h",
            marker=tema.celdas([tema.ROJO if n == meta["algoritmo"] else tema.ROJO_3 for n in nombres]),
            text=[tema.decimal(comp[n]["recall · Conflicto armado"], 2) for n in nombres], textposition="outside")
fig.add_vline(x=0.5, line=dict(color=tema.ROJO, dash="dot", width=1))
fig.add_annotation(x=0.5, y=len(nombres) - 0.4, text="meta de recall 0,50", showarrow=False, xanchor="left", xshift=6,
                   font=dict(color=tema.ROJO, size=12))
fig.update_traces(textfont=dict(family="Martian Mono", color=tema.BLANCO), cliponaxis=False)
fig.update_layout(barmode="group", height=380, xaxis=dict(range=[0, 1.05]), bargap=0.25, showlegend=False)
st.plotly_chart(fig, use_container_width=True, config=CONFIG)
st.markdown(f'<div class="leyenda-c"><span style="--c:{tema.BLANCO}">F1 macro (gris: modelos descartados)</span>'
            f'<span style="--c:{tema.ROJO}">Recall de conflicto armado (rojo oscuro: descartados)</span></div>',
            unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Matriz de confusión")
    clases = meta["matriz_confusion"]["clases"]
    valores = np.array(meta["matriz_confusion"]["valores"], dtype=float)
    pct = valores / valores.sum(axis=1, keepdims=True) * 100
    cortas = ["Conflicto", "Crimen org.", "Riñas", "Delincuencia"]
    fig = go.Figure(go.Heatmap(z=pct, x=cortas, y=cortas, colorscale=tema.ESCALA_ROJA, zmin=0, zmax=100, xgap=2, ygap=2,
                               showscale=False, hovertemplate="Real: %{y}<br>Predicho: %{x}<br>%{z:.1f} %<extra></extra>"))
    tema.textos_heatmap(fig, cortas, cortas, pct.tolist(), [[f"{tema.decimal(v)} %" for v in fila] for fila in pct], zmax=100)
    fig.update_layout(height=420, xaxis=dict(title="Predicho", side="top", tickfont=tema.TEXTO),
                      yaxis=dict(title="Real", autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True, config=CONFIG)
with col_b:
    st.subheader("Qué variables usa")
    imp = sorted(meta["variables_importantes"], key=lambda v: v["caida_f1_macro"])
    fig = go.Figure(go.Bar(x=[v["caida_f1_macro"] for v in imp], y=[v["nombre"] for v in imp], orientation="h",
                           marker=tema.celdas([tema.BLANCO if i >= len(imp) - 3 else tema.GRIS_1 for i in range(len(imp))]),
                           hovertemplate="%{y}: %{x:.3f}<extra></extra>"))
    fig.update_layout(height=420, xaxis_title="Caída de la F1 al desordenar la variable")
    st.plotly_chart(fig, use_container_width=True, config=CONFIG)

st.header("Probar el modelo")
st.markdown('<p class="entrada">Describa un homicidio y el modelo estimará la probabilidad de cada tipo de violencia. La actividad '
            'armada de UCDP se completa con el dato más reciente del departamento elegido.</p>', unsafe_allow_html=True)

opciones = meta["opciones_formulario"]
departamentos = sorted(opciones["departamentos"])
c1, c2 = st.columns(2)
depto = c1.selectbox("Departamento", departamentos, index=departamentos.index("ARAUCA") if "ARAUCA" in departamentos else 0)
municipios = {f'{x["municipio"]}': x["cod_muni"] for x in opciones["departamentos"][depto]}
muni = c2.selectbox("Municipio", sorted(municipios))

panel = datos.panel_ucdp()
clave = depto.replace("Ñ", "N")
ultimo = panel[panel["depto_clave"] == clave].sort_values("periodo").tail(1)
eventos_def = int(ultimo["eventos_ucdp_12m"].iloc[0]) if len(ultimo) else 0
muertes_def = int(ultimo["muertes_ucdp_12m"].iloc[0]) if len(ultimo) else 0

with st.form("prediccion", border=True):
    f1, f2, f3 = st.columns(3)
    zona = f1.selectbox("Zona", opciones["zonas"], index=opciones["zonas"].index("RURAL") if "RURAL" in opciones["zonas"] else 0)
    sexo = f2.selectbox("Sexo de la víctima", opciones["sexos"])
    arma = f3.selectbox("Arma usada", opciones["armas"], index=opciones["armas"].index("Arma de fuego") if "Arma de fuego" in opciones["armas"] else 0)
    f4, f5, f6, f7 = st.columns(4)
    fecha = f4.date_input("Fecha del hecho", value=date(2026, 3, 10), format="DD/MM/YYYY")
    victimas = f5.number_input("Víctimas en el hecho", min_value=1, max_value=40, value=1)
    eventos = f6.number_input("Eventos UCDP (12 meses)", min_value=0, value=eventos_def)
    muertes = f7.number_input("Muertes UCDP (12 meses)", min_value=0, value=muertes_def)
    enviado = st.form_submit_button("Estimar el tipo de violencia")

if enviado:
    registro = mdl.registro_nuevo(depto, municipios[muni], zona, sexo, arma, fecha, eventos, muertes, victimas)
    modelo = datos.modelo_entrenado()
    prob = dict(zip(modelo.classes_, modelo.predict_proba(registro)[0]))
    ganadora = max(prob, key=prob.get)
    st.subheader(f"Lo más probable: {ganadora.lower()} ({tema.decimal(prob[ganadora] * 100, 0)} %)")
    filas = "".join(f'<span>{c}</span><i style="width:{prob[c] * 100:.1f}%;color:{tema.CATEGORIAS[c]};animation-delay:{k * .08:.2f}s"></i>'
                    f'<b>{tema.decimal(prob[c] * 100)} %</b>' for k, c in enumerate(mdl.CLASES))
    st.markdown(f'<div class="prob">{filas}</div>', unsafe_allow_html=True)
    st.markdown('<p class="nota">Es una estimación estadística a partir de patrones históricos, no una determinación de lo que '
                'ocurrió. El modelo subestima el conflicto armado cuando este repunta.</p>', unsafe_allow_html=True)
