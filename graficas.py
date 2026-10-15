
import plotly.express as px
import plotly.io as pio
import os
from collections import Counter
from estacionBase import obtener_estacion_por_id_y_cercania
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize

def contar_conexiones_por_estacion(puntos, listaEstaciones):
  """Devuelve la cantidad de conexiones por estacion base utilizada"""
  contador_estaciones = Counter()
  for punto in puntos:
    for antena_cercana in punto['AntenasCercanas']:
      antena = obtener_estacion_por_id_y_cercania(antena_cercana['ID'], punto['Latitud'], punto['Longitud'], listaEstaciones)
      contador_estaciones[antena] += 1
  return contador_estaciones

def generar_grafico_barras_conexiones_por_estacion(contador_estaciones, nombre_archivo):
    """Crea un gráfico de barras con la cantidad de conexiones a todas las estaciones base del estudio"""
    try:
        estaciones = list(contador_estaciones.keys())
        etiquetas_eje_x = [str(estacion.cellID) for estacion in estaciones]
        conexiones = list(contador_estaciones.values())

        fig = px.bar(x=etiquetas_eje_x, y=conexiones, labels={'x':'ID de Estación Base', 'y':'Número de Conexiones'}, title='Número de Conexiones por Estación Base')
        fig.update_layout(
                title={'text': 'Número de Conexiones por Estación Base', 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'size': 12}},
                xaxis_title={'text': 'ID de Estación Base', 'font': {'size': 11}},
                yaxis_title={'text': 'Número de Conexiones', 'font': {'size': 11}},
                margin={'l': 10, 'r': 10, 't': 20, 'b': 10}, 
                height=325, 
                width=580 
        )
        fig.update_xaxes(tickangle=-45, tickfont=dict(size=8))
        fig.update_yaxes(tickfont=dict(size=10))
        fig.update_traces(marker_color='lightsalmon') 
        nombre_html= nombre_archivo + ".html"
        nombre_html = os.path.join('static', nombre_html)
        pio.write_html(fig, file=nombre_html, auto_open=False)
        print(f"Gráfico de conexiones por estación base guardado como {nombre_html}")
        plt.figure(figsize=(16, 12))
        plt.bar(etiquetas_eje_x, conexiones, color='lightsalmon')
        plt.title('Número de Conexiones por Estación Base', fontsize=12)
        plt.xlabel('ID de Estación Base', fontsize=11)
        plt.ylabel('Número de Conexiones', fontsize=11)
        plt.xticks(rotation=45, fontsize=8)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join('descargas', f"{nombre_archivo}.png"))
        plt.close()
        print(f"Gráfico de conexiones por estación base guardado como {nombre_archivo}.png")
    except Exception as e:
        print(f"Error al generar el gráfico de barras: {e}")

def generar_grafico_top_50_estaciones(contador_estaciones, nombre_archivo):
    """Crea un gráfico de barras con las 50 estaciones base con más cantidad de conexiones del estudio"""
    try:
        top_50_estaciones = contador_estaciones.most_common(50)
        estaciones = [estacion for estacion, _ in top_50_estaciones]
        etiquetas_eje_x = [str(estacion.cellID) for estacion in estaciones]
        conexiones = [conexiones for _, conexiones in top_50_estaciones]

        fig = px.bar(x=etiquetas_eje_x, y=conexiones, labels={'x':'ID de Estación Base', 'y':'Número de Conexiones'}, title='Top 50 Estaciones con Mayor Número de Conexiones')
        fig.update_layout(
                title={'text': 'Top 50 Estaciones con Mayor Número de Conexiones', 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'size': 12}},
                xaxis_title={'text': 'ID de Estación Base', 'font': {'size': 11}},
                yaxis_title={'text': 'Número de Conexiones', 'font': {'size': 11}},
                margin={'l': 10, 'r': 10, 't': 20, 'b': 10}, 
                height=325, 
                width=580 
        )
        fig.update_xaxes(tickangle=-45, tickfont=dict(size=8))
        fig.update_yaxes(tickfont=dict(size=10))
        fig.update_traces(marker_color='lightsalmon') 
        nombre_html= nombre_archivo + ".html"
        nombre_html = os.path.join('static', nombre_html)
        pio.write_html(fig, file=nombre_html, auto_open=False)
        print(f"Gráfico de top 50 estaciones guardado como {nombre_html}")
        plt.figure(figsize=(16, 12))
        plt.bar(etiquetas_eje_x, conexiones, color='lightsalmon')
        plt.title('Top 50 Estaciones con Mayor Número de Conexiones', fontsize=12)
        plt.xlabel('ID de Estación Base', fontsize=11)
        plt.ylabel('Número de Conexiones', fontsize=11)
        plt.xticks(rotation=45, fontsize=8)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join('descargas', f"{nombre_archivo}.png"))
        plt.close()
        print(f"Gráfico de top 50 estaciones guardado como {nombre_archivo}.png")
    except Exception as e:
        print(f"Error al generar el gráfico de barras: {e}")



def contar_conexiones_por_dia(puntos):
    """Devuelve la cantidad de conexiones por día"""
    contador_dias = Counter()
    for punto in puntos:
        fecha = datetime.strptime(punto['Dia'], "%Y-%m-%d")
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        dia_semana = dias_semana[fecha.weekday()]
        contador_dias[dia_semana] += 1
    return contador_dias

def contar_conexiones_por_hora(puntos):
    """Devuelve la cantidad de conexiones por horas"""
    contador_horas = Counter()
    for punto in puntos:
        hora = datetime.strptime(punto['Hora'], "%H:%M:%S").hour
        contador_horas[hora] += 1
    return contador_horas



def contar_conexiones_por_mes(puntos):
    """Devuelve la cantidad de conexiones por mes"""
    contador_meses = Counter()
    for punto in puntos:
        fecha = datetime.strptime(punto['Dia'], "%Y-%m-%d")
        mes = fecha.strftime("%B")  # Nombre del mes completo
        contador_meses[mes] += 1
    return dict(sorted(contador_meses.items(), key=lambda x: datetime.strptime(x[0], "%B").month))

def contar_conexiones_por_estacionAño(puntos):
    """Devuelve la cantidad de conexiones por estación del año"""
    estaciones = {
        'Primavera': [3, 4, 5],
        'Verano': [6, 7, 8],
        'Otoño': [9, 10, 11],
        'Invierno': [12, 1, 2]
    }
    
    contador_estaciones = Counter()
    for punto in puntos:
        fecha = datetime.strptime(punto['Dia'], "%Y-%m-%d")
        mes = fecha.month
        for estacion, meses in estaciones.items():
            if mes in meses:
                contador_estaciones[estacion] += 1
                break
    return dict(sorted(contador_estaciones.items(), key=lambda x: ['Primavera', 'Verano', 'Otoño', 'Invierno'].index(x[0])))



def generar_grafico_area_conexiones_por_mes(contador_meses, nombre_archivo):
    """Crea un gráfico de área con las conexiones totales por mes"""
    try:
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        mesesIng = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        conexiones = [contador_meses.get(mes, 0) for mes in mesesIng]

        fig = px.area(x=meses, y=conexiones, labels={'x':'Mes', 'y':'Número de Conexiones'}, title='Número de Conexiones por Mes')
        fig.update_layout(
            title={'text': 'Número de Conexiones por Mes', 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'size': 12}},
            xaxis_title={'text': 'Mes', 'font': {'size': 11}},
            yaxis_title={'text': 'Número de Conexiones', 'font': {'size': 11}},
            margin={'l': 10, 'r': 10, 't': 20, 'b': 10},
            height=325,
            width=580
        )
        fig.update_xaxes(tickangle=-45, tickfont=dict(size=8))
        fig.update_yaxes(tickfont=dict(size=10))
        fig.update_traces(fillcolor='lightsalmon', line=dict(color='darkorange'))

        nombre_html = nombre_archivo + ".html"
        nombre_html = os.path.join('static', nombre_html)
        pio.write_html(fig, file=nombre_html, auto_open=False)
        print(f"Gráfico de área de conexiones por mes guardado como {nombre_archivo}")

        plt.figure(figsize=(16, 12))
        plt.fill_between(meses, conexiones, color='lightsalmon', alpha=0.6)
        plt.plot(meses, conexiones, marker='o', color='darkorange')
        plt.title('Número de Conexiones por Mes', fontsize=12)
        plt.xlabel('Mes', fontsize=11)
        plt.ylabel('Número de Conexiones', fontsize=11)
        plt.xticks(rotation=45, fontsize=8)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join('descargas', f"{nombre_archivo}.png"))
        plt.close()
        print(f"Gráfico de área de conexiones por mes guardado como {nombre_archivo}.png")
    except Exception as e:
        print(f"Error al generar el gráfico de área: {e}")



def generar_grafico_area_conexiones_por_estacion(contador_estaciones, nombre_archivo):
    """Crea un gráfico de área con las conexiones totales por estación del año"""
    try:
        estaciones = ['Primavera', 'Verano', 'Otoño', 'Invierno']
        conexiones = [contador_estaciones.get(estacion, 0) for estacion in estaciones]

        fig = px.area(x=estaciones, y=conexiones, labels={'x':'Estación del Año', 'y':'Número de Conexiones'}, title='Número de Conexiones por Estación del Año')
        fig.update_layout(
            title={'text': 'Número de Conexiones por Estación del Año', 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'size': 12}},
            xaxis_title={'text': 'Estación del Año', 'font': {'size': 11}},
            yaxis_title={'text': 'Número de Conexiones', 'font': {'size': 11}},
            margin={'l': 10, 'r': 10, 't': 20, 'b': 10}, 
            height=325, 
            width=580 
        )
        fig.update_xaxes(tickangle=-45, tickfont=dict(size=8))
        fig.update_yaxes(tickfont=dict(size=10))
        fig.update_traces(fillcolor='lightsalmon', line=dict(color='darkorange'))

        nombre_html = nombre_archivo + ".html"
        nombre_html = os.path.join('static', nombre_html)
        pio.write_html(fig, file=nombre_html, auto_open=False)
        print(f"Gráfico de área de conexiones por estación del año guardado como {nombre_archivo}")

        plt.figure(figsize=(16, 12))
        plt.fill_between(estaciones, conexiones, color='lightsalmon', alpha=0.6)
        plt.plot(estaciones, conexiones, marker='o', color='darkorange')
        plt.title('Número de Conexiones por Estación del Año', fontsize=12)
        plt.xlabel('Estación del Año', fontsize=11)
        plt.ylabel('Número de Conexiones', fontsize=11)
        plt.xticks(rotation=45, fontsize=8)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join('descargas', f"{nombre_archivo}.png"))
        plt.close()
        print(f"Gráfico de área de conexiones por estación del año guardado como {nombre_archivo}.png")
    except Exception as e:
        print(f"Error al generar el gráfico de área: {e}")




def generar_grafico_area_conexiones_por_dia(contador_dias, nombre_archivo):
    """Crea un gráfico de área con las conexiones totales por día"""
    try:
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        conexiones = [contador_dias[dia] for dia in dias_semana]

        fig = px.area(x=dias_semana, y=conexiones, labels={'x':'Día de la Semana', 'y':'Número de Conexiones'}, title='Número de Conexiones por Día de la Semana')
        fig.update_layout(
            title={'text': 'Número de Conexiones por Día de la Semana', 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'size': 12}},
            xaxis_title={'text': 'Día de la Semana', 'font': {'size': 11}},
            yaxis_title={'text': 'Número de Conexiones', 'font': {'size': 11}},
            margin={'l': 10, 'r': 10, 't': 20, 'b': 10}, 
            height=325, 
            width=580 
        )
        fig.update_xaxes(tickangle=-45, tickfont=dict(size=8))
        fig.update_yaxes(tickfont=dict(size=10))
        fig.update_traces(fillcolor='lightsalmon', line=dict(color='darkorange'))

        nombre_html = nombre_archivo + ".html"
        nombre_html = os.path.join('static', nombre_html)
        pio.write_html(fig, file=nombre_html, auto_open=False)
        print(f"Gráfico de área de conexiones por día de la semana guardado como {nombre_archivo}")

        plt.figure(figsize=(16, 12))
        plt.fill_between(dias_semana, conexiones, color='lightsalmon', alpha=0.6)
        plt.plot(dias_semana, conexiones, marker='o', color='darkorange')
        plt.title('Número de Conexiones por Día de la Semana', fontsize=12)
        plt.xlabel('Día de la Semana', fontsize=11)
        plt.ylabel('Número de Conexiones', fontsize=11)
        plt.xticks(rotation=45, fontsize=8)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join('descargas', f"{nombre_archivo}.png"))
        plt.close()
        print(f"Gráfico de área de conexiones por día de la semana guardado como {nombre_archivo}.png")
    except Exception as e:
        print(f"Error al generar el gráfico de área: {e}")

    

def generar_grafico_area_conexiones_por_hora(contador_horas, nombre_archivo):
    """Crea un gráfico de área con las conexiones totales por hora"""
    try:
        horas = [f'{i}:00' for i in range(24)]
        conexiones = [contador_horas[i] for i in range(24)]

        fig = px.area(x=horas, y=conexiones, labels={'x':'Hora del Día', 'y':'Número de Conexiones'}, title='Número de Conexiones por Hora del Día')
        fig.update_layout(
            title={'text': 'Número de Conexiones por Hora del Día', 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'size': 12}},
            xaxis_title={'text': 'Hora del Día', 'font': {'size': 11}},
            yaxis_title={'text': 'Número de Conexiones', 'font': {'size': 11}},
            margin={'l': 10, 'r': 10, 't': 20, 'b': 10}, 
            height=325, 
            width=580 
        )
        fig.update_xaxes(tickangle=-45, tickfont=dict(size=8))
        fig.update_yaxes(tickfont=dict(size=10))
        fig.update_traces(fillcolor='lightsalmon', line=dict(color='darkorange'))

        nombre_html = nombre_archivo + ".html"
        nombre_html = os.path.join('static', nombre_html)
        pio.write_html(fig, file=nombre_html, auto_open=False)
        print(f"Gráfico de área de conexiones por hora del día guardado como {nombre_archivo}")

        plt.figure(figsize=(16, 12))
        plt.fill_between(horas, conexiones, color='lightsalmon', alpha=0.6)
        plt.plot(horas, conexiones, marker='o', color='darkorange')
        plt.title('Número de Conexiones por Hora del Día', fontsize=12)
        plt.xlabel('Hora del Día', fontsize=11)
        plt.ylabel('Número de Conexiones', fontsize=11)
        plt.xticks(rotation=45, fontsize=8)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join('descargas', f"{nombre_archivo}.png"))
        plt.close()
        print(f"Gráfico de área de conexiones por hora del día guardado como {nombre_archivo}.png")
    except Exception as e:
        print(f"Error al generar el gráfico de área: {e}")



def calcular_distancia_geodesica_media(estacion, puntos):
  """Calcula la distancia geodesica media a las estaciones base cercana a cada punto de movilidad estudiada"""
  distancias = []
  for punto in puntos:
    for antena in punto['AntenasCercanas']:
        if antena['ID'] == estacion.cellID:
            distancia_geodesica = antena['Distancia']
            distancias.append(distancia_geodesica)

  if distancias:
    return sum(distancias) / len(distancias)
  return 0

def generar_grafico_distancia_media_top_50(contador_estaciones, puntos, nombre_archivo):
    """Crea un gráfico de barras con la distancia media geodesica desde los dispositivos al top 50 estaciones con más conexiones totales."""
    try:
        top_50_estaciones = contador_estaciones.most_common(50)
        estaciones = [estacion for estacion, _ in top_50_estaciones]
        etiquetas_eje_x = [str(estacion.cellID) for estacion in estaciones]
        distancias_medias = [calcular_distancia_geodesica_media(estacion, puntos) for estacion in estaciones]

        fig = px.bar(
                x=etiquetas_eje_x, 
                y=distancias_medias, 
                labels={'x': 'ID de Estación Base', 'y': 'Distancia Geodésica Media (Metros)'}, 
                title='Distancia Geodésica Media de las Top 50 Estaciones con Más Conexiones'
        )
        fig.update_layout(
                title={'text': 'Distancia Geodésica Media de las Top 50 Estaciones con Más Conexiones', 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'size': 12}},
                xaxis_title={'text': 'ID de Estación Base', 'font': {'size': 11}},
                yaxis_title={'text': 'Distancia Geodésica Media (Metros)', 'font': {'size': 11}},
                margin={'l': 10, 'r': 10, 't': 20, 'b': 10}, 
                height=325, 
                width=580  
            )
        fig.update_xaxes(tickangle=-45, tickfont=dict(size=8))
        fig.update_yaxes(tickfont=dict(size=10))
        fig.update_traces(marker_color='lightsalmon') 
        nombre_html= nombre_archivo + ".html"
        nombre_html = os.path.join('static', nombre_html)
        pio.write_html(fig, file=nombre_html, auto_open=False)
        print(f"Gráfico de distancia geodésica media de las top 50 estaciones guardado como {nombre_html}")

        plt.figure(figsize=(16, 12))
        plt.bar(etiquetas_eje_x, distancias_medias, color='lightsalmon')
        plt.title('Distancia Geodésica Media de las Top 50 Estaciones con Más Conexiones', fontsize=12)
        plt.xlabel('ID de Estación Base', fontsize=11)
        plt.ylabel('Distancia Geodésica Media (Metros)', fontsize=11)
        plt.xticks(rotation=45, fontsize=8)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join('descargas', f"{nombre_archivo}.png"))
        plt.close()
        print(f"Gráfico de distancia geodésica media de las top 50 estaciones guardado como {nombre_archivo}.png")
    except Exception as e:
        print(f"Error al generar el gráfico de barras: {e}")





def contar_conexiones_por_celda(latitudes, longitudes, num_celdas):
    """Devuelve una matriz con la cantidad de estaciones por celda y los bordes en latitud y longitud que delimitan esas celdas"""
    # Crear una cuadrícula de celdas
    lat_min, lat_max = min(latitudes), max(latitudes)
    lon_min, lon_max = min(longitudes), max(longitudes)
    
    lat_bins = np.linspace(lat_min, lat_max, num_celdas + 1)
    lon_bins = np.linspace(lon_min, lon_max, num_celdas + 1)
    
    # Contar el número de puntos en cada celda
    heatmap, _, _ = np.histogram2d(latitudes, longitudes, bins=[lat_bins, lon_bins])
    
    return lat_bins, lon_bins, heatmap

def generar_mapa_calor_conexiones(puntos, lista_estaciones, nombre_archivo):
    """Genera un mapa de calor interactivo (html) y otro igual que se guarda en un archivo PNG """
    # Obtiene las coordenadas de latitud y longitud de las antenas más cercanas a los taxis
    latitudes = []
    longitudes = []
    
    for punto in puntos:
        for antena_cercana in punto['AntenasCercanas']:
            antena = obtener_estacion_por_id_y_cercania(antena_cercana['ID'], punto['Latitud'], punto['Longitud'], lista_estaciones)
            if antena:
                latitudes.append(antena.latitud)
                longitudes.append(antena.longitud)
    
    if len(latitudes) > 1 and len(longitudes) > 1:
        try:
            # Contar conexiones en una cuadrícula
            num_celdas = 50 
            lat_bins, lon_bins, heatmap = contar_conexiones_por_celda(latitudes, longitudes, num_celdas)
            
            lon_grid, lat_grid = np.meshgrid(lon_bins[:-1], lat_bins[:-1])
            fig = px.imshow(heatmap.T, x=lon_bins[:-1], y=lat_bins[:-1], color_continuous_scale='Inferno', labels={'color':'Número de Conexiones'})
            fig.update_layout(
                title='Mapa de Calor de Conexiones por Estación Base',
                title_font_size=11,
                title_x=0.5,
                title_xanchor='center',
                title_yanchor='top',
                xaxis_title='Longitud',
                xaxis_title_font_size=11,
                yaxis_title='Latitud',
                yaxis_title_font_size=11,
                margin=dict(l=10, r=10, t=20, b=10),
                height=325,
                width=580
            )
            nombre_html = nombre_archivo + ".html"
            nombre_html = os.path.join('static', nombre_html)
            pio.write_html(fig, file=nombre_html, auto_open=False, config={'displayModeBar': False})
            print(f"Mapa de calor guardado como {nombre_html}")


            plt.figure(figsize=(10, 6))
            plt.pcolormesh(lon_bins[:-1], lat_bins[:-1], heatmap.T, shading='auto', cmap='inferno', norm=Normalize(vmin=0, vmax=np.max(heatmap)))
            plt.colorbar(label='Número de Conexiones')
            plt.xlabel('Longitud')
            plt.ylabel('Latitud')
            plt.title('Mapa de Calor de Conexiones por Estación Base', fontsize=16)
            plt.savefig(os.path.join('descargas', f"{nombre_archivo}.png"))
            plt.close()

            print(f"Mapa de calor guardado como {nombre_archivo}.png")
        except Exception as e:
            print(f"Error al generar el mapa de calor: {e}")
    else:
        print("No hay suficientes datos para generar el mapa de calor.")


def generar_mapa_calor_distribucion(lista_estaciones, nombre_archivo):
    """Genera un mapa de calor interactivo (html) y otro igual que se guarda en un archivo PNG """
    # Se obtiene las coordenadas de latitud y longitud de las estaciones base
    latitudes = []
    longitudes = []

    for estacion in lista_estaciones:
        latitudes.append(estacion.latitud)
        longitudes.append(estacion.longitud)
    
    if len(latitudes) > 1 and len(longitudes) > 1:
        try:
            num_celdas = 50 
            lat_bins, lon_bins, heatmap = contar_conexiones_por_celda(latitudes, longitudes, num_celdas)
            
            fig = px.imshow(heatmap.T, x=lon_bins[:-1], y=lat_bins[:-1], color_continuous_scale='Inferno', labels={'color':'Número de Estaciones Base'})
            fig.update_layout(
                title='Mapa de Calor de Estaciones Base',
                title_font_size=11,
                title_x=0.5,
                title_xanchor='center',
                title_yanchor='top',
                xaxis_title='Longitud',
                xaxis_title_font_size=11,
                yaxis_title='Latitud',
                yaxis_title_font_size=11,
                margin=dict(l=10, r=10, t=20, b=10),
                height=325,
                width=580
            )
            nombre_html = nombre_archivo + ".html"
            nombre_html = os.path.join('static', nombre_html)
            pio.write_html(fig, file=nombre_html, auto_open=False, config={'displayModeBar': False})
            print(f"Mapa de calor guardado como {nombre_html}")

            plt.figure(figsize=(10, 6))
            plt.pcolormesh(lon_bins[:-1], lat_bins[:-1], heatmap.T, shading='auto', cmap='inferno')
            plt.colorbar(label='Número de Estaciones Base')
            plt.xlabel('Longitud')
            plt.ylabel('Latitud')
            plt.title('Mapa de Calor de Estaciones Base', fontsize=16)
            plt.savefig(os.path.join('descargas', f"{nombre_archivo}.png"))
            plt.close()

            print(f"Mapa de calor guardado como {nombre_archivo}.png")
        except Exception as e:
            print(f"Error al generar el mapa de calor: {e}")
    else:
        print("No hay suficientes datos para generar el mapa de calor.")     