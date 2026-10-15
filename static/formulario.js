
const barraLateral = document.querySelector(".formulario")
const menu = document.querySelector(".menu");

menu.addEventListener("click", ()=>{
    barraLateral.classList.toggle("mini-formulario");
    if(barraLateral.classList.contains("mini-formulario")){
        menu.children[0].style.display = "none";
        menu.children[1].style.display = "block";
    }
    else {
        menu.children[0].style.display = "block";
        menu.children[1].style.display = "none";
    }
});


// const descargaInforme = document.querySelector(".informe")
// const menuInforme = document.querySelector(".menuInforme");

// menuInforme.addEventListener("click", ()=>{
//     descargaInforme.classList.toggle("mini-informe");
//     if(descargaInforme.classList.contains("mini-informe")){
//         menuInforme.children[0].style.display = "none";
//         menuInforme.children[1].style.display = "block";
//     }
//     else {
//         menuInforme.children[0].style.display = "block";
//         menuInforme.children[1].style.display = "none";
//     }
// });



const graficasView = document.querySelector(".graficas")
const menuGraficas = document.querySelector(".menuGraficas");

menuGraficas.addEventListener("click", ()=>{
    graficasView.classList.toggle("mini-graficas");
    if(graficasView.classList.contains("mini-graficas")){
        menuGraficas.children[0].style.display = "none";
        menuGraficas.children[1].style.display = "block";
    }
    else {
        menuGraficas.children[0].style.display = "block";
        menuGraficas.children[1].style.display = "none";
    }
});


