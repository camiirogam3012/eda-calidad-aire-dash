"""tabs/objetivos.py"""

from dash import html, dcc

from components import encabezado

OBJETIVOS = [
    ("Evaluar la calidad del dataset",
     "Verificar tipos de datos, valores faltantes, duplicados, consistencia de categorías y representatividad temporal.",
     "/dataset", "Dataset y calidad"),
    ("Describir la cobertura del monitoreo",
     "Caracterizar cómo se distribuyen los registros por año, variable, estación, tipo de estación y territorio.",
     "/exploracion", "Exploración general"),
    ("Analizar la evolución de los contaminantes",
     "Estudiar la tendencia anual de PM10, PM2.5, NO₂, O₃ y SO₂ y compararla con la Resolución 2254 de 2017.",
     "/contaminantes", "Contaminantes"),
    ("Describir las variables meteorológicas",
     "Caracterizar temperatura, humedad, viento, presión, precipitación y radiación, y sus cambios en el periodo.",
     "/meteorologia", "Meteorología"),
    ("Identificar asociaciones entre variables",
     "Medir la correlación de Pearson entre contaminantes y variables meteorológicas y evaluar su confiabilidad.",
     "/correlaciones", "Correlaciones"),
    ("Detectar valores atípicos",
     "Aplicar el criterio de Tukey (1,5 × IQR) para identificar observaciones extremas y su posible influencia.",
     "/atipicos", "Valores atípicos"),
]


def layout():
    return html.Div([
        encabezado("Planteamiento", "Objetivos",
                   "Lo que el análisis se propone responder, definido antes de explorar los datos."),
        html.Div([
            html.Div("Objetivo general", className="eyebrow"),
            html.P("Caracterizar, mediante un análisis exploratorio de datos, el comportamiento de los principales "
                   "contaminantes atmosféricos y variables meteorológicas registrados en Colombia entre 2011 y 2024, "
                   "evaluando la calidad y representatividad de la información disponible."),
        ], className="obj-general"),

        html.H2("Objetivos específicos", className="section"),
        html.Div([
            html.Section(html.Div([
                html.Div(str(i), className="obj-num"),
                html.Div([html.H4(t), html.P(d),
                          dcc.Link(f"Ver en: {seccion} →", href=ruta, className="obj-link")]),
            ], className="obj-item"), className="card")
            for i, (t, d, ruta, seccion) in enumerate(OBJETIVOS, start=1)
        ], className="grid-2"),
    ])
