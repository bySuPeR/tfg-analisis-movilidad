from flask import Flask, render_template,request
import subprocess
from main import procesar_datos
import os
from flask import send_file
import zipfile
from datetime import datetime

app = Flask(__name__)

archivos_html = ["index.html", "web.html"]
pagina_actual = 0


lista_graficas = []
lista_simulacion = []

@app.route('/descargar_archivos', methods=['POST'])
def descargar_archivos():
    """
    Manda los archivos seleccionados por el usuario al navegador para su posterior descarga.
    
    Este método recibe una lista de tipos de archivo desde una solicitud POST. Los archivos
    seleccionados se buscan en la carpeta de descargas. Si alguno de los archivos seleccionados
    no se encuentra, se muestra una advertencia en los logs pero el proceso continúa. Solo los
    archivos válidos se incluyen en el archivo ZIP que se envía al usuario. Si no se encuentran
    archivos válidos, se devuelve un error 404.

    Returns:
        Response: Un archivo ZIP que contiene los archivos seleccionados, o un mensaje de error 
                  en caso de que no haya archivos válidos.
    """
    # Obtiene los tipos de archivo seleccionados desde el formulario
    tipos_seleccionados = request.form.getlist('file_type')
    
    # Verifica si se han seleccionado tipos de archivo
    if not tipos_seleccionados:
        return "No se ha seleccionado ningún tipo de archivo", 400

    archivos_seleccionados = []
    if "graficas" in tipos_seleccionados:
        archivos_seleccionados.extend(lista_graficas)
    
    if "info_simulacion" in tipos_seleccionados:
        # Filtra los archivos que no tienen la extensión '.html'. Estos archivos son internos y no deben descargarse.
        archivos_seleccionados.extend([archivo for archivo in lista_simulacion if not archivo.endswith('.html')])

    archivos_validos = []
    for nombre_archivo in archivos_seleccionados:
        ruta_archivo = os.path.join(app.root_path, 'descargas', nombre_archivo)
        if os.path.exists(ruta_archivo):
            archivos_validos.append(ruta_archivo)
        else:
            # Imprime una advertencia si el archivo no se encuentra
            print(f"Advertencia: El archivo '{nombre_archivo}' no se encuentra en la carpeta de descargas.")

    # Si no hay archivos válidos para descargar, devuelve un error 404
    if not archivos_validos:
        return "No se encontraron archivos válidos para descargar", 404

    # Crea el archivo ZIP con los archivos válidos
    nombre_zip = "informe.zip"
    ruta_zip = os.path.join(app.root_path, nombre_zip)

    with zipfile.ZipFile(ruta_zip, 'w') as zipf:
        for ruta_archivo in archivos_validos:
            zipf.write(ruta_archivo, os.path.basename(ruta_archivo))

    # Envía el archivo ZIP al usuario
    return send_file(ruta_zip, as_attachment=True, download_name=nombre_zip)



@app.route('/')
def mostrar_pagina(errores=None, datos_validos=None, lista_graficas=None, lista_simulacion=None):
    """Devuelve la página que debe cargar el navegador"""
    nombre_archivo_actual = archivos_html[pagina_actual]
    print("Main: ",nombre_archivo_actual)
    if errores:
        print("Errores: ",nombre_archivo_actual)
        return render_template(nombre_archivo_actual, errores=errores, datos=datos_validos)
    elif datos_validos and lista_graficas and lista_simulacion:
        print("Datos Validos: ",nombre_archivo_actual)
        print("Graficas procesadas app validas:", lista_graficas)
        print("Archivos simulacion procesadas app validas:", lista_simulacion)
        return render_template(nombre_archivo_actual, datos=datos_validos, lista_graficas=lista_graficas, lista_simulacion=lista_simulacion)
    else:
        print("Primera carga: ",nombre_archivo_actual)
        return render_template(nombre_archivo_actual)

@app.route('/datosElegidos', methods=["POST"])
def get_datosPreprocesar():
    """Comprueba que los datos del formulario son correctos. Consigue los archivos resultantes."""
    global pagina_actual
    errores = []
    datos_validos = {}
    global lista_graficas, lista_simulacion
    lista_simulacion.clear()
    lista_graficas.clear()

    tipoMovilidad = str(request.form['select_movilidad'])
    archivoMovilidad = request.files['archivo']
    if not archivoMovilidad:
        errores.append("Archivo de movilidad es requerido.")
    else:
        archivoMovilidad.save(archivoMovilidad.filename)
        datos_validos['select_movilidad'] = tipoMovilidad

    diaMin,diaMax, horaMin, horaMax = None,None, None, None
    if tipoMovilidad == 'taxi':
        diaMin = request.form.get('valorDiaMin')
        diaMax = request.form.get('valorDiaMax')
        if not diaMin or not diaMax:
            errores.append("Dia del taxi es requerido.")
        else:
            datos_validos['valorDiaMin'] = diaMin
            datos_validos['valorDiaMax'] = diaMax
        horaMin = request.form.get('valorHoraMin')
        if not horaMin:
            errores.append("Hora Minima del taxi es requerido.")
        else:
            datos_validos['valorHoraMin'] = horaMin
        horaMax = request.form.get('valorHoraMax')
        if not horaMax:
            errores.append("Hora Maxima del taxi es requerido.")
        else:
            datos_validos['valorHoraMax'] = horaMax


        horaFiltroTimeMax = datetime.strptime(horaMax, "%H:%M:%S").time()
        horaFiltroTimeMin = datetime.strptime(horaMin, "%H:%M:%S").time()
        if(horaFiltroTimeMax<horaFiltroTimeMin):
            errores.append("La hora máxima debe ser mayor o igual que la hora mínima")

    elif tipoMovilidad == 'humana':
        diaMin = None
        diaMax = None
        horaMin = None
        horaMax = None

    if 'select_antena' in request.form:
        tipoAntena = str(request.form['select_antena'])
        datos_validos['select_antena'] = tipoAntena
    else:
        errores.append("Tipo de antena es requerido.")
    
    if 'select_uso' not in request.form:
        errores.append("Tipo de uso es requerido.")
    else:
        tipoUso = str(request.form['select_uso'])
        datos_validos['select_uso'] = tipoUso
        archivoEstaciones = None
        extensionEst = None
        if tipoUso == 'subida':
            archivoEstaciones = request.files['archivoEst']
            if not archivoEstaciones:
                errores.append("Archivo de Estaciones es requerido.")
            else:
                archivoEstaciones.save(archivoEstaciones.filename)
                extensionEst = os.path.splitext(archivoEstaciones.filename)[1]

    ciudad = request.form['searchInput']
    if not ciudad:
        errores.append("Ciudad es requerida.")
    else:
        datos_validos['searchInput'] = ciudad
        latitud = float(request.form['latitud'])
        longitud = float(request.form['longitud'])
        datos_validos['latitud'] = latitud  
        datos_validos['longitud'] = longitud 

    if errores:
        nombre_archivo_actual = archivos_html[pagina_actual]
        return render_template(nombre_archivo_actual, errores=errores, datos=datos_validos)
    
    lista_graficas, lista_simulacion = procesar_datos(tipoMovilidad,archivoMovilidad, diaMin,diaMax, horaMin, horaMax, tipoAntena, tipoUso, archivoEstaciones,extensionEst, ciudad,latitud,longitud)

    print("Graficas procesadas app:", lista_graficas)
    print("Archivos simulacion procesadas app:", lista_simulacion)

    pagina_actual = 1  # Cambiamos a la siguiente página
    return mostrar_pagina(errores, datos_validos , lista_graficas, lista_simulacion)

if __name__ == '__main__':
    """Pone en marcha el servidor Flask"""
    app.run(debug=True, port=8000)