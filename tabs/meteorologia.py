"""tabs/meteorologia.py – Variables meteorológicas (Objetivo 4)."""

import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, Input, Output

from components import (encabezado, tarjeta, interpretacion, nota, kpi, estilo_figura, fmt, AZUL, TINTA_2)
from data.data_loader import get_df, promedio_anual, serie, unidad, METEOROLOGICAS, NOMBRES

TEXTOS = {
    "TAire": (
        ["El promedio subió de 20,9 °C (2011) a 24,9 °C (2019), pero la variable solo tiene datos en 6 años "
         "(2011–2013 y 2017–2019) y 73 registros en total, algunos años con apenas 2.",
         "Un aumento de 4 °C en 8 años no es un cambio climático plausible: refleja que cambiaron las estaciones "
         "que reportan (una estación en tierra caliente sube el promedio). Las variables TAire2 y TAire10, con "
         "834 y 334 registros, son más adecuadas para estudiar la temperatura."],
        "Representatividad media de 24 %: los promedios anuales cubren en promedio solo tres meses del año."),
    "HAire": (
        ["La humedad relativa oscila entre 62 % y 73 % sin una tendencia clara. Los valores son típicos de "
         "ciudades andinas y del trópico húmedo.",
         "Como TAire, solo tiene 7 años y 75 registros; HAire2 (693 registros) sería una mejor base para el análisis."],
        "Representatividad media de 27 %."),
    "VViento": (
        ["La velocidad del viento es baja en todo el periodo (1,2–1,7 m/s), en el rango de vientos débiles o casi "
         "en calma. Desde 2013 muestra un leve descenso.",
         "Esto importa para la contaminación: con poco viento los contaminantes se dispersan menos, sobre todo en "
         "valles cerrados como el Aburrá, donde se concentra buena parte de las estaciones."],
        None),
    "DViento": (
        ["La dirección del viento oscila entre 126° y 191°, pero ese promedio no tiene sentido físico: la dirección "
         "es una variable circular, y el promedio aritmético de 350° y 10° da 180° (sur), cuando ambos vientos "
         "vienen del norte.",
         "Para analizarla correctamente se debe usar estadística circular (promedio vectorial) o una rosa de los "
         "vientos, por lo que se excluye del análisis de correlaciones."],
        "Variable circular: el promedio aritmético no es válido."),
    "P": (
        ["La presión salta de unos 635 mmHg (2011–2014) a 851 mmHg en 2018. Ese salto no es meteorológico: la "
         "presión a nivel del mar es 760 mmHg y en Bogotá cerca de 560 mmHg, así que un promedio superior a 800 mmHg "
         "es físicamente imposible.",
         "108 registros (16 %) superan 800 mmHg, en estaciones de Cali, Medellín, Villavicencio y Barranquilla. "
         "Son valores reportados en hectopascales (hPa) pero etiquetados como mmHg. Es un error de unidades que debe "
         "corregirse antes de cualquier análisis con esta variable."],
        "Error de unidades: parte de los registros está en hPa y no en mmHg."),
    "PLiquida": (
        ["La precipitación promedio está entre 2 y 7 mm en casi todos los años, pero 2017 (56,5 mm) y 2019 (34,8 mm) "
         "se disparan por unos pocos valores extremos (máximo 3.236,7 mm).",
         "Esos valores parecen acumulados reportados como promedios. Para esta variable, la mediana es más "
         "representativa que la media."],
        "Medias distorsionadas por valores extremos."),
    "RGlobal": (
        ["La radiación global es estable, entre 165 y 199 W/m², con un leve aumento hasta 2020. Es coherente con la "
         "ubicación ecuatorial del país, donde la radiación varía poco a lo largo del año."],
        None),
    "RUVb": (
        ["La radiación UV-B pasa de 0,6 (2011–2014) a valores entre 130 y 180 desde 2019. El cambio coincide con un "
         "cambio de fuente: hasta 2014 solo reportaba la SDA (Bogotá), y desde 2017 lo hacen otras autoridades "
         "(CDMB, Corpoboyacá, CRC) con otra escala de medición.",
         "La serie no es comparable entre los dos periodos. Cualquier correlación con RUVb, incluidas las muy fuertes "
         "con PM10 (−0,83) y TAire (0,85), es un artefacto de este cambio y no una relación física."],
        "Cambio de escala entre fuentes: la serie no es homogénea."),
}


def layout():
    return html.Div([
        encabezado("Objetivo 4", "Variables meteorológicas",
                   "Condiciones atmosféricas que influyen en la dispersión de los contaminantes."),
        nota("Los datos meteorológicos llegan solo hasta 2022 (TAire hasta 2019), por lo que no se calcula el cambio "
             "2011→2024. Se reporta el cambio entre el primer y el último año disponibles.", tipo="dato"),
        tarjeta(
            html.Div([html.Div([html.Label("Variable"),
                                dcc.Dropdown(id="met-var", value="VViento", clearable=False,
                                             options=[{"label": f"{v} · {NOMBRES[v]}", "value": v}
                                                      for v in METEOROLOGICAS])], className="control")],
                     className="controls"),
            html.Div(id="met-kpis", className="grid-4", style={"marginTop": "16px"}),
            dcc.Graph(id="met-linea", config={"displaylogo": False}),
            dcc.Graph(id="met-registros", config={"displaylogo": False}),
            html.Div(id="met-txt"),
            titulo="Análisis por variable",
        ),
    ])


def register_callbacks(app):
    @app.callback(Output("met-kpis", "children"), Output("met-linea", "figure"),
                  Output("met-registros", "figure"), Output("met-txt", "children"),
                  Input("met-var", "value"))
    def _actualizar(v):
        a = promedio_anual(v)
        s = serie(v)
        u = unidad(v)
        a1, a2 = a.iloc[0], a.iloc[-1]
        cambio = (a2["Promedio"] - a1["Promedio"]) / a1["Promedio"] * 100

        kpis = [
            kpi(fmt(len(s), 0), "Registros", f"{len(a)} años con datos"),
            kpi(fmt(s.median()), f"Mediana ({u})", f"media {fmt(s.mean())}"),
            kpi(fmt(s.max()), f"Máximo ({u})", f"mínimo {fmt(s.min())}"),
            kpi(f"{fmt(cambio)} %", f"Cambio {int(a1['Año'])}→{int(a2['Año'])}",
                f"{fmt(a1['Promedio'])} → {fmt(a2['Promedio'])} {u}"),
        ]

        ah = promedio_anual(v, con_huecos=True)
        fig = go.Figure(go.Scatter(
            x=ah["Año"], y=ah["Promedio"], mode="lines+markers+text", connectgaps=False,
            line=dict(color=AZUL, width=2), marker=dict(size=8, color=AZUL, line=dict(color="white", width=2)),
            text=["" if pd.isna(y) else fmt(y) for y in ah["Promedio"]], textposition="top center", textfont=dict(size=10, color=TINTA_2),
            hovertemplate=f"<b>%{{x}}</b><br>Promedio: %{{y:.2f}} {u}<extra></extra>"))
        estilo_figura(fig, alto=360)
        fig.update_xaxes(dtick=1, title=None, range=[2010.5, 2024.5])
        lo, hi = a["Promedio"].min(), a["Promedio"].max()
        pad = (hi - lo) * .25 or 1
        fig.update_yaxes(title=f"Promedio anual ({u})", range=[max(0, lo - pad), hi + pad])

        reg = go.Figure(go.Bar(x=a["Año"], y=a["Registros"], marker_color="#86b6ef",
                               hovertemplate="<b>%{x}</b><br>%{y} registros<extra></extra>"))
        estilo_figura(reg, alto=170)
        reg.update_layout(margin=dict(t=8, b=36))
        reg.update_xaxes(dtick=1, title=None, range=[2010.5, 2024.5])
        reg.update_yaxes(title="Registros", nticks=3)

        parrafos, alerta = TEXTOS[v]
        bloque = [interpretacion(*parrafos)]
        if alerta:
            bloque.append(nota(alerta))
        return kpis, fig, reg, bloque
