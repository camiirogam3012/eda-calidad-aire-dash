"""tabs/introduccion.py"""

from dash import html

from components import encabezado, tarjeta, fmt
from data.data_loader import resumen_general


def layout():
    r = resumen_general()
    return html.Div([
        encabezado("Planteamiento", "Introducción",
                   "Por qué estudiar la calidad del aire y qué se hace en este análisis."),
        tarjeta(
            html.P("La contaminación del aire es uno de los principales riesgos ambientales para la salud. "
                   "Partículas finas como el PM2.5 penetran hasta los alvéolos pulmonares, y gases como el "
                   "dióxido de nitrógeno (NO₂) y el ozono (O₃) irritan las vías respiratorias. En Colombia, "
                   "la vigilancia de estos contaminantes la hacen las autoridades ambientales regionales y "
                   "urbanas mediante redes de estaciones de monitoreo."),
            html.P(f"Este trabajo analiza el consolidado nacional de indicadores anuales de calidad del aire entre "
                   f"{r['anio_min']} y {r['anio_max']}. Cada registro resume, para una estación, una variable y un "
                   "tiempo de exposición, los estadísticos del año: promedio, mediana, percentil 98, máximo, mínimo, "
                   "número de datos y representatividad temporal."),
            html.P(["El análisis es ", html.Strong("exploratorio"), ": no busca predecir ni probar causalidad, sino "
                    "describir los datos, evaluar su calidad, identificar patrones temporales y relaciones entre "
                    "variables, y señalar los problemas que deben resolverse antes de cualquier modelo."]),
            titulo="Motivación",
        ),
        html.Div([
            tarjeta(
                html.Ul([
                    html.Li(f"{fmt(r['filas_originales'], 0)} filas y {r['columnas']} columnas en el archivo original"),
                    html.Li(f"{r['estaciones']} estaciones de {r['autoridades']} autoridades ambientales"),
                    html.Li(f"{r['variables']} variables: contaminantes y meteorológicas"),
                    html.Li(f"Periodo {r['anio_min']}–{r['anio_max']} ({r['anios']} años)"),
                ]),
                titulo="Alcance de los datos",
            ),
            tarjeta(
                html.Ul([
                    html.Li("Análisis replicado en Python (pandas) y en R con resultados idénticos"),
                    html.Li("Cada gráfico se acompaña de su interpretación"),
                    html.Li("Las cifras de este tablero se calculan en vivo desde el dataset"),
                    html.Li("Los hallazgos responden a objetivos definidos de antemano"),
                ]),
                titulo="Cómo leer este tablero",
            ),
        ], className="grid-2"),
    ])
