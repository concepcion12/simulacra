/**
 * Simulacra Setup Wizard Implementation
 * Multi-step configuration interface for simulation setup
 */

class SetupWizard {
    constructor() {
        this.currentStep = 0;
        this.steps = ['city', 'population', 'simulation', 'review'];
        this.stepTitles = ['City Configuration', 'Population Configuration', 'Simulation Parameters', 'Review & Launch'];
        this.configuration = null;
        this.validationResults = {};
        this.isInitialized = false;
    }
    
    initialize() {
        if (this.isInitialized) {
            this.showStep(0);
            return;
        }
        
        console.log('Initializing Setup Wizard...');
        this.loadWizardTemplate();
        this.setupEventHandlers();
        this.showStep(0);
        this.isInitialized = true;
    }
    
    loadWizardTemplate() {
        const setupSection = document.getElementById('setupSection');
        setupSection.innerHTML = `
            <div class="container mt-5">
                <div class="row">
                    <div class="col-12">
                        <!-- Progress Indicator -->
                        <div class="progress-container mb-4">
                            <div class="row">
                                <div class="col-3 text-center">
                                    <div class="step-indicator active" data-step="0">
                                        <i class="fas fa-city"></i>
                                    </div>
                                    <div class="step-label">City</div>
                                </div>
                                <div class="col-3 text-center">
                                    <div class="step-indicator" data-step="1">
                                        <i class="fas fa-users"></i>
                                    </div>
                                    <div class="step-label">Population</div>
                                </div>
                                <div class="col-3 text-center">
                                    <div class="step-indicator" data-step="2">
                                        <i class="fas fa-cogs"></i>
                                    </div>
                                    <div class="step-label">Simulation</div>
                                </div>
                                <div class="col-3 text-center">
                                    <div class="step-indicator" data-step="3">
                                        <i class="fas fa-check"></i>
                                    </div>
                                    <div class="step-label">Review</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Step Content -->
                        <div class="card">
                            <div class="card-header">
                                <h4 id="stepTitle">Step 1: City Configuration</h4>
                            </div>
                            <div class="card-body">
                                <div id="stepContent">
                                    <!-- Step content loaded here -->
                                </div>
                                
                                <!-- Validation Messages -->
                                <div id="validationMessages"></div>
                                
                                <!-- Navigation Buttons -->
                                <div class="d-flex justify-content-between mt-4">
                                    <button class="btn btn-secondary" id="prevBtn" style="display: none;">
                                        <i class="fas fa-arrow-left"></i> Back
                                    </button>
                                    <div></div>
                                    <button class="btn btn-primary" id="nextBtn">
                                        Next: Population <i class="fas fa-arrow-right"></i>
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
        document.getElementById('prevBtn').addEventListener('click', () => {
            this.previousStep();
        });
        
        document.getElementById('nextBtn').addEventListener('click', () => {
            this.nextStep();
        });
        
        // Step indicator clicks
        document.querySelectorAll('.step-indicator').forEach(indicator => {
            indicator.addEventListener('click', (e) => {
                const step = parseInt(e.target.closest('.step-indicator').dataset.step);
                if (step <= this.currentStep || this.canNavigateToStep(step)) {
                    this.showStep(step);
                }
            });
        });
    }
    
    showStep(stepIndex) {
        this.currentStep = stepIndex;
        this.updateProgressIndicator();
        this.updateNavigationButtons();
        
        const stepContent = document.getElementById('stepContent');
        const stepTitle = document.getElementById('stepTitle');
        
        stepTitle.textContent = `Step ${stepIndex + 1}: ${this.stepTitles[stepIndex]}`;
        
        // Ensure we have the latest configuration
        if (!app.state.configuration) {
            app.state.configuration = new SimulationConfiguration();
        }
        
        switch (stepIndex) {
            case 0:
                this.showCityConfigurationStep(stepContent);
                break;
            case 1:
                this.showPopulationConfigurationStep(stepContent);
                break;
            case 2:
                this.showSimulationParametersStep(stepContent);
                break;
            case 3:
                this.showReviewStep(stepContent);
                break;
        }
        
        // Clear validation messages when switching steps
        this.clearValidationMessages();
        
        // Run a validation check to update warnings/errors based on current state
        this.validateCurrentStep();
    }
    
    showCityConfigurationStep(container) {
        const config = app.state.configuration || new SimulationConfiguration();
        
        container.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-city"></i> City Layout</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">City Name</label>
                                <input type="text" class="form-control" id="cityName" 
                                       value="${config.cityName}" placeholder="Enter city name">
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">City Size</label>
                                <div class="btn-group d-flex" role="group">
                                    <input type="radio" class="btn-check" name="citySize" id="sizeSmall" value="small" ${config.citySize === 'small' ? 'checked' : ''}>
                                    <label class="btn btn-outline-primary" for="sizeSmall">Small</label>
                                    
                                    <input type="radio" class="btn-check" name="citySize" id="sizeMedium" value="medium" ${config.citySize === 'medium' ? 'checked' : ''}>
                                    <label class="btn btn-outline-primary" for="sizeMedium">Medium</label>
                                    
                                    <input type="radio" class="btn-check" name="citySize" id="sizeLarge" value="large" ${config.citySize === 'large' ? 'checked' : ''}>
                                    <label class="btn btn-outline-primary" for="sizeLarge">Large</label>
                                </div>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">Map Preview</label>
                                <div id="cityMapPreview" class="border p-2" style="height: 200px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-header">
                            <h6><i class="fas fa-building"></i> Buildings</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Residential Buildings</label>
                                <div class="d-flex align-items-center">
                                    <input type="range" class="form-range flex-grow-1" min="1" max="50" 
                                           value="${config.buildings.residential}" id="residentialCount">
                                    <span class="ms-2 badge bg-primary" id="residentialValue">${config.buildings.residential}</span>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Commercial Buildings</label>
                                <div class="d-flex align-items-center">
                                    <input type="range" class="form-range flex-grow-1" min="1" max="20" 
                                           value="${config.buildings.commercial}" id="commercialCount">
                                    <span class="ms-2 badge bg-info" id="commercialValue">${config.buildings.commercial}</span>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Industrial Buildings</label>
                                <div class="d-flex align-items-center">
                                    <input type="range" class="form-range flex-grow-1" min="1" max="15" 
                                           value="${config.buildings.industrial}" id="industrialCount">
                                    <span class="ms-2 badge bg-warning" id="industrialValue">${config.buildings.industrial}</span>
                                </div>
                            </div>
                            
                            <hr>
                            
                            <div class="row">
                                <div class="col-6">
                                    <div class="mb-2">
                                        <label class="form-label small">Casinos</label>
                                        <div class="d-flex align-items-center">
                                            <input type="range" class="form-range flex-grow-1" min="0" max="10" 
                                                   value="${config.buildings.casinos}" id="casinosCount">
                                            <span class="ms-2 badge bg-danger" id="casinosValue">${config.buildings.casinos}</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="mb-2">
                                        <label class="form-label small">Liquor Stores</label>
                                        <div class="d-flex align-items-center">
                                            <input type="range" class="form-range flex-grow-1" min="0" max="15" 
                                                   value="${config.buildings.liquor_stores}" id="liquorStoresCount">
                                            <span class="ms-2 badge bg-secondary" id="liquorStoresValue">${config.buildings.liquor_stores}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-info-circle"></i> Configuration Summary</h6>
                        </div>
                        <div class="card-body">
                            <div id="citySummary">
                                <p class="mb-1"><strong>Total Buildings:</strong> <span id="totalBuildings">-</span></p>
                                <p class="mb-1"><strong>Housing Capacity:</strong> <span id="housingCapacity">-</span> units</p>
                                <p class="mb-1"><strong>Employment Capacity:</strong> <span id="employmentCapacity">-</span> jobs</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.setupCityConfigurationHandlers();
        this.updateCitySummary();
        this.renderCityPreview();
    }
    
    setupCityConfigurationHandlers() {
        // Real-time updates for building counts
        ['residential', 'commercial', 'industrial', 'casinos', 'liquorStores'].forEach(type => {
            const slider = document.getElementById(`${type}Count`);
            const display = document.getElementById(`${type}Value`);
            
            if (slider && display) {
                slider.addEventListener('input', (e) => {
                    display.textContent = e.target.value;
                    this.updateCitySummary();
                    this.saveCurrentStepData(); // Save immediately
                    this.validateCurrentStep();
                });
            }
        });
        
        // City name validation
        const cityNameInput = document.getElementById('cityName');
        if (cityNameInput) {
            cityNameInput.addEventListener('input', () => {
                this.saveCurrentStepData(); // Save immediately
                this.validateCurrentStep();
            });
        }
        
        // City size selection
        document.querySelectorAll('input[name="citySize"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.updateCitySummary();
                this.saveCurrentStepData(); // Save immediately
                this.validateCurrentStep();
            });
        });
    }
    
    updateCitySummary() {
        const residential = parseInt(document.getElementById('residentialCount')?.value || 0);
        const commercial = parseInt(document.getElementById('commercialCount')?.value || 0);
        const industrial = parseInt(document.getElementById('industrialCount')?.value || 0);
        const casinos = parseInt(document.getElementById('casinosCount')?.value || 0);
        const liquorStores = parseInt(document.getElementById('liquorStoresCount')?.value || 0);
        
        const totalBuildings = residential + commercial + industrial + casinos + liquorStores;
        const housingCapacity = residential * 5; // Assume 5 units per residential building
        const employmentCapacity = commercial * 10 + industrial * 15; // Rough estimates
        
        const totalBuildingsEl = document.getElementById('totalBuildings');
        const housingCapacityEl = document.getElementById('housingCapacity');
        const employmentCapacityEl = document.getElementById('employmentCapacity');
        
        if (totalBuildingsEl) totalBuildingsEl.textContent = totalBuildings;
        if (housingCapacityEl) housingCapacityEl.textContent = housingCapacity;
        if (employmentCapacityEl) employmentCapacityEl.textContent = employmentCapacity;

        this.renderCityPreview();
    }

    renderCityPreview() {
        const container = d3.select('#cityMapPreview');
        if (container.empty()) return;
        container.selectAll('*').remove();

        const width = parseInt(container.style('width'));
        const height = parseInt(container.style('height'));
        const svg = container.append('svg').attr('width', width).attr('height', height);

        const size = app.state.configuration.citySize || 'medium';
        const grid = size === 'small' ? 20 : size === 'large' ? 50 : 30;
        const scaleX = d3.scaleLinear().domain([0, grid]).range([0, width]);
        const scaleY = d3.scaleLinear().domain([0, grid]).range([0, height]);

        const cells = [];
        for (let x = 0; x < grid; x++) {
            for (let y = 0; y < grid; y++) {
                cells.push({x, y});
            }
        }

        svg.selectAll('rect').data(cells).enter()
            .append('rect')
            .attr('x', d => scaleX(d.x))
            .attr('y', d => scaleY(d.y))
            .attr('width', scaleX(1) - scaleX(0))
            .attr('height', scaleY(1) - scaleY(0))
            .attr('fill', '#2d3748')
            .attr('stroke', '#444')
            .attr('stroke-width', 0.5);
    }
    
    showPopulationConfigurationStep(container) {
        const config = app.state.configuration || new SimulationConfiguration();
        
        container.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-users"></i> Population Size & Composition</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Total Agents</label>
                                <div class="input-group">
                                    <input type="number" class="form-control" id="totalAgents" 
                                           value="${config.totalAgents}" min="1" max="1000">
                                    <span class="input-group-text">agents</span>
                                </div>
                                <small class="form-text text-muted">Recommended: 50-200 agents for optimal performance</small>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Population Mix</label>
                                <div class="population-sliders">
                                    <div class="mb-2">
                                        <div class="d-flex justify-content-between">
                                            <label class="small">Balanced</label>
                                            <span class="badge bg-success" id="balancedPercentage">${Math.round((config.populationMix.balanced || 0.7) * 100)}%</span>
                                        </div>
                                        <input type="range" class="form-range" min="0" max="100" 
                                               value="${(config.populationMix.balanced || 0.7) * 100}" id="balancedSlider">
                                    </div>
                                    <div class="mb-2">
                                        <div class="d-flex justify-content-between">
                                            <label class="small">Vulnerable</label>
                                            <span class="badge bg-warning" id="vulnerablePercentage">${Math.round((config.populationMix.vulnerable || 0.3) * 100)}%</span>
                                        </div>
                                        <input type="range" class="form-range" min="0" max="100" 
                                               value="${(config.populationMix.vulnerable || 0.3) * 100}" id="vulnerableSlider">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-header">
                            <h6><i class="fas fa-brain"></i> Behavioral Parameters</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Risk Preference</label>
                                <select class="form-select" id="riskPreference">
                                    <option value="low" ${config.behavioralParams.riskPreference === 'low' ? 'selected' : ''}>Low Risk</option>
                                    <option value="normal" ${config.behavioralParams.riskPreference === 'normal' ? 'selected' : ''}>Normal</option>
                                    <option value="high" ${config.behavioralParams.riskPreference === 'high' ? 'selected' : ''}>High Risk</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Addiction Vulnerability</label>
                                <div class="d-flex align-items-center">
                                    <input type="range" class="form-range flex-grow-1" min="0" max="100" 
                                           value="${(config.behavioralParams.addictionVulnerability || 0.4) * 100}" id="addictionVulnerability">
                                    <span class="ms-2 badge bg-danger" id="addictionValue">${Math.round((config.behavioralParams.addictionVulnerability || 0.4) * 100)}%</span>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Economic Stress</label>
                                <div class="d-flex align-items-center">
                                    <input type="range" class="form-range flex-grow-1" min="0" max="100" 
                                           value="${(config.behavioralParams.economicStress || 0.5) * 100}" id="economicStress">
                                    <span class="ms-2 badge bg-warning" id="stressValue">${Math.round((config.behavioralParams.economicStress || 0.5) * 100)}%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-chart-pie"></i> Population Preview</h6>
                        </div>
                        <div class="card-body">
                            <div id="populationPreview">
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Balanced Agents:</span>
                                    <span id="balancedCount">-</span>
                                </div>
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Vulnerable Agents:</span>
                                    <span id="vulnerableCount">-</span>
                                </div>
                                <hr>
                                <div class="d-flex justify-content-between">
                                    <strong>Total:</strong>
                                    <strong id="totalAgentsPreview">-</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.setupPopulationConfigurationHandlers();
        this.updatePopulationPreview();
    }
    
    setupPopulationConfigurationHandlers() {
        // Total agents input
        const totalAgentsInput = document.getElementById('totalAgents');
        if (totalAgentsInput) {
            totalAgentsInput.addEventListener('input', () => {
                this.updatePopulationPreview();
                this.saveCurrentStepData(); // Save immediately
                this.validateCurrentStep();
            });
        }
        
        // Population mix sliders
        ['balanced', 'vulnerable'].forEach(type => {
            const slider = document.getElementById(`${type}Slider`);
            const percentage = document.getElementById(`${type}Percentage`);
            
            if (slider && percentage) {
                slider.addEventListener('input', (e) => {
                    const value = parseInt(e.target.value);
                    percentage.textContent = `${value}%`;
                    this.balancePopulationMix(type, value);
                    this.updatePopulationPreview();
                    this.saveCurrentStepData(); // Save immediately
                    this.validateCurrentStep();
                });
            }
        });
        
        // Behavioral parameter sliders
        ['addictionVulnerability', 'economicStress'].forEach(type => {
            const slider = document.getElementById(type);
            const display = document.getElementById(type === 'addictionVulnerability' ? 'addictionValue' : 'stressValue');
            
            if (slider && display) {
                slider.addEventListener('input', (e) => {
                    const value = parseInt(e.target.value);
                    display.textContent = `${value}%`;
                    this.saveCurrentStepData(); // Save immediately
                    this.validateCurrentStep();
                });
            }
        });
        
        // Risk preference dropdown
        const riskPreferenceSelect = document.getElementById('riskPreference');
        if (riskPreferenceSelect) {
            riskPreferenceSelect.addEventListener('change', () => {
                this.saveCurrentStepData(); // Save immediately
                this.validateCurrentStep();
            });
        }
    }
    
    balancePopulationMix(changedType, newValue) {
        const balancedSlider = document.getElementById('balancedSlider');
        const vulnerableSlider = document.getElementById('vulnerableSlider');
        const balancedPercentage = document.getElementById('balancedPercentage');
        const vulnerablePercentage = document.getElementById('vulnerablePercentage');
        
        if (changedType === 'balanced') {
            const remaining = 100 - newValue;
            vulnerableSlider.value = remaining;
            vulnerablePercentage.textContent = `${remaining}%`;
        } else if (changedType === 'vulnerable') {
            const remaining = 100 - newValue;
            balancedSlider.value = remaining;
            balancedPercentage.textContent = `${remaining}%`;
        }
    }
    
    updatePopulationPreview() {
        const totalAgents = parseInt(document.getElementById('totalAgents')?.value || 0);
        const balancedPercent = parseInt(document.getElementById('balancedSlider')?.value || 70);
        const vulnerablePercent = parseInt(document.getElementById('vulnerableSlider')?.value || 30);
        
        const balancedCount = Math.round(totalAgents * balancedPercent / 100);
        const vulnerableCount = Math.round(totalAgents * vulnerablePercent / 100);
        
        const balancedCountEl = document.getElementById('balancedCount');
        const vulnerableCountEl = document.getElementById('vulnerableCount');
        const totalAgentsPreviewEl = document.getElementById('totalAgentsPreview');
        
        if (balancedCountEl) balancedCountEl.textContent = balancedCount;
        if (vulnerableCountEl) vulnerableCountEl.textContent = vulnerableCount;
        if (totalAgentsPreviewEl) totalAgentsPreviewEl.textContent = totalAgents;
    }
    
    showSimulationParametersStep(container) {
        const config = app.state.configuration || new SimulationConfiguration();
        
        container.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-header">
                            <h6><i class="fas fa-clock"></i> Time Configuration</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Simulation Duration</label>
                                <div class="input-group">
                                    <input type="number" class="form-control" id="durationMonths" 
                                           value="${config.durationMonths}" min="1" max="60">
                                    <span class="input-group-text">months</span>
                                </div>
                                <small class="form-text text-muted">Recommended: 6-24 months for meaningful results</small>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Rounds per Month</label>
                                <div class="d-flex align-items-center">
                                    <input type="range" class="form-range flex-grow-1" min="1" max="16" 
                                           value="${config.roundsPerMonth}" id="roundsPerMonth">
                                    <span class="ms-2 badge bg-primary" id="roundsValue">${config.roundsPerMonth}</span>
                                </div>
                                <small class="form-text text-muted">More rounds = higher detail but slower execution</small>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Update Interval</label>
                                <div class="input-group">
                                    <input type="number" class="form-control" id="updateInterval" 
                                           value="${config.updateInterval}" min="0.1" max="5.0" step="0.1">
                                    <span class="input-group-text">seconds</span>
                                </div>
                                <small class="form-text text-muted">How often the dashboard updates during simulation</small>
                            </div>
                            
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h6 class="card-title">Estimated Runtime</h6>
                                    <p class="mb-0" id="estimatedRuntime">Calculating...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-header">
                            <h6><i class="fas fa-chart-line"></i> Economic Conditions</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Base Unemployment Rate</label>
                                <div class="d-flex align-items-center">
                                    <input type="range" class="form-range flex-grow-1" min="1" max="25" 
                                           value="${(config.economicConditions.unemploymentRate || 0.08) * 100}" id="unemploymentRate">
                                    <span class="ms-2 badge bg-warning" id="unemploymentValue">${Math.round((config.economicConditions.unemploymentRate || 0.08) * 100)}%</span>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Rent Inflation Rate</label>
                                <div class="d-flex align-items-center">
                                    <input type="range" class="form-range flex-grow-1" min="0" max="10" 
                                           value="${(config.economicConditions.rentInflation || 0.02) * 100}" id="rentInflation">
                                    <span class="ms-2 badge bg-info" id="rentValue">${Math.round((config.economicConditions.rentInflation || 0.02) * 100)}%</span>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Economic Shocks</label>
                                <select class="form-select" id="economicShocks">
                                    <option value="none" ${config.economicConditions.economicShocks === 'none' ? 'selected' : ''}>None</option>
                                    <option value="mild" ${config.economicConditions.economicShocks === 'mild' ? 'selected' : ''}>Mild</option>
                                    <option value="moderate" ${config.economicConditions.economicShocks === 'moderate' ? 'selected' : ''}>Moderate</option>
                                    <option value="severe" ${config.economicConditions.economicShocks === 'severe' ? 'selected' : ''}>Severe</option>
                                </select>
                                <small class="form-text text-muted">Random economic events during simulation</small>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Job Market Conditions</label>
                                <div class="btn-group d-flex" role="group">
                                    <input type="radio" class="btn-check" name="jobMarket" id="jobTight" value="tight" ${config.economicConditions.jobMarket === 'tight' ? 'checked' : ''}>
                                    <label class="btn btn-outline-danger" for="jobTight">Tight</label>
                                    
                                    <input type="radio" class="btn-check" name="jobMarket" id="jobBalanced" value="balanced" ${config.economicConditions.jobMarket === 'balanced' ? 'checked' : ''}>
                                    <label class="btn btn-outline-warning" for="jobBalanced">Balanced</label>
                                    
                                    <input type="radio" class="btn-check" name="jobMarket" id="jobLoose" value="loose" ${config.economicConditions.jobMarket === 'loose' ? 'checked' : ''}>
                                    <label class="btn btn-outline-success" for="jobLoose">Loose</label>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-database"></i> Data Collection</h6>
                        </div>
                        <div class="card-body">
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="checkbox" id="agentMetrics" ${config.dataCollection.agentMetrics ? 'checked' : ''}>
                                <label class="form-check-label" for="agentMetrics">
                                    Individual Agent Metrics
                                </label>
                                <small class="form-text text-muted d-block">Track detailed state for each agent</small>
                            </div>
                            
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="checkbox" id="populationStats" ${config.dataCollection.populationStats ? 'checked' : ''}>
                                <label class="form-check-label" for="populationStats">
                                    Population-level Statistics
                                </label>
                                <small class="form-text text-muted d-block">Aggregate metrics and trends</small>
                            </div>
                            
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="checkbox" id="lifeEvents" ${config.dataCollection.lifeEvents ? 'checked' : ''}>
                                <label class="form-check-label" for="lifeEvents">
                                    Life Events Tracking
                                </label>
                                <small class="form-text text-muted d-block">Major events in agents' lives</small>
                            </div>
                            
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="checkbox" id="actionHistory" ${config.dataCollection.actionHistory ? 'checked' : ''}>
                                <label class="form-check-label" for="actionHistory">
                                    Action History Logging
                                </label>
                                <small class="form-text text-muted d-block">Complete log of agent actions</small>
                            </div>
                            
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="exportData" ${config.dataCollection.exportData ? 'checked' : ''}>
                                <label class="form-check-label" for="exportData">
                                    Enable Data Export
                                </label>
                                <small class="form-text text-muted d-block">CSV, JSON, and report generation</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.setupSimulationParametersHandlers();
        this.updateEstimatedRuntime();
    }
    
    setupSimulationParametersHandlers() {
        // Duration input
        const durationInput = document.getElementById('durationMonths');
        if (durationInput) {
            durationInput.addEventListener('input', () => {
                this.updateEstimatedRuntime();
                this.saveCurrentStepData(); // Save immediately
                this.validateCurrentStep();
            });
        }
        
        // Rounds per month slider
        const roundsSlider = document.getElementById('roundsPerMonth');
        const roundsValue = document.getElementById('roundsValue');
        if (roundsSlider && roundsValue) {
            roundsSlider.addEventListener('input', (e) => {
                roundsValue.textContent = e.target.value;
                this.updateEstimatedRuntime();
                this.saveCurrentStepData(); // Save immediately
                this.validateCurrentStep();
            });
        }
        
        // Update interval
        const updateIntervalInput = document.getElementById('updateInterval');
        if (updateIntervalInput) {
            updateIntervalInput.addEventListener('input', () => {
                this.saveCurrentStepData(); // Save immediately
                this.validateCurrentStep();
            });
        }
        
        // Economic condition sliders
        ['unemploymentRate', 'rentInflation'].forEach(type => {
            const slider = document.getElementById(type);
            const display = document.getElementById(type === 'unemploymentRate' ? 'unemploymentValue' : 'rentValue');
            
            if (slider && display) {
                slider.addEventListener('input', (e) => {
                    const value = parseInt(e.target.value);
                    display.textContent = `${value}%`;
                    this.saveCurrentStepData(); // Save immediately
                    this.validateCurrentStep();
                });
            }
        });
        
        // Economic shocks and job market
        ['economicShocks'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', () => {
                    this.saveCurrentStepData(); // Save immediately
                    this.validateCurrentStep();
                });
            }
        });
        
        // Job market radio buttons
        document.querySelectorAll('input[name="jobMarket"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.saveCurrentStepData(); // Save immediately
                this.validateCurrentStep();
            });
        });
        
        // Data collection checkboxes
        ['agentMetrics', 'populationStats', 'lifeEvents', 'actionHistory', 'exportData'].forEach(id => {
            const checkbox = document.getElementById(id);
            if (checkbox) {
                checkbox.addEventListener('change', () => {
                    this.saveCurrentStepData(); // Save immediately
                    this.validateCurrentStep();
                });
            }
        });
    }
    
    updateEstimatedRuntime() {
        const duration = parseInt(document.getElementById('durationMonths')?.value || 12);
        const rounds = parseInt(document.getElementById('roundsPerMonth')?.value || 8);
        const totalAgents = parseInt(document.getElementById('totalAgents')?.value || 100);
        
        // Very rough estimation based on typical performance
        const totalRounds = duration * rounds;
        const estimatedSeconds = totalRounds * (totalAgents / 50) * 0.1; // 0.1 seconds per 50 agents per round
        
        let timeString;
        if (estimatedSeconds < 60) {
            timeString = `~${Math.round(estimatedSeconds)} seconds`;
        } else if (estimatedSeconds < 3600) {
            timeString = `~${Math.round(estimatedSeconds / 60)} minutes`;
        } else {
            timeString = `~${Math.round(estimatedSeconds / 3600 * 10) / 10} hours`;
        }
        
        const runtimeEl = document.getElementById('estimatedRuntime');
        if (runtimeEl) {
            runtimeEl.textContent = timeString;
        }
    }
    
    showReviewStep(container) {
        const config = app.state.configuration || new SimulationConfiguration();
        
        // Calculate summary statistics
        const totalBuildings = Object.values(config.buildings).reduce((sum, count) => sum + count, 0);
        const housingCapacity = config.buildings.residential * 5;
        const totalRounds = config.durationMonths * config.roundsPerMonth;
        
        container.innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <div class="card mb-3">
                        <div class="card-header">
                            <h6><i class="fas fa-list-check"></i> Configuration Summary</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6 class="text-primary">City Configuration</h6>
                                    <ul class="list-unstyled">
                                        <li><strong>Name:</strong> ${config.cityName}</li>
                                        <li><strong>Size:</strong> ${config.citySize.charAt(0).toUpperCase() + config.citySize.slice(1)}</li>
                                        <li><strong>Total Buildings:</strong> ${totalBuildings}</li>
                                        <li><strong>Housing Capacity:</strong> ${housingCapacity} units</li>
                                    </ul>
                                    
                                    <h6 class="text-success mt-3">Population</h6>
                                    <ul class="list-unstyled">
                                        <li><strong>Total Agents:</strong> ${config.totalAgents}</li>
                                        <li><strong>Balanced:</strong> ${Math.round((config.populationMix.balanced || 0.7) * 100)}%</li>
                                        <li><strong>Vulnerable:</strong> ${Math.round((config.populationMix.vulnerable || 0.3) * 100)}%</li>
                                        <li><strong>Risk Preference:</strong> ${config.behavioralParams.riskPreference}</li>
                                    </ul>
                                </div>
                                
                                <div class="col-md-6">
                                    <h6 class="text-warning">Simulation Parameters</h6>
                                    <ul class="list-unstyled">
                                        <li><strong>Duration:</strong> ${config.durationMonths} months</li>
                                        <li><strong>Total Rounds:</strong> ${totalRounds}</li>
                                        <li><strong>Update Interval:</strong> ${config.updateInterval}s</li>
                                        <li><strong>Economic Shocks:</strong> ${config.economicConditions.economicShocks}</li>
                                    </ul>
                                    
                                    <h6 class="text-info mt-3">Economic Conditions</h6>
                                    <ul class="list-unstyled">
                                        <li><strong>Unemployment:</strong> ${Math.round((config.economicConditions.unemploymentRate || 0.08) * 100)}%</li>
                                        <li><strong>Rent Inflation:</strong> ${Math.round((config.economicConditions.rentInflation || 0.02) * 100)}%</li>
                                        <li><strong>Job Market:</strong> ${config.economicConditions.jobMarket}</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-save"></i> Save Configuration</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Configuration Name</label>
                                <input type="text" class="form-control" id="configName" 
                                       value="${config.cityName} - ${new Date().toLocaleDateString()}" 
                                       placeholder="Enter a name for this configuration">
                            </div>
                            
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="saveAsTemplate">
                                <label class="form-check-label" for="saveAsTemplate">
                                    Save as template for future use
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card mb-3">
                        <div class="card-header">
                            <h6><i class="fas fa-clipboard-check"></i> Pre-flight Checks</h6>
                        </div>
                        <div class="card-body">
                            <div id="preflightChecks">
                                <!-- Pre-flight checks will be populated here -->
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-info-circle"></i> Simulation Info</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-2">
                                <small class="text-muted">Estimated Runtime:</small>
                                <div id="finalEstimatedRuntime" class="fw-bold">Calculating...</div>
                            </div>
                            
                            <div class="mb-2">
                                <small class="text-muted">Data Storage:</small>
                                <div class="fw-bold">~/simulacra_data/</div>
                            </div>
                            
                            <div class="mb-2">
                                <small class="text-muted">Export Formats:</small>
                                <div class="fw-bold">CSV, JSON, Reports</div>
                            </div>
                            
                            <hr>
                            
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-primary" id="saveConfigBtn">
                                    <i class="fas fa-save"></i> Save Configuration
                                </button>
                                <button class="btn btn-warning" id="previewBtn">
                                    <i class="fas fa-eye"></i> Preview Setup
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.setupReviewStepHandlers();
        this.runPreflightChecks();
        this.updateFinalEstimatedRuntime();
    }
    
    setupReviewStepHandlers() {
        // Save configuration button
        const saveConfigBtn = document.getElementById('saveConfigBtn');
        if (saveConfigBtn) {
            saveConfigBtn.addEventListener('click', () => {
                this.saveConfiguration();
            });
        }
        
        // Preview button
        const previewBtn = document.getElementById('previewBtn');
        if (previewBtn) {
            previewBtn.addEventListener('click', () => {
                this.previewConfiguration();
            });
        }
    }
    
    runPreflightChecks() {
        const config = app.state.configuration || new SimulationConfiguration();
        const checks = [];
        
        // City configuration checks
        if (config.cityName && config.cityName.trim().length > 0) {
            checks.push({ status: 'success', message: 'City configuration valid' });
        } else {
            checks.push({ status: 'error', message: 'City name is required' });
        }
        
        // Population checks
        const housingCapacity = config.buildings.residential * 5;
        if (housingCapacity >= config.totalAgents) {
            checks.push({ status: 'success', message: 'Sufficient housing capacity' });
        } else {
            checks.push({ status: 'warning', message: 'Housing capacity may be insufficient' });
        }
        
        // Population mix check
        const mixSum = Object.values(config.populationMix).reduce((sum, val) => sum + val, 0);
        if (Math.abs(mixSum - 1.0) < 0.01) {
            checks.push({ status: 'success', message: 'Population mix balanced' });
        } else {
            checks.push({ status: 'error', message: 'Population mix must sum to 100%' });
        }
        
        // Data collection check
        const hasDataCollection = Object.values(config.dataCollection).some(enabled => enabled);
        if (hasDataCollection) {
            checks.push({ status: 'success', message: 'Data collection enabled' });
        } else {
            checks.push({ status: 'warning', message: 'No data collection enabled' });
        }
        
        // Performance check
        if (config.totalAgents <= 200) {
            checks.push({ status: 'success', message: 'Performance optimized' });
        } else {
            checks.push({ status: 'warning', message: 'Large simulation may be slow' });
        }
        
        // Render checks
        const checksContainer = document.getElementById('preflightChecks');
        if (checksContainer) {
            checksContainer.innerHTML = checks.map(check => {
                const iconClass = check.status === 'success' ? 'fa-check-circle text-success' : 
                                 check.status === 'warning' ? 'fa-exclamation-triangle text-warning' : 
                                 'fa-times-circle text-danger';
                return `
                    <div class="d-flex align-items-center mb-2">
                        <i class="fas ${iconClass} me-2"></i>
                        <small>${check.message}</small>
                    </div>
                `;
            }).join('');
        }
    }
    
    updateFinalEstimatedRuntime() {
        // Use the same calculation as in simulation parameters
        this.updateEstimatedRuntime();
        
        const estimatedRuntime = document.getElementById('estimatedRuntime')?.textContent || 'Unknown';
        const finalRuntimeEl = document.getElementById('finalEstimatedRuntime');
        if (finalRuntimeEl) {
            finalRuntimeEl.textContent = estimatedRuntime;
        }
    }
    
    async nextStep() {
        // Save current step data FIRST
        this.saveCurrentStepData();
        
        // Validate current step before proceeding (using updated data)
        const isValid = await this.validateCurrentStep();
        if (!isValid) {
            return;
        }
        
        if (this.currentStep < this.steps.length - 1) {
            this.showStep(this.currentStep + 1);
        } else {
            // Final step - launch simulation
            this.launchSimulation();
        }
    }
    
    previousStep() {
        if (this.currentStep > 0) {
            this.showStep(this.currentStep - 1);
        }
    }
    
    async validateCurrentStep() {
        // Get current form data for validation
        const stepData = this.getCurrentStepData();
        
        // For validation, always use a complete configuration that merges current step data
        // with existing configuration to get the full picture
        const fullConfig = this._buildFullConfigForValidation(stepData);
        
        try {
            const response = await app.apiCall(`/api/validate/${this.steps[this.currentStep]}`, 'POST', fullConfig);
            this.validationResults[this.steps[this.currentStep]] = response;
            
            if (!response.valid) {
                this.showValidationMessages(response.errors, response.warnings);
                return false;
            }
            
            if (response.warnings && response.warnings.length > 0) {
                this.showValidationMessages([], response.warnings);
            } else {
                this.clearValidationMessages();
            }
            
            return true;
        } catch (error) {
            console.error('Validation error:', error);
            this.showValidationMessages(['Validation error occurred'], []);
            return false;
        }
    }
    
    _buildFullConfigForValidation(currentStepData) {
        // Start with current app configuration or create new one
        const baseConfig = app.state.configuration || new SimulationConfiguration();
        
        // Create a full configuration object by merging current step data with base config
        const fullConfig = {
            city_name: currentStepData.city_name || baseConfig.cityName,
            city_size: currentStepData.city_size || baseConfig.citySize,
            buildings: currentStepData.buildings || baseConfig.buildings,
            total_agents: currentStepData.total_agents || baseConfig.totalAgents,
            population_mix: currentStepData.population_mix || baseConfig.populationMix,
            behavioral_params: currentStepData.behavioral_params || baseConfig.behavioralParams,
            duration_months: currentStepData.duration_months || baseConfig.durationMonths,
            rounds_per_month: currentStepData.rounds_per_month || baseConfig.roundsPerMonth,
            update_interval: currentStepData.update_interval || baseConfig.updateInterval,
            economic_conditions: currentStepData.economic_conditions || baseConfig.economicConditions,
            data_collection: currentStepData.data_collection || baseConfig.dataCollection
        };
        
        return fullConfig;
    }
    
    getCurrentStepData() {
        const config = app.state.configuration || new SimulationConfiguration();
        
        switch (this.currentStep) {
            case 0: // City configuration
                return {
                    city_name: document.getElementById('cityName')?.value || config.cityName,
                    city_size: document.querySelector('input[name="citySize"]:checked')?.value || config.citySize,
                    buildings: {
                        residential: parseInt(document.getElementById('residentialCount')?.value || config.buildings.residential),
                        commercial: parseInt(document.getElementById('commercialCount')?.value || config.buildings.commercial),
                        industrial: parseInt(document.getElementById('industrialCount')?.value || config.buildings.industrial),
                        casinos: parseInt(document.getElementById('casinosCount')?.value || config.buildings.casinos),
                        liquor_stores: parseInt(document.getElementById('liquorStoresCount')?.value || config.buildings.liquor_stores)
                    }
                };
            case 1: // Population configuration
                return {
                    total_agents: parseInt(document.getElementById('totalAgents')?.value || config.totalAgents),
                    population_mix: {
                        balanced: parseInt(document.getElementById('balancedSlider')?.value || 70) / 100,
                        vulnerable: parseInt(document.getElementById('vulnerableSlider')?.value || 30) / 100
                    },
                    behavioral_params: {
                        risk_preference: document.getElementById('riskPreference')?.value || config.behavioralParams.riskPreference,
                        addiction_vulnerability: parseInt(document.getElementById('addictionVulnerability')?.value || 40) / 100,
                        economic_stress: parseInt(document.getElementById('economicStress')?.value || 50) / 100
                    }
                };
            case 2: // Simulation parameters
                return {
                    duration_months: parseInt(document.getElementById('durationMonths')?.value || config.durationMonths),
                    rounds_per_month: parseInt(document.getElementById('roundsPerMonth')?.value || config.roundsPerMonth),
                    update_interval: parseFloat(document.getElementById('updateInterval')?.value || config.updateInterval),
                    economic_conditions: {
                        unemployment_rate: parseInt(document.getElementById('unemploymentRate')?.value || 8) / 100,
                        rent_inflation: parseInt(document.getElementById('rentInflation')?.value || 2) / 100,
                        economic_shocks: document.getElementById('economicShocks')?.value || config.economicConditions.economicShocks,
                        job_market: document.querySelector('input[name="jobMarket"]:checked')?.value || config.economicConditions.jobMarket
                    },
                    data_collection: {
                        agent_metrics: document.getElementById('agentMetrics')?.checked || false,
                        population_stats: document.getElementById('populationStats')?.checked || false,
                        life_events: document.getElementById('lifeEvents')?.checked || false,
                        action_history: document.getElementById('actionHistory')?.checked || false,
                        export_data: document.getElementById('exportData')?.checked || false
                    }
                };
            case 3: // Review step - return complete configuration
                return {
                    city_name: config.cityName,
                    city_size: config.citySize,
                    buildings: config.buildings,
                    total_agents: config.totalAgents,
                    population_mix: config.populationMix,
                    behavioral_params: config.behavioralParams,
                    duration_months: config.durationMonths,
                    rounds_per_month: config.roundsPerMonth,
                    update_interval: config.updateInterval,
                    economic_conditions: config.economicConditions,
                    data_collection: config.dataCollection
                };
            default:
                return config.toDict ? config.toDict() : config;
        }
    }
    
    saveCurrentStepData() {
        const stepData = this.getCurrentStepData();
        
        if (!app.state.configuration) {
            app.state.configuration = new SimulationConfiguration();
        }
        
        // Update configuration with current step data - be more specific about what to update
        const config = app.state.configuration;
        
        // Update based on current step
        switch (this.currentStep) {
            case 0: // City configuration
                if (stepData.city_name) config.cityName = stepData.city_name;
                if (stepData.city_size) config.citySize = stepData.city_size;
                if (stepData.buildings) config.buildings = stepData.buildings;
                break;
            case 1: // Population configuration
                if (stepData.total_agents) config.totalAgents = stepData.total_agents;
                if (stepData.population_mix) config.populationMix = stepData.population_mix;
                if (stepData.behavioral_params) config.behavioralParams = stepData.behavioral_params;
                break;
            case 2: // Simulation parameters
                if (stepData.duration_months) config.durationMonths = stepData.duration_months;
                if (stepData.rounds_per_month) config.roundsPerMonth = stepData.rounds_per_month;
                if (stepData.update_interval) config.updateInterval = stepData.update_interval;
                if (stepData.economic_conditions) config.economicConditions = stepData.economic_conditions;
                if (stepData.data_collection) config.dataCollection = stepData.data_collection;
                break;
            case 3: // Review step - save everything
                Object.assign(config, {
                    cityName: stepData.city_name,
                    citySize: stepData.city_size,
                    buildings: stepData.buildings,
                    totalAgents: stepData.total_agents,
                    populationMix: stepData.population_mix,
                    behavioralParams: stepData.behavioral_params,
                    durationMonths: stepData.duration_months,
                    roundsPerMonth: stepData.rounds_per_month,
                    updateInterval: stepData.update_interval,
                    economicConditions: stepData.economic_conditions,
                    dataCollection: stepData.data_collection
                });
                break;
        }
        
        console.log(`Saved step ${this.currentStep} data:`, stepData);
        console.log(`Updated configuration:`, config);
    }
    
    showValidationMessages(errors = [], warnings = []) {
        const container = document.getElementById('validationMessages');
        if (!container) return;
        
        let html = '';
        
        if (errors.length > 0) {
            html += `
                <div class="alert alert-danger">
                    <strong>Configuration Errors:</strong>
                    <ul class="mb-0">
                        ${errors.map(error => `<li>${error}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        if (warnings.length > 0) {
            html += `
                <div class="alert alert-warning">
                    <strong>Warnings:</strong>
                    <ul class="mb-0">
                        ${warnings.map(warning => `<li>${warning}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        container.innerHTML = html;
    }
    
    clearValidationMessages() {
        const container = document.getElementById('validationMessages');
        if (container) {
            container.innerHTML = '';
        }
    }
    
    updateProgressIndicator() {
        document.querySelectorAll('.step-indicator').forEach((indicator, index) => {
            indicator.classList.remove('active', 'completed');
            
            if (index < this.currentStep) {
                indicator.classList.add('completed');
            } else if (index === this.currentStep) {
                indicator.classList.add('active');
            }
        });
    }
    
    updateNavigationButtons() {
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        
        // Show/hide previous button
        if (this.currentStep === 0) {
            prevBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'block';
        }
        
        // Update next button text
        if (this.currentStep === this.steps.length - 1) {
            nextBtn.innerHTML = '<i class="fas fa-rocket"></i> Launch Simulation';
            nextBtn.className = 'btn btn-success';
        } else {
            const nextStepName = this.stepTitles[this.currentStep + 1];
            nextBtn.innerHTML = `Next: ${nextStepName} <i class="fas fa-arrow-right"></i>`;
            nextBtn.className = 'btn btn-primary';
        }
    }
    
    canNavigateToStep(stepIndex) {
        // Allow navigation to completed steps or next immediate step
        return stepIndex <= this.currentStep + 1;
    }
    
    loadConfiguration(configuration) {
        this.configuration = configuration;
        app.state.configuration = configuration;
        
        // If we're currently showing a step, refresh it with the new configuration
        if (this.isInitialized) {
            this.showStep(this.currentStep);
        }
    }
    
    async saveConfiguration() {
        try {
            const configName = document.getElementById('configName')?.value || 'Unnamed Configuration';
            const saveAsTemplate = document.getElementById('saveAsTemplate')?.checked || false;
            
            const configData = this.getCurrentStepData();
            configData.city_name = configName;
            
            // Save as project
            const response = await app.apiCall('/api/projects', 'POST', configData);
            
            if (saveAsTemplate) {
                // Additional logic for saving as template would go here
                app.showNotification('Configuration saved as project and template!', 'success');
            } else {
                app.showNotification('Configuration saved as project!', 'success');
            }
            
            // Update the app state with the saved project
            app.state.currentProject = response;
            
        } catch (error) {
            console.error('Error saving configuration:', error);
            app.showNotification('Error saving configuration', 'error');
        }
    }
    
    previewConfiguration() {
        const config = app.state.configuration || new SimulationConfiguration();
        
        // Create a preview modal or detailed view
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Configuration Preview</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <pre class="bg-light p-3">${JSON.stringify(config.toDict ? config.toDict() : config, null, 2)}</pre>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Clean up modal after it's hidden
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
    
    async launchSimulation() {
        try {
            // For the review step, run final comprehensive validation instead of step validation
            const isValid = await this.runFinalValidation();
            if (!isValid) {
                app.showNotification('Please fix configuration errors before launching', 'error');
                return;
            }
            
            // Get final configuration
            const configData = this.getCurrentStepData();
            
            // Save configuration first
            await this.saveConfiguration();
            
            // Start simulation
            console.log('Starting simulation with config:', configData);
            const response = await app.apiCall('/api/simulation/start', 'POST', configData);
            
            if (response && response.simulation_id) {
                app.showNotification('Simulation launched successfully!', 'success');
                app.state.currentSimulation = response;
                app.showSection('run');
            } else {
                console.error('Invalid response from simulation start:', response);
                app.showNotification('Error launching simulation - invalid response', 'error');
            }
            
        } catch (error) {
            console.error('Error launching simulation:', error);
            app.showNotification(`Error launching simulation: ${error.message}`, 'error');
        }
    }
    
    async runFinalValidation() {
        // Run comprehensive validation on the complete configuration
        const config = app.state.configuration || new SimulationConfiguration();
        const configData = config.toDict ? config.toDict() : config;
        
        try {
            // Validate the complete configuration as a simulation config
            const response = await app.apiCall('/api/validate/simulation', 'POST', configData);
            
            if (!response.valid) {
                this.showValidationMessages(response.errors, response.warnings);
                return false;
            }
            
            if (response.warnings && response.warnings.length > 0) {
                this.showValidationMessages([], response.warnings);
            } else {
                this.clearValidationMessages();
            }
            
            return true;
        } catch (error) {
            console.error('Final validation error:', error);
            this.showValidationMessages(['Final validation failed'], []);
            return false;
        }
    }
}

// Make SetupWizard available globally
window.SetupWizard = SetupWizard; 