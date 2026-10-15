import folium 
from folium.plugins import MarkerCluster
from geopy.distance import geodesic
import json
from estacionBase import obtener_estacion_por_id_y_cercania
from estacionBase import EstacionBase

grid_tam_lat=0.0
grid_tam_lon=0.0
casillas_antenas = {}
puntos_taxis = []
marcadores_estaciones = []
ruta_taxi = {}
diccionarioMarcadoresTaxi={}
popUpTaxi={}

puntos_humanos  = []
diccionarioMarcadoresHumanos = {}
popUpHumanos =  {}









def crear_mapa(lat,lon,zoom):
    global casillas_antenas, puntos_taxis, marcadores_estaciones, ruta_taxi, diccionarioMarcadoresTaxi, popUpTaxi, puntos_humanos, puntos_humanos, diccionarioMarcadoresHumanos, popUpHumanos

    casillas_antenas.clear()
    puntos_taxis.clear()
    marcadores_estaciones.clear()
    ruta_taxi.clear()
    diccionarioMarcadoresTaxi.clear()
    popUpTaxi.clear()

    puntos_humanos.clear()
    diccionarioMarcadoresHumanos.clear()
    popUpHumanos.clear()

    """Crea el mapa base en folium con las coordenadas dadas por parámetros"""
    map_osm = folium.Map(location=[lat, lon], zoom_start=zoom, tiles=None)
    folium.TileLayer('OpenStreetMap', name='Mapa Base').add_to(map_osm)
    return map_osm




def definir_cuadricula_mapa():
    """Define el tamaño de cuadrículas en el que se divide el mapa"""
    global grid_tam_lat
    global grid_tam_lon
    grid_tam_lat = 0.01  # Tamaño de la casilla en grados de latitud
    grid_tam_lon = 0.01  # Tamaño de la casilla en grados de longitud

def estacionesEnCuadriculas(listaEstaciones):
    """Posiciona las estaciones base en cada cuadrícula"""
    definir_cuadricula_mapa()
    global casillas_antenas
    for antena in listaEstaciones:
        lat_antena, lon_antena = antena.latitud, antena.longitud
        casilla_lat = int(lat_antena / grid_tam_lat)
        casilla_lon = int(lon_antena / grid_tam_lon)
        casillas_antenas.setdefault((casilla_lat, casilla_lon), []).append(antena)


def antenasCercanasTaxi(listaTaxis,listaEstaciones,banderaMapa):
    """Calcula las antenas cercanas a cada taxi y las añade a su pop-up del mapa interactivo"""
    i=0
    for taxi in listaTaxis:
        if(banderaMapa):
            contenidoPopUp = f"""<div style="font-size: 16px; text-align: center; white-space: nowrap; line-height: 1.">
                <img src="../static/taxi.png" alt="Imagen de Taxi" width="16" height="16"> {taxi.señalTaxi}<br>Latitud: {taxi.latitud} </b><br>Longitud: {taxi.longitud}</b><br>Dia: {taxi.dia}</b><br>Hora: {taxi.hora}</b><br>"""
        lat_taxi, lon_taxi = taxi.latitud, taxi.longitud
        global casillas_antenas
        global puntos_taxis
        global diccionarioMarcadoresTaxi
        global popUpTaxi
        if(banderaMapa):
            contenidoPopUp += popUpTaxi[taxi.señalTaxi]
        
        casilla_lat_taxi = int(lat_taxi / grid_tam_lat)
        casilla_lon_taxi = int(lon_taxi / grid_tam_lon)
        antenas_casilla = casillas_antenas.get((casilla_lat_taxi, casilla_lon_taxi), [])
        if not antenas_casilla:
            antenas_casilla = listaEstaciones
        # Calcular distancias solo con las antenas en la misma casilla
        distancias_antenas = {}
        for antena in antenas_casilla:
            lat_antena, lon_antena = antena.latitud, antena.longitud
            distancia = geodesic((lat_taxi, lon_taxi), (lat_antena, lon_antena)).meters
            distancias_antenas.setdefault(antena.tipoRadio, []).append((distancia, antena))

        for tipo_radio, antenas in distancias_antenas.items():
            if antenas:
                antenas_ordenadas = sorted(antenas, key=lambda x: x[0])
                distancia_antena_cercana, antena_cercana = antenas_ordenadas[0]
                if(banderaMapa):
                    contenidoPopUp += f"""<br> {tipo_radio} - ID: {antena_cercana.cellID} - {distancia_antena_cercana:.2f} metros"""
                puntos_taxis[i]['AntenasCercanas'].append({
                    'TipoRadio': tipo_radio,
                    'ID': antena_cercana.cellID,
                    'Distancia': round(distancia_antena_cercana, 2),
                })
        if(banderaMapa):
            contenidoPopUp += "</div>"  
            folium.Popup(contenidoPopUp).add_to(diccionarioMarcadoresTaxi[taxi.señalTaxi]) 
        i+=1     

def colocarTaxisMapa(listaTaxis,map_osm,banderaMapa):
    """Coloca el marcador de cada taxi con su pop-up en el mapa interactivo. Adicionalmente rellena parte de un diccionario con información de los taxis"""
    puntos_taxisMapa = folium.FeatureGroup(name='Taxis', show=False)
    global puntos_taxis
    global ruta_taxi
    global diccionarioMarcadoresTaxi
    global popUpTaxi
    for taxi in listaTaxis:
        lat_taxi, lon_taxi = taxi.latitud, taxi.longitud
        
        
        puntos_taxis.append({
            'ID del taxi': taxi.idTaxi,
            'SeñalTaxi': taxi.señalTaxi,
            'Latitud': taxi.latitud,
            'Longitud': taxi.longitud,
            'Dia': taxi.dia,
            'Hora': taxi.hora,
            'AntenasCercanas': []
        })
        idTaxi = taxi.idTaxi
        if idTaxi not in ruta_taxi:
            ruta_taxi[idTaxi] = []
        ruta_taxi[idTaxi].append((lat_taxi, lon_taxi))
        if(banderaMapa):
            contenidoPopUp=""
            if len(ruta_taxi[idTaxi]) == 1:
                contenidoPopUp = f"<br>ID del taxi: {idTaxi}"
            marcador=folium.CircleMarker(location=[lat_taxi, lon_taxi], radius=5, color='blue', fill=True, fill_color='blue').add_to(puntos_taxisMapa)
            diccionarioMarcadoresTaxi[taxi.señalTaxi] = marcador
            popUpTaxi[taxi.señalTaxi]= contenidoPopUp
    puntos_taxisMapa.add_to(map_osm)
    return map_osm


def crearJSONTaxis():
    """Crea el JSON con la información de los taxis"""
    global puntos_taxis
    with open('Taxi.json', 'w') as json_file:
        json.dump(puntos_taxis, json_file)







def colocarHumanosMapa(listaHumanos, map_osm):
    """Coloca el marcador de cada humano con su pop-up en el mapa interactivo. Adicionalmente rellena parte de un diccionario con información de las señales humanas"""
    puntos_humanosMapa = folium.FeatureGroup(name='Humanos', show=False)
    global puntos_humanos
    global diccionarioMarcadoresHumanos
    global popUpHumanos
    for humano in listaHumanos:
        lat_humano, lon_humano = humano.latitud, humano.longitud
        
        puntos_humanos.append({
            'Número Señal': humano.señalHumano,
            'ID del humano': humano.idHumano,
            'Latitud': lat_humano,
            'Longitud': lon_humano,
            'AntenasCercanas': []
        })
        
        marcador = folium.CircleMarker(location=[lat_humano, lon_humano], radius=5, color='royalblue', fill=True, fill_color='red').add_to(puntos_humanosMapa)
        diccionarioMarcadoresHumanos[humano.señalHumano] = marcador
    
    puntos_humanosMapa.add_to(map_osm)
    return map_osm


def crearJSONHumanos():
    """Crea el JSON con la información de los humanos"""
    global puntos_humanos
    with open('Humanos.json', 'w') as json_file:
        json.dump(puntos_humanos, json_file)


def antenasCercanasHumanos(listaHumanos, listaEstaciones):
    """Calcula las antenas cercanas a cada señal humana y las añade a su pop-up del mapa interactivo"""
    i=0
    global casillas_antenas
    for humano in listaHumanos:

        contenidoPopUp = f"""<div style="font-size: 16px; text-align: center; white-space: nowrap; line-height: 1."> <img src="../static/humano.png" alt="Imagen de Humano" width="25" height="28"><b>ID: {humano.idHumano}</b><br>Señal Humano: {humano.señalHumano}</b><br>Tiempo: {humano.tiempo}s </b><br>Latitud: {humano.latitud} </b><br>Longitud: {humano.longitud}</b><br>"""
        lat_humano, lon_humano = humano.latitud, humano.longitud
        casilla_lat_humano = int(lat_humano / grid_tam_lat)
        casilla_lon_humano = int(lon_humano / grid_tam_lon)
        antenas_casilla = casillas_antenas.get((casilla_lat_humano, casilla_lon_humano), [])
        if not antenas_casilla:
            antenas_casilla = listaEstaciones
        # Calcular distancias solo con las antenas en la misma casilla
        distancias_antenas = {}
        for antena in antenas_casilla:
            lat_antena, lon_antena = antena.latitud, antena.longitud
            distancia = geodesic((lat_humano, lon_humano), (lat_antena, lon_antena)).meters
            distancias_antenas.setdefault(antena.tipoRadio, []).append((distancia, antena))
        for tipo_radio, antenas in distancias_antenas.items():
            if antenas:
                antenas_ordenadas = sorted(antenas, key=lambda x: x[0])
                distancia_antena_cercana, antena_cercana = antenas_ordenadas[0]
                contenidoPopUp += f"<br> {tipo_radio} - ID: {antena_cercana.cellID} - {distancia_antena_cercana:.2f} metros"

                puntos_humanos[i]['AntenasCercanas'].append({
                    'TipoRadio': tipo_radio,
                    'ID': antena_cercana.cellID,
                    'Distancia': round(distancia_antena_cercana, 2),
                })
            contenidoPopUp += "</div>"  
            folium.Popup(contenidoPopUp).add_to(diccionarioMarcadoresHumanos[humano.señalHumano]) 
        i=i+1

def rellenarEstacionesBases(i,antena):
    """Rellena parte de un diccionario con información de una estación base"""
    marcadores_estaciones.append({
        'codEB': i,
        'Latitud': antena.latitud,
        'Longitud': antena.longitud,
        'TipoRadio': antena.tipoRadio,
        'MCC': antena.mcc,
        'MNC': antena.mnc,
        'LAC': antena.lac,
        'ID': antena.cellID,
        'Unit':antena.unit,
        'Rango': antena.rango,
        'Samples': antena.samples,
        'Changeables': antena.changeables,
        'Created': antena.created,
        'Updated': antena.updated,
        'AverageSignal': antena.averageSignal
    })

def rellenarEstacionesBasesModoConsola(listaEstaciones):
    """Recorre la lista de estaciones base y llama al método para rellenar el diccionario correspondiente"""
    i=1
    for antena in listaEstaciones:
        rellenarEstacionesBases(i,antena)
        i=i+1




def crear_clusters_dinamicos(mapa,listaEstaciones,banderaMapa):
    """Crea clusters dinámicos para ir agrupando las estaciones base dependiendo del zoom que haga el usuario en el mapa interactivo"""
    capaCluster = folium.FeatureGroup(name="Estaciones Base", show=False).add_to(mapa)

    marcador_cluster = MarkerCluster().add_to(capaCluster)
    i=1
    for antena in listaEstaciones:
        if(banderaMapa):
            latitud = antena.latitud
            longitud = antena.longitud
            contenidoPopUp = f"""<div style="font-size: 16px; text-align: center; white-space: nowrap; line-height: 1;"> <img src="../static/estacion.png" alt="Imagen de Estacion Base" width="25" height="28"> <b>EstacionBase: {i}</b><br>Latitud: {antena.latitud}</b><br>Longitud: {antena.longitud}
                <br>Tipo: {antena.tipoRadio}<br>CellID: {antena.cellID}"""

            if isinstance(antena, EstacionBase):
                contenidoPopUp += f"""<br>MCC: {antena.mcc}<br>MNC: {antena.mnc}<br>LAC: {antena.lac}
                                    <br>Unit: {antena.unit}<br>Rango: {antena.rango}
                                    <br>Samples: {antena.samples}<br>Changeables: {antena.changeables}
                                    <br>Created: {antena.created}<br>Updated: {antena.updated}
                                    <br>AverageSignal: {antena.averageSignal}</div>"""
            else:
                contenidoPopUp += "</div>"
            folium.Marker(location=[latitud, longitud], icon=folium.Icon(color='red'),popup=contenidoPopUp).add_to(marcador_cluster)

        marcador = {
            'codEB': i,
            'Latitud': antena.latitud,
            'Longitud': antena.longitud,
            'TipoRadio': antena.tipoRadio,
            'ID': antena.cellID
        }

        if isinstance(antena, EstacionBase):
            marcador.update({
                'MCC': antena.mcc,
                'MNC': antena.mnc,
                'LAC': antena.lac,
                'Unit': antena.unit,
                'Rango': antena.rango,
                'Samples': antena.samples,
                'Changeables': antena.changeables,
                'Created': antena.created,
                'Updated': antena.updated,
                'AverageSignal': antena.averageSignal
            })

            marcadores_estaciones.append(marcador)
        i=i+1
    crearJSONEstacionesBases(marcadores_estaciones)
    # Recorre todos los marcadores en el cluster
    markers = list(marcador_cluster._children)
    if(banderaMapa):
        for i, marker in enumerate(markers):
            if hasattr(marker, 'location'):
                latitud_marker, longitud_marker = marker.location
                cluster_cercano = None
                distancia_minima = float('inf')

                # Recorre los clusters existentes para encontrar el más cercano
                for cluster in marcador_cluster._children[:i]:
                    if hasattr(cluster[0], 'location'):
                        latitud_cluster, longitud_cluster = cluster[0].location

                        # Calcula la distancia entre el marcador y el centro del cluster
                        distancia = geodesic((latitud_marker, longitud_marker), (latitud_cluster, longitud_cluster)).meters

                        if distancia < distancia_minima:
                            distancia_minima = distancia
                            cluster_cercano = cluster

                # Mueve el marcador al cluster más cercano
                if cluster_cercano:
                    cluster_cercano.add_child(marker)

    return mapa





def crearJSONEstacionesBases(marcadores_estaciones):
    """Crea el JSON con la información de las estaciones base"""
    with open('EstacionBase.json', 'w') as json_file:
        json.dump(marcadores_estaciones, json_file)





def crear_capa_lineas_entre_dispositivo_y_estaciones_base(mapa_osm,listaEstaciones, tipoMovilidad):
    """Crea una nueva capa de información en el mapa interactivo que recoge la estación más cercana a la señal de la movilidad estudiada (dispositivo)"""
    lineas_feature_group = folium.FeatureGroup(name='Conexiones Dispositivo - Estación', show=False)
    if(tipoMovilidad=="humana"):
        global puntos_humanos
        puntos=puntos_humanos
    elif (tipoMovilidad=="taxi"):
        global puntos_taxis
        puntos=puntos_taxis
    # Recorre cada taxi en puntos_taxis
    for punto in puntos:
        # Obtiene las coordenadas del taxi
        lat_punto, lon_punto = punto['Latitud'], punto['Longitud']
        
        # Recorre cada antena cercana al taxi
        for antena_cercana in punto['AntenasCercanas']:
            # Obtiene las coordenadas de la antena
            antena_id = antena_cercana['ID']
            print("Antena id: ",antena_id)
            antena = obtener_estacion_por_id_y_cercania(antena_id, lat_punto, lon_punto,listaEstaciones)
            print("Antena: ",antena)
            lat_antena, lon_antena = antena.latitud, antena.longitud
            
            # Crea una línea entre el taxi y la antena en el mapa
            linea = folium.PolyLine([(lat_punto, lon_punto), (lat_antena, lon_antena)],color='fuchsia',  dash_array=[10, 5])
            linea.add_to(lineas_feature_group)
    lineas_feature_group.add_to(mapa_osm)

    return mapa_osm, puntos





