"""tabs/atipicos.py – Valores atípicos con el criterio de Tukey (Objetivo 6)."""

import plotly.graph_objects as go
from dash import html, dcc, Input, Output

from components import (encabezado, tarjeta, tabla, interpretacion, grafico, estilo_figura, fila, fmt,
                        AZUL, NARANJA, TINTA_2)
from data.data_loader import get_df, atipicos_tukey, serie, unidad, NOMBRES


def _fig_pct(t):
    fig = go.Figure(go.Bar(x=t["% atípicos"], y=t["Variable"], orientation="h", marker_color=AZUL,
                           customdata=t[["Atípicos", "n"]],
                           text=[f"{fmt(v)} %" for v in t["% atípicos"]], textposition="outside", cliponaxis=False,
                           textfont=dict(size=11, color=TINTA_2),
                           hovertemplate="<b>%{y}</b><br>%{customdata[0]} de %{customdata[1]} registros (%{x:.1f} %)<extra></extra>"))
    estilo_figura(fig, alto=560)
    fig.update_yaxes(categoryorder="total ascending", title=None)
    fig.update_xaxes(title="Registros atípicos (%)", showticklabels=False)
    fig.update_layout(margin=dict(l=10, r=50))
    return fig


def layout():
    t = atipicos_tukey()
    total = int(t["Atípicos"].sum())
    n_total = int(t["n"].sum())
    df = get_df()
    lim = t.set_index("Variable")["Límite superior"]
    altos = int((df["Promedio"] > df["Variable"].map(lim)).sum())
    return html.Div([
        encabezado("Objetivo 6", "Valores atípicos",
                   "Observaciones extremas según el criterio de Tukey: fuera de [Q1 − 1,5·IQR, Q3 + 1,5·IQR]."),

        fila(
            tarjeta(grafico(_fig_pct(t)), titulo="Porcentaje de atípicos por variable"),
            tarjeta(
                interpretacion(
                    f"En total, {fmt(total, 0)} de {fmt(n_total, 0)} registros ({fmt(total / n_total * 100)} %) son atípicos. "
                    f"El {fmt(altos / total * 100, 0)} % está por encima del límite superior: predominan los valores "
                    "extremadamente altos, que son los que inflan la media.",
                    "HAire encabeza la lista (16 %), pero con solo 75 registros cada atípico pesa mucho en el porcentaje. "
                    "Entre los contaminantes, el SO₂ (8,7 %) y el CO (8,6 %) son los más irregulares, coherente con "
                    "emisiones industriales puntuales que afectan a pocas estaciones.",
                    "PM10 y PM2.5 tienen pocos atípicos en proporción (3,0 % y 3,7 %), pero son 91 y 74 registros en números absolutos.",
                    "NO₂, DViento y RUVb casi no tienen atípicos, porque su rango intercuartílico es amplio.",
                ),
                html.H3("¿Se eliminan?", className="card-title", style={"marginTop": "18px"}),
                html.P("No. Un valor atípico puede ser un episodio real de contaminación (un incendio, una zona "
                       "industrial) y no un error. Se conservan y se documentan. Las excepciones son los errores "
                       "demostrables, como la presión en hPa o la representatividad mayor a 100 %, que se deben "
                       "corregir en la fuente."),
                titulo="Lectura",
            ),
        ),

        tarjeta(
            tabla(t, decimales=2, alto=400),
            titulo="Límites de Tukey por variable",
            subtitulo="Un límite inferior negativo indica que no hay atípicos bajos posibles (las variables no toman valores negativos)",
        ),

        tarjeta(
            html.Div([html.Div([html.Label("Variable"),
                                dcc.Dropdown(id="atip-var", value="PM10", clearable=False,
                                             options=[{"label": f"{v} · {NOMBRES.get(v, v)}", "value": v}
                                                      for v in sorted(t["Variable"])])], className="control")],
                     className="controls"),
            dcc.Graph(id="atip-box", config={"displaylogo": False}),
            html.Div(id="atip-tabla"),
            html.Div(id="atip-txt"),
            titulo="Detalle por variable",
            subtitulo="Dónde y cuándo ocurren los valores más extremos",
        ),
    ])


def register_callbacks(app):
    @app.callback(Output("atip-box", "figure"), Output("atip-tabla", "children"), Output("atip-txt", "children"),
                  Input("atip-var", "value"))
    def _detalle(v):
        df = get_df()
        d = df[df["Variable"] == v]
        s = d["Promedio"].dropna()
        u = unidad(v)
        q1, q3 = s.quantile(.25), s.quantile(.75)
        ls, li = q3 + 1.5 * (q3 - q1), q1 - 1.5 * (q3 - q1)
        out = d[(d["Promedio"] > ls) | (d["Promedio"] < li)]

        fig = go.Figure(go.Box(x=s, name=v, marker_color=AZUL, boxpoints="outliers", line_width=1.5,
                               marker=dict(size=6, color=NARANJA, opacity=.8),
                               hovertemplate=f"%{{x:.2f}} {u}<extra></extra>"))
        fig.add_vline(x=ls, line_dash="dash", line_color=TINTA_2, line_width=1,
                      annotation_text=f"Límite superior: {fmt(ls)}", annotation_font_size=11)
        estilo_figura(fig, alto=240)
        fig.update_xaxes(title=f"Promedio ({u})")
        fig.update_yaxes(showticklabels=False)

        top = (out.sort_values("Promedio", ascending=False)
                  .loc[:, ["Estación", "Municipio", "Año", "Tiempo de exposición (horas)", "Promedio"]]
                  .rename(columns={"Tiempo de exposición (horas)": "Exposición (h)", "Promedio": f"Promedio ({u})"})
                  .head(10))

        if len(out):
            munis = out["Municipio"].value_counts()
            txt = interpretacion(
                f"{len(out)} registros atípicos de {len(s)} ({fmt(len(out) / len(s) * 100)} %). El más alto es "
                f"{fmt(out['Promedio'].max())} {u}, {fmt(out['Promedio'].max() / s.median(), 1)} veces la mediana.",
                f"El municipio con más atípicos es {munis.index[0].title()} ({munis.iloc[0]}). Cuando los extremos se "
                "concentran en pocos lugares, apuntan a fuentes locales y no a un problema generalizado.",
            )
            return fig, tabla(top, decimales=2), txt
        return fig, html.Div(), interpretacion("Esta variable no tiene valores atípicos según el criterio de Tukey.")
