const searchInput = document.getElementById('searchInput');
const suggestionsList = document.getElementById('suggestions');
const latitudInput = document.getElementById('latitud');
const longitudInput = document.getElementById('longitud');

searchInput.addEventListener('input', function() {
    const userInput = this.value.toLowerCase();
  
    if (userInput.length > 0) {
      fetch(`http://api.geonames.org/searchJSON?q=${userInput}&maxRows=4&username=martingb`)
        .then(response => {
          if (!response.ok) {
            throw new Error('La solicitud no fue exitosa');
          }
          return response.json();
        })
        .then(data => {
          console.log('Datos de la API:', data);
          const cities = data.geonames.map(city => ({
            name: city.name,
            lat: city.lat,
            lng: city.lng
          }));
          console.log('Ciudades sugeridas:', cities);
          displaySuggestions(cities);
        })
        .catch(error => {
          console.error('Error fetching cities:', error);
        });
    } else {
      clearSuggestions();
    }
  });



// Agrega un controlador de eventos clic a la lista de sugerencias
suggestionsList.addEventListener('click', function(event) {
    // Verifica si el clic ocurrió en un elemento de la lista de sugerencias
    if (event.target.tagName === 'LI') {
      // Establece el valor del campo de búsqueda como el texto del elemento de la lista clicado
      const selectedCity = JSON.parse(event.target.dataset.city);
      searchInput.value = selectedCity.name;
      latitudInput.value = selectedCity.lat;
      longitudInput.value = selectedCity.lng;

      clearSuggestions();
    }
  });










  
function displaySuggestions(suggestions) {
  const html = suggestions.map(city => `<li data-city='${JSON.stringify(city)}'>${city.name}</li>`).join('');
  suggestionsList.innerHTML = html;
}

function clearSuggestions() {
  suggestionsList.innerHTML = '';
}
