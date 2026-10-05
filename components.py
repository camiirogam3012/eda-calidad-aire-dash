"""
components.py
-------------
Piezas de interfaz y estilo de gráficos compartidos por todas las pestañas.
"""

import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, dash_table

# Paleta (validada para daltonismo – ver skill de visualización)
AZUL = "#2a78d6"
NARANJA = "#eb6834"
AQUA = "#1baf7a"
ROJO = "#e34948"
GRIS_MEDIO = "#f0efec"
TINTA = "#0f172a"
TINTA_2 = "#475569"
TINTA_3 = "#94a3b8"
LINEA = "#e5e9f0"

FUENTE = "Inter, Segoe UI, system-ui, sans-serif"

# Escala divergente: negativo azul · cero gris · positivo rojo (mismo sentido que el EDA, RdBu_r)
ESCALA_DIVERGENTE = [[0.0, "#184f95"], [0.25, "#6da7ec"], [0.5, GRIS_MEDIO],
                     [0.75, "#ef8a89"], [1.0, "#b42b2b"]]


def estilo_figura(fig: go.Figure, alto: int = 380, leyenda: bool = False) -> go.Figure:
    fig.update_layout(
        height=alto,
        font=dict(family=FUENTE, size=12, color=TINTA_2),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=24, b=48, l=56, r=24),
        showlegend=leyenda,
        legend=dict(orientation="h", y=1.08, x=0, font=dict(size=12)),
        hoverlabel=dict(bgcolor="white", bordercolor=LINEA, font=dict(family=FUENTE, color=TINTA)),
        barcornerradius=4,
        bargap=0.25,
    )
    fig.update_xaxes(showgrid=False, linecolor=LINEA, ticks="outside", tickcolor=LINEA,
                     title_font=dict(size=12, color=TINTA_2))
    fig.update_yaxes(gridcolor="#f1f4f8", zeroline=False, linecolor=LINEA,
                     title_font=dict(size=12, color=TINTA_2))
    return fig


def grafico(fig: go.Figure, id_=None):
    props = dict(figure=fig, config={"displaylogo": False, "responsive": True,
                                     "modeBarButtonsToRemove": ["lasso2d", "select2d"]})
    if id_:
        props["id"] = id_
    return dcc.Graph(**props)


# ─────────────────────────── Bloques de layout ───────────────────────────

def encabezado(seccion: str, titulo: str, intro: str | None = None):
    return html.Header([
        html.Div(seccion, className="eyebrow"),
        html.H1(titulo, className="page-title"),
        html.P(intro, className="lead") if intro else None,
    ], className="page-header")


def tarjeta(*children, titulo: str | None = None, subtitulo: str | None = None, clase: str = ""):
    cabeza = []
    if titulo:
        cabeza.append(html.H3(titulo, className="card-title"))
    if subtitulo:
        cabeza.append(html.P(subtitulo, className="card-sub"))
    return html.Section(cabeza + list(children), className=f"card {clase}".strip())


def interpretacion(*parrafos, titulo: str = "Interpretación"):
    """Caja de interpretación que acompaña cada gráfico o tabla."""
    return html.Div([
        html.Div([html.Span("i", className="interp-icon"), titulo], className="interp-title"),
        *[html.P(p) if isinstance(p, str) else p for p in parrafos],
    ], className="interp")


def nota(texto, tipo: str = "aviso"):
    """Advertencia metodológica (tipo: aviso | dato)."""
    etiqueta = {"aviso": "Precaución", "dato": "Dato clave"}[tipo]
    return html.Div([html.Strong(etiqueta + ": "), texto], className=f"note note-{tipo}")


def kpi(valor, etiqueta, detalle=None):
    return html.Div([
        html.Div(valor, className="kpi-value"),
        html.Div(etiqueta, className="kpi-label"),
        html.Div(detalle, className="kpi-detail") if detalle else None,
    ], className="kpi")


def fila(*children, clase: str = "grid-2"):
    return html.Div(list(children), className=clase)


def tabla(df: pd.DataFrame, decimales: int = 2, alto: int | None = None, id_=None, pagina=None):
    d = df.copy()
    for c in d.select_dtypes("number").columns:
        d[c] = d[c].round(decimales)
    props = dict(
        data=d.to_dict("records"),
        columns=[{"name": c, "id": c, "type": "numeric" if pd.api.types.is_numeric_dtype(d[c]) else "text",
                  "format": {"specifier": ",." + str(decimales) + "~f"} if pd.api.types.is_float_dtype(d[c]) else None}
                 for c in d.columns],
        sort_action="native",
        style_as_list_view=True,
        style_table={"overflowX": "auto", **({"maxHeight": f"{alto}px", "overflowY": "auto"} if alto else {})},
        style_header={"backgroundColor": "#f8fafc", "fontWeight": "600", "color": TINTA,
                      "borderBottom": f"1px solid {LINEA}", "fontFamily": FUENTE, "fontSize": "12.5px"},
        style_cell={"fontFamily": FUENTE, "fontSize": "13px", "padding": "8px 12px", "color": TINTA_2,
                    "borderBottom": f"1px solid {LINEA}", "textAlign": "left", "whiteSpace": "normal",
                    "height": "auto"},
        style_cell_conditional=[{"if": {"column_type": "numeric"}, "textAlign": "right",
                                 "fontVariantNumeric": "tabular-nums"},
                                {"if": {"column_type": "text"}, "textAlign": "left"}],
        style_header_conditional=[{"if": {"column_type": "text"}, "textAlign": "left"}],
        fixed_rows={"headers": True} if alto else None,
    )
    if pagina:
        props["page_size"] = pagina
    if id_:
        props["id"] = id_
    return dash_table.DataTable(**{k: v for k, v in props.items() if v is not None})


def fmt(x, dec=1):
    """Número con separador de miles en formato colombiano (punto) y coma decimal."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")
