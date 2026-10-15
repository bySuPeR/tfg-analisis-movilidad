function mostrarCampos() {
    var tipoMovilidad = document.querySelector('.select_movilidad').value;
    var camposTaxi = document.querySelector('.campos-taxi');
    
    if (tipoMovilidad === 'taxi') {
        camposTaxi.style.display = 'block';
    } else {
        camposTaxi.style.display = 'none';
    }
}
