"""tabs/correlaciones.py – Asociaciones entre variables (Objetivo 5)."""

import numpy as np
import plotly.graph_objects as go
from dash import html, dcc, Input, Output
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import squareform

from components import (encabezado, tarjeta, tabla, interpretacion, nota, grafico, estilo_figura, fila,
                        fmt, AZUL, TINTA, TINTA_2, ESCALA_DIVERGENTE)
from data.data_loader import matriz_correlacion, n_pares, tabla_correlaciones, tabla_pivot_anual, fuerza, NOMBRES

# Variables con problemas documentados en las secciones anteriores
PROBLEMATICAS = {"RUVb": "cambio de escala entre fuentes", "P": "registros en hPa etiquetados como mmHg",
                 "TAire": "solo 6 años de datos", "HAire": "solo 7 años de datos"}


def _heatmap():
    m = matriz_correlacion()
    n = n_pares().loc[m.index, m.columns]
    orden = leaves_list(linkage(squareform((1 - m).values, checks=False), method="complete"))
    m = m.iloc[orden, orden]
    n = n.iloc[orden, orden]
    z = m.values.copy()
    z[np.tril_indices_from(z)] = np.nan       # solo triángulo superior, como en el EDA
    texto = np.where(np.isnan(z), "", np.vectorize(lambda x: f"{x:.2f}")(np.nan_to_num(z)))
    fig = go.Figure(go.Heatmap(
        z=z, x=list(m.columns), y=list(m.index), zmin=-1, zmax=1, colorscale=ESCALA_DIVERGENTE,
        text=texto, texttemplate="%{text}", textfont=dict(size=11),
        customdata=n.values, xgap=2, ygap=2,
        colorbar=dict(title="r", thickness=12, len=.8, tickvals=[-1, -.5, 0, .5, 1]),
        hovertemplate="<b>%{y} – %{x}</b><br>r = %{z:.2f}<br>Años con dato en ambas: %{customdata}<extra></extra>",
        hoverongaps=False))
    estilo_figura(fig, alto=560)
    fig.update_xaxes(side="top", showline=False, ticks="")
    fig.update_yaxes(autorange="reversed", showline=False, showgrid=False)
    fig.update_layout(margin=dict(t=60, l=70, r=20, b=20))
    return fig


def layout():
    t = tabla_correlaciones()
    t["Advertencia"] = t["Par"].apply(lambda p: "; ".join(f"{v}: {d}" for v, d in PROBLEMATICAS.items()
                                                         if v in p.split(" – ")) or "—")
    fuertes = t[t["|r|"] >= .6].drop(columns="|r|")
    variables = list(matriz_correlacion().columns)

    return html.Div([
        encabezado("Objetivo 5", "Correlaciones",
                   "Qué variables se mueven juntas a lo largo de los años, y cuáles de esas relaciones son confiables."),
        nota("Las correlaciones se calculan sobre los promedios anuales nacionales (máximo 14 puntos por par). Con tan "
             "pocos puntos, un solo año atípico puede cambiar mucho el valor de r, y una correlación alta no implica "
             "causalidad.", tipo="dato"),

        tarjeta(
            grafico(_heatmap()),
            interpretacion(
                "El agrupamiento jerárquico ordena las variables según su similitud y forma dos bloques. El primero "
                "reúne los contaminantes (PM10, PM2.5, O₃, SO₂, NO₂) con la velocidad del viento y la humedad, que "
                "se correlacionan positivamente entre sí. El segundo agrupa temperatura, radiación, presión y "
                "precipitación, que en general se relacionan negativamente con los contaminantes.",
                "Antes de interpretar ese segundo bloque hay que recordar los problemas detectados en la sección de "
                "meteorología: RUVb cambió de escala, P mezcla unidades y TAire solo tiene 6 años.",
            ),
            titulo="Matriz de correlación de Pearson",
            subtitulo="Promedios anuales · rojo = relación positiva, azul = negativa · pasa el cursor para ver cuántos años sustentan cada valor",
        ),

        tarjeta(
            tabla(fuertes, decimales=2, alto=380),
            interpretacion(
                html.P([html.Strong("Relación robusta: "), "PM10 y PM2.5 (r = 0,97, 14 años). Es esperable, porque el "
                        "PM2.5 es una fracción del PM10 y ambos provienen de las mismas fuentes (tráfico, industria, "
                        "resuspensión de polvo). Es la única relación fuerte sustentada por la serie completa y sin "
                        "problemas de datos."]),
                html.P([html.Strong("Relaciones plausibles pero frágiles: "), "TAire con PM10 (−0,79) y NO₂ (−0,73). "
                        "Físicamente tiene sentido: más temperatura favorece la mezcla vertical y la dispersión. Pero se "
                        "basan en solo 6 años y en una variable con 24 % de representatividad."]),
                html.P([html.Strong("Relaciones espurias: "), "todas las de RUVb (con PM10 −0,83, con TAire 0,85) y las de "
                        "P. Son consecuencia del cambio de escala y del error de unidades, no de procesos atmosféricos."]),
                html.P([html.Strong("Relación con interés físico: "), "NO₂ y radiación global (−0,71, 12 años). La "
                        "radiación solar descompone el NO₂ (fotólisis) y genera ozono, lo que es coherente con la "
                        "relación negativa."]),
            ),
            titulo="Relaciones fuertes y muy fuertes (|r| ≥ 0,60)",
            subtitulo="Con el número de años que sustenta cada correlación y las advertencias de calidad",
        ),

        tarjeta(
            html.Div([
                html.Div([html.Label("Variable X"),
                          dcc.Dropdown(id="cor-x", value="PM10", clearable=False, options=variables)], className="control"),
                html.Div([html.Label("Variable Y"),
                          dcc.Dropdown(id="cor-y", value="PM2.5", clearable=False, options=variables)], className="control"),
            ], className="controls"),
            dcc.Graph(id="cor-scatter", config={"displaylogo": False}),
            html.Div(id="cor-txt"),
            titulo="Explorar un par de variables",
            subtitulo="Cada punto es un año: así se ve cuántos datos hay detrás de cada r",
        ),
    ])


def register_callbacks(app):
    @app.callback(Output("cor-scatter", "figure"), Output("cor-txt", "children"),
                  Input("cor-x", "value"), Input("cor-y", "value"))
    def _scatter(x, y):
        p = tabla_pivot_anual()[[x, y]].dropna() if x != y else tabla_pivot_anual()[[x]].dropna()
        fig = go.Figure()
        if x == y:
            estilo_figura(fig, alto=380)
            return fig, interpretacion("Elige dos variables distintas.")
        r = p[x].corr(p[y])
        fig.add_trace(go.Scatter(x=p[x], y=p[y], mode="markers+text", text=p.index.astype(str),
                                 textposition="top center", textfont=dict(size=10, color=TINTA_2),
                                 marker=dict(size=10, color=AZUL, line=dict(color="white", width=2)),
                                 hovertemplate=f"<b>%{{text}}</b><br>{x}: %{{x:.2f}}<br>{y}: %{{y:.2f}}<extra></extra>"))
        if len(p) >= 3:
            b, a = np.polyfit(p[x], p[y], 1)
            xs = np.linspace(p[x].min(), p[x].max(), 20)
            fig.add_trace(go.Scatter(x=xs, y=a + b * xs, mode="lines", line=dict(color=TINTA, width=1, dash="dash"),
                                     hoverinfo="skip"))
        estilo_figura(fig, alto=400)
        fig.update_xaxes(title=f"{x} · {NOMBRES.get(x, x)}", showgrid=True, gridcolor="#f1f4f8")
        fig.update_yaxes(title=f"{y} · {NOMBRES.get(y, y)}")

        signo = "positiva (cuando una sube, la otra tiende a subir)" if r > 0 else "negativa (cuando una sube, la otra tiende a bajar)"
        alertas = [f"{v}: {PROBLEMATICAS[v]}" for v in (x, y) if v in PROBLEMATICAS]
        partes = [f"r = {fmt(r, 2)}: relación {fuerza(r).lower()} y {signo}, calculada con {len(p)} años."]
        if len(p) < 8:
            partes.append(f"Con solo {len(p)} puntos el coeficiente es muy inestable: quitar un año puede cambiarlo mucho.")
        if alertas:
            partes.append("Precaución por calidad de datos – " + "; ".join(alertas) + ". La relación puede ser espuria.")
        return fig, interpretacion(*partes)
