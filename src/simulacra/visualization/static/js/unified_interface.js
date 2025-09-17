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
        this.updateHomeMetrics();
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
        const startSetupBtn = document.getElementById('startSetupBtn');
        if (startSetupBtn) {
            startSetupBtn.addEventListener('click', () => {
                this.startNewSimulation();
            });
        }

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

        const exploreTemplatesBtn = document.getElementById('exploreTemplatesBtn');
        if (exploreTemplatesBtn) {
            exploreTemplatesBtn.addEventListener('click', () => {
                this.showTemplateGallery();
            });
        }

        const refreshTemplatesBtn = document.getElementById('refreshTemplatesBtn');
        if (refreshTemplatesBtn) {
            refreshTemplatesBtn.addEventListener('click', () => {
                this.refreshTemplateGallery();
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
            this.updateHomeMetrics();

            // Load template gallery
            const templates = await this.apiCall('/api/templates');
            this.state.templates = templates;
            this.displayTemplateGallery(templates);
            this.updateHomeMetrics();

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

        if (!container) {
            return;
        }

        if (!projects || projects.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-2x mb-3"></i>
                    <p class="mb-0">No recent projects yet. Create a new simulation to see it here.</p>
                </div>
            `;
            return;
        }

        const projectItems = projects.slice(0, 5).map(project => {
            const projectId = project.id ?? '';
            const name = project.name || project.configuration?.city_name || 'Untitled Project';
            const agents = project.agents ?? project.total_agents;
            const duration = project.duration ?? project.duration_months;
            const createdAt = project.modified_at || project.updated_at || project.created_at;

            const metaParts = [];
            const agentsNumeric = agents !== undefined && agents !== null ? Number(agents) : null;
            if (agentsNumeric !== null && !Number.isNaN(agentsNumeric)) {
                metaParts.push(`${agentsNumeric.toLocaleString()} agents`);
            } else if (typeof agents === 'string' && agents.trim()) {
                metaParts.push(`${agents.trim()} agents`);
            }

            const durationNumeric = duration !== undefined && duration !== null ? Number(duration) : null;
            if (durationNumeric !== null && !Number.isNaN(durationNumeric)) {
                metaParts.push(`${durationNumeric} months`);
            } else if (typeof duration === 'string' && duration.trim()) {
                metaParts.push(`${duration.trim()} months`);
            }
            if (createdAt) {
                const date = new Date(createdAt);
                if (!Number.isNaN(date.getTime())) {
                    metaParts.push(date.toLocaleDateString());
                }
            }

            const status = project.status || 'Draft';

            return `
                <div class="list-group-item project-item" data-project-id="${projectId}">
                    <div>
                        <h6 class="mb-1">${name}</h6>
                        <div class="project-meta">${metaParts.join(' • ') || 'Awaiting configuration'}</div>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                        <span class="badge badge-outline">${status}</span>
                        <button type="button" class="btn btn-sm btn-outline-light project-load-btn" data-project-id="${projectId}">
                            Load
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = `<div class="list-group list-group-flush project-list">${projectItems}</div>`;

        container.querySelectorAll('.project-item').forEach(item => {
            item.addEventListener('click', (event) => {
                if (!(event.target instanceof HTMLElement)) {
                    return;
                }

                if (event.target.closest('.project-load-btn')) {
                    return;
                }

                const projectId = item.getAttribute('data-project-id');
                if (projectId) {
                    this.loadProject(projectId);
                }
            });
        });

        container.querySelectorAll('.project-load-btn').forEach(button => {
            button.addEventListener('click', (event) => {
                event.stopPropagation();
                const projectId = button.getAttribute('data-project-id');
                if (projectId) {
                    this.loadProject(projectId);
                }
            });
        });
    }

    displayTemplateGallery(templates) {
        const container = document.getElementById('templateGallery');

        if (!container) {
            return;
        }

        if (!templates || templates.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-layer-group fa-2x mb-3"></i>
                        <p class="mb-0">No templates available yet. Save a configuration to reuse it later.</p>
                    </div>
                </div>
            `;
            return;
        }

        const templatesHtml = templates.map(template => {
            const tags = Array.isArray(template.tags)
                ? template.tags.map(tag => `<span class="badge badge-outline">${tag}</span>`).join(' ')
                : '';

            return `
                <div class="col-sm-6 col-xl-3 d-flex">
                    <div class="card template-card flex-grow-1" data-template-id="${template.id}">
                        <div class="card-body">
                            <h6 class="card-title">${template.name}</h6>
                            <p class="card-text small text-muted">${template.description || 'No description provided.'}</p>
                            <div class="d-flex justify-content-between align-items-end gap-2 mt-auto">
                                <span class="badge badge-outline">${template.category || 'General'}</span>
                                <button type="button" class="btn btn-sm btn-primary use-template-btn" data-template-id="${template.id}">
                                    Use
                                </button>
                            </div>
                            ${tags ? `<div class="mt-2 d-flex flex-wrap gap-2">${tags}</div>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = templatesHtml;

        container.querySelectorAll('.template-card').forEach(card => {
            card.addEventListener('click', () => {
                const templateId = card.getAttribute('data-template-id');
                if (templateId) {
                    this.useTemplate(templateId);
                }
            });
        });

        container.querySelectorAll('.use-template-btn').forEach(button => {
            button.addEventListener('click', (event) => {
                event.stopPropagation();
                const templateId = button.getAttribute('data-template-id');
                if (templateId) {
                    this.useTemplate(templateId);
                }
            });
        });
    }

    async refreshTemplateGallery() {
        try {
            this.showLoading(true);
            const templates = await this.apiCall('/api/templates');
            this.state.templates = templates;
            this.displayTemplateGallery(templates);
            this.updateHomeMetrics();
            this.showNotification('Template library updated', 'success');
        } catch (error) {
            console.error('Error refreshing templates:', error);
            this.showNotification('Unable to refresh templates', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    updateHomeMetrics() {
        const projectCountEl = document.getElementById('metricProjects');
        if (projectCountEl) {
            const projectCount = Array.isArray(this.state.projects) ? this.state.projects.length : 0;
            projectCountEl.textContent = projectCount.toLocaleString();
        }

        const templateCountEl = document.getElementById('metricTemplates');
        if (templateCountEl) {
            const templateCount = Array.isArray(this.state.templates) ? this.state.templates.length : 0;
            templateCountEl.textContent = templateCount.toLocaleString();
        }

        const lastUpdatedEl = document.getElementById('metricLastUpdated');
        if (lastUpdatedEl) {
            let latestDate = null;

            if (Array.isArray(this.state.projects)) {
                for (const project of this.state.projects) {
                    const timestamp = project.modified_at || project.updated_at || project.created_at;
                    if (!timestamp) {
                        continue;
                    }

                    const date = new Date(timestamp);
                    if (Number.isNaN(date.getTime())) {
                        continue;
                    }

                    if (!latestDate || date > latestDate) {
                        latestDate = date;
                    }
                }
            }

            lastUpdatedEl.textContent = latestDate ? latestDate.toLocaleDateString() : 'Awaiting first save';
        }

        const statusEl = document.getElementById('metricStatus');
        if (statusEl) {
            statusEl.textContent = this.socket && this.socket.connected ? 'Live Connection' : 'Offline Mode';
        }
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
        // Create a modal listing available projects for the user to choose from
        const modal = document.createElement('div');
        modal.className = 'modal fade';

        const projects = this.state.projects || [];
        const projectItems = projects.length > 0 ?
            projects.map(p => `
                <button type="button" class="list-group-item list-group-item-action" data-project-id="${p.id}">
                    <strong>${p.name}</strong><br/>
                    <small class="text-muted">${p.agents || 0} agents, ${p.duration || 0} months</small>
                </button>
            `).join('') :
            '<p class="text-muted mb-0">No projects available</p>';

        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Load Project</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="list-group">${projectItems}</div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Handle selection
        modal.querySelectorAll('[data-project-id]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const projId = e.currentTarget.getAttribute('data-project-id');
                bsModal.hide();
                this.loadProject(projId);
            });
        });

        // Clean up modal once hidden
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
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

        this.updateHomeMetrics();
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
        const typeMap = {
            success: 'success',
            info: 'info',
            warning: 'warning',
            error: 'danger'
        };
        const alertType = typeMap[type] ?? 'info';
        notification.className = `alert alert-${alertType} alert-dismissible fade show position-fixed`;
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