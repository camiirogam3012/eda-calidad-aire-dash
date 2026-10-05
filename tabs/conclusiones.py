"""tabs/conclusiones.py – Respuesta a cada objetivo."""

from dash import html, dcc

from components import encabezado, tarjeta, fmt
from data.data_loader import resumen_general, cambio_porcentual


def layout():
    r = resumen_general()
    c = {v: cambio_porcentual(v)["cambio"] for v in ["PM10", "PM2.5", "NO2", "O3", "SO2"]}

    hallazgos = [
        ("Calidad del dataset", "/dataset",
         f"El dataset requiere depuración antes de usarse: el {fmt(r['pct_duplicados'])} % de las filas estaba "
         f"duplicado, los departamentos aparecen con {r['deptos_crudos']} nombres para {r['deptos']} departamentos "
         "reales, la presión mezcla hPa y mmHg, la radiación UV-B cambia de escala y hay representatividades "
         "mayores a 100 %. Los faltantes, en cambio, son mínimos (menos de 0,5 %)."),
        ("Cobertura del monitoreo", "/exploracion",
         "La red se triplicó entre 2011 y 2022, pero está concentrada: Antioquia y Bogotá aportan la mitad de los "
         "registros y el monitoreo se centra en material particulado. Las conclusiones nacionales representan "
         "sobre todo a las ciudades andinas."),
        ("Evolución de los contaminantes", "/contaminantes",
         f"El material particulado bajó de forma sostenida (PM10 {fmt(c['PM10'])} %, PM2.5 {fmt(c['PM2.5'])} %) y en "
         "2024 el PM2.5 nacional ya está por debajo de la meta 2030. El NO₂ bajó hasta 2017 y luego repunta; el "
         f"ozono es el único que aumenta ({fmt(c['O3'])} %). La caída del SO₂ ({fmt(c['SO2'])} %) no es confiable por su "
         "irregularidad."),
        ("Variables meteorológicas", "/meteorologia",
         "Los vientos son débiles en todo el periodo (1,2–1,7 m/s), lo que limita la dispersión. Varias series "
         "meteorológicas no permiten concluir tendencias: TAire y HAire tienen muy pocos años, P tiene un error de "
         "unidades, RUVb cambia de escala y DViento no puede promediarse aritméticamente."),
        ("Asociaciones entre variables", "/correlaciones",
         "La única relación fuerte y confiable es PM10–PM2.5 (r = 0,97), explicada por sus fuentes comunes. Las "
         "relaciones de la temperatura con los contaminantes son físicamente plausibles pero se apoyan en 6 años. "
         "Las correlaciones de RUVb y presión son espurias, producto de problemas en los datos."),
        ("Valores atípicos", "/atipicos",
         "Cerca del 4 % de los registros es atípico, en su mayoría por valores altos. Se concentran en SO₂, CO y "
         "humedad, y en pocos municipios, lo que sugiere fuentes locales. Se conservan, porque pueden ser episodios "
         "reales de contaminación."),
    ]

    return html.Div([
        encabezado("Cierre", "Conclusiones",
                   "La respuesta a cada objetivo específico y a la pregunta de investigación."),

        tarjeta(
            html.P("¿Cómo se han comportado los contaminantes y las variables meteorológicas en Colombia entre 2011 y "
                   "2024, y qué tan confiable es la información?", className="pregunta"),
            html.P(["La calidad del aire mejoró en material particulado, el contaminante más vigilado y más dañino para "
                    "la salud, mientras el ozono aumenta y el NO₂ repunta. Pero la información tiene ",
                    html.Strong("limitaciones serias de calidad y cobertura"),
                    ": antes de modelar o de comparar con la norma hay que corregir unidades, normalizar categorías, "
                    "filtrar por representatividad y separar por tiempo de exposición."],
                   style={"marginTop": "16px"}),
            titulo="Respuesta a la pregunta de investigación",
        ),

        html.H2("Hallazgos por objetivo", className="section"),
        html.Div([
            html.Section(html.Div([
                html.Div(str(i), className="obj-num"),
                html.Div([html.H4(t), html.P(texto), dcc.Link("Ver evidencia →", href=ruta, className="obj-link")]),
            ], className="obj-item"), className="card")
            for i, (t, ruta, texto) in enumerate(hallazgos, start=1)
        ], className="grid-2"),
    ])
