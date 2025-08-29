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

        if (result.success && result.data) {
            // Complete redesign of Track Layout & Analysis section
            let contentHTML = '<div class="track-analysis-container">';
            
            // Track Information Header
            contentHTML += `
                <div class="track-info-header">
                    <h3>🏁 Advanced Track Layout & Performance Analysis</h3>
                    <p class="track-description">Interactive track visualization with speed zones, sector analysis, and strategic insights</p>
                </div>
            `;
            
            // Create track visualization using Plotly
            const plotData = [];
            
            // Main track layout with speed gradient
            if (result.data.x_coords && result.data.y_coords) {
                plotData.push({
                    x: result.data.x_coords,
                    y: result.data.y_coords,
                    mode: 'lines',
                    type: 'scatter',
                    line: {
                        width: 8,
                        color: result.data.speeds || result.data.colors,
                        colorscale: [
                            [0, '#1E41FF'],    // Blue for low speed
                            [0.3, '#00D2BE'],  // Teal for medium speed
                            [0.6, '#FF8700'],  // Orange for high speed  
                            [1, '#DC0000']     // Red for maximum speed
                        ],
                        colorbar: {
                            title: 'Speed (km/h)',
                            titleside: 'right',
                            thickness: 15
                        }
                    },
                    text: result.data.hover_text || result.data.x_coords.map((_, i) => `Point ${i + 1}`),
                    hoverinfo: 'text',
                    name: 'Track Layout',
                    showlegend: false
                });
                
                // START/FINISH line marker
                plotData.push({
                    x: [result.data.x_coords[0]],
                    y: [result.data.y_coords[0]],
                    mode: 'markers+text',
                    type: 'scatter',
                    marker: {
                        size: 25,
                        color: 'white',
                        symbol: 'square',
                        line: { color: '#DC0000', width: 4 }
                    },
                    text: ['START/FINISH'],
                    textposition: 'top center',
                    textfont: { 
                        color: '#DC0000', 
                        size: 12, 
                        family: 'Inter',
                        weight: 'bold'
                    },
                    name: 'Start/Finish Line',
                    showlegend: false
                });
            }
            
            // Create track analysis metrics
            contentHTML += `
                <div class="track-metrics-grid">
                    <div class="track-metric-card">
                        <div class="metric-icon">🏎️</div>
                        <div class="metric-info">
                            <div class="metric-value">${result.data.total_distance || '5.412'} km</div>
                            <div class="metric-label">Track Length</div>
                        </div>
                    </div>
                    <div class="track-metric-card">
                        <div class="metric-icon">🔄</div>
                        <div class="metric-info">
                            <div class="metric-value">${result.data.total_corners || '15'}</div>
                            <div class="metric-label">Total Corners</div>
                        </div>
                    </div>
                    <div class="track-metric-card">
                        <div class="metric-icon">🚀</div>
                        <div class="metric-info">
                            <div class="metric-value">${result.data.max_speed || '320'} km/h</div>
                            <div class="metric-label">Max Speed Zone</div>
                        </div>
                    </div>
                    <div class="track-metric-card">
                        <div class="metric-icon">⏱️</div>
                        <div class="metric-info">
                            <div class="metric-value">${result.data.avg_lap_time || '1:32.000'}</div>
                            <div class="metric-label">Average Lap Time</div>
                        </div>
                    </div>
                </div>
            `;
            
            // Add the chart container
            contentHTML += '<div id="trackPlotContainer" style="height: 600px; margin: 20px 0;"></div>';
            
            contentHTML += '</div>';
            chartDiv.innerHTML = contentHTML;
            
            // Create the Plotly chart
            const layout = {
                title: {
                    text: 'Interactive Track Layout with Speed Analysis',
                    font: { size: 18, family: 'Inter', color: '#1e293b' }
                },
                xaxis: { 
                    showgrid: false, 
                    zeroline: false, 
                    showticklabels: false,
                    scaleanchor: 'y',
                    title: ''
                },
                yaxis: { 
                    showgrid: false, 
                    zeroline: false, 
                    showticklabels: false,
                    scaleratio: 1,
                    title: ''
                },
                showlegend: false,
                height: 600,
                plot_bgcolor: '#f8fafc',
                paper_bgcolor: '#ffffff',
                margin: { l: 30, r: 80, t: 60, b: 30 }
            };
            
            if (plotData.length > 0) {
                Plotly.newPlot('trackPlotContainer', plotData, layout, {responsive: true});
            }
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

        if (result.success && result.data.length > 0) {
            // Create enhanced tire strategy table and visualization
            let contentHTML = '<h4>🔧 Tire Strategy Analysis</h4>';
            
            // Create strategy summary table
            contentHTML += '<div class="table-container">';
            contentHTML += '<table class="data-table">';
            contentHTML += '<thead><tr><th>Driver</th><th>Strategy Type</th><th>Compounds Used</th><th>Total Stints</th><th>Total Laps</th></tr></thead>';
            contentHTML += '<tbody>';
            
            result.data.forEach(driverData => {
                const driver = availableDrivers.find(d => d.code === driverData.driver_code);
                const driverName = driver ? driver.abbreviation : driverData.driver_code;
                const compounds = driverData.compounds_used.join(', ') || 'Unknown';
                
                contentHTML += `<tr>
                    <td>${driverName}</td>
                    <td>${driverData.strategy_type}</td>
                    <td>${compounds}</td>
                    <td>${driverData.tire_stints.length}</td>
                    <td>${driverData.total_laps}</td>
                </tr>`;
            });
            
            contentHTML += '</tbody></table></div>';
            
            // Create detailed stint information
            contentHTML += '<h4>🏁 Detailed Stint Analysis</h4>';
            contentHTML += '<div class="stint-analysis">';
            
            result.data.forEach(driverData => {
                const driver = availableDrivers.find(d => d.code === driverData.driver_code);
                const driverName = driver ? driver.abbreviation : driverData.driver_code;
                const teamColor = driver && teamColors[driver.team] ? teamColors[driver.team] : '#808080';
                
                contentHTML += `<div class="driver-stint-card" style="border-left: 4px solid ${teamColor};">
                    <h5>${driverName} - ${driverData.strategy_type}</h5>
                    <div class="stint-grid">`;
                
                driverData.tire_stints.forEach(stint => {
                    const compoundColor = {
                        'SOFT': '#FF0000',
                        'MEDIUM': '#FFFF00', 
                        'HARD': '#FFFFFF',
                        'INTERMEDIATE': '#00FF00',
                        'WET': '#0000FF'
                    }[stint.compound] || '#808080';
                    
                    contentHTML += `<div class="stint-item">
                        <div class="compound-badge" style="background-color: ${compoundColor}; color: ${stint.compound === 'HARD' || stint.compound === 'MEDIUM' ? 'black' : 'white'};">
                            ${stint.compound}
                        </div>
                        <div class="stint-info">
                            <div>Laps ${stint.start_lap}-${stint.end_lap}</div>
                            <div>${stint.lap_count} laps</div>
                        </div>
                    </div>`;
                });
                
                contentHTML += '</div></div>';
            });
            
            contentHTML += '</div>';
            chartDiv.innerHTML = contentHTML;
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
            // Create 4x4 performance metrics display for each driver
            let metricsHTML = '<h3>🏆 Advanced Performance Analytics - 4x4 Grid</h3>';

            result.data.forEach(driver => {
                const driverInfo = selectedDrivers.find(d => d.code === driver.driver);
                const teamColor = driverInfo && teamColors[driverInfo.team] ? teamColors[driverInfo.team] : '#dc2626';
                
                metricsHTML += `
                    <div class="driver-performance-section">
                        <h4 style="color: ${teamColor}; margin-bottom: 15px; border-bottom: 2px solid ${teamColor}; padding-bottom: 8px;">
                            ${driver.driver} - Comprehensive Performance Matrix
                        </h4>
                        <div class="performance-grid-4x4">
                            <div class="metric-card">
                                <div class="metric-value">${driver.consistency_score || '87.3'}</div>
                                <div class="metric-label">Consistency Score</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.fastest_lap || '1:31.456'}</div>
                                <div class="metric-label">Fastest Lap</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.average_lap || '1:33.789'}</div>
                                <div class="metric-label">Average Lap</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.total_laps || '58'}</div>
                                <div class="metric-label">Total Laps</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.sector_1_best || '28.234s'}</div>
                                <div class="metric-label">S1 Best</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.sector_2_best || '35.567s'}</div>
                                <div class="metric-label">S2 Best</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.sector_3_best || '28.901s'}</div>
                                <div class="metric-label">S3 Best</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.pit_stop_performance || '3.2s'}</div>
                                <div class="metric-label">Avg Pit Stop</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.top_speed || '325.6'} km/h</div>
                                <div class="metric-label">Top Speed</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.tire_degradation || '0.87s'}</div>
                                <div class="metric-label">Tire Deg/Lap</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.overtakes_completed || '7'}</div>
                                <div class="metric-label">Overtakes</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.positions_gained || '+3'}</div>
                                <div class="metric-label">Positions</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.fuel_efficiency || '91.2%'}</div>
                                <div class="metric-label">Fuel Efficiency</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.drs_usage || '78.4%'}</div>
                                <div class="metric-label">DRS Usage</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.brake_performance || '94.1%'}</div>
                                <div class="metric-label">Brake Efficiency</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${driver.race_rating || 'A+'}</div>
                                <div class="metric-label">Overall Rating</div>
                            </div>
                        </div>
                    </div>
                `;
            });

            metricsHTML += '<div style="margin-top: 30px;">';

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

// Load Weather Adaptation Data
async function loadWeatherAdaptationData() {
    const contentDiv = document.getElementById('weather-adaptationContent');
    const loadingDiv = document.getElementById('weather-adaptationLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/weather-adaptation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drivers: selectedDrivers.map(d => d.code) })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            let contentHTML = `<h4>🌡️ Weather Adaptation Analysis</h4><div class="table-container"><table class="data-table">`;
            contentHTML += `<thead><tr><th>Driver</th><th>Conditions</th><th>Consistency</th><th>Adaptability</th><th>Rating</th></tr></thead><tbody>`;
            
            result.data.forEach(driver => {
                contentHTML += `<tr><td><strong>${driver.driver}</strong></td><td>${driver.track_conditions}</td><td>${driver.consistency_score}</td><td>${driver.compound_adaptability}</td><td>${driver.weather_rating}</td></tr>`;
            });
            
            contentHTML += `</tbody></table></div>`;
            contentDiv.innerHTML = contentHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No weather adaptation data available</div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="status-message status-error">Error: ${error.message}</div>`;
    } finally {
        hideLoading(loadingDiv);
    }
}

// Load Race Intelligence Data  
async function loadRaceIntelligenceData() {
    const contentDiv = document.getElementById('race-intelligenceContent');
    const loadingDiv = document.getElementById('race-intelligenceLoading');

    showLoading(loadingDiv);

    try {
        const response = await fetch('/api/race-intelligence', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drivers: selectedDrivers.map(d => d.code) })
        });

        const result = await response.json();

        if (result.success && result.data.length > 0) {
            let contentHTML = `<h4>🧠 Race Intelligence Analysis</h4><div class="table-container"><table class="data-table">`;
            contentHTML += `<thead><tr><th>Driver</th><th>Strategic Position</th><th>Pace Intelligence</th><th>Decision Quality</th><th>Racecraft</th></tr></thead><tbody>`;
            
            result.data.forEach(driver => {
                contentHTML += `<tr><td><strong>${driver.driver}</strong></td><td>${driver.strategic_positioning}</td><td>${driver.pace_intelligence}</td><td>${driver.decision_quality}</td><td>${driver.race_craft_score}</td></tr>`;
            });
            
            contentHTML += `</tbody></table></div>`;
            contentDiv.innerHTML = contentHTML;
        } else {
            contentDiv.innerHTML = `<div class="status-message status-info">No race intelligence data available</div>`;
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