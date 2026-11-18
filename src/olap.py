"""Operaciones OLAP sobre los cubos del proyecto (slice, dice, roll-up, drill-down y pivot).

Los cubos son DataFrames en formato largo: columnas de dimensiones + columnas de medidas.
El notebook y el dashboard usan estas mismas funciones, así que los filtros del dashboard
devuelven exactamente las cifras que se muestran en el análisis.
"""

from typing import Iterable

import pandas as pd


def filtrar(cubo: pd.DataFrame, **filtros) -> pd.DataFrame:
    """Slice (un valor por dimensión) o dice (lista de valores o rango (desde, hasta)).

    Ejemplos:
        filtrar(cubo, anio=2025)                                   # slice
        filtrar(cubo, departamento=["CAUCA", "ARAUCA"], anio=(2017, 2025))  # dice
    """
    mascara = pd.Series(True, index=cubo.index)
    for dimension, valor in filtros.items():
        if valor is None:
            continue
        if isinstance(valor, tuple) and len(valor) == 2:
            mascara &= cubo[dimension].between(*valor)
        elif isinstance(valor, (list, set)):
            mascara &= cubo[dimension].isin(list(valor))
        else:
            mascara &= cubo[dimension] == valor
    return cubo[mascara]


def agregar(cubo: pd.DataFrame, dimensiones: Iterable[str], medidas: dict) -> pd.DataFrame:
    """Roll-up (menos dimensiones) o drill-down (más dimensiones) sumando las medidas.

    medidas: {"columna_resultado": ("columna_origen", "sum")}
    """
    dimensiones = list(dimensiones)
    if not dimensiones:
        return cubo.agg({origen: funcion for origen, funcion in medidas.values()}).to_frame().T
    return (cubo.groupby(dimensiones, observed=True)
            .agg(**medidas)
            .reset_index())


def pivotear(cubo: pd.DataFrame, filas: str, columnas: str, medida: str, totales: bool = True) -> pd.DataFrame:
    """Tabla cruzada filas × columnas con la suma de la medida (y totales opcionales)."""
    tabla = cubo.pivot_table(index=filas, columns=columnas, values=medida, aggfunc="sum",
                             fill_value=0, observed=True)
    if totales:
        tabla.loc["Total"] = tabla.sum()
        tabla["Total"] = tabla.sum(axis=1)
    return tabla


def participacion(tabla: pd.DataFrame, eje: int = 1) -> pd.DataFrame:
    """Convierte una tabla cruzada en porcentajes por fila (eje=1) o por columna (eje=0)."""
    base = tabla.drop(columns="Total", errors="ignore").drop(index="Total", errors="ignore")
    return (base.div(base.sum(axis=eje), axis=0 if eje == 1 else 1) * 100).round(1)
