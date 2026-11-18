"""Mundo visual del dashboard: rejilla de construcción en negro, blanco y rojo.

Paleta cerrada (solo estos tonos): tinta, seis grises y cuatro rojos. Chakra Petch para cifras y títulos,
Barlow para la interfaz y Martian Mono para datos. Filetes de 1 px, cero radio y una sola diagonal roja.
"""

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

TINTA = "#0A0A0A"
TINTA_2 = "#121212"
FILETE = "#262626"
FILETE_2 = "#3A3A3A"
GRIS_1 = "#5A5A5A"
GRIS_2 = "#8A8A8A"
GRIS_3 = "#B8B8B8"
BLANCO = "#F2F2F2"
ROJO = "#FF3B2A"
ROJO_2 = "#E0190F"
ROJO_3 = "#A31010"
ROJO_4 = "#4A0806"

# Categorías: el rojo siempre es la violencia del conflicto; el blanco, el crimen organizado
CATEGORIAS = {
    "Conflicto armado": ROJO,
    "Crimen organizado y sicariato": BLANCO,
    "Convivencia y riñas": GRIS_2,
    "Delincuencia común": GRIS_1,
    "Otras modalidades": FILETE_2,
    "Sin información": FILETE,
}
TIPOS_UCDP = {"Conflicto estatal": ROJO, "Conflicto no estatal": BLANCO, "Violencia unilateral": GRIS_2}
# Escala secuencial con luminosidad creciente: más rojo y más claro = más intenso
ESCALA_ROJA = [[0, TINTA_2], [0.35, ROJO_4], [0.7, ROJO_3], [1, ROJO]]
CELDA = 5      # paso de la celda del mapa (4 px de tinta + 1 px de separación); todas las tramas lo comparten


def tokens_css():
    """Variables de la paleta cerrada para los componentes HTML incrustados (iframe)."""
    return (f":root{{--tinta:{TINTA};--tinta-2:{TINTA_2};--filete:{FILETE};--filete-2:{FILETE_2};--gris-1:{GRIS_1};"
            f"--gris-2:{GRIS_2};--gris-3:{GRIS_3};--blanco:{BLANCO};--rojo:{ROJO};--rojo-2:{ROJO_2};--rojo-3:{ROJO_3};"
            f"--rojo-4:{ROJO_4};--celda:{CELDA}px}}")


def celdas(color):
    """Relleno de barra con el mismo paso de celda del mapa (Plotly marker)."""
    return dict(color=color, line=dict(width=0),
                pattern=dict(shape="|", size=CELDA, solidity=0.2, fgcolor=TINTA, fillmode="overlay"))


def textos_heatmap(fig, x, y, z, textos, zmax=None):
    """Rótulos de mapa de calor con el color de texto que contrasta con cada celda (≥ 4,5:1)."""
    z = [[v for v in fila] for fila in z]
    maximo = zmax or max(max(f) for f in z) or 1
    xs, ys, ts, cs = [], [], [], []
    for i, fila in enumerate(z):
        for j, v in enumerate(fila):
            xs.append(x[j]); ys.append(y[i]); ts.append(textos[i][j])
            cs.append(TINTA if v / maximo >= 0.86 else BLANCO)  # sobre ROJO, tinta; sobre rojos oscuros, blanco
    fig.add_scatter(x=xs, y=ys, mode="text", text=ts, textfont=dict(family="Martian Mono", size=12, color=cs),
                    hoverinfo="skip", showlegend=False)

CSS = f"""
<style>
@font-face{{font-family:"Chakra Petch";font-weight:600;src:url("app/static/fuentes/ChakraPetch-SemiBold.ttf") format("truetype");font-display:swap}}
@font-face{{font-family:"Chakra Petch";font-weight:700;src:url("app/static/fuentes/ChakraPetch-Bold.ttf") format("truetype");font-display:swap}}
@font-face{{font-family:"Barlow";font-weight:400;src:url("app/static/fuentes/Barlow-Regular.ttf") format("truetype");font-display:swap}}
@font-face{{font-family:"Barlow";font-weight:500;src:url("app/static/fuentes/Barlow-Medium.ttf") format("truetype");font-display:swap}}
@font-face{{font-family:"Barlow";font-weight:600;src:url("app/static/fuentes/Barlow-SemiBold.ttf") format("truetype");font-display:swap}}
@font-face{{font-family:"Martian Mono";font-weight:100 800;font-stretch:75% 112.5%;src:url("app/static/fuentes/MartianMono-Variable.ttf") format("truetype");font-display:swap}}

:root{{--tinta:{TINTA};--filete:{FILETE};--filete-2:{FILETE_2};--gris-2:{GRIS_2};--gris-3:{GRIS_3};--blanco:{BLANCO};--rojo:{ROJO}}}
html,body,.stApp{{background:{TINTA}}}
.stApp{{background-image:linear-gradient({TINTA_2} 1px,transparent 1px),linear-gradient(90deg,{TINTA_2} 1px,transparent 1px);
  background-size:24px 24px;background-position:-1px -1px;animation:rejilla 1.2s cubic-bezier(.16,1,.3,1) both}}
@keyframes rejilla{{from{{background-size:24px 0,0 24px}}to{{background-size:24px 24px,24px 24px}}}}
.stApp, .stApp p, .stApp li, .stApp label, .stMarkdown{{font-family:Barlow,system-ui,sans-serif}}
::selection{{background:{ROJO};color:{TINTA}}}
*{{scrollbar-width:thin;scrollbar-color:{FILETE_2} {TINTA}}}
::-webkit-scrollbar{{width:10px;height:10px}}::-webkit-scrollbar-track{{background:{TINTA}}}::-webkit-scrollbar-thumb{{background:{FILETE_2}}}
.block-container{{padding-top:3.6rem;padding-bottom:4rem;max-width:1480px}}
[data-testid="stHeader"]{{background:{TINTA};border-bottom:1px solid {FILETE}}}
[data-testid="stHeader"] .rc-overflow{{justify-content:flex-end}}
[data-testid="stHeaderLogo"], [data-testid="stLogo"]{{height:20px!important;max-width:none!important;
  margin-left:calc(max(0px, (100vw - 1480px) / 2) + var(--margen, 5rem))}}  /* la marca se alinea con la columna del contenido */
@media (max-width:735px){{[data-testid="stHeaderLogo"], [data-testid="stLogo"]{{--margen:1rem}}}}
[data-testid="stToolbar"]{{right:1rem}}
[data-testid="stDecoration"]{{display:none}}

/* títulos: tipografía de rejilla y un filete que se traza al aparecer */
h1,h2,h3,h4{{font-family:"Chakra Petch",sans-serif!important;letter-spacing:-.005em}}
.stApp h1{{font-size:clamp(2.1rem,3.4vw,3.15rem)!important;font-weight:700!important;line-height:1!important;padding:0!important}}
.stApp h2{{font-size:1.75rem!important;font-weight:700!important;margin-top:1.2rem!important;padding-bottom:.55rem!important;position:relative}}
.stApp h2::after{{content:"";position:absolute;left:0;bottom:0;height:1px;width:100%;background:{FILETE_2};transform-origin:left;
  animation:trazo .9s cubic-bezier(.16,1,.3,1) both}}
.stApp h3{{font-size:1.15rem!important;font-weight:600!important;text-transform:uppercase;letter-spacing:.06em!important}}
@keyframes trazo{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.stApp a{{text-underline-offset:3px}}

/* navegación superior: activo subrayado por la diagonal roja */
[data-testid="stTopNavLink"], [data-testid="stNavSectionHeader"]{{font-family:"Chakra Petch",sans-serif!important;text-transform:uppercase;letter-spacing:.07em;border-radius:0!important}}
[data-testid="stTopNavLink"] span{{font-family:"Chakra Petch",sans-serif!important;font-weight:600}}
[data-testid="stTopNavLink"][aria-current="page"]{{background:transparent!important;position:relative}}
[data-testid="stTopNavLink"][aria-current="page"]::after{{content:"";position:absolute;left:8px;right:8px;bottom:2px;height:3px;background:{ROJO};
  clip-path:polygon(4px 0,100% 0,calc(100% - 4px) 100%,0 100%)}}

/* controles: cero radio, filetes de 1 px, foco rojo */
.stButton>button, .stDownloadButton>button, .stFormSubmitButton>button{{border-radius:0!important;font-family:"Chakra Petch",sans-serif!important;
  text-transform:uppercase;letter-spacing:.07em;font-weight:600;border:1px solid {FILETE_2};position:relative;padding-right:2.6rem;transition:background .2s,color .2s,border-color .2s}}
.stButton>button::after, .stDownloadButton>button::after, .stFormSubmitButton>button::after{{content:"";position:absolute;right:.9rem;top:50%;width:14px;height:2px;
  background:currentColor;transform:translateY(-50%) rotate(-45deg)}}
.stButton>button[kind="primary"], .stFormSubmitButton>button, .stDownloadButton>button{{background:{BLANCO};color:{TINTA};border-color:{BLANCO}}}
.stButton>button:hover, .stFormSubmitButton>button:hover, .stDownloadButton>button:hover{{background:{ROJO}!important;color:{TINTA}!important;border-color:{ROJO}!important}}
button:focus-visible, input:focus-visible, [role="slider"]:focus-visible{{outline:2px solid {ROJO}!important;outline-offset:2px}}
[data-baseweb="select"]>div, [data-baseweb="input"]>div, .stDateInput>div>div, .stNumberInput>div>div{{border-radius:0!important;background:{TINTA_2}}}
[data-baseweb="tag"]{{border-radius:0!important;background:{ROJO_4}!important}}
[data-baseweb="tag"] span{{color:{BLANCO}!important}}
[data-testid="stHeaderActionElements"]{{display:none}}
button[kind^="pills"], button[kind^="segmented"]{{border-radius:0!important}}
[data-testid="stSegmentedControl"] button, [data-testid="stPills"] button{{border-radius:0!important;font-family:"Chakra Petch",sans-serif;text-transform:uppercase;letter-spacing:.06em}}
[data-testid="stSlider"] [role="slider"]{{border-radius:0!important;width:14px;height:20px}}
[data-testid="stExpander"] details{{border-radius:0;border-color:{FILETE_2}}}
[data-testid="stForm"]{{border-radius:0;border-color:{FILETE_2};background:rgba(18,18,18,.85)}}
[data-testid="stDataFrame"]{{border:1px solid {FILETE_2}}}
[data-testid="stMetric"]{{border-top:1px solid {FILETE_2};padding-top:.6rem}}
[data-testid="stMetricValue"]{{font-family:"Chakra Petch",sans-serif;font-weight:700}}
[data-testid="stAlert"]{{border-radius:0}}
/* cada gráfica es un módulo con filete de 1 px sobre la rejilla */
[data-testid="stPlotlyChart"]{{border:1px solid {FILETE_2};background:{TINTA};padding:6px 10px 2px}}

/* piezas propias */
.entrada{{font-size:1.08rem;color:{GRIS_3};max-width:68ch;margin:.5rem 0 1rem;line-height:1.5}}
.nota{{font-size:.82rem;color:{GRIS_2}}}
.cifras-fila{{display:grid;grid-template-columns:repeat(var(--n,4),1fr);border-top:1px solid {FILETE};border-bottom:1px solid {FILETE};margin:.4rem 0 1.4rem}}
.cifra-c{{padding:14px 18px 12px;display:flex;flex-direction:column;gap:4px;justify-content:flex-end}}
.cifra-c + .cifra-c{{border-left:1px solid {FILETE}}}
.cifra-c strong{{font:700 clamp(2rem,3.4vw,3.2rem)/.9 "Chakra Petch",sans-serif;font-variant-numeric:tabular-nums;animation:subir .9s cubic-bezier(.16,1,.3,1) both}}
.cifra-c span{{font-size:.86rem;color:{GRIS_3};max-width:30ch}}
.cifra-c.roja{{background:{ROJO};color:{TINTA}}}.cifra-c.roja span{{color:{TINTA}}}
.cifra-c:nth-child(2) strong{{animation-delay:.08s}}.cifra-c:nth-child(3) strong{{animation-delay:.16s}}.cifra-c:nth-child(4) strong{{animation-delay:.24s}}
@keyframes subir{{from{{opacity:0;transform:translateY(14px);filter:blur(4px)}}to{{opacity:1;transform:none;filter:none}}}}
.lista-diagonal{{list-style:none;padding:0;margin:0}}
.lista-diagonal li{{position:relative;padding:12px 0 12px 34px;border-bottom:1px solid {FILETE};animation:subir .7s cubic-bezier(.16,1,.3,1) both}}
.lista-diagonal li::before{{content:"";position:absolute;left:4px;top:22px;width:16px;height:2px;background:{ROJO};transform:rotate(-45deg)}}
.lista-diagonal li b{{font-family:"Chakra Petch",sans-serif;font-size:1.06rem;display:block;margin-bottom:3px}}
.lista-diagonal li span{{color:{GRIS_3};font-size:.95rem}}
.lista-diagonal li em{{display:block;margin-top:6px;font-style:normal;color:{GRIS_2};font-size:.78rem;text-transform:uppercase;letter-spacing:.06em}}
.composicion{{display:flex;height:34px;margin:6px 0 4px;gap:2px}}
.composicion i{{display:block;height:100%;transform-origin:left;animation:crecer 1.1s cubic-bezier(.16,1,.3,1) both;
  background-image:repeating-linear-gradient(90deg,currentColor 0 4px,transparent 4px 5px)}}
@keyframes crecer{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.leyenda-c{{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.82rem;color:{GRIS_3}}}
.leyenda-c span::before{{content:"";display:inline-block;width:10px;height:10px;margin-right:6px;background:var(--c);vertical-align:-1px}}
.prob{{display:grid;grid-template-columns:minmax(150px,1fr) 3fr auto;gap:10px 14px;align-items:center;margin:.4rem 0}}
.prob span{{font-size:.95rem}}
.prob i{{display:block;height:18px;transform-origin:left;animation:crecer 1s cubic-bezier(.16,1,.3,1) both;
  background-image:repeating-linear-gradient(90deg,currentColor 0 4px,transparent 4px 5px)}}
.prob b{{font:700 1.15rem "Chakra Petch",sans-serif;font-variant-numeric:tabular-nums;min-width:4.2ch;text-align:right}}
.vacio{{border:1px solid {FILETE_2};padding:28px;background-image:radial-gradient({FILETE_2} 1px,transparent 1.2px);background-size:12px 12px;color:{GRIS_3}}}
@media (max-width:760px){{
  .cifras-fila{{grid-template-columns:1fr 1fr}}
  .cifra-c + .cifra-c{{border-left:0}}
  .cifra-c:nth-child(even){{border-left:1px solid {FILETE}}}
  .cifra-c:nth-child(n+3){{border-top:1px solid {FILETE}}}
  .cifra-c strong{{font-size:2rem}}
  .prob{{grid-template-columns:1fr auto}}.prob i{{grid-column:1/3;grid-row:auto}}
}}
@media (prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important;transition:none!important}}}}
</style>
"""


def aplicar():
    """Inyecta el CSS global y registra la plantilla de Plotly del proyecto."""
    st.markdown(CSS, unsafe_allow_html=True)
    pio.templates["rejilla"] = go.layout.Template(layout=dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Barlow, sans-serif", color=BLANCO, size=13),
        title=dict(font=dict(family="Chakra Petch, sans-serif", size=20, color=BLANCO), x=0, xanchor="left"),
        colorway=[ROJO, BLANCO, GRIS_2, GRIS_1, ROJO_3, GRIS_3],
        xaxis=dict(automargin=True, gridcolor=TINTA_2, linecolor=FILETE_2, zerolinecolor=FILETE_2, tickcolor=FILETE_2,
                   tickfont=dict(family="Martian Mono, monospace", color=GRIS_2, size=11.5), title_font=dict(color=GRIS_3)),
        # el eje y suele llevar categorías (países, clases): Barlow; los números van en Martian Mono
        yaxis=dict(automargin=True, gridcolor=FILETE, linecolor=FILETE_2, zerolinecolor=FILETE_2, tickcolor=FILETE_2,
                   tickfont=dict(family="Barlow, sans-serif", color=GRIS_3, size=12.5), title_font=dict(color=GRIS_3)),
        hoverlabel=dict(bgcolor=TINTA, bordercolor=FILETE_2, font=dict(family="Martian Mono, monospace", color=BLANCO, size=12.5)),
        legend=dict(font=dict(color=GRIS_3), bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.18, x=0),
        margin=dict(l=8, r=8, t=56, b=8), separators=",.",
        transition=dict(duration=600, easing="cubic-in-out"),
    ))
    pio.templates.default = "rejilla"


MONO = dict(family="Martian Mono, monospace", color=GRIS_2, size=11.5)
TEXTO = dict(family="Barlow, sans-serif", color=GRIS_3, size=12.5)
CONFIG_GRAFICA = {"displayModeBar": False, "locale": "es"}


def cifras(items, roja=None):
    """Fila de cifras sobre la rejilla. items: lista de (valor, texto). roja: índice de la cifra sobre plano rojo."""
    celdas = "".join(f'<div class="cifra-c {"roja" if i == roja else ""}"><strong>{v}</strong><span>{t}</span></div>'
                     for i, (v, t) in enumerate(items))
    st.markdown(f'<div class="cifras-fila" style="--n:{len(items)}">{celdas}</div>', unsafe_allow_html=True)


def miles(valor):
    return f"{valor:,.0f}".replace(",", ".")


def decimal(valor, d=1):
    return f"{valor:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
