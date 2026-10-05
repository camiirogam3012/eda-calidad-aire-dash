"""tabs/exploracion.py – Cobertura del monitoreo y estadística descriptiva (Objetivo 2)."""

import plotly.graph_objects as go
from dash import html, dcc, Input, Output

from components import (encabezado, tarjeta, tabla, interpretacion, grafico, estilo_figura,
                        fila, fmt, AZUL, TINTA)
from data.data_loader import get_df, conteo, estadistica_por_variable, serie, unidad, NOMBRES


def _barras_h(d, cat, alto, titulo_x="Número de registros"):
    fig = go.Figure(go.Bar(x=d["Registros"], y=d[cat].astype(str), orientation="h", marker_color=AZUL,
                           text=d["Registros"], textposition="outside", cliponaxis=False,
                           textfont=dict(size=11, color="#475569"),
                           hovertemplate="<b>%{y}</b><br>%{x:,} registros<extra></extra>"))
    estilo_figura(fig, alto=alto)
    fig.update_yaxes(categoryorder="total ascending", title=None, tickfont=dict(size=11))
    fig.update_xaxes(title=titulo_x, showticklabels=False)
    fig.update_layout(margin=dict(l=10, r=40))
    return fig


def layout():
    df = get_df()
    total = len(df)

    # Por año
    anios = df["Año"].value_counts().sort_index()
    fig_anio = go.Figure(go.Bar(x=anios.index, y=anios.values, marker_color=AZUL,
                                hovertemplate="<b>%{x}</b><br>%{y:,} registros<extra></extra>"))
    estilo_figura(fig_anio, alto=340)
    fig_anio.update_xaxes(dtick=1, title="Año")
    fig_anio.update_yaxes(title="Registros")
    pico = anios.idxmax()

    # Por variable
    var = conteo("Variable")
    pm = var.set_index("Variable")["Registros"]
    pct_pm = (pm["PM10"] + pm["PM2.5"]) / total * 100

    # Estaciones, tipo, territorio
    est = conteo("Estación", top=15)
    tipo = conteo("Tipo de Estación")
    pct_fija = tipo.set_index("Tipo de Estación")["Registros"].get("Fija", 0) / total * 100
    dep = conteo("Departamento")
    pct_top2 = dep["Registros"].head(2).sum() / total * 100
    mun = conteo("Municipio", top=20)

    desc = estadistica_por_variable().rename(columns={"Desv": "Desv. est."})

    return html.Div([
        encabezado("Objetivo 2", "Exploración general",
                   "Dónde, cuándo y qué se mide: la cobertura del monitoreo condiciona todo lo demás."),

        tarjeta(
            grafico(fig_anio),
            interpretacion(
                f"El número de registros pasó de {anios.iloc[0]} en {anios.index[0]} a un máximo de "
                f"{fmt(anios.max(), 0)} en {pico}, es decir, se triplicó: la red de monitoreo se expandió durante el periodo.",
                f"La caída en {anios.index[-2]}–{anios.index[-1]} ({anios.iloc[-2]} y {anios.iloc[-1]} registros) "
                "puede deberse a reportes incompletos o al cierre de estaciones; el dataset no permite distinguir entre las dos causas.",
                "Consecuencia para el análisis: cuando el promedio anual de una variable cambia, parte del cambio puede "
                "venir de que entraron o salieron estaciones, y no solo de cambios reales en el aire.",
            ),
            titulo="Registros por año",
        ),

        fila(
            tarjeta(
                grafico(_barras_h(var, "Variable", 560)),
                interpretacion(
                    f"El material particulado domina el dataset: PM10 y PM2.5 suman el {fmt(pct_pm, 0)} % de los registros. "
                    "Son los contaminantes que más se vigilan por su efecto en la salud.",
                    "En el otro extremo, TAire, HAire y RUVb tienen menos de 80 registros cada uno. "
                    "Cualquier conclusión sobre ellos descansa en muy poca información.",
                ),
                titulo="Registros por variable",
            ),
            tarjeta(
                grafico(_barras_h(est, "Estación", 560)),
                interpretacion(
                    "Las estaciones con más registros (Centro de Alto Rendimiento, Kennedy, Tunal, Las Ferias) son "
                    "de Bogotá. Son estaciones que miden muchas variables a la vez durante todo el periodo.",
                ),
                titulo="15 estaciones con más registros",
            ),
        ),

        fila(
            tarjeta(
                grafico(_barras_h(dep, "Departamento", 720)),
                interpretacion(
                    f"Antioquia y Bogotá concentran el {fmt(pct_top2, 0)} % de los registros, seguidos por Valle del "
                    "Cauca y Cundinamarca. La Orinoquía, la Amazonía y gran parte del Pacífico casi no tienen monitoreo.",
                    "Los resultados nacionales son, en la práctica, resultados de la región Andina urbana.",
                ),
                titulo="Registros por departamento (nombres normalizados)",
            ),
            html.Div([
                tarjeta(
                    grafico(_barras_h(tipo, "Tipo de Estación", 180)),
                    interpretacion(
                        f"El {fmt(pct_fija, 0)} % de los registros viene de estaciones fijas, que operan de forma continua. "
                        "Las indicativas son campañas temporales, con menos cobertura en el año."),
                    titulo="Tipo de estación",
                ),
                tarjeta(
                    grafico(_barras_h(mun, "Municipio", 520)),
                    titulo="20 municipios con más registros",
                ),
            ]),
        ),

        tarjeta(
            tabla(desc, decimales=2, alto=420),
            interpretacion(
                "Las escalas son muy distintas entre variables (presión cerca de 700 mmHg, viento cerca de 1 m/s), así que "
                "solo tiene sentido comparar cada variable consigo misma.",
                "En la mayoría de los contaminantes la media es algo mayor que la mediana (PM10: 37,1 frente a 34,6; SO₂: "
                "9,4 frente a 6,0). Esto indica asimetría positiva: hay pocas estaciones con valores altos que jalan el promedio hacia arriba.",
                "PLiquida es el caso extremo: su media (9,8 mm) es siete veces su mediana (1,4 mm) por unos pocos valores "
                "enormes (máximo 3.236,7 mm). Para esta variable la mediana es la medida de tendencia central adecuada.",
            ),
            titulo="Estadística descriptiva por variable",
            subtitulo="Calculada sobre la columna Promedio · ordena haciendo clic en los encabezados",
        ),

        tarjeta(
            html.Div([
                html.Div([html.Label("Variable"),
                          dcc.Dropdown(id="exp-var", options=[{"label": f"{v} · {NOMBRES.get(v, v)}", "value": v}
                                                              for v in sorted(df["Variable"].unique())],
                                       value="PM10", clearable=False)], className="control"),
            ], className="controls"),
            dcc.Graph(id="exp-box", config={"displaylogo": False}),
            html.Div(id="exp-box-txt"),
            titulo="Distribución de una variable",
            subtitulo="Diagrama de caja e histograma · elige la variable",
        ),
    ])


def register_callbacks(app):
    @app.callback(Output("exp-box", "figure"), Output("exp-box-txt", "children"), Input("exp-var", "value"))
    def _box(v):
        s = serie(v)
        u = unidad(v)
        fig = go.Figure()
        fig.add_trace(go.Box(x=s, name=v, marker_color=AZUL, boxpoints="outliers", line_width=1.5,
                             marker=dict(size=5, opacity=.6), xaxis="x", yaxis="y2",
                             hovertemplate=f"%{{x:.2f}} {u}<extra></extra>"))
        fig.add_trace(go.Histogram(x=s, marker_color=AZUL, opacity=.85, nbinsx=50,
                                   hovertemplate=f"%{{x}} {u}<br>%{{y}} registros<extra></extra>"))
        estilo_figura(fig, alto=380)
        fig.update_layout(yaxis=dict(domain=[0, .72], title="Registros"),
                          yaxis2=dict(domain=[.78, 1], showticklabels=False, showgrid=False), bargap=.05)
        fig.update_xaxes(title=f"Promedio ({u})")
        media, mediana = s.mean(), s.median()
        sesgo = s.skew()
        forma = ("fuertemente asimétrica a la derecha" if sesgo > 1 else
                 "moderadamente asimétrica a la derecha" if sesgo > .5 else
                 "asimétrica a la izquierda" if sesgo < -.5 else "aproximadamente simétrica")
        txt = interpretacion(
            f"{NOMBRES.get(v, v)}: {len(s)} registros, media {fmt(media, 2)} y mediana {fmt(mediana, 2)} {u}. "
            f"La distribución es {forma} (coeficiente de asimetría {fmt(sesgo, 2)}).",
            "Los puntos aislados a la derecha del diagrama de caja son los valores atípicos según el criterio de Tukey; "
            "se analizan en la sección de valores atípicos.",
        )
        return fig, txt
