import L, { Map, TileLayer, LayerGroup, Polyline, CircleMarker, Control } from 'leaflet';

// Initialize the map
const map = new Map('map').setView([0, 0], 2);
const tiles = new TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Optimization variables
const CHUNK_SIZE = 1000; // Process 1000 rows at a time
const MAX_POINTS_PER_BEACON = 5000; // Limit points to prevent memory issues
const MARKER_CLUSTER_RADIUS = 30; // Cluster radius in pixels
let worker;

// Color palette for different beacons
const beaconColors = [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF',
    '#00FFFF', '#FFA500', '#800080', '#008000', '#000080'
];

// Store beacon data and layers
let beaconData = {};
let beaconLayers = {};
let beaconFilters = {}; // To track filter state

// Function to get URL parameter
function getUrlParameter(name) {
    name = name.replace(/[\[\]]/g, '\\$&');
    const regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)');
    const results = regex.exec(window.location.href);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

// Initialize Web Worker
function initWorker() {
    if (worker) {
        worker.terminate();
    }
    worker = new Worker('/static/js/app_map_worker.js');

    worker.onmessage = function (e) {
        switch (e.data.type) {
            case 'chunk':
                processDataChunk(e.data.data);
                break;
            case 'complete':
                finalizeProcessing();
                break;
            case 'error':
                console.error('Worker error:', e.data.error);
                break;
        }
    };
}

// Function to load and process data
async function loadData(filename) {
    if (!filename) {
        return;
    }

    document.getElementById('status').textContent = 'Loading data...';

    // Clear previous data
    clearMapData();
    initWorker();

    try {
        // Fetch the data from your API endpoint
        const response = await fetch(`/profile/download_session?filename=${encodeURIComponent(filename)}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const text = await response.text();

        // Split the text into lines and remove the first 2 lines (JSON header)
        const lines = text.split('\n').slice(2).join('\n');

        // Send to worker for processing
        worker.postMessage({
            lines: lines,
            chunkSize: CHUNK_SIZE
        });
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Process data chunks from worker
function processDataChunk(chunk) {
    chunk.forEach(row => {
        if (!beaconData[row.beacon_id]) {
            beaconData[row.beacon_id] = [];
            beaconLayers[row.beacon_id] = new LayerGroup().addTo(map);
        }

        // Limit the number of points stored per beacon
        if (beaconData[row.beacon_id].length < MAX_POINTS_PER_BEACON) {
            beaconData[row.beacon_id].push(row);
        }
    });
}

// Finalize processing after all chunks are done
function finalizeProcessing() {
    // Clear any existing filter control
    if (map.beaconFilterControl) {
        map.removeControl(map.beaconFilterControl);
    }

    // Create filter container
    const filterContainer = L.DomUtil.create('div', 'beacon-filter-container');
    filterContainer.style.backgroundColor = 'white';
    filterContainer.style.padding = '10px';
    filterContainer.style.borderRadius = '5px';
    filterContainer.style.boxShadow = '0 0 10px rgba(0,0,0,0.2)';

    // Add title
    const title = L.DomUtil.create('h3', 'filter-title', filterContainer);
    title.textContent = 'Filter Beacons';
    title.style.fontWeight = 'bold';
    title.style.color = '#333';
    title.style.marginTop = '0';
    title.style.marginBottom = '10px';

    // Create checkboxes for each beacon
    Object.keys(beaconData).forEach((beaconId, index) => {
        const color = beaconColors[index % beaconColors.length];

        const filterItem = L.DomUtil.create('div', 'beacon-filter-item', filterContainer);
        filterItem.style.color = '#333';

        const checkbox = L.DomUtil.create('input', '', filterItem);
        checkbox.type = 'checkbox';
        checkbox.id = `filter-${beaconId}`;
        checkbox.checked = true;
        checkbox.style.marginRight = '8px';
        checkbox.style.accentColor = color;

        const label = L.DomUtil.create('label', '', filterItem);
        label.htmlFor = `filter-${beaconId}`;
        label.innerHTML = `
            <span style="display:inline-block; width:12px; height:12px; background-color:${color}; margin-right:5px;"></span>
            ${beaconId}
        `;

        // Store initial filter state
        beaconFilters[beaconId] = true;

        // Add event listener
        checkbox.addEventListener('change', (e) => {
            beaconFilters[beaconId] = e.target.checked;
            updateBeaconVisibility();
        });

        filterItem.style.marginBottom = '5px';
    });

    // Add "Toggle All" buttons in two rows
    const toggleButtons = L.DomUtil.create('div', 'toggle-buttons', filterContainer);
    toggleButtons.style.display = 'flex';
    toggleButtons.style.flexDirection = 'column';

    // Top row: Show All, Hide All
    const topRow = L.DomUtil.create('div', '', toggleButtons);
    topRow.style.display = 'flex';
    topRow.style.justifyContent = 'space-between';
    topRow.style.gap = '8px';

    const showAll = L.DomUtil.create('button', '', topRow);
    showAll.innerHTML = '<i class="fa fa-eye"></i> Show All';
    showAll.style.padding = '3px 8px';
    showAll.style.fontSize = '12px';

    const hideAll = L.DomUtil.create('button', '', topRow);
    hideAll.innerHTML = '<i class="fa fa-eye-slash"></i> Hide All';
    hideAll.style.padding = '3px 8px';
    hideAll.style.fontSize = '12px';

    // Bottom row: Toggle Checked
    const bottomRow = L.DomUtil.create('div', '', toggleButtons);
    bottomRow.style.display = 'flex';
    bottomRow.style.justifyContent = 'center';

    const toggleChecked = L.DomUtil.create('button', '', bottomRow);
    toggleChecked.innerHTML = '<i class="fa fa-toggle-on"></i> Toggle Checked';
    toggleChecked.style.padding = '3px 8px';
    toggleChecked.style.fontSize = '12px';

    showAll.addEventListener('click', () => {
        Object.keys(beaconFilters).forEach(beaconId => {
            beaconFilters[beaconId] = true;
            document.getElementById(`filter-${beaconId}`).checked = true;
        });
        updateBeaconVisibility();
    });

    hideAll.addEventListener('click', () => {
        Object.keys(beaconFilters).forEach(beaconId => {
            beaconFilters[beaconId] = false;
            document.getElementById(`filter-${beaconId}`).checked = false;
        });
        updateBeaconVisibility();
    });

    toggleChecked.addEventListener('click', () => {
        Object.keys(beaconFilters).forEach(beaconId => {
            const checkbox = document.getElementById(`filter-${beaconId}`);
            beaconFilters[beaconId] = !checkbox.checked;
            checkbox.checked = beaconFilters[beaconId];
        });
        updateBeaconVisibility();
    });

    // Create custom control
    const BeaconFilterControl = Control.extend({
        options: {
            position: 'topright'
        },

        onAdd: function (map) {
            return filterContainer;
        },

        onRemove: function (map) {  // Is cleanup neede?
        }
    });

    // Add control to map
    map.beaconFilterControl = new BeaconFilterControl();
    map.addControl(map.beaconFilterControl);

    // Plot the data for each beacon
    Object.keys(beaconData).forEach((beaconId, index) => {
        const color = beaconColors[index % beaconColors.length];
        const layerGroup = beaconLayers[beaconId];

        // Filter valid points
        const validPoints = beaconData[beaconId].filter(
            point => !isNaN(point.latitude) && !isNaN(point.longitude)
        );

        if (validPoints.length > 0) {
            // Create simplified polyline (every 10th point for performance)
            const simplifiedPoints = [];
            for (let i = 0; i < validPoints.length; i += Math.max(1, Math.floor(validPoints.length / 1000))) {
                simplifiedPoints.push([validPoints[i].latitude, validPoints[i].longitude]);
            }

            const path = new Polyline(simplifiedPoints, { color }).addTo(layerGroup);

            // Add all markers
            validPoints.forEach(point => {
                const marker = new CircleMarker([point.latitude, point.longitude], {
                    radius: 5,
                    fillColor: color,
                    color: '#000',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                }).bindPopup(createPopupContent(point));
                layerGroup.addLayer(marker);
            });

            // Fit map to show all points from first beacon
            if (index === 0) {
                map.fitBounds(path.getBounds());
            }
        }
    });

    document.getElementById('status').textContent = 'Data loaded successfully';
}

function createPopupContent(point) {
    return `
        <b>Beacon ID:</b> ${point.beacon_id}<br>
        <b>Time:</b> ${point.localized_timestamp}<br>
        <b>Latitude:</b> ${point.latitude.toFixed(6)}<br>
        <b>Longitude:</b> ${point.longitude.toFixed(6)}<br>
        <b>Azimuth:</b> ${point.azimuth.toFixed(2)}°
    `;
}

function clearMapData() {
    Object.values(beaconLayers).forEach(layerGroup => {
        map.removeLayer(layerGroup);
        layerGroup.clearLayers();
    });
    beaconData = {};
    beaconLayers = {};
    beaconFilters = {};

    // Remove filter control if it exists
    if (map.beaconFilterControl) {
        map.removeControl(map.beaconFilterControl);
        map.beaconFilterControl = null;
    }
}

// Update visibility based on filters
function updateBeaconVisibility() {
    Object.keys(beaconLayers).forEach(beaconId => {
        if (beaconFilters[beaconId]) {
            map.addLayer(beaconLayers[beaconId]);
        } else {
            map.removeLayer(beaconLayers[beaconId]);
        }
    });
}

// Event listeners and initialization
document.addEventListener('DOMContentLoaded', () => {
    const filenameParam = getUrlParameter('filename');
    if (filenameParam) {
        loadData(filenameParam);
    } else {  // Redirect to /profile
        window.location.replace("/profile");
    }
});

// Clean up worker when page unloads
window.addEventListener('beforeunload', () => {
    if (worker) {
        worker.terminate();
    }
});
