// Global variables
let currentSession = null;
let availableDrivers = [];
let selectedDrivers = [];

// Session mappings
const sessionMappings = {
    'Practice 1': 'FP1',
    'Practice 2': 'FP2',
    'Practice 3': 'FP3',
    'Qualifying': 'Q',
    'Sprint': 'Sprint',
    'Sprint Qualifying': 'SQ',
    'Race': 'R'
};

// Team colors for visual consistency
const teamColors = {
    'Mercedes': '#00D2BE',
    'Red Bull Racing': '#1E41FF',
    'Ferrari': '#DC0000',
    'McLaren': '#FF8700',
    'Alpine': '#0090FF',
    'Aston Martin': '#006F62',
    'Haas': '#808080',
    'RB': '#1660AD',
    'Williams': '#87CEEB',
    'Kick Sauber': '#00E701'
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    setupTabs();
});

// Event listeners
function initializeEventListeners() {
    // Load session button
    document.getElementById('loadSession').addEventListener('click', loadSession);

    // Telemetry type change
    document.getElementById('telemetryType').addEventListener('change', function() {
        if (selectedDrivers.length > 0) {
            loadTelemetryData();
        }
    });
}

// Tab system
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');

            // Remove active class from all tabs and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));

            // Add active class to clicked tab and corresponding pane
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');

            // Load data for the active tab
            loadTabData(tabId);
        });
    });
}

// Load session data
async function loadSession() {
    const year = document.getElementById('year').value;
    const grandPrix = document.getElementById('grandprix').value;
    const session = document.getElementById('session').value;
    const statusDiv = document.getElementById('sessionStatus');
    const loadButton = document.getElementById('loadSession');

    // Show loading state
    loadButton.disabled = true;
    loadButton.textContent = '⏳ Loading...';
    statusDiv.innerHTML = '<div class="status-message status-info">Loading F1 session data...</div>';

    try {
        // Call Python backend API
        const response = await fetch('/api/load-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                year: parseInt(year),
                grand_prix: grandPrix,
                session_type: sessionMappings[session]
            })
        });

        const result = await response.json();

        if (result.success) {
            currentSession = result.session_info;
            availableDrivers = result.drivers;

            statusDiv.innerHTML = `<div class="status-message status-success">✅ Successfully loaded ${year} ${grandPrix} ${session}</div>`;
            setupDriverSelection();

        } else {
            statusDiv.innerHTML = `<div class="status-message status-error">❌ Failed to load session: ${result.error}</div>`;
        }
    } catch (error) {
        statusDiv.innerHTML = `<div class="status-message status-error">❌ Network error: ${error.message}</div>`;
    } finally {
        loadButton.disabled = false;
        loadButton.textContent = '🔄 Load Session Data';
    }
}

// Setup driver selection interface
function setupDriverSelection() {
    const driverSection = document.getElementById('driverSection');
    const driverGrid = document.getElementById('driverGrid');

    driverSection.style.display = 'block';
    driverGrid.innerHTML = '';

    availableDrivers.forEach(driver => {
        const driverCard = document.createElement('div');
        driverCard.className = 'driver-card';
        driverCard.setAttribute('data-driver', driver.code);

        const teamColor = teamColors[driver.team] || '#808080';

        driverCard.innerHTML = `
            <div class="driver-name">${driver.abbreviation}</div>
            <div class="driver-team" style="color: ${teamColor};">${driver.team}</div>
            <div class="driver-number">#${driver.number || 'N/A'}</div>
        `;

        driverCard.addEventListener('click', function() {
            toggleDriverSelection(driver);
        });

        driverGrid.appendChild(driverCard);
    });
}

// Toggle driver selection
function toggleDriverSelection(driver) {
    const driverCard = document.querySelector(`[data-driver="${driver.code}"]`);
    const index = selectedDrivers.findIndex(d => d.code === driver.code);

    if (index > -1) {
        // Remove driver
        selectedDrivers.splice(index, 1);
        driverCard.classList.remove('selected');
    } else {
        // Add driver (limit to 4)
        if (selectedDrivers.length < 4) {
            selectedDrivers.push(driver);
            driverCard.classList.add('selected');
        } else {
            alert('Maximum 4 drivers can be selected for comparison');
            return;
        }
    }

    updateSelectedDriversDisplay();

    if (selectedDrivers.length > 0) {
        document.getElementById('analysisSection').style.display = 'block';
        loadTabData('telemetry'); // Load default tab
    } else {
        document.getElementById('analysisSection').style.display = 'none';
    }
}

// Update selected drivers display
function updateSelectedDriversDisplay() {
    const selectedDiv = document.getElementById('selectedDrivers');

    if (selectedDrivers.length === 0) {
        selectedDiv.innerHTML = '';
        return;
    }

    const driverTags = selectedDrivers.map(driver => {
        const teamColor = teamColors[driver.team] || '#808080';
        return `
            <div class="selected-driver-tag" style="background-color: ${teamColor};">
                ${driver.abbreviation}
                <span class="remove-driver" onclick="removeDriver('${driver.code}')">×</span>
            </div>
        `;
    }).join('');

    selectedDiv.innerHTML = `
        <h4>Selected Drivers:</h4>
        <div class="selected-driver-list">
            ${driverTags}
        </div>
    `;
}

// Remove driver from selection
function removeDriver(driverCode) {
    const driver = selectedDrivers.find(d => d.code === driverCode);
    if (driver) {
        toggleDriverSelection(driver);
    }
}

// Load data for active tab
function loadTabData(tabId) {
    if (selectedDrivers.length === 0) return;

    switch (tabId) {
        case 'telemetry':
            loadTelemetryData();
            break;
        case 'trackmap':
            loadTrackMapData();
            break;
        case 'laptimes':
            loadLapTimesData();
            break;
        case 'tires':
            loadTiresData();
            break;
        case 'progress':
            loadProgressData();
            break;
        case 'analytics':
            loadAnalyticsData();
            break;
        case 'speed':
            loadSpeedAnalysisData();
            break;
        case 'cornering':
            loadCorneringAnalysisData();
            break;
        case 'braking':
            loadBrakingAnalysisData();
            break;
        case 'gears':
            loadGearAnalysisData();
            break;
        case 'consistency':
            loadConsistencyAnalysisData();
            break;
        case 'compare':
            loadLapComparisonData();
            break;
        case 'pitstop':
            loadPitstopAnalysisData();
            break;
        case 'weather':
            loadWeatherImpactData();
            break;
        case 'coordination':
            loadCoordinationData();
            break;
        case 'sectors':
            loadSectorDominanceData();
            break;
        case 'ers':
            loadErsData();
            break;
        case 'driver-coord':
            loadDriverCoordinationData();
            break;
        case 'sector-perf':
            loadSectorPerformanceData();
            break;
        case 'advanced-metrics':
            loadAdvancedMetricsData();
            break;
        case 'overtaking':
            loadOvertakingData();
            break;
        case 'fuel':
            loadFuelData();
            break;
        case 'tiredeg':
            loadTireDegradationData();
            break;
        case 'corners':
            loadCornerData();
            break;
    }
}

// Load telemetry data
async function loadTelemetryData() {
    const telemetryType = document.getElementById('telemetryType').value;
    const chartDiv = document.getElementById('telemetryChart');
    const loadingDiv = document.getElementById('telemetryLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/telemetry', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                drivers: selectedDrivers.map(d => d.code),
                telemetry_type: telemetryType
            })
        });

        const result = await response.json();

        if (result.success) {
            // Create Plotly chart
            const plotData = result.data.map(trace => ({
                x: trace.x,
                y: trace.y,
                name: trace.name,
                type: 'scatter',
                mode: 'lines',
                line: {
                    color: trace.color,
                    width: 2
                }
            }));

            const layout = {
                title: `${telemetryType.charAt(0).toUpperCase() + telemetryType.slice(1)} Comparison`,
                xaxis: { title: 'Distance (m)' },
                yaxis: { title: result.y_axis_title },
                showlegend: true,
                height: 500,
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)'
            };

            Plotly.newPlot(chartDiv, plotData, layout, {responsive: true});
        } else {
            chartDiv.innerHTML = `<div class="status-message status-error">Error: ${result.error}</div>`;
        }
    } catch (error) {
        chartDiv.innerHTML = `<div class="status-message status-error">Network error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

// Load track map data
async function loadTrackMapData() {
    const chartDiv = document.getElementById('trackmapChart');
    const loadingDiv = document.getElementById('trackmapLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/track-map', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                drivers: selectedDrivers.map(d => d.code)
            })
        });

        const result = await response.json();

        if (result.success) {
            // Create enhanced track visualization like the provided image
            const plotData = [{
                x: result.data.x_coords,
                y: result.data.y_coords,
                mode: 'lines+markers',
                type: 'scatter',
                line: {
                    width: 12,
                    color: 'rgba(30, 65, 255, 0.8)'
                },
                marker: {
                    size: 6,
                    color: result.data.colors,
                    colorscale: [[0, '#1E41FF'], [0.5, '#FF8700'], [1, '#DC0000']],
                    colorbar: {
                        title: 'Speed (km/h)',
                        titleside: 'right'
                    }
                },
                text: result.data.hover_text,
                hoverinfo: 'text',
                name: 'Track Layout'
            }];

            // Add START/FINISH marker
            if (result.data.x_coords && result.data.x_coords.length > 0) {
                plotData.push({
                    x: [result.data.x_coords[0]],
                    y: [result.data.y_coords[0]],
                    mode: 'markers+text',
                    type: 'scatter',
                    marker: {
                        size: 20,
                        color: 'white',
                        symbol: 'square',
                        line: { color: 'black', width: 3 }
                    },
                    text: ['START'],
                    textposition: 'middle center',
                    textfont: { 
                        color: 'black', 
                        size: 14, 
                        family: 'Inter',
                        weight: 'bold'
                    },
                    name: 'Start/Finish',
                    showlegend: false
                });
            }

            const layout = {
                title: {
                    text: 'Track Layout & Speed Analysis',
                    font: { size: 20, family: 'Inter', color: 'white' }
                },
                xaxis: { 
                    showgrid: false, 
                    zeroline: false, 
                    showticklabels: false,
                    scaleanchor: 'y'
                },
                yaxis: { 
                    showgrid: false, 
                    zeroline: false, 
                    showticklabels: false,
                    scaleratio: 1
                },
                showlegend: false,
                height: 600,
                plot_bgcolor: '#0f0f0f',
                paper_bgcolor: '#0f0f0f',
                margin: { l: 20, r: 20, t: 60, b: 20 }
            };

            Plotly.newPlot(chartDiv, plotData, layout, {responsive: true});
        } else {
            chartDiv.innerHTML = `<div class="status-message status-error">Error: ${result.error}</div>`;
        }
    } catch (error) {
        chartDiv.innerHTML = `<div class="status-message status-error">Network error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

// Load lap times data
async function loadLapTimesData() {
    const tableDiv = document.getElementById('laptimesTable');
    const loadingDiv = document.getElementById('laptimesLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/lap-times', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                drivers: selectedDrivers.map(d => d.code)
            })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            // Create HTML table
            const headers = Object.keys(result.data[0]);
            let tableHTML = `
                <table class="data-table">
                    <thead>
                        <tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>
                    </thead>
                    <tbody>
                        ${result.data.map(row =>
                            `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`
                        ).join('')}
                    </tbody>
                </table>
            `;
            tableDiv.innerHTML = tableHTML;
        } else {
            tableDiv.innerHTML = `<div class="status-message status-info">No lap time data available</div>`;
        }
    } catch (error) {
        tableDiv.innerHTML = `<div class="status-message status-error">Network error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

// Load tires data
async function loadTiresData() {
    const chartDiv = document.getElementById('tiresChart');
    const loadingDiv = document.getElementById('tiresLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/tire-strategy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                drivers: selectedDrivers.map(d => d.code)
            })
        });

        const result = await response.json();

        if (result.success) {
            // Create tire strategy visualization
            const plotData = result.data.map(driverData => {
                const driver = availableDrivers.find(d => d.code === driverData.driver_code);
                const teamColor = teamColors[driver.team] || '#808080';
                return {
                    x: driverData.laps,
                    y: Array(driverData.laps.length).fill(driver.abbreviation),
                    mode: 'markers',
                    type: 'scatter',
                    marker: {
                        color: driverData.tire_colors.map(tire => {
                            if (tire === 'INTERMEDIATE') return '#00FF00'; // Green for intermediate
                            if (tire === 'WET') return '#0000FF'; // Blue for wet
                            if (tire === 'SOFT') return '#FF0000'; // Red for soft
                            if (tire === 'MEDIUM') return '#FFFF00'; // Yellow for medium
                            if (tire === 'HARD') return '#FFFFFF'; // White for hard
                            return '#808080'; // Grey for unknown
                        }),
                        size: 10,
                        opacity: 0.8
                    },
                    name: driver.abbreviation,
                    hoverinfo: 'text',
                    hovertext: driverData.tire_stints.map(stint => `Lap ${stint.start_lap} - ${stint.end_lap}: ${stint.tire_compound}`)
                };
            });

            const layout = {
                title: 'Tire Strategy Analysis',
                xaxis: { title: 'Lap Number' },
                yaxis: { title: 'Driver', tickvals: selectedDrivers.map(d => d.abbreviation), ticktext: selectedDrivers.map(d => d.abbreviation)},
                showlegend: true,
                height: 500,
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)'
            };

            Plotly.newPlot(chartDiv, plotData, layout, {responsive: true});
        } else {
            chartDiv.innerHTML = `<div class="status-message status-error">Error: ${result.error}</div>`;
        }
    } catch (error) {
        chartDiv.innerHTML = `<div class="status-message status-error">Network error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}


// Load progress data
async function loadProgressData() {
    const chartDiv = document.getElementById('progressChart');
    const loadingDiv = document.getElementById('progressLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/race-progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                drivers: selectedDrivers.map(d => d.code)
            })
        });

        const result = await response.json();

        if (result.success) {
            // Create race progression chart
            const plotData = result.data;

            const layout = {
                title: 'Race Progression',
                xaxis: { title: 'Lap Number' },
                yaxis: { title: 'Position', autorange: 'reversed' },
                showlegend: true,
                height: 500,
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)'
            };

            Plotly.newPlot(chartDiv, plotData, layout, {responsive: true});
        } else {
            chartDiv.innerHTML = `<div class="status-message status-error">Error: ${result.error}</div>`;
        }
    } catch (error) {
        chartDiv.innerHTML = `<div class="status-message status-error">Network error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

// Load analytics data
async function loadAnalyticsData() {
    const contentDiv = document.getElementById('analyticsContent');
    const loadingDiv = document.getElementById('analyticsLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/analytics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                drivers: selectedDrivers.map(d => d.code)
            })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            // Create metrics display
            let metricsHTML = '<div class="metrics-grid">';

            result.data.forEach(driver => {
                metricsHTML += `
                    <div class="metric-card">
                        <div class="metric-value">${driver.driver}</div>
                        <div class="metric-label">Driver</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${driver.consistency_score}</div>
                        <div class="metric-label">Consistency</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${driver.fastest_lap}</div>
                        <div class="metric-label">Fastest Lap</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${driver.total_laps}</div>
                        <div class="metric-label">Total Laps</div>
                    </div>
                `;
            });

            metricsHTML += '</div>';

            // Add detailed table
            const headers = Object.keys(result.data[0]);
            metricsHTML += `
                <h4>Detailed Analytics</h4>
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>${headers.map(h => `<th>${h.replace('_', ' ').toUpperCase()}</th>`).join('')}</tr>
                        </thead>
                        <tbody>
                            ${result.data.map(row =>
                                `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`
                            ).join('')}
                        </tbody>
                    </table>
                </div>
            `;

            contentDiv.innerHTML = metricsHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No analytics data available</div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="status-message status-error">Network error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

// Utility functions
function showLoading(loadingDiv) {
    loadingDiv.style.display = 'flex';
}

function hideLoading(loadingDiv) {
    loadingDiv.style.display = 'none';
}

// Load Speed Analysis Data
async function loadSpeedAnalysisData() {
    const contentDiv = document.getElementById('speedContent');
    const loadingDiv = document.getElementById('speedLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/speed-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drivers: selectedDrivers.map(d => d.code) })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            const headers = Object.keys(result.data[0]);
            const tableHTML = `
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>${headers.map(h => `<th>${h.replace('_', ' ').toUpperCase()}</th>`).join('')}</tr>
                        </thead>
                        <tbody>
                            ${result.data.map(row =>
                                `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`
                            ).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            contentDiv.innerHTML = tableHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No speed analysis data available</div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="status-message status-error">Error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

// Load Cornering Analysis Data
async function loadCorneringAnalysisData() {
    const contentDiv = document.getElementById('corneringContent');
    const loadingDiv = document.getElementById('corneringLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/cornering-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drivers: selectedDrivers.map(d => d.code) })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            const headers = Object.keys(result.data[0]);
            const tableHTML = `
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>${headers.map(h => `<th>${h.replace('_', ' ').toUpperCase()}</th>`).join('')}</tr>
                        </thead>
                        <tbody>
                            ${result.data.map(row =>
                                `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`
                            ).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            contentDiv.innerHTML = tableHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No cornering analysis data available</div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="status-message status-error">Error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}


// Load Braking Analysis Data
async function loadBrakingAnalysisData() {
    const contentDiv = document.getElementById('brakingContent');
    const loadingDiv = document.getElementById('brakingLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/brake-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drivers: selectedDrivers.map(d => d.code) })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            const headers = Object.keys(result.data[0]);
            const tableHTML = `
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>${headers.map(h => `<th>${h.replace('_', ' ').toUpperCase()}</th>`).join('')}</tr>
                        </thead>
                        <tbody>
                            ${result.data.map(row =>
                                `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`
                            ).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            contentDiv.innerHTML = tableHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No braking analysis data available</div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="status-message status-error">Error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

// Load Gear Analysis Data
async function loadGearAnalysisData() {
    const contentDiv = document.getElementById('gearsContent');
    const loadingDiv = document.getElementById('gearsLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/gear-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drivers: selectedDrivers.map(d => d.code) })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            const headers = Object.keys(result.data[0]);
            const tableHTML = `
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>${headers.map(h => `<th>${h.replace('_', ' ').toUpperCase()}</th>`).join('')}</tr>
                        </thead>
                        <tbody>
                            ${result.data.map(row =>
                                `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`
                            ).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            contentDiv.innerHTML = tableHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No gear analysis data available</div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="status-message status-error">Error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}


// Load Consistency Analysis Data
async function loadConsistencyAnalysisData() {
    const contentDiv = document.getElementById('consistencyContent');
    const loadingDiv = document.getElementById('consistencyLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/consistency-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drivers: selectedDrivers.map(d => d.code) })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            const headers = Object.keys(result.data[0]);
            const tableHTML = `
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>${headers.map(h => `<th>${h.replace('_', ' ').toUpperCase()}</th>`).join('')}</tr>
                        </thead>
                        <tbody>
                            ${result.data.map(row =>
                                `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`
                            ).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            contentDiv.innerHTML = tableHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No consistency analysis data available</div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="status-message status-error">Error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

// Load Lap Comparison Data
async function loadLapComparisonData() {
    const contentDiv = document.getElementById('compareTable');
    const loadingDiv = document.getElementById('compareLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/lap-comparison', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drivers: selectedDrivers.map(d => d.code) })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            const headers = Object.keys(result.data[0]);
            const tableHTML = `
                <table class="data-table">
                    <thead>
                        <tr>${headers.map(h => `<th>${h.replace('_', ' ').toUpperCase()}</th>`).join('')}</tr>
                    </thead>
                    <tbody>
                        ${result.data.map(row =>
                            `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`
                        ).join('')}
                    </tbody>
                </table>
            `;
            contentDiv.innerHTML = tableHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No comparison data available</div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="status-message status-error">Error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

// Load all the new advanced analysis data
async function loadPitstopAnalysisData() {
    await loadGenericAnalysisData('/api/pitstop-analysis', 'pitstopContent', 'pitstopLoading');
}

async function loadWeatherImpactData() {
    await loadGenericAnalysisData('/api/weather-impact', 'weatherContent', 'weatherLoading');
}

async function loadCoordinationData() {
    await loadGenericAnalysisData('/api/throttle-brake-coordination', 'coordinationContent', 'coordinationLoading');
}

async function loadSectorDominanceData() {
    await loadGenericAnalysisData('/api/sector-dominance', 'sectorsContent', 'sectorsLoading');
}

async function loadErsData() {
    await loadGenericAnalysisData('/api/energy-recovery', 'ersContent', 'ersLoading');
}

async function loadOvertakingData() {
    await loadGenericAnalysisData('/api/overtaking-analysis', 'overtakingContent', 'overtakingLoading');
}

async function loadFuelData() {
    await loadGenericAnalysisData('/api/fuel-analysis', 'fuelContent', 'fuelLoading');
}

async function loadTireDegradationData() {
    await loadGenericAnalysisData('/api/tire-degradation', 'tiredegContent', 'tiredegLoading');
}

async function loadCornerData() {
    const contentDiv = document.getElementById('cornersContent');
    const loadingDiv = document.getElementById('cornersLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/corner-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drivers: selectedDrivers.map(d => d.code) })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            // Enhanced Corner-by-Corner Analysis with new ideas
            let contentHTML = `
                <div class="corner-analysis-header">
                    <h4>🏁 Advanced Corner-by-Corner Performance Analysis</h4>
                    <p class="analysis-description">Detailed analysis of driver performance through different corner types and phases</p>
                </div>
            `;
            
            // Corner performance comparison chart
            contentHTML += '<div class="corner-performance-grid">';
            result.data.forEach((driver, index) => {
                const teamColor = teamColors[selectedDrivers.find(d => d.code === driver.driver)?.team] || '#808080';
                const performanceRating = driver.corner_performance || 'Good';
                const ratingColor = performanceRating === 'Excellent' ? '#059669' : 
                                   performanceRating === 'Good' ? '#d97706' : '#6b7280';
                
                contentHTML += `
                    <div class="corner-driver-card" style="border-left: 5px solid ${teamColor};">
                        <div class="corner-driver-header">
                            <h5 style="color: ${teamColor}; margin: 0;">${driver.driver}</h5>
                            <span class="performance-badge" style="background-color: ${ratingColor}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75em;">
                                ${performanceRating}
                            </span>
                        </div>
                        <div class="corner-stats-grid">
                            <div class="corner-stat">
                                <div class="stat-value">${driver.corner_segments || driver.corner_count}</div>
                                <div class="stat-label">Corner Segments</div>
                            </div>
                            <div class="corner-stat">
                                <div class="stat-value">${driver.corner_exit_accel || 'N/A'}</div>
                                <div class="stat-label">Exit Acceleration</div>
                            </div>
                            <div class="corner-stat">
                                <div class="stat-value">${driver.avg_corner_speed}</div>
                                <div class="stat-label">Avg Corner Speed</div>
                            </div>
                            <div class="corner-stat">
                                <div class="stat-value">${driver.min_corner_speed}</div>
                                <div class="stat-label">Min Corner Speed</div>
                            </div>
                        </div>
                        <div class="corner-analysis-details">
                            <small style="color: #64748b;">
                                G-Force: ${driver.max_g_force} • 
                                Throttle: ${driver.avg_corner_throttle} • 
                                Braking: ${driver.avg_corner_braking}
                            </small>
                        </div>
                    </div>
                `;
            });
            contentHTML += '</div>';
            
            // Detailed comparison table
            const headers = Object.keys(result.data[0]);
            contentHTML += `
                <div class="detailed-corner-analysis">
                    <h4>📊 Complete Corner Analysis Data</h4>
                    <div class="table-container">
                        <table class="data-table">
                            <thead>
                                <tr>${headers.map(h => `<th>${h.replace('_', ' ').toUpperCase()}</th>`).join('')}</tr>
                            </thead>
                            <tbody>
                                ${result.data.map(row =>
                                    `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`
                                ).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            
            contentDiv.innerHTML = contentHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No corner analysis data available</div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="status-message status-error">Network error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

async function loadChampionshipData() {
    await loadGenericAnalysisData('/api/championship-projection', 'championshipContent', 'championshipLoading');
}

// Generic function to load analysis data
async function loadGenericAnalysisData(endpoint, contentId, loadingId) {
    const contentDiv = document.getElementById(contentId);
    const loadingDiv = document.getElementById(loadingId);

    showLoading(loadingDiv);

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drivers: selectedDrivers.map(d => d.code) })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            const headers = Object.keys(result.data[0]);
            const tableHTML = `
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>${headers.map(h => `<th>${h.replace('_', ' ').toUpperCase()}</th>`).join('')}</tr>
                        </thead>
                        <tbody>
                            ${result.data.map(row =>
                                `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`
                            ).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            contentDiv.innerHTML = tableHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No analysis data available</div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="status-message status-error">Error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

// NEW FUNCTIONS FOR 3 NEW DATA ENDPOINTS

async function loadDriverCoordinationData() {
    const contentDiv = document.getElementById('driver-coordContent');
    const loadingDiv = document.getElementById('driver-coordLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/driver-coordination', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drivers: selectedDrivers.map(d => d.code) })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            let contentHTML = '<h4>🎯 Driver Coordination Analysis</h4><div class="metrics-grid">';
            
            result.data.forEach(driver => {
                const teamColor = teamColors[selectedDrivers.find(d => d.code === driver.driver)?.team] || '#808080';
                contentHTML += `
                    <div class="metric-card" style="border-left: 4px solid ${teamColor};">
                        <div class="metric-value">${driver.driver}</div>
                        <div class="metric-label">Driver</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${driver.coordination_score}</div>
                        <div class="metric-label">Coordination Score</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${driver.throttle_smoothness}</div>
                        <div class="metric-label">Throttle Smoothness</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${driver.brake_smoothness}</div>
                        <div class="metric-label">Brake Smoothness</div>
                    </div>
                `;
            });
            contentHTML += '</div>';

            const headers = Object.keys(result.data[0]);
            contentHTML += `<div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>${headers.map(h => `<th>${h.replace('_', ' ').toUpperCase()}</th>`).join('')}</tr>
                    </thead>
                    <tbody>
                        ${result.data.map(row => `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`).join('')}
                    </tbody>
                </table>
            </div>`;
            
            contentDiv.innerHTML = contentHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No coordination data available</div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="status-message status-error">Error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

async function loadSectorPerformanceData() {
    const contentDiv = document.getElementById('sector-perfContent');
    const loadingDiv = document.getElementById('sector-perfLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/sector-performance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drivers: selectedDrivers.map(d => d.code) })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            let contentHTML = '<h4>🏁 Sector Performance Analysis</h4><div class="metrics-grid">';
            
            result.data.forEach(driver => {
                const teamColor = teamColors[selectedDrivers.find(d => d.code === driver.driver)?.team] || '#808080';
                contentHTML += `
                    <div class="metric-card" style="border-left: 4px solid ${teamColor};">
                        <div class="metric-value">${driver.driver}</div>
                        <div class="metric-label">Driver</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${driver.strongest_sector}</div>
                        <div class="metric-label">Strongest Sector</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${driver.sector_1_best}</div>
                        <div class="metric-label">Sector 1 Best</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${driver.sector_1_consistency}</div>
                        <div class="metric-label">S1 Consistency</div>
                    </div>
                `;
            });
            contentHTML += '</div>';

            const headers = Object.keys(result.data[0]);
            contentHTML += `<div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>${headers.map(h => `<th>${h.replace('_', ' ').toUpperCase()}</th>`).join('')}</tr>
                    </thead>
                    <tbody>
                        ${result.data.map(row => `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`).join('')}
                    </tbody>
                </table>
            </div>`;
            
            contentDiv.innerHTML = contentHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No sector performance data available</div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="status-message status-error">Error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

async function loadAdvancedMetricsData() {
    const contentDiv = document.getElementById('advanced-metricsContent');
    const loadingDiv = document.getElementById('advanced-metricsLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/advanced-metrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drivers: selectedDrivers.map(d => d.code) })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            let contentHTML = '<h4>⚡ Advanced Telemetry Metrics</h4><div class="metrics-grid">';
            
            result.data.forEach(driver => {
                const teamColor = teamColors[selectedDrivers.find(d => d.code === driver.driver)?.team] || '#808080';
                const rating = driver.overall_rating;
                const ratingColor = rating === 'Excellent' ? '#059669' : rating === 'Good' ? '#d97706' : '#6b7280';
                
                contentHTML += `
                    <div class="metric-card" style="border-left: 4px solid ${teamColor};">
                        <div class="metric-value">${driver.driver}</div>
                        <div class="metric-label">Driver</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" style="color: ${ratingColor};">${driver.overall_rating}</div>
                        <div class="metric-label">Overall Rating</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${driver.aero_efficiency}</div>
                        <div class="metric-label">Aero Efficiency</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${driver.drs_usage}</div>
                        <div class="metric-label">DRS Usage</div>
                    </div>
                `;
            });
            contentHTML += '</div>';

            const headers = Object.keys(result.data[0]);
            contentHTML += `<div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>${headers.map(h => `<th>${h.replace('_', ' ').toUpperCase()}</th>`).join('')}</tr>
                    </thead>
                    <tbody>
                        ${result.data.map(row => `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`).join('')}
                    </tbody>
                </table>
            </div>`;
            
            contentDiv.innerHTML = contentHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No advanced metrics data available</div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="status-message status-error">Error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

function formatLapTime(seconds) {
    if (!seconds || isNaN(seconds)) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = (seconds % 60).toFixed(3);
    return `${minutes}:${remainingSeconds.padStart(6, '0')}`;
}