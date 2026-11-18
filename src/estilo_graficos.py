"""Guía de estilo de las visualizaciones del proyecto.

Aplica los criterios del curso (Herramientas y visualización de datos, unidades 1 a 4):
- Paleta cualitativa Okabe-Ito, segura para daltonismo, con máximo 7 colores con significado.
- El mismo color significa lo mismo en todas las gráficas (consistencia).
- Base en grises para el contexto y color de acento solo para lo que se quiere destacar.
- Una sola familia tipográfica sans-serif con jerarquía por tamaño y peso.
- Alto data-ink ratio: sin bordes superiores/derechos, grilla gris suave solo en el eje de valores.
- Títulos que enuncian el hallazgo, subtítulo con qué se mide y fuente al pie.

El dashboard (Streamlit) importa este mismo módulo para que las gráficas sean coherentes.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------- colores
# Colores Okabe-Ito (Okabe & Ito, 2008). Cada uno tiene un significado fijo en todo el proyecto.
CATEGORIAS_VIOLENCIA = {
    "Conflicto armado": "#D55E00",               # bermellón: alerta, violencia militarizada
    "Crimen organizado y sicariato": "#0072B2",  # azul
    "Convivencia y riñas": "#CC79A7",            # púrpura rojizo
    "Delincuencia común": "#009E73",             # verde azulado
    "Otras modalidades": "#B3B3B3",              # gris: contexto
    "Sin información": "#DDDDDD",                # gris claro: dato faltante
}
# Tipos de violencia de UCDP. 'Estatal' comparte el bermellón del conflicto armado (misma idea:
# violencia militarizada) y 'No estatal' el azul del crimen organizado (enfrentamientos entre grupos).
TIPOS_UCDP = {
    "Conflicto estatal": "#D55E00",
    "Conflicto no estatal": "#0072B2",
    "Violencia unilateral": "#882255",           # vino (Paul Tol): ataques contra civiles
}
ARMA_DE_FUEGO = "#E69F00"   # naranja Okabe-Ito: reservado para el arma de fuego
COLOR_MODELO = "#000000"    # negro (también parte de Okabe-Ito): el modelo elegido / variables clave
GRIS_OSCURO = "#333333"     # texto principal (contraste 12,6:1 sobre blanco)
GRIS_TEXTO = "#4D4D4D"      # subtítulos (8,4:1)
GRIS_FUENTE = "#595959"     # notas y fuente (7,0:1, nivel AAA)
GRIS_CONTEXTO = "#B3B3B3"   # datos de contexto
GRIS_GRILLA = "#E6E6E6"     # grilla y guías
MAPA_SECUENCIAL = "cividis" # secuencial perceptualmente uniforme y apto para daltonismo

CARPETA_FIGURAS = Path(__file__).resolve().parent.parent / "reports" / "figuras"


def aplicar_estilo() -> None:
    """Configura matplotlib con la tipografía y el data-ink ratio del proyecto."""
    plt.rcParams.update({
        "font.family": "DejaVu Sans",          # una sola familia sans-serif
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10.5,
        "axes.labelcolor": GRIS_OSCURO,
        "axes.edgecolor": GRIS_CONTEXTO,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "axes.axisbelow": True,
        "xtick.color": GRIS_TEXTO,
        "ytick.color": GRIS_TEXTO,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "grid.color": GRIS_GRILLA,
        "grid.linewidth": 0.8,
        "legend.frameon": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })


def grilla(ax, eje: str = "y") -> None:
    """Grilla gris suave solo en el eje de valores; se oculta la línea de ese eje."""
    ax.grid(axis=eje, color=GRIS_GRILLA, linewidth=0.8)
    ax.spines["left" if eje == "y" else "bottom"].set_visible(False)
    ax.tick_params(axis=eje, length=0)


def encabezado(fig, titulo: str, subtitulo: str = "", espacio_extra: float = 0.0) -> None:
    """Título con el hallazgo (15 pt, negrita) y subtítulo con qué se mide (11 pt), alineados a la izquierda.

    Las posiciones se calculan en pulgadas para que títulos de una o dos líneas no se encimen.
    """
    alto = fig.get_figheight()
    y_titulo = 1 - 0.10 / alto
    fig.text(0.01, y_titulo, titulo, fontsize=15, fontweight="bold", color=GRIS_OSCURO,
             ha="left", va="top", linespacing=1.25)
    lineas_titulo = titulo.count("\n") + 1
    y_sub = y_titulo - (lineas_titulo * 0.29 + 0.05) / alto
    if subtitulo:
        fig.text(0.01, y_sub, subtitulo, fontsize=11, color=GRIS_TEXTO, ha="left", va="top", linespacing=1.3)
        y_sub -= (subtitulo.count("\n") + 1) * 0.21 / alto
    fig.subplots_adjust(top=y_sub - (0.30 + espacio_extra) / alto)


def pie_de_fuente(fig, texto: str, espacio_ejes: float = 0.55) -> None:
    """Fuente y notas metodológicas al pie (8,5 pt, gris con contraste AAA).

    espacio_ejes: pulgadas que se reservan entre la nota y el área del gráfico (etiquetas del eje x).
    """
    alto = fig.get_figheight()
    fig.text(0.01, 0.06 / alto, texto, fontsize=8.5, color=GRIS_FUENTE, ha="left", va="bottom", linespacing=1.35)
    lineas = texto.count("\n") + 1
    fig.subplots_adjust(bottom=(0.06 + lineas * 0.17 + espacio_ejes) / alto)


def separar_etiquetas(valores, distancia_minima: float):
    """Devuelve posiciones para etiquetas que conservan el orden y quedan al menos a 'distancia_minima'.

    Sirve para etiquetar directamente líneas que terminan muy cerca (evita la leyenda, principio de proximidad).
    """
    valores = np.asarray(valores, dtype=float)
    orden = np.argsort(valores)
    posiciones = valores[orden].copy()
    for i in range(1, len(posiciones)):
        posiciones[i] = max(posiciones[i], posiciones[i - 1] + distancia_minima)
    resultado = np.empty_like(posiciones)
    resultado[orden] = posiciones
    return resultado


def formato_miles(valor, _pos=None) -> str:
    """Formato de miles con punto, como se escribe en español."""
    return f"{valor:,.0f}".replace(",", ".")


def formato_decimal(decimales: int = 1):
    """Formateador de ejes con coma decimal (para usar con matplotlib.ticker.FuncFormatter)."""
    return lambda valor, _pos=None: f"{valor:.{decimales}f}".replace(".", ",")


def porcentaje(valor: float, decimales: int = 1) -> str:
    return f"{valor:.{decimales}f} %".replace(".", ",")


def guardar(fig, nombre: str) -> str:
    """Guarda la figura en reports/figuras/ (200 ppp) y devuelve la ruta relativa al proyecto."""
    CARPETA_FIGURAS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_FIGURAS / f"{nombre}.png"
    fig.savefig(ruta)
    return f"reports/figuras/{ruta.name}"

