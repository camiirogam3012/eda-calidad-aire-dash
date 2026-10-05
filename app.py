"""
app.py
------
Punto de entrada del dashboard: Análisis Exploratorio de la Calidad del Aire
en Colombia (2011-2024).

Ejecutar localmente:
    pip install -r requirements.txt
    python app.py            ->  http://localhost:8050

Producción (Render):
    gunicorn app:server
"""

import os

import dash
from dash import html, dcc, Input, Output

from data.data_loader import get_df
from tabs import (inicio, introduccion, contexto, problema, objetivos, metodologia,
                  dataset, exploracion, contaminantes, meteorologia, correlaciones,
                  atipicos, conclusiones, limitaciones)

# ── Enlaces externos (cámbialos por los tuyos) ──
AUTOR = "Camilo Romero"
URL_EDA_PYTHON = os.environ.get("URL_EDA_PYTHON", "#")
URL_EDA_R = os.environ.get("URL_EDA_R", "#")
URL_REPO = os.environ.get("URL_REPO", "#")

get_df()  # precarga del dataset al arrancar el servidor

app = dash.Dash(
    __name__,
    title="EDA · Calidad del aire en Colombia",
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

# Ruta, etiqueta, módulo  — agrupadas como el flujo de un informe académico
SECCIONES = [
    ("Planteamiento", [
        ("/", "Inicio", inicio),
        ("/introduccion", "Introducción", introduccion),
        ("/contexto", "Contexto", contexto),
        ("/problema", "Problema", problema),
        ("/objetivos", "Objetivos", objetivos),
        ("/metodologia", "Metodología", metodologia),
    ]),
    ("Datos", [
        ("/dataset", "Dataset y calidad", dataset),
    ]),
    ("Análisis exploratorio", [
        ("/exploracion", "Exploración general", exploracion),
        ("/contaminantes", "Contaminantes", contaminantes),
        ("/meteorologia", "Meteorología", meteorologia),
        ("/correlaciones", "Correlaciones", correlaciones),
        ("/atipicos", "Valores atípicos", atipicos),
    ]),
    ("Cierre", [
        ("/conclusiones", "Conclusiones", conclusiones),
        ("/limitaciones", "Limitaciones", limitaciones),
    ]),
]
RUTAS = {ruta: modulo for _, items in SECCIONES for ruta, _, modulo in items}
ORDEN = [(ruta, etiqueta) for _, items in SECCIONES for ruta, etiqueta, _ in items]

for modulo in RUTAS.values():
    if hasattr(modulo, "register_callbacks"):
        modulo.register_callbacks(app)


def barra_lateral():
    grupos = []
    for grupo, items in SECCIONES:
        grupos.append(html.Div(grupo, className="nav-group"))
        for ruta, etiqueta, _ in items:
            grupos.append(dcc.Link(etiqueta, href=ruta, id=f"nav{ruta.replace('/', '-') or '-inicio'}",
                                   className="nav-link"))
    return html.Aside([
        html.Div([
            html.Div("EDA", className="brand-mark"),
            html.Div([html.Div("Calidad del aire", className="brand-title"),
                      html.Div("Colombia · 2011–2024", className="brand-sub")]),
        ], className="brand"),
        html.Nav(grupos, className="nav"),
        html.Div([
            html.A("EDA en Python ↗", href=URL_EDA_PYTHON, target="_blank", className="side-link"),
            html.A("EDA en R ↗", href=URL_EDA_R, target="_blank", className="side-link"),
            html.A("Repositorio ↗", href=URL_REPO, target="_blank", className="side-link"),
            html.Div(AUTOR, className="side-author"),
        ], className="side-foot"),
    ], className="sidebar")


app.layout = html.Div([
    dcc.Location(id="url"),
    barra_lateral(),
    html.Main([
        html.Div(id="contenido", className="content"),
        html.Div(id="paginacion", className="pager"),
        html.Footer(f"{AUTOR} · Análisis exploratorio de datos · Python, Dash y Plotly",
                    className="footer"),
    ], className="main"),
], className="shell")


@app.callback(
    Output("contenido", "children"),
    Output("paginacion", "children"),
    *[Output(f"nav{ruta.replace('/', '-') or '-inicio'}", "className") for ruta, _ in ORDEN],
    Input("url", "pathname"),
)
def enrutar(ruta):
    ruta = ruta if ruta in RUTAS else "/"
    contenido = RUTAS[ruta].layout()

    i = [r for r, _ in ORDEN].index(ruta)
    anterior = dcc.Link(["← ", ORDEN[i - 1][1]], href=ORDEN[i - 1][0], className="pager-link") if i > 0 else html.Span()
    siguiente = dcc.Link([ORDEN[i + 1][1], " →"], href=ORDEN[i + 1][0],
                         className="pager-link pager-next") if i < len(ORDEN) - 1 else html.Span()

    clases = ["nav-link active" if r == ruta else "nav-link" for r, _ in ORDEN]
    return (html.Div(contenido, className="fade-in", key=ruta), [anterior, siguiente], *clases)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("DEBUG", "false").lower() == "true")
