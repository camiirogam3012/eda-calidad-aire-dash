"""tabs/inicio.py – Portada del dashboard."""

from dash import html, dcc

from components import kpi, fmt
from data.data_loader import resumen_general, cambio_porcentual

RUTA = [
    ("01", "Planteamiento", "Contexto, problema, objetivos y metodología del análisis.", "/introduccion"),
    ("02", "Calidad de los datos", "Faltantes, duplicados, nombres inconsistentes y representatividad.", "/dataset"),
    ("03", "Análisis exploratorio", "Cobertura, contaminantes, meteorología, correlaciones y atípicos.", "/exploracion"),
    ("04", "Conclusiones", "Respuesta a cada objetivo, limitaciones y recomendaciones.", "/conclusiones"),
]


def layout():
    r = resumen_general()
    pm25 = cambio_porcentual("PM2.5")
    pm10 = cambio_porcentual("PM10")
    return html.Div([
        html.Section([
            html.Div("Análisis exploratorio de datos", className="eyebrow"),
            html.H1("Calidad del aire en Colombia, 2011–2024"),
            html.P(f"Exploración de {fmt(r['filas_unicas'], 0)} registros anuales de contaminantes y variables "
                   f"meteorológicas medidos en {r['estaciones']} estaciones de {r['deptos']} departamentos, "
                   "para entender cómo ha cambiado el aire que respiramos y qué tan confiable es la información disponible."),
            dcc.Link("Comenzar el recorrido →", href="/introduccion", className="hero-cta"),
        ], className="hero"),

        html.Div([
            kpi(fmt(r["filas_unicas"], 0), "Registros únicos", f"de {fmt(r['filas_originales'], 0)} originales"),
            kpi(str(r["estaciones"]), "Estaciones", f"{r['autoridades']} autoridades ambientales"),
            kpi(str(r["deptos"]), "Departamentos", f"{r['munis']} municipios"),
            kpi(str(r["variables"]), "Variables", f"{r['anios']} años de registro"),
        ], className="grid-4"),

        html.Div([
            kpi(f"{fmt(pm25['cambio'])} %", "Cambio en PM2.5", f"{fmt(pm25['v1'])} → {fmt(pm25['v2'])} µg/m³ (2011→2024)"),
            kpi(f"{fmt(pm10['cambio'])} %", "Cambio en PM10", f"{fmt(pm10['v1'])} → {fmt(pm10['v2'])} µg/m³ (2011→2024)"),
            kpi(f"{fmt(r['pct_duplicados'])} %", "Filas duplicadas", "eliminadas antes del análisis"),
            kpi("0,97", "r (PM10, PM2.5)", "la asociación más fuerte"),
        ], className="grid-4"),

        html.H2("Ruta del análisis", className="section"),
        html.Div([
            dcc.Link(html.Div([html.Div(n, className="n"), html.H4(t), html.P(d)], className="ruta-card"), href=h)
            for n, t, d, h in RUTA
        ], className="ruta"),
    ])
