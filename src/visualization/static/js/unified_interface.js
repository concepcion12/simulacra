/**
 * Simulacra Unified Interface JavaScript Application
 * Main application framework for the complete simulation workflow
 */

class SimulacraApp {
    constructor() {
        this.currentSection = 'home';
        this.socket = io();
        this.state = {
            currentProject: null,
            configuration: null,
            simulation: null,
            templates: [],
            projects: []
        };
        
        // Component references (will be initialized later)
        this.setupWizard = null;
        this.dashboard = null;
        this.analysisTools = null;
        this.exportCenter = null;
        
        this.init();
    }
    
    init() {
        console.log('Initializing Simulacra Unified Interface...');
        this.setupNavigation();
        this.setupSocketHandlers();
        this.loadInitialData();
        
        // Show home section by default
        this.showSection('home');
    }
    
    setupNavigation() {
        // Handle main navigation clicks
        document.querySelectorAll('#mainNavigation .nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.closest('.nav-link').dataset.section;
                this.showSection(section);
            });
        });
        
        // Handle quick action buttons
        const newSimBtn = document.getElementById('newSimulationBtn');
        if (newSimBtn) {
            newSimBtn.addEventListener('click', () => {
                this.startNewSimulation();
            });
        }
        
        const loadProjectBtn = document.getElementById('loadProjectBtn');
        if (loadProjectBtn) {
            loadProjectBtn.addEventListener('click', () => {
                this.showLoadProjectDialog();
            });
        }
        
        const viewExamplesBtn = document.getElementById('viewExamplesBtn');
        if (viewExamplesBtn) {
            viewExamplesBtn.addEventListener('click', () => {
                this.showTemplateGallery();
            });
        }
        
        // Project dropdown handlers
        const saveProjectBtn = document.getElementById('saveProject');
        if (saveProjectBtn) {
            saveProjectBtn.addEventListener('click', () => {
                this.saveCurrentProject();
            });
        }
        
        const loadProjectDropdownBtn = document.getElementById('loadProject');
        if (loadProjectDropdownBtn) {
            loadProjectDropdownBtn.addEventListener('click', () => {
                this.showLoadProjectDialog();
            });
        }
        
        const newProjectBtn = document.getElementById('newProject');
        if (newProjectBtn) {
            newProjectBtn.addEventListener('click', () => {
                this.createNewProject();
            });
        }
    }
    
    setupSocketHandlers() {
        // Connection status
        this.socket.on('connect', () => {
            console.log('Connected to Simulacra server');
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from Simulacra server');
            this.updateConnectionStatus(false);
        });
        
        // Real-time simulation updates
        this.socket.on('simulation_update', (data) => {
            if (this.currentSection === 'run' && this.dashboard) {
                this.dashboard.updateSimulationData(data);
            }
        });
        
        // Configuration validation results
        this.socket.on('validation_result', (data) => {
            if (this.setupWizard) {
                this.setupWizard.handleValidationResult(data);
            }
        });
        
        // Export completion notifications
        this.socket.on('export_complete', (data) => {
            if (this.exportCenter) {
                this.exportCenter.handleExportComplete(data);
            }
            this.showNotification('Export completed successfully', 'success');
        });
        
        // Error handling
        this.socket.on('error', (error) => {
            console.error('Socket error:', error);
            this.showNotification('Connection error occurred', 'error');
        });
    }
    
    async loadInitialData() {
        this.showLoading(true);
        
        try {
            // Load recent projects
            const projects = await this.apiCall('/api/projects');
            this.state.projects = projects;
            this.displayRecentProjects(projects);
            
            // Load template gallery
            const templates = await this.apiCall('/api/templates');
            this.state.templates = templates;
            this.displayTemplateGallery(templates);
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('Error loading application data', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Update navigation
        document.querySelectorAll('#mainNavigation .nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Show target section
        const targetSection = document.getElementById(`${sectionName}Section`);
        const targetNavLink = document.querySelector(`[data-section="${sectionName}"]`);
        
        if (targetSection && targetNavLink) {
            targetSection.classList.add('active');
            targetNavLink.classList.add('active');
            this.currentSection = sectionName;
            
            // Initialize section-specific functionality
            this.initializeSection(sectionName);
        }
    }
    
    initializeSection(sectionName) {
        switch (sectionName) {
            case 'home':
                // Home section is always ready
                break;
            case 'setup':
                this.initializeSetupWizard();
                break;
            case 'run':
                this.initializeRunDashboard();
                break;
            case 'analyze':
                this.initializeAnalysisTools();
                break;
            case 'export':
                this.initializeExportCenter();
                break;
        }
    }
    
    initializeSetupWizard() {
        // Lazy load setup wizard
        if (!this.setupWizard && window.SetupWizard) {
            console.log('Initializing Setup Wizard...');
            this.setupWizard = new SetupWizard();
        }
        if (this.setupWizard) {
            this.setupWizard.initialize();
        }
    }
    
    initializeRunDashboard() {
        if (!this.state.configuration && !this.state.simulation) {
            this.showNotification('Please complete simulation setup first', 'warning');
            this.showSection('setup');
            return;
        }
        
        // Lazy load realtime dashboard
        if (!this.dashboard && window.RealtimeDashboard) {
            console.log('Initializing Real-time Dashboard...');
            this.dashboard = new RealtimeDashboard();
        }
        
        if (this.dashboard) {
            this.dashboard.initialize(this.state.simulation);
        }
    }
    
    initializeAnalysisTools() {
        console.log('Initializing Analysis Tools...');
    }
    
    initializeExportCenter() {
        console.log('Initializing Export Center...');
    }
    
    async startNewSimulation() {
        this.state.configuration = new SimulationConfiguration();
        this.showSection('setup');
    }
    
    async apiCall(endpoint, method = 'GET', data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(endpoint, options);
        
        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    displayRecentProjects(projects) {
        const container = document.getElementById('recentProjects');
        
        if (!projects || projects.length === 0) {
            container.innerHTML = '<p class="text-muted">No recent projects</p>';
            return;
        }
        
        const projectsHtml = projects.slice(0, 5).map(project => `
            <div class="project-item d-flex justify-content-between align-items-center" 
                 onclick="app.loadProject('${project.id}')">
                <div>
                    <h6 class="mb-0">${project.name}</h6>
                    <small class="text-muted">
                        ${project.agents} agents, ${project.duration} months
                        ${project.created_at ? '• ' + new Date(project.created_at).toLocaleDateString() : ''}
                    </small>
                </div>
                <div>
                    <span class="badge bg-secondary">${project.status}</span>
                    <button class="btn btn-sm btn-outline-primary ms-2" 
                            onclick="event.stopPropagation(); app.loadProject('${project.id}')">
                        Load
                    </button>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = projectsHtml;
    }
    
    displayTemplateGallery(templates) {
        const container = document.getElementById('templateGallery');
        
        if (!templates || templates.length === 0) {
            container.innerHTML = '<div class="col-12"><p class="text-muted">No templates available</p></div>';
            return;
        }
        
        const templatesHtml = templates.map(template => `
            <div class="col-md-3 mb-3">
                <div class="card template-card" onclick="app.useTemplate('${template.id}')">
                    <div class="card-body">
                        <h6 class="card-title">${template.name}</h6>
                        <p class="card-text small">${template.description}</p>
                        <div class="d-flex justify-content-between align-items-end">
                            <span class="badge bg-secondary">${template.category}</span>
                            <button class="btn btn-sm btn-primary" 
                                    onclick="event.stopPropagation(); app.useTemplate('${template.id}')">
                                Use
                            </button>
                        </div>
                        ${template.tags ? `
                            <div class="mt-2">
                                ${template.tags.map(tag => `<span class="badge bg-outline-secondary me-1">${tag}</span>`).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = templatesHtml;
    }
    
    async useTemplate(templateId) {
        try {
            this.showLoading(true);
            const template = await this.apiCall(`/api/templates/${templateId}`);
            
            if (template && template.configuration) {
                this.state.configuration = new SimulationConfiguration(template.configuration);
                this.showSection('setup');
                
                if (this.setupWizard) {
                    this.setupWizard.loadConfiguration(this.state.configuration);
                }
                
                this.showNotification(`Loaded template: ${template.name}`, 'success');
            } else {
                throw new Error('Template not found');
            }
            
        } catch (error) {
            console.error('Error loading template:', error);
            this.showNotification('Error loading template', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async loadProject(projectId) {
        try {
            this.showLoading(true);
            const project = await this.apiCall(`/api/projects/${projectId}`);
            
            if (project && project.configuration) {
                this.state.currentProject = project;
                this.state.configuration = new SimulationConfiguration(project.configuration);
                this.showNotification(`Loaded project: ${project.configuration.city_name}`, 'success');
            } else {
                throw new Error('Project not found');
            }
            
        } catch (error) {
            console.error('Error loading project:', error);
            this.showNotification('Error loading project', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async saveCurrentProject() {
        if (!this.state.configuration) {
            this.showNotification('No configuration to save', 'warning');
            return;
        }
        
        try {
            this.showLoading(true);
            
            if (this.state.currentProject) {
                // Update existing project
                const response = await this.apiCall(
                    `/api/projects/${this.state.currentProject.id}`, 
                    'PUT', 
                    this.state.configuration.toDict()
                );
                this.showNotification('Project saved successfully', 'success');
            } else {
                // Create new project
                const response = await this.apiCall(
                    '/api/projects', 
                    'POST', 
                    this.state.configuration.toDict()
                );
                this.state.currentProject = response;
                this.showNotification('Project created successfully', 'success');
            }
            
            // Refresh projects list
            this.loadInitialData();
            
        } catch (error) {
            console.error('Error saving project:', error);
            this.showNotification('Error saving project', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    createNewProject() {
        this.state.currentProject = null;
        this.state.configuration = new SimulationConfiguration();
        this.showSection('setup');
        this.showNotification('Started new project', 'info');
    }
    
    showLoadProjectDialog() {
        // For now, just show the projects list
        this.showSection('home');
        // TODO: Implement proper project selection dialog
    }
    
    showTemplateGallery() {
        this.showSection('home');
        // Scroll to template gallery
        setTimeout(() => {
            const gallery = document.getElementById('templateGallery');
            if (gallery) {
                gallery.scrollIntoView({ behavior: 'smooth' });
            }
        }, 300);
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            if (connected) {
                statusElement.className = 'connection-status connected';
                statusElement.innerHTML = '<i class="fas fa-wifi"></i> Connected';
            } else {
                statusElement.className = 'connection-status disconnected';
                statusElement.innerHTML = '<i class="fas fa-wifi"></i> Disconnected';
            }
        }
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 90px; right: 20px; z-index: 9999; min-width: 300px;';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Configuration object for simulation setup
class SimulationConfiguration {
    constructor(data = {}) {
        // City configuration
        this.cityName = data.city_name || "New City";
        this.citySize = data.city_size || "medium";
        this.districts = data.districts || [];
        this.buildings = data.buildings || {
            residential: 10,
            commercial: 5,
            industrial: 3,
            casinos: 2,
            liquor_stores: 5
        };
        
        // Population configuration
        this.totalAgents = data.total_agents || 100;
        this.populationMix = data.population_mix || {
            balanced: 0.7,
            vulnerable: 0.3
        };
        this.behavioralParams = data.behavioral_params || {
            riskPreference: "normal",
            addictionVulnerability: 0.4,
            economicStress: 0.5,
            impulsivityRange: [0.2, 0.8]
        };
        
        // Simulation parameters
        this.durationMonths = data.duration_months || 12;
        this.roundsPerMonth = data.rounds_per_month || 8;
        this.updateInterval = data.update_interval || 1.0;
        
        this.economicConditions = data.economic_conditions || {
            unemploymentRate: 0.08,
            rentInflation: 0.02,
            economicShocks: "mild",
            jobMarket: "balanced"
        };
        
        this.dataCollection = data.data_collection || {
            agentMetrics: true,
            populationStats: true,
            lifeEvents: true,
            actionHistory: true,
            exportData: true
        };
        
        // Metadata
        this.createdAt = data.created_at;
        this.modifiedAt = data.modified_at;
        this.projectId = data.project_id;
    }
    
    toDict() {
        return {
            city_name: this.cityName,
            city_size: this.citySize,
            districts: this.districts,
            buildings: this.buildings,
            total_agents: this.totalAgents,
            population_mix: this.populationMix,
            behavioral_params: this.behavioralParams,
            duration_months: this.durationMonths,
            rounds_per_month: this.roundsPerMonth,
            update_interval: this.updateInterval,
            economic_conditions: this.economicConditions,
            data_collection: this.dataCollection,
            created_at: this.createdAt,
            modified_at: this.modifiedAt,
            project_id: this.projectId
        };
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Simulacra Unified Interface DOM loaded');
    window.app = new SimulacraApp();
}); 