// F1 Analysis Platform JavaScript

class F1App {
    constructor() {
        this.currentSession = null;
        this.selectedDrivers = [];
        this.availableDrivers = [];
        this.sessionData = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadGrandPrixList();
        this.showSection('session-selection');
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const section = e.target.dataset.section;
                this.showSection(section);
                this.updateActiveNav(e.target);
            });
        });

        // Session controls
        document.getElementById('year-select').addEventListener('change', () => {
            this.loadGrandPrixList();
        });

        document.getElementById('load-session').addEventListener('click', () => {
            this.loadSession();
        });

        // Telemetry controls
        document.getElementById('generate-telemetry').addEventListener('click', () => {
            this.generateTelemetryPlot();
        });

        // Driver selection
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('driver-card')) {
                this.toggleDriverSelection(e.target);
            }
        });
    }

    showSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Show driver selection if session is loaded and not on session-selection
        const driverSelection = document.getElementById('driver-selection');
        if (this.currentSession && sectionId !== 'session-selection') {
            driverSelection.classList.remove('hidden');
        } else {
            driverSelection.classList.add('hidden');
        }
    }

    updateActiveNav(activeButton) {
        document.querySelectorAll('.nav-button').forEach(button => {
            button.classList.remove('active');
        });
        activeButton.classList.add('active');
    }

    async loadGrandPrixList() {
        const year = document.getElementById('year-select').value;
        const gpSelect = document.getElementById('gp-select');
        
        try {
            const response = await fetch(`/api/grandprix?year=${year}`);
            const grandPrixList = await response.json();
            
            gpSelect.innerHTML = '<option value="">انتخاب کنید...</option>';
            grandPrixList.forEach(gp => {
                const option = document.createElement('option');
                option.value = gp.value;
                option.textContent = gp.name;
                gpSelect.appendChild(option);
            });
        } catch (error) {
            console.error('خطا در بارگذاری لیست گرندپری:', error);
            this.showError('خطا در بارگذاری لیست گرندپری');
        }
    }

    async loadSession() {
        const year = document.getElementById('year-select').value;
        const gp = document.getElementById('gp-select').value;
        const session = document.getElementById('session-select').value;

        if (!year || !gp || !session) {
            this.showError('لطفاً تمام فیلدها را انتخاب کنید');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch('/api/load-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    year: parseInt(year),
                    grand_prix: gp,
                    session_type: session
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.currentSession = result.session_data;
                this.availableDrivers = result.drivers;
                this.sessionData = result;
                
                this.displaySessionInfo(result);
                this.createDriverSelection(result.drivers);
                this.showSuccess('داده‌ها با موفقیت بارگذاری شدند');
                
                // Enable navigation buttons
                document.querySelectorAll('.nav-button').forEach(button => {
                    if (button.dataset.section !== 'session-selection') {
                        button.disabled = false;
                    }
                });
            } else {
                this.showError(result.error || 'خطا در بارگذاری داده‌ها');
            }
        } catch (error) {
            console.error('خطا در بارگذاری جلسه:', error);
            this.showError('خطا در ارتباط با سرور');
        } finally {
            this.showLoading(false);
        }
    }

    displaySessionInfo(sessionData) {
        const sessionInfo = document.getElementById('session-info');
        const sessionDetails = document.getElementById('session-details');
        
        sessionDetails.innerHTML = `
            <div class="session-detail-grid">
                <div class="session-detail-item">
                    <span class="detail-label">گرندپری:</span>
                    <span class="detail-value">${sessionData.grand_prix}</span>
                </div>
                <div class="session-detail-item">
                    <span class="detail-label">جلسه:</span>
                    <span class="detail-value">${sessionData.session_type}</span>
                </div>
                <div class="session-detail-item">
                    <span class="detail-label">سال:</span>
                    <span class="detail-value">${sessionData.year}</span>
                </div>
                <div class="session-detail-item">
                    <span class="detail-label">تعداد راننده‌ها:</span>
                    <span class="detail-value">${sessionData.drivers.length}</span>
                </div>
            </div>
        `;
        
        sessionInfo.classList.remove('hidden');
    }

    createDriverSelection(drivers) {
        const driverList = document.getElementById('driver-list');
        driverList.innerHTML = '';

        drivers.forEach(driver => {
            const driverCard = document.createElement('div');
            driverCard.className = 'driver-card';
            driverCard.dataset.driver = driver.abbreviation;
            
            driverCard.innerHTML = `
                <div class="driver-name">${driver.full_name}</div>
                <div class="driver-team" style="color: ${driver.team_color}">${driver.team}</div>
                <div class="driver-number">#${driver.driver_number}</div>
            `;
            
            driverList.appendChild(driverCard);
        });

        document.getElementById('driver-selection').classList.remove('hidden');
    }

    toggleDriverSelection(driverCard) {
        const driverAbbr = driverCard.dataset.driver;
        
        if (driverCard.classList.contains('selected')) {
            driverCard.classList.remove('selected');
            this.selectedDrivers = this.selectedDrivers.filter(d => d !== driverAbbr);
        } else {
            if (this.selectedDrivers.length < 6) { // Limit to 6 drivers
                driverCard.classList.add('selected');
                this.selectedDrivers.push(driverAbbr);
            } else {
                this.showError('حداکثر 6 راننده قابل انتخاب است');
            }
        }

        this.updateAnalysisSections();
    }

    async generateTelemetryPlot() {
        if (this.selectedDrivers.length === 0) {
            this.showError('لطفاً حداقل یک راننده انتخاب کنید');
            return;
        }

        const telemetryType = document.getElementById('telemetry-type').value;
        
        try {
            const response = await fetch('/api/telemetry', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    drivers: this.selectedDrivers,
                    telemetry_type: telemetryType
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.displayPlot('telemetry-plot', result.plot_data);
            } else {
                this.showError(result.error || 'خطا در تولید نمودار');
            }
        } catch (error) {
            console.error('خطا در تولید نمودار تله‌متری:', error);
            this.showError('خطا در ارتباط با سرور');
        }
    }

    async updateAnalysisSections() {
        if (this.selectedDrivers.length === 0) return;

        // Update all analysis sections
        await Promise.all([
            this.loadTireStrategy(),
            this.loadRaceProgression(),
            this.loadTrackDominance()
        ]);
    }

    async loadTireStrategy() {
        try {
            const response = await fetch('/api/tire-strategy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    drivers: this.selectedDrivers
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.displayPlot('tire-plot', result.plot_data);
                this.displayTireDetails(result.tire_details);
            }
        } catch (error) {
            console.error('خطا در بارگذاری استراتژی تایر:', error);
        }
    }

    async loadRaceProgression() {
        try {
            const response = await fetch('/api/race-progression', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    drivers: this.selectedDrivers
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.displayPlot('race-plot', result.plot_data);
                this.displayRaceStats(result.race_stats);
            }
        } catch (error) {
            console.error('خطا در بارگذاری پیشرفت مسابقه:', error);
        }
    }

    async loadTrackDominance() {
        try {
            const response = await fetch('/api/track-dominance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    drivers: this.selectedDrivers
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.displayPlot('track-plot', result.plot_data);
            }
        } catch (error) {
            console.error('خطا در بارگذاری تسلط بر پیست:', error);
        }
    }

    displayPlot(containerId, plotData) {
        const container = document.getElementById(containerId);
        Plotly.newPlot(container, plotData.data, plotData.layout, {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToAdd: ['downloadPlot'],
            displaylogo: false
        });
    }

    displayTireDetails(tireDetails) {
        const container = document.getElementById('tire-details');
        if (!tireDetails || tireDetails.length === 0) {
            container.innerHTML = '<p>اطلاعات تایر در دسترس نیست</p>';
            return;
        }

        let html = '<h3>جزئیات استراتژی تایر</h3><div class="tire-summary">';
        
        // Group by driver
        const driverTires = {};
        tireDetails.forEach(stint => {
            if (!driverTires[stint.driver]) {
                driverTires[stint.driver] = [];
            }
            driverTires[stint.driver].push(stint);
        });

        Object.entries(driverTires).forEach(([driver, stints]) => {
            html += `<div class="driver-tire-summary">
                <h4>${driver}</h4>
                <div class="tire-stints">`;
            
            stints.forEach(stint => {
                const compoundClass = `tire-${stint.compound.toLowerCase()}`;
                html += `<span class="tire-compound ${compoundClass}">
                    ${stint.compound} (${stint.length} دور)
                </span>`;
            });
            
            html += '</div></div>';
        });

        html += '</div>';
        container.innerHTML = html;
    }

    displayRaceStats(raceStats) {
        const container = document.getElementById('race-stats');
        if (!raceStats) {
            container.innerHTML = '';
            return;
        }

        let html = '';
        raceStats.forEach(stat => {
            html += `<div class="stat-card">
                <h4>${stat.title}</h4>
                <div class="stat-value">${stat.value}</div>
                <div class="stat-description">${stat.description}</div>
            </div>`;
        });

        container.innerHTML = html;
    }

    showLoading(show) {
        const loading = document.getElementById('loading-indicator');
        if (show) {
            loading.classList.remove('hidden');
        } else {
            loading.classList.add('hidden');
        }
    }

    showError(message) {
        // Create or update error message display
        this.showMessage(message, 'error');
    }

    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    showMessage(message, type) {
        // Remove existing messages
        const existingMessages = document.querySelectorAll('.message');
        existingMessages.forEach(msg => msg.remove());

        // Create new message
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        
        // Style based on type
        if (type === 'error') {
            messageDiv.style.background = 'rgba(255, 0, 0, 0.1)';
            messageDiv.style.borderColor = '#ff0000';
            messageDiv.style.color = '#ff6666';
        } else if (type === 'success') {
            messageDiv.style.background = 'rgba(0, 255, 0, 0.1)';
            messageDiv.style.borderColor = '#00ff00';
            messageDiv.style.color = '#66ff66';
        }
        
        messageDiv.style.cssText += `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border: 2px solid;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            z-index: 1000;
            font-weight: 500;
            animation: slideInRight 0.3s ease-out;
        `;

        document.body.appendChild(messageDiv);

        // Remove after 5 seconds
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new F1App();
});

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .session-detail-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .session-detail-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
    }
    
    .detail-label {
        font-weight: 600;
        color: #e10600;
    }
    
    .detail-value {
        color: #ffffff;
    }
    
    .driver-number {
        font-size: 0.8rem;
        opacity: 0.7;
        margin-top: 0.25rem;
    }
    
    .tire-summary {
        margin-top: 1rem;
    }
    
    .driver-tire-summary {
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    .driver-tire-summary h4 {
        color: #e10600;
        margin-bottom: 0.5rem;
    }
    
    .tire-stints {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
`;
document.head.appendChild(style);