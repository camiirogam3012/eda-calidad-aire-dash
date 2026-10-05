"""tabs/contaminantes.py – Evolución de contaminantes vs. norma (Objetivo 3)."""

import plotly.graph_objects as go
from dash import html, dcc, Input, Output

from components import (encabezado, tarjeta, interpretacion, nota, kpi, grafico, estilo_figura,
                        fmt, AZUL, ROJO, TINTA, TINTA_2, TINTA_3)
from data.data_loader import (promedio_anual, cambio_porcentual, serie, unidad,
                              CONTAMINANTES, NOMBRES, NORMA_ANUAL)

TEXTOS = {
    "PM10": [
        "El PM10 bajó de forma sostenida desde 2016: pasó de cerca de 44 µg/m³ entre 2011 y 2016 a 30,8 µg/m³ en 2024, "
        "una reducción de casi 28 %. Es la tendencia más estable de todos los contaminantes.",
        "Todos los años el promedio nacional estuvo por debajo del nivel anual vigente (50 µg/m³). En 2024 quedó "
        "apenas por encima de la meta a 2030 (30 µg/m³), así que el país está cerca de cumplir el estándar futuro, "
        "aunque las estaciones más contaminadas pueden estar muy por encima del promedio.",
    ],
    "PM2.5": [
        "El PM2.5 cayó 31 % entre 2011 y 2024. El cambio más marcado ocurrió en 2017, cuando bajó de 23,7 a 18,6 µg/m³.",
        "Ese salto coincide con que el número de registros se duplicó (de 65 a 142). Al entrar estaciones nuevas, "
        "posiblemente en zonas menos contaminadas, el promedio puede bajar sin que el aire haya mejorado en las "
        "estaciones existentes. Es un efecto de composición de la red que el EDA no puede descartar.",
        "Desde 2023 el promedio nacional (14,0–14,7 µg/m³) ya está por debajo de la meta 2030 (15 µg/m³).",
    ],
    "NO2": [
        "El NO₂ bajó con fuerza entre 2011 y 2017 (de 36,3 a 21,3 µg/m³), pero desde entonces sube lentamente "
        "hasta 26,9 µg/m³ en 2024. El cambio total de −26 % esconde ese repunte reciente.",
        "El NO₂ proviene sobre todo de la combustión vehicular, así que el repunte podría reflejar el aumento del "
        "parque automotor. Todos los valores están muy por debajo del nivel vigente (60 µg/m³) y de la meta 2030 (40 µg/m³).",
        "Con solo 20 a 59 registros por año, la serie es sensible a qué estaciones reportan cada año.",
    ],
    "O3": [
        "El ozono es el único contaminante que aumentó: pasó de 23,9 a 27,3 µg/m³ (+14 %), con un pico de "
        "32,6 µg/m³ en 2015.",
        "El O₃ no se emite directamente: se forma en la atmósfera a partir de NOx y compuestos orgánicos volátiles "
        "con la radiación solar. Por eso puede subir aunque bajen otros contaminantes. La norma solo define un "
        "límite de 8 horas (100 µg/m³), así que no se traza un nivel anual.",
    ],
    "SO2": [
        "El SO₂ muestra la caída porcentual más grande (−35 %), pero su serie es muy irregular: baja a 5,9 µg/m³ en "
        "2014 y sube a 15,9 µg/m³ en 2016.",
        "Ese comportamiento de sierra sugiere que el promedio depende de pocas estaciones cercanas a fuentes "
        "industriales que entran y salen de la red. Por eso el −35 % no debe leerse como una mejora clara. "
        "Además, el SO₂ tiene el mayor porcentaje de atípicos entre los contaminantes principales (8,7 %).",
    ],
}


def _fig_comparacion():
    datos = [(v, cambio_porcentual(v)["cambio"]) for v in CONTAMINANTES]
    datos.sort(key=lambda x: x[1])
    fig = go.Figure(go.Bar(
        x=[d[1] for d in datos], y=[d[0] for d in datos], orientation="h",
        marker_color=[AZUL if d[1] < 0 else ROJO for d in datos],
        text=[f"{fmt(d[1])} %" for d in datos], textposition="inside", insidetextanchor="middle",
        textfont=dict(color="white", size=12),
        hovertemplate="<b>%{y}</b><br>Cambio 2011→2024: %{x:.1f} %<extra></extra>"))
    estilo_figura(fig, alto=300)
    fig.add_vline(x=0, line_color=TINTA_3, line_width=1)
    fig.update_xaxes(title="Cambio 2011 → 2024 (%)", range=[-40, 20])
    fig.update_yaxes(title=None)
    return fig


def layout():
    return html.Div([
        encabezado("Objetivo 3", "Contaminantes atmosféricos",
                   "Evolución del promedio anual nacional de los cinco contaminantes principales."),

        tarjeta(
            grafico(_fig_comparacion()),
            interpretacion(
                "Cuatro de los cinco contaminantes bajaron entre 2011 y 2024, y el material particulado, el más "
                "relevante para la salud, se redujo cerca de 30 %. El ozono es la excepción: aumentó 14 %.",
                "El tamaño del cambio no indica qué tan confiable es: el SO₂ tiene la mayor caída pero la serie "
                "más irregular. Conviene revisar cada contaminante abajo.",
            ),
            titulo="Comparación del cambio porcentual",
            subtitulo="Azul: disminuyó · Rojo: aumentó",
        ),

        tarjeta(
            html.Div([
                html.Div([html.Label("Contaminante"),
                          dcc.Dropdown(id="cont-var", value="PM10", clearable=False,
                                       options=[{"label": f"{v} · {NOMBRES[v]}", "value": v} for v in CONTAMINANTES])],
                         className="control"),
            ], className="controls"),
            html.Div(id="cont-kpis", className="grid-4", style={"marginTop": "16px"}),
            dcc.Graph(id="cont-linea", config={"displaylogo": False}),
            dcc.Graph(id="cont-registros", config={"displaylogo": False}),
            html.Div(id="cont-txt"),
            nota("Los promedios mezclan registros de 1 hora y 24 horas de exposición y estaciones que cambian cada año. "
                 "La comparación con la norma anual es una referencia, no una verificación de cumplimiento."),
            titulo="Análisis por contaminante",
        ),
    ])


def register_callbacks(app):
    @app.callback(Output("cont-kpis", "children"), Output("cont-linea", "figure"),
                  Output("cont-registros", "figure"), Output("cont-txt", "children"),
                  Input("cont-var", "value"))
    def _actualizar(v):
        a = promedio_anual(v)
        s = serie(v)
        u = unidad(v)
        c = cambio_porcentual(v)

        kpis = [
            kpi(fmt(len(s), 0), "Registros", f"{a['Año'].min()}–{a['Año'].max()}"),
            kpi(f"{fmt(s.median())}", f"Mediana ({u})", f"media {fmt(s.mean())}"),
            kpi(f"{fmt(s.max())}", f"Máximo ({u})", f"mínimo {fmt(s.min())}"),
            kpi(f"{fmt(c['cambio'])} %", "Cambio 2011→2024", f"{fmt(c['v1'])} → {fmt(c['v2'])} {u}"),
        ]

        fig = go.Figure(go.Scatter(
            x=a["Año"], y=a["Promedio"], mode="lines+markers+text", name=v,
            line=dict(color=AZUL, width=2), marker=dict(size=8, color=AZUL, line=dict(color="white", width=2)),
            text=[fmt(y) for y in a["Promedio"]], textposition="top center", textfont=dict(size=10, color=TINTA_2),
            hovertemplate=f"<b>%{{x}}</b><br>Promedio: %{{y:.2f}} {u}<extra></extra>"))
        ymax = a["Promedio"].max() * 1.2
        if v in NORMA_ANUAL:
            n = NORMA_ANUAL[v]
            fig.add_hline(y=n["vigente"], line_dash="dash", line_color=TINTA, line_width=1,
                          annotation_text=f"Norma anual vigente: {n['vigente']}", annotation_position="top left",
                          annotation_font=dict(size=11, color=TINTA))
            fig.add_hline(y=n["meta_2030"], line_dash="dot", line_color=TINTA_2, line_width=1,
                          annotation_text=f"Meta 2030: {n['meta_2030']}", annotation_position="bottom left",
                          annotation_font=dict(size=11, color=TINTA_2))
            ymax = max(ymax, n["vigente"] * 1.1)
        estilo_figura(fig, alto=380)
        fig.update_xaxes(dtick=1, title=None)
        fig.update_yaxes(title=f"Promedio anual ({u})", range=[0, ymax])

        reg = go.Figure(go.Bar(x=a["Año"], y=a["Registros"], marker_color="#86b6ef",
                               hovertemplate="<b>%{x}</b><br>%{y} registros<extra></extra>"))
        estilo_figura(reg, alto=170)
        reg.update_layout(margin=dict(t=8, b=36))
        reg.update_xaxes(dtick=1, title=None)
        reg.update_yaxes(title="Registros", nticks=3)

        return kpis, fig, reg, interpretacion(*TEXTOS[v])
