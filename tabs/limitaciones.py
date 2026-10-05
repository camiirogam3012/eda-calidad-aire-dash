"""tabs/limitaciones.py"""

from dash import html

from components import encabezado, tarjeta

LIMITACIONES = [
    ("Composición cambiante de la red",
     "Las estaciones entran y salen cada año. Un cambio en el promedio nacional puede deberse a qué estaciones "
     "reportan y no a un cambio real en el aire."),
    ("Tiempos de exposición mezclados",
     "Se promedian juntos registros de 1, 8 y 24 horas, lo que impide verificar el cumplimiento de la norma."),
    ("Agregación anual y nacional",
     "Las correlaciones usan como máximo 14 puntos (años) y esconden las diferencias entre ciudades. Una relación "
     "a escala nacional puede no cumplirse en cada estación."),
    ("Errores en la fuente",
     "Unidades inconsistentes (P, RUVb) y representatividades imposibles indican problemas de captura que no se "
     "pueden corregir sin información adicional de cada autoridad."),
    ("Cobertura geográfica sesgada",
     "La Amazonía, la Orinoquía y el Pacífico casi no tienen monitoreo, así que los resultados no son extrapolables a esas regiones."),
]

RECOMENDACIONES = [
    "Convertir a mmHg los registros de presión en hPa (valores mayores a 800) y homogeneizar la escala de RUVb.",
    "Filtrar por representatividad temporal ≥ 75 % y analizar por separado cada tiempo de exposición.",
    "Analizar las tendencias por estación (o solo con estaciones activas en todo el periodo) para eliminar el efecto de composición.",
    "Usar TAire2, HAire2 y TAire10 en lugar de TAire y HAire, que tienen pocos registros.",
    "Tratar la dirección del viento con estadística circular.",
    "Para el material particulado, comparar los registros de 24 horas con la norma diaria y estudiar estacionalidad con datos mensuales.",
]


def layout():
    return html.Div([
        encabezado("Cierre", "Limitaciones y recomendaciones",
                   "Lo que este análisis no puede afirmar y cómo mejorarlo en la siguiente etapa."),
        html.Div([
            tarjeta(html.Ul([html.Li([html.Strong(t + ". "), d]) for t, d in LIMITACIONES]), titulo="Limitaciones"),
            tarjeta(html.Ol([html.Li(r) for r in RECOMENDACIONES]), titulo="Recomendaciones para la siguiente etapa"),
        ], className="grid-2"),
    ])
