"""tabs/contexto.py"""

import pandas as pd
from dash import html

from components import encabezado, tarjeta, tabla, interpretacion
from data.data_loader import conteo

NORMA = pd.DataFrame([
    {"Contaminante": "PM10", "Tiempo de exposición": "Anual", "Nivel vigente (µg/m³)": "50", "Meta 2030 (µg/m³)": "30"},
    {"Contaminante": "PM10", "Tiempo de exposición": "24 horas", "Nivel vigente (µg/m³)": "75", "Meta 2030 (µg/m³)": "—"},
    {"Contaminante": "PM2.5", "Tiempo de exposición": "Anual", "Nivel vigente (µg/m³)": "25", "Meta 2030 (µg/m³)": "15"},
    {"Contaminante": "PM2.5", "Tiempo de exposición": "24 horas", "Nivel vigente (µg/m³)": "37", "Meta 2030 (µg/m³)": "—"},
    {"Contaminante": "NO₂", "Tiempo de exposición": "Anual", "Nivel vigente (µg/m³)": "60", "Meta 2030 (µg/m³)": "40"},
    {"Contaminante": "NO₂", "Tiempo de exposición": "1 hora", "Nivel vigente (µg/m³)": "200", "Meta 2030 (µg/m³)": "—"},
    {"Contaminante": "SO₂", "Tiempo de exposición": "24 horas", "Nivel vigente (µg/m³)": "50", "Meta 2030 (µg/m³)": "20"},
    {"Contaminante": "O₃", "Tiempo de exposición": "8 horas", "Nivel vigente (µg/m³)": "100", "Meta 2030 (µg/m³)": "—"},
])


def layout():
    aut = conteo("Autoridad Ambiental", top=5)
    total = conteo("Autoridad Ambiental")["Registros"].sum()
    pct_top5 = aut["Registros"].sum() / total * 100
    return html.Div([
        encabezado("Planteamiento", "Contexto",
                   "El marco normativo y operativo en el que se generan estos datos."),
        tarjeta(
            html.P("En Colombia, la Resolución 2254 de 2017 del Ministerio de Ambiente y Desarrollo Sostenible "
                   "fija los niveles máximos permisibles de contaminantes en el aire. Además de los niveles vigentes, "
                   "define metas más estrictas a 2030 que acercan al país a las guías de la Organización Mundial de la Salud."),
            tabla(NORMA),
            interpretacion(
                "La norma sirve como referencia para leer los promedios del EDA: un valor anual por debajo del nivel "
                "vigente no significa aire limpio, porque la meta a 2030 es casi la mitad para material particulado.",
                "Como el dataset mezcla tiempos de exposición (1 hora, 24 horas), los promedios del EDA se comparan "
                "con la norma anual solo como referencia orientativa, no como verificación de cumplimiento.",
            ),
            titulo="Marco normativo: Resolución 2254 de 2017",
            subtitulo="Niveles máximos permisibles en aire ambiente",
        ),
        tarjeta(
            html.P("La medición la hacen los Sistemas de Vigilancia de Calidad del Aire (SVCA), operados por "
                   "corporaciones autónomas regionales y autoridades ambientales urbanas. Sus datos se consolidan a "
                   "nivel nacional, y de ese consolidado proviene el dataset analizado."),
            tabla(aut.rename(columns={"Autoridad Ambiental": "Autoridad ambiental"}), decimales=0),
            interpretacion(
                f"Cinco autoridades concentran el {pct_top5:.0f} % de los registros: la Secretaría Distrital de "
                "Ambiente de Bogotá (SDA), el Área Metropolitana del Valle de Aburrá (AMVA), la CAR de Cundinamarca, "
                "CORANTIOQUIA y el DAGMA de Cali. Por eso los resultados nacionales reflejan sobre todo lo que "
                "ocurre en las grandes ciudades andinas.",
            ),
            titulo="¿Quién mide la calidad del aire?",
            subtitulo="Cinco autoridades con más registros",
        ),
    ])
