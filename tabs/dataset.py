"""tabs/dataset.py – Calidad de los datos (Objetivo 1)."""

import pandas as pd
import plotly.graph_objects as go
from dash import html

from components import (encabezado, tarjeta, tabla, interpretacion, nota, kpi, grafico,
                        estilo_figura, fmt, AZUL, TINTA_2, LINEA)
from data.data_loader import (get_df, resumen_general, nulos, representatividad,
                              CONTAMINANTES)


def _variantes(normalizado: str, columna: str, col_norm: str) -> str:
    df = get_df()
    v = df.loc[df[col_norm] == normalizado, columna].value_counts()
    return " · ".join(f"“{k}” ({n})" for k, n in v.items())


def layout():
    r = resumen_general()
    df = get_df()

    # Nombres inconsistentes
    ejemplos = pd.DataFrame([
        {"Nombre normalizado": n, "Variantes encontradas (registros)": _variantes(n, "Nombre del Departamento", "Departamento")}
        for n in ["BOGOTA, D.C.", "ANTIOQUIA", "BOYACA", "ATLANTICO"]
    ])

    # Representatividad
    rep = representatividad()
    fig_rep = go.Figure(go.Bar(
        x=rep["Media"], y=rep["Variable"], orientation="h", marker_color=AZUL,
        hovertemplate="<b>%{y}</b><br>Representatividad media: %{x:.1f} %<extra></extra>"))
    fig_rep.add_vline(x=75, line_dash="dash", line_color=TINTA_2, line_width=1,
                      annotation_text="75 %", annotation_position="top", annotation_font_size=11)
    estilo_figura(fig_rep, alto=520)
    fig_rep.update_yaxes(categoryorder="total ascending", title=None)
    fig_rep.update_xaxes(title="Representatividad temporal media (%)", range=[0, 100])

    pct_75 = (df["Representatividad Temporal"] >= 75).mean() * 100
    n_sobre_100 = int((df["Representatividad Temporal"] > 100).sum())

    # Tiempos de exposición mezclados
    exp = (df[df["Variable"].isin(CONTAMINANTES)]
           .groupby(["Variable", "Tiempo de exposición (horas)"]).size()
           .unstack(fill_value=0))
    exp.columns = [f"{c} h" for c in exp.columns]
    exp = exp.reset_index()

    return html.Div([
        encabezado("Objetivo 1", "Dataset y calidad de los datos",
                   "Antes de analizar, se verifica qué tan confiable es la información."),

        html.Div([
            kpi(fmt(r["filas_originales"], 0), "Filas originales", f"{r['columnas']} columnas"),
            kpi(fmt(r["duplicados"], 0), "Filas duplicadas", f"{fmt(r['pct_duplicados'])} % del total"),
            kpi(fmt(r["filas_unicas"], 0), "Filas únicas", "base del análisis"),
            kpi(f"{fmt(pct_75)} %", "Registros con ≥ 75 %", "de representatividad temporal"),
        ], className="grid-4"),

        tarjeta(
            tabla(nulos(), decimales=3),
            interpretacion(
                "Solo tres columnas tienen faltantes y ninguna supera el 0,5 %. La más afectada es la "
                "representatividad temporal (148 filas). Ninguna de las columnas usadas en el análisis "
                "(Variable, Año, Promedio) tiene faltantes, así que no fue necesario imputar ni eliminar filas por este motivo.",
            ),
            titulo="Valores faltantes", subtitulo="Columnas con al menos un valor nulo",
        ),

        tarjeta(
            html.P(f"El archivo contiene {fmt(r['duplicados'], 0)} filas idénticas a otra fila, es decir, casi la mitad "
                   f"del dataset ({fmt(r['pct_duplicados'])} %)."),
            interpretacion(
                "Una proporción tan alta indica que el consolidado se armó juntando reportes que se solaparon, y no "
                "que se repitieran mediciones reales. Si no se eliminaran, cada estación duplicada pesaría el doble en "
                "los promedios y en los conteos. Por eso todo el análisis usa las "
                f"{fmt(r['filas_unicas'], 0)} filas únicas.",
            ),
            titulo="Duplicados",
        ),

        tarjeta(
            tabla(ejemplos),
            interpretacion(
                f"Los nombres de departamento aparecen en mayúsculas, minúsculas, con y sin tilde. Un conteo directo da "
                f"{r['deptos_crudos']} departamentos, pero al normalizar (quitar tildes y unificar mayúsculas) quedan "
                f"{r['deptos']}. Con los municipios pasa lo mismo: de {r['munis_crudos']} nombres distintos se pasa a {r['munis']}.",
                "Este hallazgo corrige el conteo del EDA original, que reportaba 49 departamentos. En este tablero "
                "todos los análisis territoriales usan los nombres normalizados.",
            ),
            titulo="Nombres inconsistentes de departamento y municipio",
            subtitulo="Ejemplos de un mismo departamento escrito de varias formas",
        ),

        html.Div([
            tarjeta(
                grafico(fig_rep),
                titulo="Representatividad temporal por variable",
                subtitulo="Porcentaje del año cubierto por datos válidos (media por variable)",
            ),
            tarjeta(
                interpretacion(
                    "La representatividad indica qué fracción del año tiene datos válidos. Casi todas las variables "
                    "promedian entre 63 % y 75 %: en un registro típico falta cerca de un tercio del año.",
                    "TAire y HAire, sin altura especificada, tienen una representatividad muy baja (24 % y 27 %). "
                    "Sus promedios anuales se basan en pocos meses y deben leerse con cautela.",
                    f"Solo el {fmt(pct_75)} % de los registros alcanza el 75 % de cobertura, un umbral comúnmente "
                    "usado para considerar válido un promedio anual.",
                ),
                nota(f"{n_sobre_100} registros reportan representatividad mayor a 100 % (máximo 167 %), lo cual es "
                     "imposible. Es un error de captura que se documenta pero no se corrige."),
                html.H3("Tiempos de exposición mezclados", className="card-title", style={"marginTop": "18px"}),
                tabla(exp, decimales=0),
                html.P("Un mismo contaminante tiene registros a 1, 3, 8 y 24 horas. El EDA promedia todos juntos, "
                       "lo que es válido para describir tendencias generales pero no para verificar cumplimiento de norma.",
                       style={"fontSize": "14px", "marginTop": "10px"}),
                titulo="Lectura",
            ),
        ], className="grid-2"),
    ])
