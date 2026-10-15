import estacionBase
import opencellid
import mapa
import argparse
import folium
from subprocess import Popen
import os
import movilidad
import mapaCalor
import consola
import archivo
import graficas
import warnings
import sys
warnings.filterwarnings("ignore", category=DeprecationWarning)

def procesar_datos(tipoMovilidad,archivoMovilidad, diaMin,diaMax, horaMin, horaMax, tipo_antena, tipoUso, archivoEstaciones,extensionEst, ciudad, latitudCiudad,longitudCiudad):

    lista_graficas=[]
    lista_simulacion=[]
    estaciones_json = []
    archivo.recrear_carpeta('descargas')
    if(tipoUso=="subida"):
        longitudMax=longitudCiudad+0.3
        longitudMin=longitudCiudad-0.3
        latitudMax=latitudCiudad+0.3
        latitudMin=latitudCiudad-0.3
        if(extensionEst==".gz"):
            listaEstaciones = estacionBase.leerArchivoEstacionesBases(tipo_antena, archivoEstaciones.filename,longitudMax,longitudMin,latitudMax,latitudMin)
            print(len(listaEstaciones))
            estacionBase.guardarEstacionesProcesadas(listaEstaciones)
            print("Estaciones guardadas")  
            lista_simulacion.append("estacionesBases.csv")
               
        else:
            listaEstaciones = estacionBase.procesarEstaciones(archivoEstaciones.filename,tipo_antena,longitudMax,longitudMin,latitudMax,latitudMin)
            print(len(listaEstaciones))
            estacionBase.guardarEstacionesProcesadas(listaEstaciones)
            print("Estaciones guardadas")  
            lista_simulacion.append("estacionesBases.csv")
        for estacion in listaEstaciones:
            estacion_json = {
            'ID': estacion.cellID,
            'Latitud': estacion.latitud,
            'Longitud': estacion.longitud,
            'Tipo de Radio': estacion.tipoRadio,
            'MCC': estacion.mcc,
            'MNC': estacion.mnc,
            'LAC': estacion.lac
            }
            estaciones_json.append(estacion_json)
            



    elif (tipoUso=="api"):
         #aqui conecta con la api
        url = "http://opencellid.org/cell/getInArea"
        latitudMin = latitudCiudad-0.05
        latitudMax = latitudCiudad+0.05
        longitudMin = longitudCiudad-0.05
        longitudMax = longitudCiudad+0.05
        total_celdas = opencellid.calcular_total_celdas(latitudMin,latitudMax,longitudMin,longitudMax)
        print(total_celdas)
        listaEstaciones=opencellid.escribir_estaciones_base_csv(url, "estaciones_base.csv", total_celdas, latitudMin,latitudMax,longitudMin,longitudMax,tipo_antena)
        print(len(listaEstaciones))
        lista_simulacion.append("estaciones_base.csv")
        for estacion in listaEstaciones:
            estacion_json = {
            'ID': estacion.cellID,
            'Latitud': estacion.latitud,
            'Longitud': estacion.longitud,
            'Tipo de Radio': estacion.tipoRadio,
            }
            estaciones_json.append(estacion_json)
    
    if not listaEstaciones:
        print(("Error: La lista de estaciones está vacía. Terminando el programa."))
        sys.exit(0)         
    archivo.guardar_datos_en_archivo(estaciones_json, 'EstacionesBase.json')
    lista_simulacion.append("EstacionesBase.json")

    mapa_osm = mapa.crear_mapa(latitudCiudad,longitudCiudad, 14)
    print("Mapa inicial creado")
    mapa.estacionesEnCuadriculas(listaEstaciones)
    print("Cuadriculas creadas")
    
    mapa_osm= mapa.crear_clusters_dinamicos(mapa_osm,listaEstaciones,banderaMapa=True)
    print("Clusters Estaciones creados")

    

    if(tipoMovilidad=="humana"):
        listaHumanos = movilidad.leer_datos_desde_csv(archivoMovilidad.filename)
        movilidad.guardar_datos_en_csv(listaHumanos)
        lista_simulacion.append("datosHumanos.csv")
        mapa_osm=mapa.colocarHumanosMapa(listaHumanos, mapa_osm)
        print("Humanos colocados")
        mapa.antenasCercanasHumanos(listaHumanos, listaEstaciones)
        rutas= movilidad.crearRutasHumanos(listaHumanos)
        print("Rutas creadas")
        mapa_osm, rutas_json=movilidad.colocarRutas(rutas, mapa_osm, 2)  #2 es para Humanos
        print("Rutas colocadas")
        archivo.guardar_datos_en_archivo(rutas_json, nombre_archivo="rutas.json")
        lista_simulacion.append("rutas.json")


        mapa.crearJSONHumanos()
        mapa_osm,puntos_humanos = mapa.crear_capa_lineas_entre_dispositivo_y_estaciones_base(mapa_osm,listaEstaciones,tipoMovilidad)
        archivo.guardar_datos_en_archivo(puntos_humanos, nombre_archivo='Humanos.json')
        lista_simulacion.append("Humanos.json")
        mapa_osm=mapaCalor.crear_mapa_calor(mapa_osm,listaEstaciones, puntos_humanos)
        puntos=puntos_humanos
        
    elif(tipoMovilidad=="taxi"):
        listaTaxis = movilidad.leerArchivoTaxi(diaMin, diaMax,horaMin, horaMax, archivoMovilidad.filename)
        movilidad.guardarTaxisProcesados(listaTaxis) 
        lista_simulacion.append("taxis.csv")
        print("taxis guardados")
        print(len(listaTaxis))
        mapa_osm=mapa.colocarTaxisMapa(listaTaxis,mapa_osm,True)
        print("Taxis colocados")
        mapa.antenasCercanasTaxi(listaTaxis,listaEstaciones, True)
        print("Antenas cercanas calculadas")
        rutas= movilidad.crearRutasTaxis(listaTaxis)
        print("Rutas creadas")
        mapa_osm, rutas_json=movilidad.colocarRutas(rutas, mapa_osm, 1)  #1 es para Taxis
        print("Rutas colocadas")
        archivo.guardar_datos_en_archivo(rutas_json, nombre_archivo="rutas.json")
        lista_simulacion.append("rutas.json")


        mapa.crearJSONTaxis()
        print("JSON Taxis creados")
        mapa_osm,puntos_taxis = mapa.crear_capa_lineas_entre_dispositivo_y_estaciones_base(mapa_osm,listaEstaciones, tipoMovilidad)
        archivo.guardar_datos_en_archivo(puntos_taxis, nombre_archivo='Taxi.json')
        lista_simulacion.append("Taxi.json")
        mapa_osm=mapaCalor.crear_mapa_calor(mapa_osm,listaEstaciones, puntos_taxis)
        puntos=puntos_taxis
        contador_dias=graficas.contar_conexiones_por_dia(puntos)
        contador_horas=graficas.contar_conexiones_por_hora(puntos)
        contador_mes=graficas.contar_conexiones_por_mes(puntos)
        contador_estacionesAño=graficas.contar_conexiones_por_estacionAño(puntos)
        graficas.generar_grafico_area_conexiones_por_dia(contador_dias, "Distribución_de_Conexiones_Semanales")
        graficas.generar_grafico_area_conexiones_por_hora(contador_horas, "Distribución_de_Conexiones_por_Hora")
        graficas.generar_grafico_area_conexiones_por_mes(contador_mes, "Distribución_de_Conexiones_por_Mes")
        graficas.generar_grafico_area_conexiones_por_estacion(contador_estacionesAño, "Distribución_de_Conexiones_por_Estación")
        lista_simulacion.append("Distribución_de_Conexiones_Semanales.html")
        lista_simulacion.append("Distribución_de_Conexiones_por_Hora.html")
        lista_simulacion.append("Distribución_de_Conexiones_por_Mes.html")
        lista_simulacion.append("Distribución_de_Conexiones_por_Estación.html")
        lista_graficas.append("Distribución_de_Conexiones_Semanales.png")
        lista_graficas.append("Distribución_de_Conexiones_por_Hora.png")
        lista_graficas.append("Distribución_de_Conexiones_por_Mes.png")
        lista_graficas.append("Distribución_de_Conexiones_por_Estación.png")
        


    graficas.generar_mapa_calor_distribucion(listaEstaciones, nombre_archivo="Mapa_de_Estaciones_Base")
    contador_estaciones=graficas.contar_conexiones_por_estacion(puntos, listaEstaciones)
    graficas.generar_mapa_calor_conexiones(puntos,listaEstaciones, 'Mapa_Calor_de_Conexiones_Establecidas')
    graficas.generar_grafico_barras_conexiones_por_estacion(contador_estaciones, 'Conexiones_Totales_por_Estación')
    graficas.generar_grafico_top_50_estaciones(contador_estaciones, '50_Estaciones_con_Más_Conexiones')
    graficas.generar_grafico_distancia_media_top_50(contador_estaciones, puntos, 'Distancia_Media_de_Usuarios')
    lista_simulacion.append("Mapa_Calor_de_Conexiones_Establecidas.html")
    lista_graficas.append("Mapa_Calor_de_Conexiones_Establecidas.png")
    lista_simulacion.append("Mapa_de_Estaciones_Base.html")
    lista_graficas.append("Mapa_de_Estaciones_Base.png")
    lista_simulacion.append("Conexiones_Totales_por_Estación.html")
    lista_simulacion.append("50_Estaciones_con_Más_Conexiones.html")
    lista_simulacion.append("Distancia_Media_de_Usuarios.html")
    

    lista_graficas.append("Conexiones_Totales_por_Estación.png")
    lista_graficas.append("50_Estaciones_con_Más_Conexiones.png")
    lista_graficas.append("Distancia_Media_de_Usuarios.png")
 

    control_capas = folium.LayerControl()
    control_capas.add_to(mapa_osm)

    mapa_osm.save("static/mapa.html")
    print("Graficas generadas main:", lista_graficas)
    print("Archivos simulacion generadas main:", lista_simulacion)

    return lista_graficas, lista_simulacion
    
def preprocesarDatos():
    print("En primer lugar hay que escoger el tipo de movilidad que se quiere estudiar")
    tipoMovilidad = consola.obtener_opcion_valida(['taxis', 'humanos'], "¿Qué tipo de movilidad se quiere procesar? 'Taxis', 'Humanos': ")

    archivoMovilidad, extensionMov = archivo.obtener_ruta_archivo("CSV para cargar los datos sobre la movilidad", ["csv"])
    diaMin=diaMax=horaMin=horaMax=None
    if tipoMovilidad == "taxis":
        print("Para proporcionar los datos necesarios para el estudio, el sistema necesita la siguiente información sobre los taxis...")
        diaMin = consola.obtener_fecha("Una fecha mínima concreta para las rutas de los taxis siguiendo el formato YYYY-MM-DD: ")
        diaMax = consola.obtener_fecha("Una fecha máxima concreta para las rutas de los taxis siguiendo el formato YYYY-MM-DD: ")
        print("Ahora se debe especificar el intervalo de tiempo de estudio...")
        horaMin = consola.obtener_hora("Hora mínima siguiendo el formato HH:MM:SS: ")
        horaMax = consola.obtener_hora("Hora máxima siguiendo el formato HH:MM:SS: ")
    
    print("En segundo lugar se debe elegir la siguiente información sobre las estaciones base... ")
    tipoAnt = consola.obtener_opcion_valida(['gsm', 'umts', 'lte', 'todas'], "¿Qué tipo de estaciones base se quieres procesar? 'GSM', 'UMTS', 'LTE' o 'Todas': ")
    print(f"Estaciones base de tipo {tipoAnt.upper()} escogidas...")
    tipoUso = consola.obtener_opcion_valida(['api', 'archivo'], "¿Quieres utilizar la API de OpenCellID o subir un archivo para obtenerlas? 'API', 'Archivo': ")
    archivoEstaciones=extensionEst=None
    if tipoUso == "archivo":
        archivoEstaciones, extensionEst  = archivo.obtener_ruta_archivo("CSV o GZ para cargar los datos sobre las estaciones base", ["csv", "gz"])
    while True:
        nombre_ciudad = consola.obtener_nombre_ciudad()
        sugerencias =consola.obtener_sugerencias_ciudades(nombre_ciudad) 
        if sugerencias:
            print("Sugerencias de ciudades encontradas:")
            consola.mostrar_sugerencias(sugerencias)
            ciudad_seleccionada = consola.seleccionar_ciudad(sugerencias)
            latitudCiudad = float(ciudad_seleccionada.get('lat', 'N/A'))
            longitudCiudad = float(ciudad_seleccionada.get('lng', 'N/A'))
            print(f"Ciudad seleccionada: {ciudad_seleccionada.get('name', 'N/A')}, {ciudad_seleccionada.get('countryName', 'N/A')}")
            break
        else:
            print("No se encontraron sugerencias para la ciudad proporcionada.")

    return tipoMovilidad,archivoMovilidad, diaMin, diaMax, horaMin, horaMax, tipoAnt, tipoUso, archivoEstaciones,extensionEst, ciudad_seleccionada, latitudCiudad,longitudCiudad



if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description='Descripción de tu programa')
    parser.add_argument('modo', choices=['grafico', 'consola', 'preprocesarDatos'], help='Modo de ejecución: grafico, consola o preprocesarDatos')
    args = parser.parse_args()
    modo_ejecucion = args.modo


    if modo_ejecucion == 'grafico':    
        
        app_process = Popen(['python', 'app.py'])
        os.system("start http://localhost:8000/")
        pass
    elif modo_ejecucion == 'consola':
        opcion = input("¿Quieres cargar datos nuevos? Responde con 'si' o 'no'. En caso negativo se usarán los datos guardados: ")
        opcion = opcion.lower()
        while True:
            if opcion == "si":
                datos=preprocesarDatos()
                archivo.guardar_datos_en_archivo(datos)
            if opcion in ["si", "no"]:  
                if opcion == "no":
                    datos = archivo.cargar_datos_desde_archivo()
                    print("Datos anteriores: ",datos)
                if datos:
                    tipoMovilidad, archivoMovilidad, diaMin, diaMax, horaMin, horaMax, tipoAnt, tipoUso, archivoEstaciones, extensionEst, ciudad_seleccionada, latitudCiudad, longitudCiudad = datos
                    lista_graficas=[]
                    lista_simulacion=[]
                    estaciones_json = []
                    archivo.recrear_carpeta('descargas')
                    if(tipoUso=="archivo"):
                        longitudMax=longitudCiudad+0.3
                        longitudMin=longitudCiudad-0.3
                        latitudMax=latitudCiudad+0.3
                        latitudMin=latitudCiudad-0.3
                        if(extensionEst=="gz"):
                            listaEstaciones = estacionBase.leerArchivoEstacionesBases(tipoAnt, archivoEstaciones,longitudMax,longitudMin,latitudMax,latitudMin)
                            print(len(listaEstaciones))
                            estacionBase.guardarEstacionesProcesadas(listaEstaciones)
                            print("Estaciones guardadas")  
                            lista_simulacion.append("estacionesBases.csv")
                            
                        elif (extensionEst=="csv"):
                            estaciones_json = []
                            listaEstaciones = estacionBase.procesarEstaciones(archivoEstaciones,tipoAnt,longitudMax,longitudMin,latitudMax,latitudMin)
                            print(len(listaEstaciones))
                            estacionBase.guardarEstacionesProcesadas(listaEstaciones)
                            print("Estaciones guardadas")  
                            lista_simulacion.append("estacionesBases.csv")
                        for estacion in listaEstaciones:
                            estacion_json = {
                                'ID': estacion.cellID,
                                'Latitud': estacion.latitud,
                                'Longitud': estacion.longitud,
                                'Tipo de Radio': estacion.tipoRadio,
                                'MCC': estacion.mcc,
                                'MNC': estacion.mnc,
                                'LAC': estacion.lac
                            }
                            estaciones_json.append(estacion_json)

                    elif (tipoUso=="api"):
                        url = "http://opencellid.org/cell/getInArea"
                        latitudMin = latitudCiudad-0.05
                        latitudMax = latitudCiudad+0.05
                        longitudMin = longitudCiudad-0.05
                        longitudMax = longitudCiudad+0.05
                        total_celdas = opencellid.calcular_total_celdas(latitudMin,latitudMax,longitudMin,longitudMax)
                        print(total_celdas)
                        listaEstaciones=opencellid.escribir_estaciones_base_csv(url, "estaciones_base.csv", total_celdas, latitudMin,latitudMax,longitudMin,longitudMax,tipoAnt)
                        print(len(listaEstaciones))
                        lista_simulacion.append("estaciones_base.csv")
                        for estacion in listaEstaciones:
                            estacion_json = {
                                'ID': estacion.cellID,
                                'Latitud': estacion.latitud,
                                'Longitud': estacion.longitud,
                                'Tipo de Radio': estacion.tipoRadio,
                            }
                            estaciones_json.append(estacion_json)
                    
                  
                    if not listaEstaciones:
                        sys.exit("Error: La lista de estaciones está vacía. Terminando el programa.") 
                    archivo.guardar_datos_en_archivo(estaciones_json, 'EstacionesBase.json')
                    lista_simulacion.append("EstacionesBase.json")

                    ball_trees, estaciones_por_tipo = consola.construir_ball_trees_por_tipo(listaEstaciones)

                    if(tipoMovilidad=="humanos"):
                        listaHumanos = movilidad.leer_datos_desde_csv(archivoMovilidad)
                        movilidad.guardar_datos_en_csv(listaHumanos)
                        lista_simulacion.append("datosHumanos.csv")
                        print(len(listaHumanos))

                        humanos_json = []
                        for humano in listaHumanos:
                            latitud_humano = humano.latitud
                            longitud_humano = humano.longitud
                            estaciones_cercanas = consola.encontrar_estaciones_mas_cercanas_por_tipo_ball_tree(ball_trees, estaciones_por_tipo, latitud_humano, longitud_humano)
                            humano_json = {
                                'ID': humano.idHumano,
                                'Latitud': latitud_humano,
                                'Longitud': longitud_humano,
                                'AntenasCercanas': list(estaciones_cercanas.values())
                            }
                            humanos_json.append(humano_json)
                        archivo.guardar_datos_en_archivo(humanos_json, 'Humanos.json')
                        puntos=humanos_json
                        lista_simulacion.append("Humanos.json")
                    else:
                        listaTaxis = movilidad.leerArchivoTaxi(diaMin,diaMax,horaMin, horaMax, archivoMovilidad) #buscaTaxi
                        movilidad.guardarTaxisProcesados(listaTaxis) 
                        lista_simulacion.append("taxis.csv")
                        print(len(listaTaxis))
                        print("taxis guardados")
                        taxis_json = []
                        for taxi in listaTaxis:
                            latitud_taxi = taxi.latitud
                            longitud_taxi = taxi.longitud
                            estaciones_cercanas = consola.encontrar_estaciones_mas_cercanas_por_tipo_ball_tree(ball_trees, estaciones_por_tipo, latitud_taxi, longitud_taxi)
                            taxi_json = {
                                'ID': taxi.idTaxi,
                                'SeñalTaxi': taxi.señalTaxi,
                                'Latitud': latitud_taxi,
                                'Longitud': longitud_taxi,
                                'Dia': taxi.dia,
                                'Hora': taxi.hora,
                                'AntenasCercanas': list(estaciones_cercanas.values())
                            }
                            taxis_json.append(taxi_json)

                        puntos=taxis_json
                        archivo.guardar_datos_en_archivo(taxis_json, 'Taxi.json')
                        lista_simulacion.append("Taxi.json")
    
                    graficas.generar_mapa_calor_distribucion(listaEstaciones, nombre_archivo="Mapa_de_Estaciones_Base")
                    contador_estaciones=graficas.contar_conexiones_por_estacion(puntos, listaEstaciones)
                    graficas.generar_mapa_calor_conexiones(puntos,listaEstaciones, 'Mapa_Calor_de_Conexiones_Establecidas')
                    graficas.generar_grafico_barras_conexiones_por_estacion(contador_estaciones, 'Conexiones_Totales_por_Estación')
                    graficas.generar_grafico_top_50_estaciones(contador_estaciones, '50_Estaciones_con_Más_Conexiones')
                    graficas.generar_grafico_distancia_media_top_50(contador_estaciones, puntos, 'Distancia_Media_de_Usuarios')

                    lista_graficas.append("Mapa_Calor_de_Conexiones_Establecidas.png")
                    lista_graficas.append("Mapa_de_Estaciones_Base.png")
                    lista_graficas.append("Conexiones_Totales_por_Estación.png")
                    lista_graficas.append("50_Estaciones_con_Más_Conexiones.png")
                    lista_graficas.append("Distancia_Media_de_Usuarios.png")
                    contador_dias=graficas.contar_conexiones_por_dia(puntos)
                    contador_horas=graficas.contar_conexiones_por_hora(puntos)
                    contador_mes=graficas.contar_conexiones_por_mes(puntos)
                    contador_estacionesAño=graficas.contar_conexiones_por_estacionAño(puntos)
                    graficas.generar_grafico_area_conexiones_por_dia(contador_dias, "Distribución_de_Conexiones_Semanales")
                    graficas.generar_grafico_area_conexiones_por_hora(contador_horas, "Distribución_de_Conexiones_por_Hora")
                    graficas.generar_grafico_area_conexiones_por_mes(contador_mes, "Distribución_de_Conexiones_por_Mes")
                    graficas.generar_grafico_area_conexiones_por_estacion(contador_estacionesAño, "Distribución_de_Conexiones_por_Estación")
                    lista_graficas.append("Distribución_de_Conexiones_Semanales.png")
                    lista_graficas.append("Distribución_de_Conexiones_por_Hora.png")
                    lista_graficas.append("Distribución_de_Conexiones_por_Mes.png")
                    lista_graficas.append("Distribución_de_Conexiones_por_Estación.png")

                    archivos_seleccionados = archivo.mostrar_opciones_predeterminadas()
                    archivos_a_descargar = []
                    if archivos_seleccionados:
                        if "Gráficas" in archivos_seleccionados:
                            archivos_a_descargar += lista_graficas
                        if "Información de simulación" in archivos_seleccionados:
                            archivos_a_descargar += lista_simulacion

                        destino = input("Ingresa la ubicación de destino para el archivo ZIP (o presiona Enter para descargarlo en el escritorio): ").strip()
                        if destino:
                            archivo.descargar_archivos(archivos_a_descargar, destino)
                        else:
                            archivo.descargar_archivos(archivos_a_descargar)
                        break
                    else:
                        print("Programa Finalizado")
                else:
                    print("No hay datos para procesar")
                    break
            else:
                opcion = input("Opción no válida. Responde con 'si' o 'no': ").strip().lower()       

        pass