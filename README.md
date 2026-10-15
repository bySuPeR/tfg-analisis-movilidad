# Análisis y visualización de movilidad mediante redes celulares

Aplicación web desarrollada como Trabajo de Fin de Grado en Ingeniería Informática del Software para analizar y visualizar patrones de movilidad a partir de datos de movilidad y estaciones base de telefonía móvil.

## Funcionalidades

- Procesamiento y filtrado de datos de movilidad.
- Análisis de estaciones base y cálculo de proximidad geográfica.
- Generación de mapas interactivos y mapas de calor.
- Visualización de información mediante gráficas.
- Interfaz web desarrollada con Flask.

## Tecnologías

- **Lenguaje:** Python
- **Backend:** Flask
- **Análisis y procesamiento:** NumPy, Pandas, Matplotlib, Plotly y scikit-learn.
- **Geolocalización y mapas:** Folium, GeoPy y OpenStreetMap.
- **Servicios externos:** Mapbox, OpenCelliD y Valhalla.

## Requisitos

- Python 3.11 o una versión compatible con las dependencias del proyecto.
- Credenciales propias para los servicios externos que las requieran.

## Instalación y ejecución

1. Clona el repositorio:

   ```bash
   git clone https://github.com/bySuPeR/tfg-analisis-movilidad.git
   cd tfg-analisis-movilidad
   ```

2. Crea y activa un entorno virtual.

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Copia `.env.example` a un nuevo archivo llamado `.env` y sustituye los valores de ejemplo por tus propias credenciales.

5. Ejecuta la aplicación:

   ```bash
   python app.py
   ```

6. Abre `http://127.0.0.1:8000` en el navegador.

## Autoría

Proyecto académico desarrollado como Trabajo de Fin de Grado en Ingeniería Informática del Software.