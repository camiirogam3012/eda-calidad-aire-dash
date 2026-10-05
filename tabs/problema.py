"""tabs/problema.py"""

from dash import html

from components import encabezado, tarjeta, fmt
from data.data_loader import resumen_general


def layout():
    r = resumen_general()
    return html.Div([
        encabezado("Planteamiento", "Planteamiento del problema"),
        tarjeta(
            html.P("Colombia cuenta con más de una década de mediciones de calidad del aire, pero esa información "
                   "llega de decenas de autoridades con estaciones que entran y salen de operación, tiempos de "
                   "exposición distintos y criterios de registro no homogéneos. Antes de usarla para tomar "
                   "decisiones o construir modelos, hace falta saber qué contiene realmente, qué tan completa es "
                   "y qué patrones muestra."),
            html.P(["Sin esa caracterización se corre el riesgo de sacar conclusiones de artefactos de los datos. "
                    "Un ejemplo de este mismo dataset: los nombres de los departamentos aparecen escritos de varias formas, "
                    f"de modo que un conteo directo arroja {r['deptos_crudos']} departamentos cuando en realidad hay ",
                    html.Strong(str(r["deptos"])), "."]),
            titulo="Situación",
        ),
        tarjeta(
            html.P("¿Cómo se han comportado los principales contaminantes atmosféricos y las variables meteorológicas "
                   "registradas en Colombia entre 2011 y 2024, y qué tan confiable y representativa es la información "
                   "disponible para analizarlos?", className="pregunta"),
            titulo="Pregunta de investigación",
        ),
        html.Div([
            tarjeta(html.Ul([
                html.Li("¿Qué problemas de calidad tiene el dataset y cómo afectan el análisis?"),
                html.Li("¿Dónde y cuándo se concentra el monitoreo?"),
                html.Li("¿Han disminuido o aumentado los contaminantes? ¿Están cerca de la norma?"),
            ]), titulo="Preguntas orientadoras (1)"),
            tarjeta(html.Ul([
                html.Li("¿Cómo varían las condiciones meteorológicas en el periodo?"),
                html.Li("¿Qué variables se asocian entre sí y qué tan confiables son esas asociaciones?"),
                html.Li("¿Hay valores extremos que puedan distorsionar los resultados?"),
            ]), titulo="Preguntas orientadoras (2)"),
        ], className="grid-2"),
    ])
