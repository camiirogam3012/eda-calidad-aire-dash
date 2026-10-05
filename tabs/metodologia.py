"""tabs/metodologia.py"""

import pandas as pd
from dash import html

from components import encabezado, tarjeta, tabla

PASOS = [
    ("Carga y conversión de tipos",
     "Las columnas numéricas venían como texto con comas de miles (\"1,003.6\"). Se eliminan las comas y se convierten a número."),
    ("Diagnóstico de calidad",
     "Conteo de faltantes y duplicados, revisión de categorías (departamentos y municipios) y de la representatividad temporal."),
    ("Depuración",
     "Se eliminan las filas duplicadas exactas. Los valores atípicos se conservan, porque un dato extremo no es necesariamente un error."),
    ("Análisis univariado",
     "Estadística descriptiva (mínimo, cuartiles, media, máximo, desviación) y diagramas de caja por variable."),
    ("Análisis temporal",
     "Promedio anual de cada variable y cambio porcentual entre 2011 y 2024."),
    ("Análisis bivariado",
     "Correlación de Pearson sobre los promedios anuales de 12 variables, con la escala de fuerza indicada abajo."),
    ("Valores atípicos",
     "Criterio de Tukey: es atípico todo valor por debajo de Q1 − 1,5·IQR o por encima de Q3 + 1,5·IQR."),
]

ESCALA = pd.DataFrame([
    {"|r|": "≥ 0,80", "Fuerza": "Muy fuerte"},
    {"|r|": "0,60 – 0,79", "Fuerza": "Fuerte"},
    {"|r|": "0,40 – 0,59", "Fuerza": "Moderada"},
    {"|r|": "0,20 – 0,39", "Fuerza": "Débil"},
    {"|r|": "< 0,20", "Fuerza": "Muy débil"},
])


def layout():
    return html.Div([
        encabezado("Planteamiento", "Metodología",
                   "El flujo de trabajo aplicado, igual en Python y en R."),
        html.Div([
            tarjeta(html.Ol([html.Li([html.Strong(t), d]) for t, d in PASOS], className="steps"),
                    titulo="Flujo del análisis"),
            html.Div([
                tarjeta(
                    html.P(["Cada fila del dataset es el resumen anual de una variable, en una estación y para un "
                            "tiempo de exposición. Todas las estadísticas se calculan sobre la columna ",
                            html.Strong("Promedio"), "."]),
                    titulo="Unidad de análisis",
                ),
                tarjeta(tabla(ESCALA), titulo="Escala de fuerza de la correlación",
                        subtitulo="Aplicada al valor absoluto de r"),
                tarjeta(
                    html.Div([html.Span(t, className="chip") for t in
                              ["Python", "pandas", "NumPy", "SciPy", "Matplotlib", "seaborn", "R", "Dash", "Plotly"]]),
                    titulo="Herramientas",
                ),
            ]),
        ], className="grid-2"),
    ])
