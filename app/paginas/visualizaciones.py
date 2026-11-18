"""Visualizaciones interactivas con filtros: mundo (UCDP) y Colombia (homicidios)."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import datos
import tema

CONFIG = tema.CONFIG_GRAFICA
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

st.title("Visualizaciones")
lado = st.segmented_control("Escala", ["Mundo", "Colombia"], default="Mundo", label_visibility="collapsed") or "Mundo"


def grafica(fig, alto=430):
    fig.update_layout(height=alto)
    st.plotly_chart(fig, use_container_width=True, config=CONFIG)


if lado == "Mundo":
    ev = datos.eventos_ucdp()
    a1 = int(ev["anio"].max())
    c1, c2 = st.columns([3, 2])
    rango = c1.slider("Años", int(ev["anio"].min()), a1, (1989, a1 - 1))
    regiones = c2.multiselect("Región", sorted(ev["region"].dropna().unique()), placeholder="Todas las regiones")
    sel = ev[ev["anio"].between(*rango) & (ev["region"].isin(regiones) if regiones else True)]
    if sel.empty:
        st.markdown('<div class="vacio">No hay eventos con estos filtros. Amplíe el rango de años o quite regiones.</div>',
                    unsafe_allow_html=True)
        st.stop()

    anual = sel.groupby(["anio", "tipo_violencia"], observed=True).size().unstack(fill_value=0)
    total = anual.sum(axis=1)
    pico = int(total.idxmax())
    st.subheader(f"La violencia organizada tuvo su año más intenso en {pico}: {tema.miles(total.max())} eventos")
    fig = go.Figure()
    for tipo, color in tema.TIPOS_UCDP.items():
        if tipo not in anual:
            continue
        serie = anual[tipo]
        fig.add_scatter(x=serie.index, y=serie.values, name=tipo, mode="lines", line=dict(color=color, width=2.4, shape="linear"),
                        hovertemplate=f"{tipo}<br>%{{x}}: %{{y:,.0f}} eventos<extra></extra>")
        fig.add_annotation(x=serie.index[-1], y=serie.values[-1], text=f"<b>{tipo}</b>", showarrow=False, xanchor="left", xshift=8,
                           font=dict(color=color, family="Chakra Petch", size=13))
    if a1 in anual.index:
        fig.add_vrect(x0=a1 - 0.5, x1=a1 + 0.5, fillcolor=tema.FILETE, opacity=.5, line_width=0,
                      annotation_text="2026 parcial", annotation_position="top left", annotation_font_color=tema.GRIS_2)
    fig.update_layout(showlegend=False, margin=dict(r=170), yaxis_title="Eventos por año",
                      xaxis=dict(range=[anual.index.min() - 0.5, anual.index.max() + 0.5]))
    grafica(fig)

    mapa = datos.mapa_mundo()
    i0, i1 = rango[0] - mapa["anios"][0], rango[1] - mapa["anios"][0]
    filas = [{"pais": p["nombre"], "muertes": sum(p["muertes"][i0:i1 + 1]), "area": p["area_km2"]} for p in mapa["paises"]]
    paises = pd.DataFrame(filas)
    paises["tasa"] = paises["muertes"] / paises["area"] * 1000
    top = paises[paises["area"] > 2000].nlargest(12, "tasa").iloc[::-1]
    col_a, col_b = st.columns([5, 6])
    with col_a:
        st.subheader(f"{top.iloc[-1]['pais']} encabeza la violencia por área")
        fig = go.Figure(go.Bar(x=top["tasa"], y=top["pais"], orientation="h",
                               marker=tema.celdas([tema.ROJO if i == len(top) - 1 else tema.ROJO_3 for i in range(len(top))]),
                               text=[tema.decimal(v) for v in top["tasa"]], textposition="outside",
                               textfont=dict(family="Martian Mono", color=tema.BLANCO),
                               cliponaxis=False, hovertemplate="%{y}: %{x:,.1f} muertes por 1.000 km²<extra></extra>"))
        fig.update_layout(xaxis_title="Muertes por cada 1.000 km²", margin=dict(r=90))
        grafica(fig, 470)
        st.markdown('<p class="nota">Países de más de 2.000 km². Superficie calculada en proyección de áreas iguales.</p>',
                    unsafe_allow_html=True)
    with col_b:
        region_anio = sel.groupby(["region", "anio"], observed=True).size().unstack(fill_value=0)
        maxima = region_anio.stack().idxmax()
        st.subheader(f"{maxima[0]} concentra el pico regional ({maxima[1]})")
        fig = go.Figure(go.Heatmap(z=region_anio.values, x=region_anio.columns, y=region_anio.index, colorscale=tema.ESCALA_ROJA,
                                   xgap=2, ygap=2, colorbar=dict(title="Eventos", outlinewidth=0, thickness=10),
                                   hovertemplate="%{y} · %{x}<br>%{z:,.0f} eventos<extra></extra>"))
        grafica(fig, 470)

else:
    hom = datos.homicidios()
    a1 = int(hom["anio"].max())
    c1, c2 = st.columns([3, 2])
    rango = c1.slider("Años", 2005, a1, (2005, a1))
    deptos = c2.multiselect("Departamento", sorted(hom["departamento"].astype(str).unique()), placeholder="Todo el país")
    sel = hom[hom["anio"].between(*rango) & (hom["departamento"].astype(str).isin(deptos) if deptos else True)]
    if sel.empty:
        st.markdown('<div class="vacio">No hay homicidios con estos filtros. Amplíe el rango de años o quite departamentos.</div>',
                    unsafe_allow_html=True)
        st.stop()

    comp = sel.pivot_table(index="anio", columns="categoria_violencia", values="cantidad", aggfunc="sum", observed=True).fillna(0)
    pct = comp.div(comp.sum(axis=1), axis=0) * 100
    crimen = pct.get("Crimen organizado y sicariato", pd.Series(dtype=float))
    # El último año es parcial (hasta septiembre): el titular compara contra el último año completo
    completos = crimen[crimen.index < a1] if (a1 in crimen.index and len(crimen) > 1) else crimen
    st.subheader(f"El crimen organizado y el sicariato pasaron de {tema.decimal(completos.iloc[0], 0)} % a "
                 f"{tema.decimal(completos.iloc[-1], 0)} % de los homicidios ({completos.index[0]}–{completos.index[-1]})")
    fig = go.Figure()
    for cat, color in tema.CATEGORIAS.items():
        if cat in pct:
            fig.add_bar(x=pct.index, y=pct[cat], name=cat, marker=tema.celdas(color),
                        hovertemplate=f"{cat}<br>%{{x}}: %{{y:.1f}} %<extra></extra>")
    fig.add_vline(x=2016.5, line=dict(color=tema.BLANCO, width=1, dash="dot"))
    fig.add_annotation(x=2016.5, y=104, text="Acuerdo de Paz", showarrow=False, xanchor="right", font=dict(color=tema.GRIS_3, size=12))
    fig.update_layout(barmode="stack", bargap=0.12, yaxis=dict(range=[0, 108], ticksuffix=" %"), legend=dict(y=-0.14))
    grafica(fig, 470)

    col_a, col_b = st.columns(2)
    clases = ["Conflicto armado", "Crimen organizado y sicariato", "Convivencia y riñas", "Delincuencia común"]
    con_clase = sel[sel["categoria_violencia"].isin(clases)]
    with col_a:
        armas = con_clase.pivot_table(index="categoria_violencia", columns="arma_grupo", values="cantidad", aggfunc="sum",
                                      observed=True).fillna(0).reindex(clases)
        armas = armas.div(armas.sum(axis=1), axis=0) * 100
        fuego = armas.get("Arma de fuego", pd.Series(0, index=clases))
        st.subheader(f"El sicariato es con arma de fuego en el {tema.decimal(fuego.get('Crimen organizado y sicariato', 0))} % de los casos")
        orden_armas = ["Arma de fuego", "Arma blanca", "Contundente", "Explosivos"]
        colores_armas = [tema.ROJO, tema.GRIS_3, tema.GRIS_1, tema.ROJO_3]
        fig = go.Figure()
        for arma, color in zip(orden_armas, colores_armas):
            if arma in armas:
                fig.add_bar(y=armas.index, x=armas[arma], name=arma, orientation="h", marker=tema.celdas(color),
                            hovertemplate=f"{arma}<br>%{{y}}: %{{x:.1f}} %<extra></extra>")
        fig.update_layout(barmode="stack", xaxis=dict(range=[0, 100], ticksuffix=" %"), legend=dict(y=-0.2))
        grafica(fig, 430)
    with col_b:
        semana = con_clase.pivot_table(index="categoria_violencia", columns="dia_semana", values="cantidad", aggfunc="sum",
                                       observed=True).reindex(index=clases, columns=DIAS).fillna(0)
        semana = semana.div(semana.sum(axis=1), axis=0) * 100
        domingo = semana.loc["Convivencia y riñas", "Domingo"] if "Convivencia y riñas" in semana.index else np.nan
        st.subheader(f"Las riñas se concentran en domingo: {tema.decimal(domingo)} % de sus víctimas")
        cortas = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        etiquetas = ["Conflicto", "Crimen org.", "Riñas", "Delincuencia"]
        fig = go.Figure(go.Heatmap(z=semana.values, x=cortas, y=etiquetas, colorscale=tema.ESCALA_ROJA, xgap=2, ygap=2,
                                   showscale=False,
                                   hovertemplate="%{y} · %{x}<br>%{z:.1f} % de sus víctimas<extra></extra>"))
        tema.textos_heatmap(fig, cortas, etiquetas, semana.values.tolist(),
                            [[f"{tema.decimal(v)} %" for v in fila] for fila in semana.values])
        fig.update_layout(xaxis=dict(tickfont=tema.TEXTO, side="top"), yaxis=dict(autorange="reversed"))
        grafica(fig, 430)

    st.subheader("Departamentos con más víctimas en el periodo")
    categoria = st.pills("Categoría", clases, default="Conflicto armado", label_visibility="collapsed") or "Conflicto armado"
    dep = (sel[sel["categoria_violencia"] == categoria].groupby("departamento", observed=True)["cantidad"].sum()
           .sort_values(ascending=False).head(12).iloc[::-1])
    fig = go.Figure(go.Bar(x=dep.values, y=dep.index.astype(str), orientation="h",
                           marker=tema.celdas([tema.CATEGORIAS[categoria] if i == len(dep) - 1 else tema.GRIS_1 for i in range(len(dep))]),
                           text=[tema.miles(v) for v in dep.values], textposition="outside",
                           textfont=dict(family="Martian Mono", color=tema.BLANCO),
                           cliponaxis=False, hovertemplate="%{y}: %{x:,.0f} víctimas<extra></extra>"))
    fig.update_layout(xaxis_title="Víctimas", margin=dict(r=80))
    grafica(fig, 460)

st.markdown('<p class="nota">Fuentes: UCDP GED 26.1 y Candidate 2026 (Uppsala University); homicidios del Ministerio de Defensa '
            'Nacional (datos.gov.co). 2026 es parcial.</p>', unsafe_allow_html=True)
