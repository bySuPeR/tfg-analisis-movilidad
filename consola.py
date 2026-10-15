
from sklearn.neighbors import BallTree
from haversine import haversine
import requests
from datetime import datetime
from geopy.distance import geodesic

def obtener_opcion_valida(opciones, mensaje):
    """Comprueba si se ha escogido una opción válida entre las opciones. En caso negativo, devuelve un mensaje de error."""
    while True:
        opcion = input(mensaje).strip().lower()
        if opcion in opciones:
            return opcion
        else:
            print(f"Opción no válida. Por favor, elige entre las siguientes opciones: {', '.join(opciones)}.")


def obtener_nombre_ciudad():
    """Pide al usuario el nombre de la ciudad del estudio. En caso de estar vacía la respuesta, la pide de nuevo."""
    while True:
        nombre_ciudad = input("Introduce el nombre de la ciudad de estudio: ").strip()
        if nombre_ciudad:
            return nombre_ciudad
        else:
            print("El nombre de la ciudad no puede estar vacío. Inténtalo de nuevo.")


def obtener_fecha(mensaje):
    """Pide al usuario la fecha para las rutas de los taxi. En caso de no seguir el formato especificado, la pide de nuevo."""
    while True:
        dia = input(mensaje).strip()
        try:
            datetime.strptime(dia, "%Y-%m-%d")
            return dia
        except ValueError:
            print("Formato de fecha no válido. Por favor, sigue el formato YYYY-MM-DD.")

def obtener_hora(mensaje):
    """Pide al usuario la hora para las rutas de los taxi. En caso de no seguir el formato especificado, la pide de nuevo."""
    while True:
        hora = input(mensaje).strip()
        try:
            datetime.strptime(hora, "%H:%M:%S")
            return hora
        except ValueError:
            print("Formato de hora no válido. Por favor, sigue el formato HH:MM:SS.")

def obtener_sugerencias_ciudades(nombre_ciudad):
    """Devuelve 4 sugerencias de ciudades respecto a lo escrito anteriormente por el usuario. Para estas sugerencias se realiza una solicitud a la API de Geonaames."""
    url = "http://api.geonames.org/searchJSON"
    params = {
        "q": nombre_ciudad,
        "maxRows": 4,
        "username": "martingb" 
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('geonames', [])
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return []

def mostrar_sugerencias(sugerencias):
    """Muestra al usuario las sugerencias devueltas por la API de Geonames en un formato concreto."""
    for i, sugerencia in enumerate(sugerencias, start=1):
        nombre = sugerencia.get('name', 'N/A')
        pais = sugerencia.get('countryName', 'N/A')
        latitud = sugerencia.get('lat', 'N/A')
        longitud = sugerencia.get('lng', 'N/A')
        print(f"{i}. {nombre}, {pais} (Lat: {latitud}, Lon: {longitud})")

def seleccionar_ciudad(sugerencias):
    """Pide al usuario que seleccione una sugerencia. En caso de no seleccionarla correctamente, lo pide de nuevo."""
    while True:
        try:
            seleccion = int(input("Selecciona el número de la ciudad correcta: ").strip())
            if 1 <= seleccion <= len(sugerencias):
                return sugerencias[seleccion - 1]
            else:
                print("Selección no válida. Inténtalo de nuevo.")
        except ValueError:
            print("Entrada no válida. Por favor, introduce un número.")


def construir_ball_trees_por_tipo(lista_estaciones):
    """Construye un árbol distinto de tipo BallTree por cada tipo de estaciones base que se estudia. A cada árbol creado, se le añaden todas las estaciones de ese tipo."""
    estaciones_por_tipo = {}
    
    for estacion in lista_estaciones:
        if estacion.tipoRadio not in estaciones_por_tipo:
            estaciones_por_tipo[estacion.tipoRadio] = []
        estaciones_por_tipo[estacion.tipoRadio].append(estacion)
    
    ball_trees = {}
    for tipo, estaciones in estaciones_por_tipo.items():
        puntos = [(estacion.latitud, estacion.longitud) for estacion in estaciones]
        ball_trees[tipo] = BallTree(puntos, metric=haversine)
    
    return ball_trees, estaciones_por_tipo

def encontrar_estaciones_mas_cercanas_por_tipo_ball_tree(ball_trees, estaciones_por_tipo, latitud, longitud):
    """Devuelve la estación más cercana a unas coordenadas pasadas por parametro."""
    estaciones_cercanas = {}
    for tipo, ball_tree in ball_trees.items():
        distancia_km, indice = ball_tree.query([(latitud, longitud)], k=1)
        distancia_metros = distancia_km[0] * 1000  # Se convierte de kilómetros a metros
        indice = int(indice)  # Se convierte el índice en un entero
        estacion_cercana_objeto = estaciones_por_tipo[tipo][indice]
        estaciones_cercanas[tipo] = {
            'TipoRadio': tipo,
            'ID': estacion_cercana_objeto.cellID,
            'Distancia': round(float(distancia_metros), 2)  # Se redondea la distancia a dos decimales
        }
    return estaciones_cercanas



def calcular_distancia_geodesica(lat1, lon1, lat2, lon2):
    """Calcula la distancia geodesica de dos puntos pasados por parametros (latitud y longitud)."""
    punto1 = (lat1, lon1)
    punto2 = (lat2, lon2)
    distancia = geodesic(punto1, punto2).meters
    return distancia






