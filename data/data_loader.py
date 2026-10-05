"""
data/data_loader.py
-------------------
Carga, limpieza y agregaciones del dataset de calidad del aire.

La limpieza replica exactamente la del EDA (Python y R):
  1. Conversión de columnas numéricas que vienen como texto con comas de miles.
  2. Eliminación de filas duplicadas exactas.
Adicionalmente (hallazgo del dashboard) se normalizan los nombres de
departamento y municipio, que aparecen escritos de varias formas.

Todas las funciones usan caché: el CSV se lee una sola vez por proceso.
"""

from functools import lru_cache
from pathlib import Path
import unicodedata

import numpy as np
import pandas as pd

RUTA_CSV = Path(__file__).parent / "dataset_calidad_aire.csv"

COLUMNAS_NUMERICAS = [
    "ID Estacion", "Suma", "No. de datos", "Promedio",
    "Mediana", "Percentil 98", "Máximo", "Mínimo",
]

CONTAMINANTES = ["PM10", "PM2.5", "NO2", "O3", "SO2"]
METEOROLOGICAS = ["TAire", "HAire", "VViento", "DViento", "P", "PLiquida", "RGlobal", "RUVb"]
VARIABLES_CORRELACION = ["PM10", "PM2.5", "NO2", "SO2", "O3", "TAire",
                         "HAire", "VViento", "P", "PLiquida", "RGlobal", "RUVb"]

NOMBRES = {
    "PM10": "Material particulado PM10",
    "PM2.5": "Material particulado PM2.5",
    "NO2": "Dióxido de nitrógeno (NO₂)",
    "O3": "Ozono (O₃)",
    "SO2": "Dióxido de azufre (SO₂)",
    "CO": "Monóxido de carbono (CO)",
    "NO": "Monóxido de nitrógeno (NO)",
    "PST": "Partículas suspendidas totales (PST)",
    "TAire": "Temperatura del aire",
    "TAire2": "Temperatura del aire a 2 m",
    "TAire10": "Temperatura del aire a 10 m",
    "HAire": "Humedad relativa del aire",
    "HAire2": "Humedad relativa a 2 m",
    "HAire10": "Humedad relativa a 10 m",
    "VViento": "Velocidad del viento",
    "DViento": "Dirección del viento",
    "P": "Presión atmosférica",
    "PLiquida": "Precipitación líquida",
    "RGlobal": "Radiación solar global",
    "RUVb": "Radiación ultravioleta B",
}

# Resolución 2254 de 2017 (MinAmbiente) – niveles máximos permisibles, promedio anual (µg/m³)
NORMA_ANUAL = {
    "PM10": {"vigente": 50, "meta_2030": 30},
    "PM2.5": {"vigente": 25, "meta_2030": 15},
    "NO2": {"vigente": 60, "meta_2030": 40},
}


def _normalizar(texto) -> str:
    """Quita tildes, pasa a mayúsculas y recorta espacios."""
    if pd.isna(texto):
        return texto
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return " ".join(t.upper().split())


@lru_cache(maxsize=1)
def get_raw() -> pd.DataFrame:
    """Dataset tal como viene, solo con tipos numéricos corregidos (antes de quitar duplicados)."""
    df = pd.read_csv(RUTA_CSV)
    df["Año"] = df["Año"].astype(str).str.replace(",", "").astype(int)
    for col in COLUMNAS_NUMERICAS:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "").str.strip(), errors="coerce")
    return df


@lru_cache(maxsize=1)
def get_df() -> pd.DataFrame:
    """Dataset limpio: sin duplicados y con departamento/municipio normalizados."""
    df = get_raw().drop_duplicates().reset_index(drop=True)
    df["Departamento"] = df["Nombre del Departamento"].map(_normalizar)
    df["Municipio"] = df["Nombre del Municipio"].map(_normalizar)
    return df


# ───────────────────────── Agregaciones ─────────────────────────

@lru_cache(maxsize=1)
def resumen_general() -> dict:
    raw, df = get_raw(), get_df()
    return {
        "filas_originales": len(raw),
        "filas_unicas": len(df),
        "duplicados": len(raw) - len(df),
        "pct_duplicados": (len(raw) - len(df)) / len(raw) * 100,
        "columnas": raw.shape[1],
        "estaciones": df["Estación"].nunique(),
        "variables": df["Variable"].nunique(),
        "autoridades": df["Autoridad Ambiental"].nunique(),
        "deptos_crudos": df["Nombre del Departamento"].nunique(),
        "deptos": df["Departamento"].nunique(),
        "munis_crudos": df["Nombre del Municipio"].nunique(),
        "munis": df["Municipio"].nunique(),
        "anio_min": int(df["Año"].min()),
        "anio_max": int(df["Año"].max()),
        "anios": df["Año"].nunique(),
    }


def nulos() -> pd.DataFrame:
    raw = get_raw()
    n = raw.isna().sum()
    out = pd.DataFrame({"Columna": n.index, "Nulos": n.values,
                        "Porcentaje": (n.values / len(raw) * 100)})
    return out[out["Nulos"] > 0].reset_index(drop=True)


def conteo(columna: str, top: int | None = None) -> pd.DataFrame:
    s = get_df()[columna].value_counts()
    if top:
        s = s.head(top)
    return s.rename_axis(columna).reset_index(name="Registros")


def estadistica_por_variable() -> pd.DataFrame:
    df = get_df()
    return (df.groupby("Variable")["Promedio"]
              .agg(n="size", Media="mean", Mediana="median", Desv="std", Mínimo="min",
                   Q1=lambda s: s.quantile(.25), Q3=lambda s: s.quantile(.75), Máximo="max")
              .reset_index())


def serie(variable: str) -> pd.Series:
    df = get_df()
    return df.loc[df["Variable"] == variable, "Promedio"].dropna()


def promedio_anual(variable: str, con_huecos: bool = False) -> pd.DataFrame:
    """Promedio anual. Con con_huecos=True incluye los años sin datos como NaN (para no unir huecos en las líneas)."""
    df = get_df()
    d = df[df["Variable"] == variable]
    a = (d.groupby("Año")["Promedio"].agg(Promedio="mean", Registros="size")
          .reset_index().sort_values("Año"))
    if con_huecos:
        todos = pd.DataFrame({"Año": range(int(df["Año"].min()), int(df["Año"].max()) + 1)})
        a = todos.merge(a, on="Año", how="left")
    return a


def cambio_porcentual(variable: str, a1: int = 2011, a2: int = 2024):
    a = promedio_anual(variable).set_index("Año")["Promedio"]
    if a1 not in a.index or a2 not in a.index:
        return None
    return {"v1": a[a1], "v2": a[a2], "cambio": (a[a2] - a[a1]) / a[a1] * 100}


UNIDADES_LEGIBLES = {"ugm3": "µg/m³", "Celsius": "°C", "perc": "%", "ms": "m/s", "deg": "°",
                     "mmHg": "mmHg", "mm": "mm", "Wm2": "W/m²", "MEDh": "MED/h"}


def unidad(variable: str) -> str:
    df = get_df()
    u = df.loc[df["Variable"] == variable, "Unidades"].dropna()
    crudo = u.mode().iat[0] if len(u) else ""
    return UNIDADES_LEGIBLES.get(crudo, crudo)


@lru_cache(maxsize=1)
def tabla_pivot_anual() -> pd.DataFrame:
    """Promedio anual por variable (filas = años). Base de las correlaciones del EDA."""
    df = get_df()
    return df.groupby(["Año", "Variable"])["Promedio"].mean().unstack()


@lru_cache(maxsize=1)
def matriz_correlacion() -> pd.DataFrame:
    p = tabla_pivot_anual()
    cols = [v for v in VARIABLES_CORRELACION if v in p.columns]
    return p[cols].corr(method="pearson")


def n_pares() -> pd.DataFrame:
    """Número de años con dato en ambas variables (tamaño muestral de cada r)."""
    p = tabla_pivot_anual()[matriz_correlacion().columns]
    m = p.notna().astype(int)
    return m.T @ m


def fuerza(r: float) -> str:
    a = abs(r)
    if a >= 0.80:
        return "Muy fuerte"
    if a >= 0.60:
        return "Fuerte"
    if a >= 0.40:
        return "Moderada"
    if a >= 0.20:
        return "Débil"
    return "Muy débil"


def tabla_correlaciones() -> pd.DataFrame:
    m, n = matriz_correlacion(), n_pares()
    filas = []
    cols = list(m.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            r = m.loc[a, b]
            if pd.notna(r):
                filas.append({"Par": f"{a} – {b}", "r": r, "|r|": abs(r),
                              "Fuerza": fuerza(r), "Años (n)": int(n.loc[a, b])})
    return pd.DataFrame(filas).sort_values("|r|", ascending=False).reset_index(drop=True)


def atipicos_tukey() -> pd.DataFrame:
    df = get_df()
    filas = []
    for v, g in df.groupby("Variable"):
        s = g["Promedio"].dropna()
        q1, q3 = s.quantile(.25), s.quantile(.75)
        iqr = q3 - q1
        li, ls = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_out = int(((s < li) | (s > ls)).sum())
        filas.append({"Variable": v, "Q1": q1, "Q3": q3, "IQR": iqr,
                      "Límite inferior": li, "Límite superior": ls,
                      "Atípicos": n_out, "n": len(s), "% atípicos": n_out / len(s) * 100})
    return pd.DataFrame(filas).sort_values("% atípicos", ascending=False).reset_index(drop=True)


def representatividad() -> pd.DataFrame:
    df = get_df()
    return (df.groupby("Variable")["Representatividad Temporal"]
              .agg(Media="mean", Mediana="median", Mínimo="min", Máximo="max")
              .reset_index().sort_values("Media", ascending=False))
