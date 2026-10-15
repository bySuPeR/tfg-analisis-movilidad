document.addEventListener('DOMContentLoaded', function () {
    // Obtener referencias a los elementos relevantes
    const selectMovilidad = document.querySelector(".select_movilidad");
    //const archivoTaxi = document.getElementById("archivoTaxi");
    //const archivoHumano = document.getElementById("archivoHumano");
    const fecha = document.querySelector(".fecha");
    const selectUso = document.querySelector(".select_uso");
    const archivoEstacion = document.getElementById("archivoEstacion")



    // Función para manejar el cambio en el select
    function cambiarSeccionMovilidad() {
        if (selectMovilidad.value === 'taxi') {
            // archivoTaxi.style.visibility = 'visible';
            // archivoHumano.style.visibility = 'hidden';
            fecha.style.visibility = 'visible'; // Mostrar input de fecha y hora
        } else if (selectMovilidad.value === 'humana') {
            // archivoTaxi.style.visibility = 'hidden';
            // archivoHumano.style.visibility = 'visible';
            fecha.style.visibility = 'hidden'; // Ocultar input de fecha y hora
        }
    }

    function cambiarSeccionEstacionesBase() {
        var campoArchivo = document.getElementById("archivoEst");
        var labelTipoArchivo = document.getElementById("labelTipoArchivoEstacion");
        var formatoEstacion = document.getElementById("formatoEstacion");
        if (selectUso.value === 'subida') {
            archivoEstacion.style.visibility = 'visible';
            campoArchivo.accept = ".csv,.gz";
            labelTipoArchivo.textContent = "CSV, GZ";
            formatoEstacion.textContent = "Formato: 'tipoRadio, mcc, mnc, lac, cellID, unit, longitud, latitud, rango, samples, changeables, created, updated, averageSignal'";

        } else {
            archivoEstacion.style.visibility = 'hidden';
            campoArchivo.accept = ""; // Para aceptar cualquier tipo de archivo
            labelTipoArchivo.textContent = "";
            formatoEstacion.textContent = "";
        }
    }

    function cambiarTipoArchivo() {
        var campoArchivo = document.getElementById("archivo");
        var labelTipoArchivo = document.getElementById("labelTipoArchivo");
        var formato = document.getElementById("formato");
        if (selectMovilidad.value === "taxi") {
            campoArchivo.accept = ".csv";
            labelTipoArchivo.textContent = "CSV";
            // formato.textContent = "Formato: 'idTaxi; fecha (YYYY-MM-DD hh:mm:ss + 01); posicion (POINT(lat, lon))'";
            formato.textContent = "Formato: 'id, día, hora, latitud, longitud' ";

        } else if (selectMovilidad.value === "humana") {
            campoArchivo.accept = ".csv";
            labelTipoArchivo.textContent = "CSV";
            // formato.textContent = "Formato: 'tiempo (s), coord_x_metros, coord_y_metros' ";
            formato.textContent = "Formato: 'id, tiempo, latitud, longitud' ";
        } else {
            campoArchivo.accept = ""; // Para aceptar cualquier tipo de archivo
            labelTipoArchivo.textContent = "";
        }
    }






    // Agregar un event listener para el cambio en el select
    selectMovilidad.addEventListener('change', cambiarSeccionMovilidad);
    selectUso.addEventListener("change", cambiarSeccionEstacionesBase );
    selectMovilidad.addEventListener("change", cambiarTipoArchivo );
    

    // Llamar a la función handleSelectChange() para establecer el estado inicial
    cambiarSeccionMovilidad();
    cambiarSeccionEstacionesBase();
    cambiarTipoArchivo();
    
});