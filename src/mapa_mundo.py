"""Prepara el mapamundi del dashboard: países en proyección Equal Earth y violencia por país y año.

- Proyección Equal Earth (Šavrič, Patterson y Jenny, 2018): conserva las áreas, así que el tamaño de
  cada país en pantalla es proporcional a su superficie real (a diferencia de Mercator).
- Intensidad: muertes estimadas de UCDP (`best`) por cada 1.000 km². UCDP no trae población, por eso
  la medida es por área y no por habitante. El dashboard la calcula para el periodo que elija el visitante.
- Focos: celdas de 1° × 1° con las muertes de cada año, para marcar las zonas más violentas.

Uso (desde la raíz del proyecto, dentro del contenedor):
    python src/mapa_mundo.py
Escribe data/processed/mapa_mundo.json, que el dashboard lee sin recalcular nada.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.path import Path as Trazado

RAIZ = Path(__file__).resolve().parent.parent
RUTA_GEOJSON = RAIZ / "data" / "raw" / "ne_50m_admin_0_countries.geojson"
RUTA_EVENTOS = RAIZ / "data" / "processed" / "ucdp_eventos.parquet"
RUTA_SALIDA = RAIZ / "data" / "processed" / "mapa_mundo.json"

RADIO_TIERRA_KM = 6371.0088
LATITUD_MINIMA = -58.0      # se recorta la Antártida
ANCHO = 1000.0              # unidades del lienzo; el dashboard escala a su tamaño real
PRECISION = 1               # decimales de las coordenadas del contorno
AREA_MINIMA_ISLA = 0.6      # unidades² del lienzo: islas más pequeñas se omiten si el país tiene otras partes

_A1, _A2, _A3, _A4 = 1.340264, -0.081106, 0.000893, 0.003796
_M = np.sqrt(3) / 2


def equal_earth(lon_grados, lat_grados):
    """Proyecta longitud/latitud (grados) a Equal Earth sobre una esfera unitaria."""
    lam = np.radians(np.asarray(lon_grados, dtype=float))
    phi = np.radians(np.asarray(lat_grados, dtype=float))
    theta = np.arcsin(_M * np.sin(phi))
    t2 = theta ** 2
    t6 = t2 ** 3
    x = (2 * np.sqrt(3) * lam * np.cos(theta)) / (3 * (9 * _A4 * t6 * t2 + 7 * _A3 * t6 + 3 * _A2 * t2 + _A1))
    y = theta * (_A4 * t6 * t2 + _A3 * t6 + _A2 * t2 + _A1)
    return x, y


X_MAX = float(equal_earth(180, 0)[0])
Y_MAX = float(equal_earth(0, 90)[1])
Y_MIN = float(equal_earth(0, LATITUD_MINIMA)[1])
ESCALA = ANCHO / (2 * X_MAX)
ALTO = (Y_MAX - Y_MIN) * ESCALA


def a_lienzo(lon, lat):
    """Longitud/latitud → coordenadas del lienzo (origen arriba a la izquierda)."""
    x, y = equal_earth(lon, lat)
    return (x + X_MAX) * ESCALA, (Y_MAX - y) * ESCALA


def _poligonos(geometria):
    if geometria["type"] == "Polygon":
        return [geometria["coordinates"]]
    return geometria["coordinates"]


def _area(x, y):
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def _a_ruta(x, y):
    """Contorno → comando SVG, sin vértices repetidos tras redondear."""
    puntos = np.round(np.column_stack([x, y]), PRECISION)
    distintos = np.ones(len(puntos), dtype=bool)
    distintos[1:] = np.any(np.diff(puntos, axis=0) != 0, axis=1)
    puntos = puntos[distintos]
    if len(puntos) < 3:
        return ""
    texto = " ".join(f"{px:g} {py:g}" for px, py in puntos)
    return f"M{texto}Z"


def cargar_paises(ruta=RUTA_GEOJSON):
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    paises = []
    for feature in datos["features"]:
        props = feature["properties"]
        if props.get("ADM0_A3") == "ATA":
            continue
        rutas, trazados, area_total, partes = [], [], 0.0, []
        for poligono in _poligonos(feature["geometry"]):
            anillo = np.asarray(poligono[0])
            x, y = a_lienzo(anillo[:, 0], anillo[:, 1])
            partes.append((_area(x, y), x, y))
        partes.sort(key=lambda p: -p[0])
        for i, (area, x, y) in enumerate(partes):
            area_total += area
            trazados.append(Trazado(np.column_stack([x, y])))
            if i == 0 or area >= AREA_MINIMA_ISLA:
                rutas.append(_a_ruta(x, y))
        mayor = partes[0]
        paises.append({
            "iso": props.get("ADM0_A3"),
            "nombre": props.get("NAME_ES") or props.get("NAME"),
            "continente": props.get("CONTINENT"),
            "area_km2": round(area_total / ESCALA ** 2 * RADIO_TIERRA_KM ** 2),
            "ruta": "".join(r for r in rutas if r),
            "centro": [round(float(np.mean(mayor[1])), 1), round(float(np.mean(mayor[2])), 1)],
            "_trazados": trazados,
        })
    return paises


def asignar_paises(paises, x, y):
    """Índice del país de cada punto (−1 si cae en el mar). Filtra por caja antes del punto-en-polígono."""
    indice = np.full(len(x), -1, dtype=int)
    puntos = np.column_stack([x, y])
    for i, pais in enumerate(paises):
        for trazado in pais["_trazados"]:
            (x0, y0), (x1, y1) = trazado.get_extents().get_points()
            candidatos = np.flatnonzero((indice == -1) & (x >= x0) & (x <= x1) & (y >= y0) & (y <= y1))
            if len(candidatos):
                indice[candidatos[trazado.contains_points(puntos[candidatos])]] = i
    return indice


def preparar():
    paises = cargar_paises()
    eventos = pd.read_parquet(RUTA_EVENTOS, columns=["latitude", "longitude", "best", "anio", "adm_1", "country"])
    eventos = eventos[eventos["latitude"] >= LATITUD_MINIMA]
    x, y = a_lienzo(eventos["longitude"].to_numpy(), eventos["latitude"].to_numpy())
    eventos = eventos.assign(x=x, y=y, pais=asignar_paises(paises, x, y))

    anios = list(range(int(eventos["anio"].min()), int(eventos["anio"].max()) + 1))
    con_pais = eventos[eventos["pais"] >= 0]
    muertes = con_pais.pivot_table(index="pais", columns="anio", values="best", aggfunc="sum", fill_value=0)
    conteo = con_pais.pivot_table(index="pais", columns="anio", values="best", aggfunc="size", fill_value=0)
    for i, pais in enumerate(paises):
        pais["muertes"] = [int(muertes.loc[i, a]) if i in muertes.index and a in muertes.columns else 0 for a in anios]
        pais["eventos"] = [int(conteo.loc[i, a]) if i in conteo.index and a in conteo.columns else 0 for a in anios]
        del pais["_trazados"]

    # Focos: celdas de 1° × 1° por año, con el lugar más frecuente de la celda
    # el país del foco se nombra en español con el polígono que lo contiene (UCDP lo trae en inglés)
    nombres = np.array([p["nombre"] for p in paises] + [""], dtype=object)
    eventos["pais_es"] = np.where(eventos["pais"] >= 0, nombres[eventos["pais"].to_numpy()], eventos["country"].astype(str))
    eventos["celda_lat"] = np.floor(eventos["latitude"]).astype(int)
    eventos["celda_lon"] = np.floor(eventos["longitude"]).astype(int)
    eventos["lugar"] = eventos["adm_1"].astype(str).str.replace(r"\s+(province|prefecture|department|district|region|state|governorate|oblast|county|municipality)$",
                                                                "", regex=True, case=False)
    focos = (eventos.groupby(["anio", "celda_lat", "celda_lon"], observed=True)
             .agg(muertes=("best", "sum"),
                  lugar=("lugar", lambda s: s.mode().iat[0] if not s.mode().empty else ""),
                  pais=("pais_es", lambda s: str(s.mode().iat[0]) if not s.mode().empty else ""))
             .reset_index())
    focos = focos[focos["muertes"] >= 10]
    fx, fy = a_lienzo(focos["celda_lon"] + 0.5, focos["celda_lat"] + 0.5)
    focos_salida = [[round(float(a), 1), round(float(b), 1), int(anio), int(m), str(l).replace("nan", ""), p]
                    for a, b, anio, m, l, p in zip(fx, fy, focos["anio"], focos["muertes"], focos["lugar"], focos["pais"])]

    salida = {
        "fuente": "UCDP GED 26.1 + Candidate 2026; límites: Natural Earth 1:50m",
        "proyeccion": "Equal Earth",
        "ancho": ANCHO, "alto": round(ALTO, 1),
        "anios": anios,
        "anio_ultimo_completo": anios[-1] - 1,
        "paises": paises,
        "focos": focos_salida,
        "eventos_sin_pais": int((eventos["pais"] < 0).sum()),
    }
    RUTA_SALIDA.write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return salida


if __name__ == "__main__":
    resultado = preparar()
    print(f"{RUTA_SALIDA.relative_to(RAIZ)}: {len(resultado['paises'])} países, {len(resultado['focos'])} focos, "
          f"{RUTA_SALIDA.stat().st_size / 1e6:.2f} MB | eventos en el mar o sin país: {resultado['eventos_sin_pais']}")
