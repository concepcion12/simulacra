/**
 * Real-time Simulation Dashboard
 * Displays live simulation progress and metrics
 */

class RealtimeDashboard {
    constructor() {
        this.currentSimulation = null;
        this.isInitialized = false;
        this.charts = {};
        this.updateInterval = null;
    }
    
    initialize(simulationData = null) {
        if (this.isInitialized && !simulationData) {
            return;
        }
        
        console.log('Initializing Realtime Dashboard...');
        this.loadDashboardTemplate();
        this.setupEventHandlers();
        
        if (simulationData) {
            this.currentSimulation = simulationData;
            this.startMonitoring();
        }
        
        this.isInitialized = true;
    }
    
    loadDashboardTemplate() {
        const runSection = document.getElementById('runSection');
        runSection.innerHTML = `
            <div class="container-fluid mt-4">
                <!-- Simulation Header -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">
                                    <i class="fas fa-play-circle"></i> 
                                    <span id="simulationTitle">Simulation Dashboard</span>
                                </h5>
                                <div class="simulation-controls">
                                    <button class="btn btn-sm btn-warning" id="pauseBtn" style="display: none;">
                                        <i class="fas fa-pause"></i> Pause
                                    </button>
                                    <button class="btn btn-sm btn-success" id="resumeBtn" style="display: none;">
                                        <i class="fas fa-play"></i> Resume
                                    </button>
                                    <button class="btn btn-sm btn-danger" id="stopBtn" style="display: none;">
                                        <i class="fas fa-stop"></i> Stop
                                    </button>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-3">
                                        <div class="progress mb-2">
                                            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                                 id="simulationProgress" role="progressbar" style="width: 0%">
                                            </div>
                                        </div>
                                        <small class="text-muted">
                                            <span id="progressText">Initializing...</span>
                                        </small>
                                    </div>
                                    <div class="col-md-2">
                                        <div class="text-center">
                                            <div class="h5 mb-0" id="currentMonth">-</div>
                                            <small class="text-muted">Current Month</small>
                                        </div>
                                    </div>
                                    <div class="col-md-2">
                                        <div class="text-center">
                                            <div class="h5 mb-0" id="currentRound">-</div>
                                            <small class="text-muted">Current Round</small>
                                        </div>
                                    </div>
                                    <div class="col-md-2">
                                        <div class="text-center">
                                            <div class="h5 mb-0" id="totalAgents">-</div>
                                            <small class="text-muted">Total Agents</small>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="text-center">
                                            <div class="h5 mb-0" id="elapsedTime">00:00:00</div>
                                            <small class="text-muted">Elapsed Time</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Metrics Dashboard -->
                <div class="row">
                    <!-- Key Metrics Cards -->
                    <div class="col-md-3 mb-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <i class="fas fa-briefcase fa-2x text-primary mb-2"></i>
                                <h4 class="card-title mb-0" id="employmentRate">-</h4>
                                <p class="card-text small text-muted">Employment Rate</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <i class="fas fa-dollar-sign fa-2x text-success mb-2"></i>
                                <h4 class="card-title mb-0" id="avgWealth">-</h4>
                                <p class="card-text small text-muted">Average Wealth</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <i class="fas fa-home fa-2x text-info mb-2"></i>
                                <h4 class="card-title mb-0" id="homelessRate">-</h4>
                                <p class="card-text small text-muted">Homeless Rate</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <i class="fas fa-pills fa-2x text-danger mb-2"></i>
                                <h4 class="card-title mb-0" id="addictionRate">-</h4>
                                <p class="card-text small text-muted">Addiction Rate</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Charts Row -->
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">Population Trends</h6>
                            </div>
                            <div class="card-body">
                                <canvas id="populationChart" height="300"></canvas>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">Economic Indicators</h6>
                            </div>
                            <div class="card-body">
                                <canvas id="economicChart" height="300"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Agent Activity Log -->
                <div class="row">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">Recent Activity</h6>
                            </div>
                            <div class="card-body">
                                <div id="activityLog" style="height: 200px; overflow-y: auto;">
                                    <p class="text-muted">Waiting for simulation data...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Export Panel -->
                <div class="row mt-3">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">Quick Export</h6>
                            </div>
                            <div class="card-body">
                                <div class="btn-group" role="group">
                                    <button type="button" class="btn btn-outline-primary" id="exportCSV">
                                        <i class="fas fa-file-csv"></i> Export CSV
                                    </button>
                                    <button type="button" class="btn btn-outline-primary" id="exportJSON">
                                        <i class="fas fa-file-code"></i> Export JSON
                                    </button>
                                    <button type="button" class="btn btn-outline-primary" id="exportReport">
                                        <i class="fas fa-file-alt"></i> Generate Report
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    setupEventHandlers() {
        // Control buttons
        document.getElementById('pauseBtn')?.addEventListener('click', () => {
            this.pauseSimulation();
        });
        
        document.getElementById('resumeBtn')?.addEventListener('click', () => {
            this.resumeSimulation();
        });
        
        document.getElementById('stopBtn')?.addEventListener('click', () => {
            this.stopSimulation();
        });
        
        // Export buttons
        document.getElementById('exportCSV')?.addEventListener('click', () => {
            this.exportData('csv');
        });
        
        document.getElementById('exportJSON')?.addEventListener('click', () => {
            this.exportData('json');
        });
        
        document.getElementById('exportReport')?.addEventListener('click', () => {
            this.exportData('report');
        });
    }
    
    startMonitoring() {
        if (!this.currentSimulation) return;
        
        // Update simulation title
        const titleEl = document.getElementById('simulationTitle');
        if (titleEl) {
            titleEl.textContent = `${this.currentSimulation.config?.city_name || 'Simulation'} - Running`;
        }
        
        // Show control buttons
        document.getElementById('pauseBtn').style.display = 'inline-block';
        document.getElementById('stopBtn').style.display = 'inline-block';
        
        // Start progress tracking
        this.startTime = Date.now();
        this.updateElapsedTime();
        
        // Initialize charts
        this.initializeCharts();
        
        // Start polling for updates
        this.startProgressPolling();
    }
    
    updateSimulationData(data) {
        // Update progress bar
        const progressBar = document.getElementById('simulationProgress');
        const progressText = document.getElementById('progressText');
        
        if (progressBar && data.progress !== undefined) {
            const percentage = Math.round(data.progress * 100);
            progressBar.style.width = `${percentage}%`;
            progressBar.textContent = `${percentage}%`;
        }
        
        if (progressText) {
            progressText.textContent = `Round ${data.round || 0} of ${data.total_rounds || 0}`;
        }
        
        // Update current stats
        this.updateElement('currentMonth', data.current_month || '-');
        this.updateElement('currentRound', data.round || '-');
        
        // Update metrics if available
        if (data.metrics) {
            this.updateMetrics(data.metrics);
        }
        
        // Add to activity log
        this.addActivityLog(`Round ${data.round}: ${this.formatMetricsSummary(data.metrics)}`);
    }
    
    updateMetrics(metrics) {
        // Update metric cards
        this.updateElement('employmentRate', this.formatPercentage(metrics.employment_rate));
        this.updateElement('avgWealth', this.formatCurrency(metrics.avg_wealth));
        this.updateElement('homelessRate', this.formatPercentage(metrics.homeless_rate));
        this.updateElement('addictionRate', this.formatPercentage(metrics.addiction_rate));
        
        // Update charts
        this.updateCharts(metrics);
    }
    
    initializeCharts() {
        // Population trends chart
        const popCtx = document.getElementById('populationChart');
        if (popCtx && window.Chart) {
            this.charts.population = new Chart(popCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Employed',
                            data: [],
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1
                        },
                        {
                            label: 'Homeless',
                            data: [],
                            borderColor: 'rgb(255, 99, 132)',
                            tension: 0.1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
        
        // Economic indicators chart
        const econCtx = document.getElementById('economicChart');
        if (econCtx && window.Chart) {
            this.charts.economic = new Chart(econCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Average Wealth',
                            data: [],
                            borderColor: 'rgb(54, 162, 235)',
                            tension: 0.1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }
    
    updateCharts(metrics) {
        const round = metrics.current_round || Date.now();
        
        // Update population chart
        if (this.charts.population) {
            this.charts.population.data.labels.push(round);
            this.charts.population.data.datasets[0].data.push(metrics.employment_rate * 100);
            this.charts.population.data.datasets[1].data.push(metrics.homeless_rate * 100);
            
            // Keep only last 50 data points
            if (this.charts.population.data.labels.length > 50) {
                this.charts.population.data.labels.shift();
                this.charts.population.data.datasets.forEach(dataset => dataset.data.shift());
            }
            
            this.charts.population.update('none');
        }
        
        // Update economic chart
        if (this.charts.economic) {
            this.charts.economic.data.labels.push(round);
            this.charts.economic.data.datasets[0].data.push(metrics.avg_wealth);
            
            if (this.charts.economic.data.labels.length > 50) {
                this.charts.economic.data.labels.shift();
                this.charts.economic.data.datasets.forEach(dataset => dataset.data.shift());
            }
            
            this.charts.economic.update('none');
        }
    }
    
    addActivityLog(message) {
        const logContainer = document.getElementById('activityLog');
        if (!logContainer) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = 'mb-1';
        logEntry.innerHTML = `<small class="text-muted">${timestamp}</small> ${message}`;
        
        logContainer.appendChild(logEntry);
        
        // Auto-scroll to bottom
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Limit log entries
        const entries = logContainer.children;
        if (entries.length > 100) {
            logContainer.removeChild(entries[0]);
        }
    }
    
    updateElapsedTime() {
        if (!this.startTime) return;
        
        const updateTimer = () => {
            const elapsed = Date.now() - this.startTime;
            const hours = Math.floor(elapsed / 3600000);
            const minutes = Math.floor((elapsed % 3600000) / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            
            const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            this.updateElement('elapsedTime', timeString);
        };
        
        updateTimer();
        this.elapsedTimeInterval = setInterval(updateTimer, 1000);
    }
    
    startProgressPolling() {
        if (!this.currentSimulation) return;
        
        this.progressInterval = setInterval(async () => {
            try {
                const status = await app.apiCall(`/api/simulation/${this.currentSimulation.simulation_id}/status`);
                
                if (status.status === 'completed') {
                    this.handleSimulationComplete();
                } else if (status.status === 'error') {
                    this.handleSimulationError(status.error);
                }
            } catch (error) {
                console.error('Error polling simulation status:', error);
            }
        }, 2000); // Poll every 2 seconds
    }
    
    handleSimulationComplete() {
        clearInterval(this.progressInterval);
        clearInterval(this.elapsedTimeInterval);
        
        const titleEl = document.getElementById('simulationTitle');
        if (titleEl) {
            titleEl.textContent = titleEl.textContent.replace('Running', 'Completed');
        }
        
        // Hide control buttons
        document.getElementById('pauseBtn').style.display = 'none';
        document.getElementById('resumeBtn').style.display = 'none';
        document.getElementById('stopBtn').style.display = 'none';
        
        // Show completion message
        app.showNotification('Simulation completed successfully!', 'success');
        
        // Enable analysis section
        setTimeout(() => {
            app.showNotification('Data analysis tools are now available', 'info');
        }, 2000);
    }
    
    handleSimulationError(error) {
        clearInterval(this.progressInterval);
        clearInterval(this.elapsedTimeInterval);
        
        app.showNotification(`Simulation error: ${error}`, 'error');
        this.addActivityLog(`Error: ${error}`);
    }
    
    // Control methods
    async pauseSimulation() {
        if (!this.currentSimulation) return;

        try {
            const response = await app.apiCall('/api/simulation-control', 'POST', { action: 'pause' });

            if (response.status === 'paused') {
                clearInterval(this.progressInterval);
                clearInterval(this.elapsedTimeInterval);

                document.getElementById('pauseBtn').style.display = 'none';
                document.getElementById('resumeBtn').style.display = 'inline-block';

                this.addActivityLog('Simulation paused');
                app.showNotification('Simulation paused', 'info');
            } else {
                app.showNotification('Unable to pause simulation', 'warning');
            }
        } catch (error) {
            console.error('Pause error:', error);
            app.showNotification('Error pausing simulation', 'error');
        }
    }

    async resumeSimulation() {
        if (!this.currentSimulation) return;

        try {
            const response = await app.apiCall('/api/simulation-control', 'POST', { action: 'resume' });

            if (response.status === 'running') {
                document.getElementById('resumeBtn').style.display = 'none';
                document.getElementById('pauseBtn').style.display = 'inline-block';

                this.updateElapsedTime();
                this.startProgressPolling();

                this.addActivityLog('Simulation resumed');
                app.showNotification('Simulation resumed', 'success');
            } else {
                app.showNotification('Unable to resume simulation', 'warning');
            }
        } catch (error) {
            console.error('Resume error:', error);
            app.showNotification('Error resuming simulation', 'error');
        }
    }

    async stopSimulation() {
        if (confirm('Are you sure you want to stop the simulation? This cannot be undone.')) {
            try {
                const response = await app.apiCall('/api/simulation-control', 'POST', { action: 'stop' });

                if (response.status === 'stopped') {
                    clearInterval(this.progressInterval);
                    clearInterval(this.elapsedTimeInterval);

                    document.getElementById('pauseBtn').style.display = 'none';
                    document.getElementById('resumeBtn').style.display = 'none';
                    document.getElementById('stopBtn').style.display = 'none';

                    const titleEl = document.getElementById('simulationTitle');
                    if (titleEl) {
                        titleEl.textContent = titleEl.textContent.replace('Running', 'Stopped');
                    }

                    this.addActivityLog('Simulation stopped');
                    app.showNotification('Simulation stopped', 'info');
                } else {
                    app.showNotification('Unable to stop simulation', 'warning');
                }
            } catch (error) {
                console.error('Stop error:', error);
                app.showNotification('Error stopping simulation', 'error');
            }
        }
    }
    
    async exportData(format) {
        if (!this.currentSimulation) {
            app.showNotification('No active simulation to export', 'warning');
            return;
        }
        
        try {
            const response = await app.apiCall(`/api/export/${this.currentSimulation.simulation_id}/${format}`, 'POST');
            
            if (response.export_path) {
                app.showNotification(`Data exported successfully: ${response.export_path}`, 'success');
            } else {
                app.showNotification('Export failed', 'error');
            }
        } catch (error) {
            console.error('Export error:', error);
            app.showNotification('Error exporting data', 'error');
        }
    }
    
    // Utility methods
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
    
    formatPercentage(value) {
        if (value === undefined || value === null) return '-';
        return `${Math.round(value * 100)}%`;
    }
    
    formatCurrency(value) {
        if (value === undefined || value === null) return '-';
        return `$${Math.round(value).toLocaleString()}`;
    }
    
    formatMetricsSummary(metrics) {
        if (!metrics) return 'No metrics available';
        
        return `Employment: ${this.formatPercentage(metrics.employment_rate)}, ` +
               `Wealth: ${this.formatCurrency(metrics.avg_wealth)}, ` +
               `Homeless: ${this.formatPercentage(metrics.homeless_rate)}`;
    }
    
    cleanup() {
        // Clear intervals
        if (this.progressInterval) clearInterval(this.progressInterval);
        if (this.elapsedTimeInterval) clearInterval(this.elapsedTimeInterval);
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) chart.destroy();
        });
        this.charts = {};
    }
}

// Make RealtimeDashboard available globally
window.RealtimeDashboard = RealtimeDashboard; 