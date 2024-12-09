// initializare harta 
var map = L.map('map').setView([45.9432, 24.9668], 7); // Centered on Romania

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);



// adaugare pini pe harta  
function addPins(results) {
    results.forEach(result => {
        if (result.latitude && result.longitude) {
            L.marker([result.latitude, result.longitude])
                .bindPopup(`<b>${result.name}</b><br>${result.county}<br>${result.category}`)
                .addTo(map);
        }
    });
}

// filtram rezultatele si  le afisam pe harta 
function fetchMapData() {
    const formData = new FormData(document.querySelector('.search-container'));
    fetch('/map_data', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        addPins(data.results);
    })
    .catch(error => console.error('Error fetching map data:', error));
}

// actualizare harta la apasarea butonului cauta 
document.querySelector('.search-container').addEventListener('submit', function (e) {
    e.preventDefault();
    map.eachLayer(layer => { if (layer instanceof L.Marker) map.removeLayer(layer); }); // se sterg pinii vechi 
    fetchMapData();
});