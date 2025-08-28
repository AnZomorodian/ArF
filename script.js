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
        case 'championship':
            loadChampionshipData();
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
            // Create track dominance map
            const plotData = [{
                x: result.x_coords,
                y: result.y_coords,
                mode: 'markers',
                type: 'scatter',
                marker: {
                    color: result.colors,
                    size: 8,
                    colorscale: 'Viridis'
                },
                text: result.hover_text,
                hoverinfo: 'text'
            }];

            const layout = {
                title: 'Track Dominance Map',
                xaxis: { title: 'X Position', showgrid: false },
                yaxis: { title: 'Y Position', showgrid: false },
                showlegend: false,
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
    await loadGenericAnalysisData('/api/corner-analysis', 'cornersContent', 'cornersLoading');
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

function formatLapTime(seconds) {
    if (!seconds || isNaN(seconds)) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = (seconds % 60).toFixed(3);
    return `${minutes}:${remainingSeconds.padStart(6, '0')}`;
}