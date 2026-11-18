"""Genera el reporte PDF del proyecto a partir del documento de análisis guardado en MongoDB.

El reporte no se escribe a mano: todo el contenido (cifras, tablas, insights, recomendaciones y
la lista de gráficas) se lee del documento más reciente de la colección de análisis.

Uso:
    python src/generar_reporte.py            # usa MONGO_URI y MONGO_BD del entorno (contenedor)
También se puede importar y llamar a generar_reporte() desde el notebook.
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
from PIL import Image as ImagenPIL
from pymongo import MongoClient
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

RAIZ = Path(__file__).resolve().parent.parent
COLECCION = "analisis"

# Misma familia tipográfica que las gráficas (DejaVu Sans, incluida con matplotlib)
CARPETA_FUENTES = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
pdfmetrics.registerFont(TTFont("DejaVu", str(CARPETA_FUENTES / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(CARPETA_FUENTES / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Oblique", str(CARPETA_FUENTES / "DejaVuSans-Oblique.ttf")))
# Sin esto, <b> e <i> dentro de los párrafos no encuentran la variante de la fuente
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold", italic="DejaVu-Oblique",
                              boldItalic="DejaVu-Bold")

GRIS_OSCURO = colors.HexColor("#333333")
GRIS_TEXTO = colors.HexColor("#4D4D4D")
GRIS_FUENTE = colors.HexColor("#595959")
GRIS_LINEA = colors.HexColor("#CCCCCC")
GRIS_FONDO = colors.HexColor("#F2F2F2")
ACENTO = colors.HexColor("#D55E00")  # bermellón del proyecto (conflicto armado)

ESTILOS = {
    "portada_titulo": ParagraphStyle("portada_titulo", fontName="DejaVu-Bold", fontSize=24, leading=30, textColor=GRIS_OSCURO),
    "portada_sub": ParagraphStyle("portada_sub", fontName="DejaVu", fontSize=13, leading=18, textColor=GRIS_TEXTO),
    "h1": ParagraphStyle("h1", fontName="DejaVu-Bold", fontSize=16, leading=21, textColor=GRIS_OSCURO, spaceBefore=6, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="DejaVu-Bold", fontSize=12, leading=16, textColor=GRIS_OSCURO, spaceBefore=8, spaceAfter=4),
    "cuerpo": ParagraphStyle("cuerpo", fontName="DejaVu", fontSize=9.5, leading=13.5, textColor=GRIS_OSCURO, alignment=TA_LEFT, spaceAfter=5),
    "nota": ParagraphStyle("nota", fontName="DejaVu", fontSize=8, leading=10.5, textColor=GRIS_FUENTE, spaceAfter=8),
    "celda": ParagraphStyle("celda", fontName="DejaVu", fontSize=7.5, leading=9.5, textColor=GRIS_OSCURO),
    "celda_titulo": ParagraphStyle("celda_titulo", fontName="DejaVu-Bold", fontSize=7, leading=9, textColor=GRIS_OSCURO),
}
ANCHO_UTIL = A4[0] - 4 * cm


def miles(valor) -> str:
    try:
        return f"{float(valor):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return str(valor)


def numero(valor, decimales=3) -> str:
    try:
        return f"{float(valor):.{decimales}f}".replace(".", ",")
    except (TypeError, ValueError):
        return str(valor)


def tabla(filas, encabezados, anchos=None, numericas=()):
    """Tabla con estilo del proyecto: sin bordes verticales, encabezado gris, líneas finas (data-ink)."""
    def encabezado(texto):
        texto = escape(str(texto))
        # Rangos de años ("1990–1994") en dos líneas para que no se partan a mitad de número
        return Paragraph(re.sub(r"^(\d{4})–(\d{4}\*?)$", r"\1–<br/>\2", texto), ESTILOS["celda_titulo"])

    datos = [[encabezado(e) for e in encabezados]]
    for fila in filas:
        datos.append([Paragraph(escape(str(v)), ESTILOS["celda"]) for v in fila])
    t = Table(datos, colWidths=anchos, repeatRows=1, hAlign="LEFT")
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), GRIS_FONDO),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, GRIS_OSCURO),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, GRIS_LINEA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for columna in numericas:
        estilo.append(("ALIGN", (columna, 1), (columna, -1), "RIGHT"))
    t.setStyle(TableStyle(estilo))
    return t


def imagen(ruta: Path, ancho_max=ANCHO_UTIL, alto_max=11 * cm):
    """Inserta una figura respetando su proporción."""
    with ImagenPIL.open(ruta) as img:
        ancho_px, alto_px = img.size
    escala = min(ancho_max / ancho_px, alto_max / alto_px)
    return Image(str(ruta), width=ancho_px * escala, height=alto_px * escala)


def tabla_agregacion(agregacion, max_filas=20):
    columnas = agregacion["columnas"]
    filas = agregacion["filas"][-max_filas:]
    if agregacion.get("formato") == "porcentaje":
        formatear = lambda v: f"{numero(v, 1)} %" if isinstance(v, (int, float)) else v
    else:
        formatear = lambda v: miles(v) if isinstance(v, (int, float)) else v
    filas_fmt = [[fila[0]] + [formatear(v) for v in fila[1:]] for fila in filas]
    ancho_primera = 3.2 * cm
    resto = (ANCHO_UTIL - ancho_primera) / max(len(columnas) - 1, 1)
    return tabla(filas_fmt, columnas, [ancho_primera] + [resto] * (len(columnas) - 1),
                 numericas=range(1, len(columnas)))


def pie_de_pagina(lienzo, documento, titulo_corto):
    lienzo.saveState()
    lienzo.setFont("DejaVu", 7.5)
    lienzo.setFillColor(GRIS_FUENTE)
    lienzo.drawString(2 * cm, 1.2 * cm, titulo_corto)
    lienzo.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {documento.page}")
    lienzo.setStrokeColor(GRIS_LINEA)
    lienzo.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    lienzo.restoreState()


def leer_documento(uri: str, base_datos: str) -> dict:
    """Lee el documento de análisis más reciente desde MongoDB."""
    with MongoClient(uri, serverSelectionTimeoutMS=8000) as cliente:
        documento = cliente[base_datos][COLECCION].find_one(sort=[("metadata.fecha_analisis", -1)])
    if documento is None:
        raise RuntimeError("No hay documentos de análisis en MongoDB: ejecute primero el notebook.")
    return documento


def construir_historia(doc: dict, raiz: Path) -> list:
    meta, calidad, modelo = doc["metadata"], doc["calidad_datos"], doc["modelo"]
    estadisticas = doc["estadisticas_descriptivas"]
    h = []

    # ---------------- portada
    h += [Spacer(1, 5 * cm),
          Paragraph(meta["titulo"], ESTILOS["portada_titulo"]), Spacer(1, 0.5 * cm),
          Paragraph(meta["subtitulo"], ESTILOS["portada_sub"]), Spacer(1, 1.5 * cm),
          Paragraph(f"<b>Autor:</b> {', '.join(meta['autores'])}", ESTILOS["cuerpo"]),
          Paragraph(f"<b>Curso:</b> {meta['curso']}", ESTILOS["cuerpo"]),
          Paragraph(f"<b>Fecha del análisis:</b> {meta['fecha_analisis'][:10]}", ESTILOS["cuerpo"]),
          Paragraph(f"<b>Registros analizados:</b> {miles(meta['dataset']['registros'])}", ESTILOS["cuerpo"]),
          Spacer(1, 1 * cm),
          Paragraph(f"<b>Pregunta de negocio.</b> {meta['pregunta_negocio']}", ESTILOS["cuerpo"]),
          Spacer(1, 3 * cm),
          Paragraph("Reporte generado automáticamente a partir del documento de análisis almacenado en MongoDB "
                    f"(colección <i>{COLECCION}</i>, id {doc['_id']}).", ESTILOS["nota"]),
          PageBreak()]

    # ---------------- 1. resumen del dataset
    h.append(Paragraph("1. Resumen de los datos", ESTILOS["h1"]))
    h.append(Paragraph(meta["dataset"]["descripcion"], ESTILOS["cuerpo"]))
    filas = [[f["nombre"], f["periodo"], miles(f["registros"]), f["columnas"], numero(f["peso_mb"], 1), f["url"]]
             for f in meta["dataset"]["fuentes"]]
    h.append(tabla(filas, ["Fuente", "Periodo", "Registros", "Columnas", "MB", "URL"],
                   [3.8 * cm, 2.2 * cm, 1.9 * cm, 1.8 * cm, 1.2 * cm, ANCHO_UTIL - 10.9 * cm], numericas=(2, 3, 4)))
    hom, ucdp = estadisticas["homicidios"], estadisticas["ucdp"]
    h.append(Spacer(1, 0.3 * cm))
    h.append(Paragraph(
        f"<b>Homicidios en Colombia:</b> {miles(hom['victimas'])} víctimas entre {hom['periodo']}; "
        f"el {numero(hom['pct_arma_fuego'], 1)} % con arma de fuego y el {numero(hom['pct_rural'], 1)} % en zona rural. "
        f"<b>Violencia organizada global (UCDP):</b> {miles(ucdp['eventos'])} eventos en {ucdp['paises']} países "
        f"entre {ucdp['periodo']}, con {miles(ucdp['muertes_estimadas'])} muertes estimadas.", ESTILOS["cuerpo"]))

    # ---------------- 2. calidad de datos
    h.append(Paragraph("2. Problemas de calidad detectados y resueltos", ESTILOS["h1"]))
    h.append(Paragraph(
        f"Se detectaron {len(calidad['problemas_detectados'])} problemas de calidad. Se eliminaron "
        f"{miles(calidad['registros_eliminados'])} registros: los problemas eran de valores (nulos, categorías de "
        "'sin información' con nombres distintos, fechas como texto) y se corrigieron sin perder víctimas.", ESTILOS["cuerpo"]))
    filas = [[p["dataset"], p["columna"], p["problema"], miles(p["registros_afectados"]), p["decision"]]
             for p in calidad["problemas_detectados"]]
    h.append(tabla(filas, ["Dataset", "Columna", "Problema", "Registros", "Decisión"],
                   [1.9 * cm, 2.6 * cm, 5.1 * cm, 1.9 * cm, ANCHO_UTIL - 11.5 * cm], numericas=(3,)))
    h.append(PageBreak())

    # ---------------- 3. agregaciones
    h.append(Paragraph("3. Agregaciones multidimensionales (OLAP)", ESTILOS["h1"]))
    for agregacion in doc["agregaciones"]:
        bloque = [Paragraph(agregacion["nombre"], ESTILOS["h2"]),
                  Paragraph(f"{agregacion['descripcion']} Dimensiones: {' × '.join(agregacion['dimensiones'])}; "
                            f"medida: {agregacion['medida']}.", ESTILOS["nota"]),
                  tabla_agregacion(agregacion), Spacer(1, 0.3 * cm)]
        h.append(KeepTogether(bloque))
    h.append(PageBreak())

    # ---------------- 4. visualizaciones
    h.append(Paragraph("4. Visualizaciones", ESTILOS["h1"]))
    h.append(Paragraph("Gráficas diseñadas con la paleta Okabe-Ito (apta para daltonismo), títulos que enuncian el hallazgo "
                       "y etiquetas directas. Cada una responde una de las preguntas del análisis.", ESTILOS["cuerpo"]))
    graficas_analisis = [v for v in doc["visualizaciones_generadas"]
                         if v["pregunta"].startswith("Pregunta") and Path(raiz / v["archivo"]).exists()]
    for numero_figura, viz in enumerate(graficas_analisis, start=1):
        h.append(KeepTogether([imagen(raiz / viz["archivo"]),
                               Paragraph(f"Figura {numero_figura}. {viz['tipo_grafico']} · {viz['pregunta']} · "
                                         f"paleta: {viz['paleta']}.", ESTILOS["nota"])]))
    h.append(PageBreak())

    # ---------------- 5. modelo
    h.append(Paragraph("5. Resultados del modelo de Machine Learning", ESTILOS["h1"]))
    h.append(Paragraph(
        f"<b>Tarea:</b> {modelo['tarea']}. <b>Algoritmo elegido:</b> {modelo['algoritmo']}. "
        f"<b>Entrenamiento:</b> {modelo['periodo_entrenamiento']}; <b>prueba:</b> {modelo['periodo_prueba']}. "
        f"{modelo['descripcion']}", ESTILOS["cuerpo"]))
    filas = [[nombre, numero(m["accuracy"]), numero(m["precision_macro"]), numero(m["recall_macro"]),
              numero(m["f1_macro"]), numero(m["recall · Conflicto armado"])]
             for nombre, m in modelo["comparacion_modelos"].items()]
    h.append(tabla(filas, ["Modelo", "Accuracy", "Precisión macro", "Recall macro", "F1 macro", "Recall conflicto"],
                   [5.0 * cm] + [(ANCHO_UTIL - 5.0 * cm) / 5] * 5, numericas=(1, 2, 3, 4, 5)))
    h.append(Spacer(1, 0.3 * cm))
    filas = [[c["criterio"], c["valor"], "Sí" if c["cumple"] else "No"] for c in modelo["criterios_exito"]]
    h.append(tabla(filas, ["Criterio de éxito", "Valor en la prueba", "¿Cumple?"], [9 * cm, 4 * cm, 4 * cm]))
    h.append(Spacer(1, 0.3 * cm))
    filas = [[v["nombre"], numero(v["caida_f1_macro"])] for v in modelo["variables_importantes"]]
    h.append(Paragraph("Importancia de las variables (caída de la F1 macro al permutar cada una)", ESTILOS["h2"]))
    h.append(tabla(filas, ["Variable", "Importancia"], [10 * cm, 3 * cm], numericas=(1,)))
    for viz in [v for v in doc["visualizaciones_generadas"] if v["pregunta"] == "Machine Learning"]:
        if Path(raiz / viz["archivo"]).exists():
            h.append(KeepTogether([Spacer(1, 0.3 * cm), imagen(raiz / viz["archivo"], alto_max=9.5 * cm)]))
    h.append(PageBreak())

    # ---------------- 6 y 7. insights y recomendaciones
    h.append(Paragraph("6. Insights", ESTILOS["h1"]))
    for insight in doc["insights"]:
        h.append(Paragraph(f"<b>{insight['id']}. {insight['titulo']}</b> <font color='#595959'>[{insight['tema']}]</font>",
                           ESTILOS["cuerpo"]))
        h.append(Paragraph(insight["detalle"], ESTILOS["cuerpo"]))
    h.append(Paragraph("7. Recomendaciones", ESTILOS["h1"]))
    for rec in doc["recomendaciones"]:
        h.append(Paragraph(f"<b>{rec['id']}. {rec['titulo']}</b> <font color='#595959'>(prioridad {rec['prioridad']})</font>",
                           ESTILOS["cuerpo"]))
        h.append(Paragraph(rec["detalle"], ESTILOS["cuerpo"]))
        h.append(Paragraph(f"Sustento: {rec['sustento']}", ESTILOS["nota"]))
    return h


def generar_reporte(uri: str, base_datos: str, ruta_salida: Path, raiz: Path = RAIZ) -> Path:
    """Lee el documento de MongoDB y escribe el PDF en ruta_salida. Devuelve la ruta."""
    documento = leer_documento(uri, base_datos)
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    titulo_corto = f"{documento['metadata']['titulo']} · {documento['metadata']['autores'][0]}"
    pdf = SimpleDocTemplate(str(ruta_salida), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=2 * cm,
                            title=documento["metadata"]["titulo"], author=", ".join(documento["metadata"]["autores"]),
                            subject=documento["metadata"]["subtitulo"])
    historia = construir_historia(documento, raiz)
    pdf.build(historia, onFirstPage=lambda c, d: None, onLaterPages=lambda c, d: pie_de_pagina(c, d, titulo_corto))
    return ruta_salida


if __name__ == "__main__":
    salida = RAIZ / "reports" / "reporte_violencia_armada.pdf"
    ruta = generar_reporte(os.environ["MONGO_URI"], os.environ.get("MONGO_BD", "violencia_armada"), salida)
    print(f"Reporte generado: {ruta} ({ruta.stat().st_size / 1e6:.1f} MB) — {datetime.now():%Y-%m-%d %H:%M}")
    sys.exit(0)
