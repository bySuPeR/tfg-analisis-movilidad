import folium
from folium.plugins import HeatMap
from estacionBase import obtener_estacion_por_id_y_cercania


def crear_mapa_calor(mapa,listaEstaciones,puntos):
    """Genera un mapa de calor interactivo como una nueva capa de información en el mapa de Folium. Este mapa de calor se adapta al zoom actual del usuario. """
    print("mapa Calor")
    # Se crea un objeto de mapa de Folium centrado en una ubicación específica
    mapa_calor = folium.FeatureGroup(name='Mapa de Uso de Estaciones Base', show=False)
 
    # Se crea una lista de tuplas (latitud, longitud, peso) para HeatMap
    heat_data = []
    for punto in puntos:
        lat_punto, lon_punto = punto['Latitud'], punto['Longitud']
        for antena_cercana in punto['AntenasCercanas']:
            # Obtiene las coordenadas de la antena
            antena_id = antena_cercana['ID']
            print("Antena id: ",antena_id)
            antena = obtener_estacion_por_id_y_cercania(antena_id, lat_punto, lon_punto,listaEstaciones)  # Debes implementar esta función para obtener la antena por su ID
            print("Antena: ",antena)
            lat_antena, lon_antena = antena.latitud, antena.longitud
            heat_data.append((lat_antena, lon_antena, 1))

    # Se agrega HeatMap al mapa
    HeatMap(heat_data).add_to(mapa_calor)
    mapa_calor.add_to(mapa)

    # Guardar el mapa como un archivo HTML o visualizar en Jupyter Notebook
    return mapa


