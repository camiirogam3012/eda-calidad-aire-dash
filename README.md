# Calidad del aire en Colombia (2011–2024) · Dashboard del EDA

Dashboard interactivo en **Dash** que presenta el análisis exploratorio de datos (EDA) de la calidad del aire en Colombia, con planteamiento del problema, objetivos, metodología, interpretación de cada resultado y conclusiones por objetivo.

**Autor:** Camilo Romero

## Contenido

| Sección | Pestaña | Qué muestra |
|---|---|---|
| Planteamiento | Inicio, Introducción, Contexto, Problema, Objetivos, Metodología | Motivación, Res. 2254/2017, pregunta de investigación, objetivo general y 6 específicos |
| Datos | Dataset y calidad | Faltantes, duplicados (47 %), nombres inconsistentes, representatividad |
| Análisis | Exploración general · Contaminantes · Meteorología · Correlaciones · Valores atípicos | Gráficos interactivos, cada uno con su interpretación |
| Cierre | Conclusiones · Limitaciones | Hallazgo por objetivo y recomendaciones |

## Estructura

```
├── app.py                 # Punto de entrada y navegación
├── components.py          # Componentes de interfaz y estilo de gráficos
├── data/
│   ├── data_loader.py     # Carga, limpieza (igual al EDA) y agregaciones
│   └── dataset_calidad_aire.csv
├── tabs/                  # Una pestaña por archivo: layout() + register_callbacks(app)
├── assets/styles.css      # Estilos (Dash los carga automáticamente)
├── requirements.txt
├── Procfile               # Comando de arranque para Render
└── .python-version        # Python 3.12
```

## Ejecutar localmente

```bash
pip install -r requirements.txt
python app.py
```

Abrir http://localhost:8050

## Desplegar en Render

1. Subir esta carpeta completa a un repositorio de GitHub (el CSV incluido).
2. En Render: **New → Web Service** → conectar el repositorio.
3. Configurar:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:server --workers 2 --timeout 120`
   - **Instance type:** Free
4. (Opcional) En **Environment** agregar los enlaces de la barra lateral:
   `URL_EDA_PYTHON`, `URL_EDA_R`, `URL_REPO`.

## Datos

Consolidado nacional de indicadores anuales de calidad del aire reportados por 31 autoridades ambientales (2011–2024): 29.683 filas originales, 15.745 únicas, 654 estaciones y 20 variables.
