// Initialize the map
const map = L.map('map').setView([0, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Color palette for different beacons
const beaconColors = [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', 
    '#00FFFF', '#FFA500', '#800080', '#008000', '#000080'
];

// Store beacon data and layers
const beaconData = {};
const beaconLayers = {};

// Function to get URL parameter
function getUrlParameter(name) {
    name = name.replace(/[\[\]]/g, '\\$&');
    const regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)');
    const results = regex.exec(window.location.href);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

// Function to load and process data
async function loadData(filename) {
    if (!filename) {
        return;
    }

    try {
        // Fetch the data from your API endpoint
        const response = await fetch(`/profile/download_session?filename=${encodeURIComponent(filename)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const text = await response.text();
        
        // Split the text into lines and remove the first 2 lines (JSON header)
        const lines = text.split('\n').slice(2).join('\n');
        
        // Parse the CSV data
        const results = Papa.parse(lines, {
            header: true,
            skipEmptyLines: true,
            dynamicTyping: true
        });
        
        // Process the data
        processData(results.data);
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Process the parsed data (same as before)
function processData(data) {
    // Clear previous data
    Object.values(beaconLayers).forEach(layerGroup => map.removeLayer(layerGroup));
    Object.keys(beaconData).forEach(key => delete beaconData[key]);
    Object.keys(beaconLayers).forEach(key => delete beaconLayers[key]);
    
    // Group data by beacon_id
    data.forEach(row => {
        if (!beaconData[row.beacon_id]) {
            beaconData[row.beacon_id] = [];
            beaconLayers[row.beacon_id] = L.layerGroup().addTo(map);
        }
        beaconData[row.beacon_id].push(row);
    });
    
    // Plot the data for each beacon
    Object.keys(beaconData).forEach((beaconId, index) => {
        const color = beaconColors[index % beaconColors.length];
        const layerGroup = beaconLayers[beaconId];
        
        // Filter out points with invalid coordinates
        const validPoints = beaconData[beaconId].filter(
            point => !isNaN(point.latitude) && !isNaN(point.longitude)
        );
        
        if (validPoints.length > 0) {
            // Create a polyline connecting the points
            const path = L.polyline(
                validPoints.map(point => [point.latitude, point.longitude]),
                { color }
            ).addTo(layerGroup);
            
            // Add markers for each point
            validPoints.forEach(point => {
                const marker = L.circleMarker([point.latitude, point.longitude], {
                    radius: 5,
                    fillColor: color,
                    color: '#000',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                }).addTo(layerGroup);
                
                // Add popup with details
                marker.bindPopup(`
                    <b>Beacon ID:</b> ${point.beacon_id}<br>
                    <b>Time:</b> ${point.localized_timestamp}<br>
                    <b>Latitude:</b> ${point.latitude.toFixed(6)}<br>
                    <b>Longitude:</b> ${point.longitude.toFixed(6)}<br>
                    <b>Azimuth:</b> ${point.azimuth.toFixed(2)}°
                `);
            });
            
            // Fit map to show all points
            if (index === 0) {
                map.fitBounds(path.getBounds());
            }
        }
        
        // Add beacon ID to layer control
        layerGroup.addTo(map);
    });
    
    // Add layer control if we have multiple beacons
    if (Object.keys(beaconData).length > 1) {
        L.control.layers(null, beaconLayers, { collapsed: false }).addTo(map);
    }
}

// On page load, check for filename parameter
document.addEventListener('DOMContentLoaded', () => {
    const filenameParam = getUrlParameter('filename');
    if (filenameParam) {
        loadData(filenameParam);
    }
});
