import requests
from geopy.distance import distance
import requests
from geopy.distance import geodesic

def crear_solicitud_meli_desde_puntos(df_viaje, modo):
    """
    Genera el cuerpo de la solicitud para Meili a partir de un DataFrame de puntos.
    
    Parámetros:
    df_viaje (DataFrame): DataFrame que contiene los puntos de la ruta en formato latitud y longitud.
    modo (int): El modo de transporte. Puede ser 1 para taxi o 2 para peatón.
    
    Retorna:
    str: Cuerpo de la solicitud en formato JSON para Meili.
    """
    coordenadas_meili = df_viaje.to_json(orient='records')
    encabezado_meili = '{"shape":'

    if modo == 1:
        pie_meili = ""","search_radius": 150, "shape_match":"map_snap", "costing":"taxi", "format":"osrm"}"""
    elif modo == 2:
        pie_meili = ""","search_radius": 150,"shape_match": "map_snap","costing": "pedestrian", "format": "osrm"}"""
    
    cuerpo_solicitud_meili = encabezado_meili + coordenadas_meili + pie_meili
    return cuerpo_solicitud_meili

def obtener_mejor_ruta_mapbox(punto1, punto2, token_acceso, modo):
    """
    Obtiene la mejor ruta entre dos puntos utilizando la API de Mapbox.
    
    Parámetros:
    punto1 (tuple): Coordenadas del primer punto (latitud, longitud).
    punto2 (tuple): Coordenadas del segundo punto (latitud, longitud).
    token_acceso (str): Token de acceso para la API de Mapbox.
    modo (int): El modo de transporte. Puede ser 1 para taxi/ciclismo o 2 para peatón.
    
    Retorna:
    list: La mejor ruta (lista de coordenadas) basada en el perfil y las condiciones de la ruta.
    """
    if modo == 1:
        perfiles = ['cycling', 'driving']
    elif modo == 2:
        perfiles = ['walking']
    
    info_rutas = []

    for perfil in perfiles:
        url = f"https://api.mapbox.com/directions/v5/mapbox/{perfil}/{punto1[1]},{punto1[0]};{punto2[1]},{punto2[0]}?geometries=geojson&alternatives=true&access_token={token_acceso}"
        respuesta = requests.get(url)
        
        if respuesta.status_code == 200:
            rutas = respuesta.json()['routes']
            for ruta in rutas:
                coordenadas_ruta = [(lat, lon) for lon, lat in ruta['geometry']['coordinates']]
                distancia_a_destino = geodesic(punto2, coordenadas_ruta[-1]).meters
                info_rutas.append((perfil, coordenadas_ruta, len(coordenadas_ruta), distancia_a_destino))
        else:
            print(f"Error ({perfil}): {respuesta.status_code}, {respuesta.text}")
    
    if info_rutas:
        # Se ordena las rutas primero por longitud y luego por distancia al destino
        info_rutas.sort(key=lambda x: (x[2], x[3]))
        mejor_ruta = info_rutas[0][1]
        
        print(f"Mejor perfil de ruta: {info_rutas[0][0]}")
        print(f"Longitud de la ruta: {info_rutas[0][2]}, Distancia al punto2: {info_rutas[0][3]}")
        return mejor_ruta
    else:
        return []


