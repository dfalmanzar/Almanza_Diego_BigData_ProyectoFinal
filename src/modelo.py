"""Variables del modelo de clasificación y preparación de registros.

El notebook usa estas definiciones para entrenar y el dashboard las usa para armar un registro
nuevo desde el formulario de predicción: así los dos preparan los datos exactamente igual.
"""

import pandas as pd

OBJETIVO = "categoria_violencia"
CLASES = ["Conflicto armado", "Crimen organizado y sicariato", "Convivencia y riñas", "Delincuencia común"]

# Variables conocidas en el momento del hecho (no dependen de la investigación posterior)
VARIABLES_CATEGORICAS = ["departamento", "zona", "sexo", "arma_grupo", "dia_semana", "mes"]
VARIABLE_MUNICIPIO = ["cod_muni"]  # 1.100 municipios: se codifica con target encoding
VARIABLES_CONTEO = ["eventos_ucdp_12m", "muertes_ucdp_12m", "cantidad"]
VARIABLES_BINARIAS = ["fin_de_semana", "post_acuerdo_paz"]
VARIABLES_NUMERICAS = VARIABLES_CONTEO + VARIABLES_BINARIAS
VARIABLES_MODELO = VARIABLES_CATEGORICAS + VARIABLE_MUNICIPIO + VARIABLES_NUMERICAS

# Nombres para mostrar en gráficas y en el dashboard (lenguaje de negocio)
NOMBRES_VARIABLES = {
    "departamento": "Departamento",
    "cod_muni": "Municipio",
    "zona": "Zona (urbana / rural)",
    "sexo": "Sexo de la víctima",
    "arma_grupo": "Arma usada",
    "dia_semana": "Día de la semana",
    "mes": "Mes",
    "eventos_ucdp_12m": "Eventos de conflicto (UCDP) en 12 meses previos",
    "muertes_ucdp_12m": "Muertes de conflicto (UCDP) en 12 meses previos",
    "cantidad": "Víctimas en el mismo hecho",
    "fin_de_semana": "Fin de semana",
    "post_acuerdo_paz": "Después del Acuerdo de Paz",
}

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
FECHA_ACUERDO_PAZ = pd.Timestamp("2016-11-24")


def preparar_variables(tabla: pd.DataFrame) -> pd.DataFrame:
    """Selecciona las variables del modelo con tipos simples (texto, enteros) que entienden los codificadores."""
    datos = tabla[VARIABLES_MODELO].copy()
    for columna in ["departamento", "zona", "sexo", "arma_grupo", "dia_semana"]:
        datos[columna] = datos[columna].astype(str)
    datos["mes"] = datos["mes"].astype(int)
    datos["cod_muni"] = datos["cod_muni"].astype(int)
    for columna in VARIABLES_CONTEO:
        datos[columna] = datos[columna].astype(float)
    for columna in VARIABLES_BINARIAS:
        datos[columna] = datos[columna].astype(int)
    return datos


def registro_nuevo(departamento: str, cod_muni: int, zona: str, sexo: str, arma_grupo: str, fecha,
                   eventos_ucdp_12m: float, muertes_ucdp_12m: float, cantidad: int = 1) -> pd.DataFrame:
    """Arma un registro de una fila para predecir, derivando las variables de calendario de la fecha."""
    fecha = pd.Timestamp(fecha)
    fila = {
        "departamento": departamento, "cod_muni": cod_muni, "zona": zona, "sexo": sexo, "arma_grupo": arma_grupo,
        "dia_semana": DIAS_SEMANA[fecha.dayofweek], "mes": fecha.month,
        "eventos_ucdp_12m": eventos_ucdp_12m, "muertes_ucdp_12m": muertes_ucdp_12m, "cantidad": cantidad,
        "fin_de_semana": fecha.dayofweek >= 5, "post_acuerdo_paz": fecha >= FECHA_ACUERDO_PAZ,
    }
    return preparar_variables(pd.DataFrame([fila]))
