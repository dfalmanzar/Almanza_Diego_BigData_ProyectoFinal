"""Datos: tabla filtrable del dataset limpio y tablas dinámicas (OLAP) sobre los cubos."""

import pandas as pd
import streamlit as st
from matplotlib.colors import LinearSegmentedColormap

import datos
import tema

st.title("Datos")
st.markdown('<p class="entrada">Filtre los registros limpios que dejó el proceso ETL y arme tablas dinámicas sobre los cubos '
            'OLAP. Todo lo que ve aquí se puede descargar en CSV.</p>', unsafe_allow_html=True)

fuente = st.segmented_control("Fuente", ["Mundo · eventos UCDP", "Colombia · homicidios"], default="Mundo · eventos UCDP",
                              label_visibility="collapsed")
fuente = fuente or "Mundo · eventos UCDP"
mundo = fuente.startswith("Mundo")

if mundo:
    tabla = datos.eventos_ucdp()
    a0, a1 = int(tabla["anio"].min()), int(tabla["anio"].max())
    c1, c2, c3 = st.columns([2, 2, 2])
    rango = c1.slider("Años", a0, a1, (2016, a1 - 1))
    regiones = c2.multiselect("Región", sorted(tabla["region"].dropna().unique()), placeholder="Todas las regiones")
    tipos = c3.multiselect("Tipo de violencia", list(tema.TIPOS_UCDP), placeholder="Todos los tipos")
    filtro = tabla["anio"].between(*rango)
    if regiones:
        filtro &= tabla["region"].isin(regiones)
    if tipos:
        filtro &= tabla["tipo_violencia"].isin(tipos)
    vista = tabla[filtro].sort_values("date_start", ascending=False)
    tema.cifras([(tema.miles(len(vista)), "eventos con los filtros actuales"),
                 (tema.miles(vista["best"].sum()), "muertes estimadas"),
                 (tema.miles(vista["country"].nunique()), "países")])
    columnas = {"date_start": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
                "tipo_violencia": "Tipo de violencia", "country": "País", "region": "Región", "adm_1": "Zona",
                "conflict_name": "Conflicto", "side_a": "Actor A", "side_b": "Actor B",
                "best": st.column_config.NumberColumn("Muertes", format="%d"),
                "deaths_civilians": st.column_config.NumberColumn("Civiles", format="%d")}
else:
    tabla = datos.homicidios()
    a0, a1 = int(tabla["anio"].min()), int(tabla["anio"].max())
    c1, c2, c3 = st.columns([2, 2, 2])
    rango = c1.slider("Años", a0, a1, (2017, a1))
    deptos = c2.multiselect("Departamento", sorted(tabla["departamento"].astype(str).unique()), placeholder="Todos los departamentos")
    categorias = c3.multiselect("Categoría de violencia", list(tema.CATEGORIAS), placeholder="Todas las categorías")
    filtro = tabla["anio"].between(*rango)
    if deptos:
        filtro &= tabla["departamento"].astype(str).isin(deptos)
    if categorias:
        filtro &= tabla["categoria_violencia"].astype(str).isin(categorias)
    vista = tabla[filtro].sort_values("fecha_hecho", ascending=False)
    fuego = vista.loc[vista["es_arma_fuego"], "cantidad"].sum() / max(1, vista["cantidad"].sum()) * 100
    tema.cifras([(tema.miles(vista["cantidad"].sum()), "víctimas con los filtros actuales"),
                 (f"{tema.decimal(fuego)} %", "con arma de fuego"),
                 (tema.miles(vista["cod_muni"].nunique()), "municipios")])
    columnas = {"fecha_hecho": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
                "departamento": "Departamento", "municipio": "Municipio", "zona": "Zona", "sexo": "Sexo",
                "arma_grupo": "Arma", "modalidad_presunta": "Modalidad", "categoria_violencia": "Categoría",
                "cantidad": st.column_config.NumberColumn("Víctimas", format="%d"),
                "eventos_ucdp_12m": st.column_config.NumberColumn("Eventos UCDP 12 meses", format="%d")}

if vista.empty:
    st.markdown('<div class="vacio">Ningún registro cumple estos filtros. Amplíe el rango de años o quite algún filtro.</div>',
                unsafe_allow_html=True)
else:
    st.dataframe(vista[list(columnas)].head(5000), column_config=columnas, hide_index=True, height=420, use_container_width=True)
    st.markdown(f'<p class="nota">Se muestran los {tema.miles(min(5000, len(vista)))} registros más recientes de '
                f'{tema.miles(len(vista))}. La descarga incluye todos.</p>', unsafe_allow_html=True)
    st.download_button("Descargar CSV filtrado", vista[list(columnas)].to_csv(index=False).encode("utf-8"),
                       file_name="violencia_armada_filtrado.csv", mime="text/csv")

st.header("Tabla dinámica (OLAP)")
st.markdown('<p class="entrada">Elija qué dimensión va en las filas y cuál en las columnas: la tabla se reagrupa sobre el cubo '
            '(roll-up y drill-down) con los mismos filtros de años.</p>', unsafe_allow_html=True)
if mundo:
    cubo = datos.cubo_ucdp().rename(columns={"year": "anio"})
    cubo = cubo[cubo["anio"].between(*rango)]
    dimensiones = {"Región": "region", "País": "country", "Tipo de violencia": "tipo_violencia", "Año": "anio"}
    medidas = {"Eventos": "eventos", "Muertes estimadas": "muertes_estimadas", "Muertes de civiles": "muertes_civiles"}
    filas_def, cols_def = "Región", "Tipo de violencia"
else:
    cubo = datos.cubo_homicidios()
    cubo = cubo[cubo["anio"].between(*rango)]
    dimensiones = {"Departamento": "departamento", "Categoría": "categoria_violencia", "Arma": "arma_grupo",
                   "Zona": "zona", "Año": "anio", "Modalidad": "modalidad_presunta"}
    medidas = {"Víctimas": "victimas", "Registros": "registros"}
    filas_def, cols_def = "Departamento", "Categoría"

d1, d2, d3 = st.columns(3)
filas = d1.selectbox("Filas", list(dimensiones), index=list(dimensiones).index(filas_def))
opciones_cols = [d for d in dimensiones if d != filas]
cols = d2.selectbox("Columnas", opciones_cols, index=opciones_cols.index(cols_def) if cols_def in opciones_cols else 0)
medida = d3.selectbox("Medida", list(medidas))
pivote = datos.olap.pivotear(cubo.astype({dimensiones[filas]: str, dimensiones[cols]: str}),
                             dimensiones[filas], dimensiones[cols], medidas[medida])
pivote = pivote.sort_index() if filas == "Año" else pivote.sort_values("Total", ascending=False)
escala_roja = LinearSegmentedColormap.from_list("rojo", [tema.TINTA_2, tema.ROJO_4, tema.ROJO_3, tema.ROJO])
celdas = pd.IndexSlice[pivote.index.drop("Total", errors="ignore"), pivote.columns.drop("Total", errors="ignore")]
st.dataframe(pivote.style.format(tema.miles).background_gradient(cmap=escala_roja, subset=celdas),
             height=420, use_container_width=True)
st.download_button("Descargar tabla dinámica", pivote.to_csv().encode("utf-8"), file_name="tabla_dinamica.csv", mime="text/csv",
                   key="descarga_pivote")
