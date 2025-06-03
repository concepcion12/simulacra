# Simulacra Unified UI Implementation Roadmap

## Implementation Strategy

This roadmap provides specific technical guidance for implementing the unified UI design, building incrementally on the existing codebase infrastructure.

## Phase 1: Core Infrastructure (Week 1-2)

### 1.1 Enhanced Flask Application Structure

**Current**: `src/visualization/visualization_server.py` 
**Enhancement**: Extend to support multi-section SPA

```python
# src/visualization/unified_app.py
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from typing import Dict, Any, Optional
import json
from pathlib import Path

class UnifiedSimulacraApp:
    """
    Enhanced Flask application supporting the complete Simulacra workflow.
    Extends existing visualization_server.py capabilities.
    """
    
    def __init__(self, port: int = 5000, debug: bool = False):
        self.app = Flask(__name__, 
                        template_folder='templates',
                        static_folder='static')
        self.app.secret_key = 'simulacra_secret_key'  # TODO: Use environment variable
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.port = port
        self.debug = debug
        
        # State management
        self.project_manager = ProjectManager()
        self.template_manager = TemplateManager()
        self.simulation_manager = SimulationManager()
        
        self._register_routes()
        self._register_socket_handlers()
    
    def _register_routes(self):
        """Register all route handlers for the unified interface."""
        
        # Main application route
        @self.app.route('/')
        def index():
            return render_template('unified_interface.html')
        
        # Project management routes
        @self.app.route('/api/projects', methods=['GET'])
        def get_projects():
            return jsonify(self.project_manager.list_projects())
        
        @self.app.route('/api/projects', methods=['POST'])
        def create_project():
            data = request.get_json()
            project = self.project_manager.create_project(data)
            return jsonify(project.to_dict())
        
        @self.app.route('/api/projects/<project_id>', methods=['GET'])
        def get_project(project_id: str):
            project = self.project_manager.get_project(project_id)
            return jsonify(project.to_dict() if project else None)
        
        # Template management routes
        @self.app.route('/api/templates', methods=['GET'])
        def get_templates():
            return jsonify(self.template_manager.list_templates())
        
        @self.app.route('/api/templates/<template_id>', methods=['GET'])
        def get_template(template_id: str):
            template = self.template_manager.get_template(template_id)
            return jsonify(template.to_dict() if template else None)
        
        # Configuration validation routes
        @self.app.route('/api/validate/city', methods=['POST'])
        def validate_city_config():
            config = request.get_json()
            validation_result = self._validate_city_configuration(config)
            return jsonify(validation_result)
        
        @self.app.route('/api/validate/population', methods=['POST'])
        def validate_population_config():
            config = request.get_json()
            validation_result = self._validate_population_configuration(config)
            return jsonify(validation_result)
        
        # Simulation control routes
        @self.app.route('/api/simulation/start', methods=['POST'])
        def start_simulation():
            config = request.get_json()
            simulation_id = self.simulation_manager.start_simulation(config)
            return jsonify({'simulation_id': simulation_id, 'status': 'started'})
        
        @self.app.route('/api/simulation/<sim_id>/status', methods=['GET'])
        def get_simulation_status(sim_id: str):
            status = self.simulation_manager.get_status(sim_id)
            return jsonify(status)
        
        # Data export routes
        @self.app.route('/api/export/<sim_id>/<export_type>', methods=['POST'])
        def export_simulation_data(sim_id: str, export_type: str):
            options = request.get_json() or {}
            export_path = self.simulation_manager.export_data(sim_id, export_type, options)
            return jsonify({'export_path': str(export_path), 'status': 'complete'})
```

### 1.2 State Management System

```python
# src/visualization/state_manager.py
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from pathlib import Path

@dataclass
class SimulationConfiguration:
    """Complete simulation configuration state."""
    # City configuration
    city_name: str = "New City"
    city_size: str = "medium"  # small, medium, large
    districts: List[Dict[str, Any]] = None
    buildings: Dict[str, int] = None  # building_type -> count
    
    # Population configuration
    total_agents: int = 100
    population_mix: Dict[str, float] = None  # population_type -> proportion
    behavioral_params: Dict[str, Any] = None
    
    # Simulation parameters
    duration_months: int = 12
    rounds_per_month: int = 8
    update_interval: float = 1.0
    economic_conditions: Dict[str, Any] = None
    data_collection: Dict[str, bool] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    project_id: Optional[str] = None
    
    def __post_init__(self):
        # Set defaults for complex fields
        if self.districts is None:
            self.districts = []
        if self.buildings is None:
            self.buildings = {"residential": 10, "commercial": 5, "industrial": 3}
        if self.population_mix is None:
            self.population_mix = {"balanced": 0.7, "vulnerable": 0.3}
        if self.behavioral_params is None:
            self.behavioral_params = {
                "risk_preference": "normal",
                "addiction_vulnerability": 0.4,
                "economic_stress": 0.5,
                "impulsivity_range": [0.2, 0.8]
            }
        if self.economic_conditions is None:
            self.economic_conditions = {
                "unemployment_rate": 0.08,
                "rent_inflation": 0.02,
                "economic_shocks": "mild",
                "job_market": "balanced"
            }
        if self.data_collection is None:
            self.data_collection = {
                "agent_metrics": True,
                "population_stats": True,
                "life_events": True,
                "action_history": True,
                "export_data": True
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimulationConfiguration':
        """Create instance from dictionary."""
        return cls(**data)
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate configuration and return validation results.
        
        Returns:
            Dict with 'valid' boolean and 'errors'/'warnings' lists
        """
        errors = []
        warnings = []
        
        # Validate city configuration
        if not self.city_name or len(self.city_name.strip()) == 0:
            errors.append("City name is required")
        
        if self.total_agents < 1:
            errors.append("Must have at least 1 agent")
        elif self.total_agents > 1000:
            warnings.append("Large populations (>1000) may cause performance issues")
        
        # Validate population mix
        mix_sum = sum(self.population_mix.values())
        if abs(mix_sum - 1.0) > 0.01:
            errors.append(f"Population mix must sum to 1.0, currently sums to {mix_sum:.2f}")
        
        # Validate building capacity
        total_housing = self.buildings.get("residential", 0) * 5  # Assume 5 units per building
        if total_housing < self.total_agents:
            warnings.append(f"Insufficient housing capacity ({total_housing}) for population ({self.total_agents})")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


class ProjectManager:
    """Manages simulation projects and their configurations."""
    
    def __init__(self, projects_dir: str = "simulacra_projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(exist_ok=True)
        self._projects: Dict[str, SimulationConfiguration] = {}
        self._load_existing_projects()
    
    def create_project(self, config_data: Dict[str, Any]) -> 'Project':
        """Create a new project from configuration data."""
        project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        config = SimulationConfiguration.from_dict(config_data)
        config.project_id = project_id
        config.created_at = datetime.now()
        
        project = Project(project_id, config)
        self._projects[project_id] = config
        self._save_project(project)
        return project
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all available projects."""
        return [
            {
                'id': pid,
                'name': config.city_name,
                'created_at': config.created_at.isoformat() if config.created_at else None,
                'agents': config.total_agents,
                'duration': config.duration_months
            }
            for pid, config in self._projects.items()
        ]

@dataclass 
class Project:
    """Represents a simulation project."""
    id: str
    configuration: SimulationConfiguration
    status: str = "configured"  # configured, running, completed, error
    simulation_id: Optional[str] = None
    results_path: Optional[Path] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'configuration': self.configuration.to_dict(),
            'status': self.status,
            'simulation_id': self.simulation_id,
            'results_path': str(self.results_path) if self.results_path else None
        }
```

### 1.3 Template System

```python
# src/visualization/template_manager.py
from typing import Dict, List, Any
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class SimulationTemplate:
    """Pre-configured simulation template."""
    id: str
    name: str
    description: str
    category: str  # basic, addiction, economic, policy
    configuration: SimulationConfiguration
    preview_image: Optional[str] = None
    tags: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'configuration': self.configuration.to_dict(),
            'preview_image': self.preview_image,
            'tags': self.tags or []
        }

class TemplateManager:
    """Manages simulation templates and presets."""
    
    def __init__(self):
        self.templates = self._create_default_templates()
    
    def _create_default_templates(self) -> Dict[str, SimulationTemplate]:
        """Create the default template library."""
        templates = {}
        
        # Basic Urban Study Template
        basic_config = SimulationConfiguration(
            city_name="Basic Urban Study",
            total_agents=50,
            duration_months=6,
            population_mix={"balanced": 0.8, "vulnerable": 0.2}
        )
        templates['basic_urban'] = SimulationTemplate(
            id='basic_urban',
            name='Basic Urban Study',
            description='Simple urban simulation for learning and basic research',
            category='basic',
            configuration=basic_config,
            tags=['beginner', 'education', 'general']
        )
        
        # Addiction Research Template
        addiction_config = SimulationConfiguration(
            city_name="Addiction Research Study",
            total_agents=100,
            duration_months=18,
            population_mix={"balanced": 0.5, "vulnerable": 0.5},
            buildings={"residential": 15, "commercial": 8, "liquor_stores": 6, "casinos": 3}
        )
        addiction_config.behavioral_params["addiction_vulnerability"] = 0.6
        templates['addiction_research'] = SimulationTemplate(
            id='addiction_research',
            name='Addiction Research',
            description='Study addiction patterns and intervention effectiveness',
            category='addiction',
            configuration=addiction_config,
            tags=['addiction', 'healthcare', 'research']
        )
        
        # Economic Inequality Template
        economic_config = SimulationConfiguration(
            city_name="Economic Inequality Study",
            total_agents=150,
            duration_months=24,
            population_mix={"wealthy": 0.1, "middle_class": 0.3, "working_class": 0.4, "poor": 0.2}
        )
        economic_config.economic_conditions["unemployment_rate"] = 0.12
        templates['economic_inequality'] = SimulationTemplate(
            id='economic_inequality',
            name='Economic Inequality',
            description='Examine wealth distribution and economic mobility',
            category='economic',
            configuration=economic_config,
            tags=['economics', 'inequality', 'policy']
        )
        
        # Policy Testing Template
        policy_config = SimulationConfiguration(
            city_name="Policy Testing Environment",
            total_agents=200,
            duration_months=12,
            population_mix={"balanced": 0.6, "vulnerable": 0.3, "resilient": 0.1}
        )
        templates['policy_testing'] = SimulationTemplate(
            id='policy_testing',
            name='Policy Testing',
            description='Test policy interventions and their effectiveness',
            category='policy',
            configuration=policy_config,
            tags=['policy', 'government', 'intervention']
        )
        
        return templates
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """Get list of all available templates."""
        return [template.to_dict() for template in self.templates.values()]
    
    def get_template(self, template_id: str) -> Optional[SimulationTemplate]:
        """Get specific template by ID."""
        return self.templates.get(template_id)
```

## Phase 2: Frontend SPA Framework (Week 2-3)

### 2.1 Main HTML Template

```html
<!-- src/visualization/templates/unified_interface.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulacra - Unified Simulation Platform</title>
    
    <!-- CSS Libraries -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    
    <!-- Custom Styles -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/unified_interface.css') }}">
</head>
<body>
    <!-- Main Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">
                <i class="fas fa-city"></i> Simulacra
            </a>
            
            <!-- Primary Navigation -->
            <ul class="navbar-nav nav-pills" id="mainNavigation">
                <li class="nav-item">
                    <a class="nav-link active" href="#" data-section="home">
                        <i class="fas fa-home"></i> Home
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#" data-section="setup">
                        <i class="fas fa-cogs"></i> Setup
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#" data-section="run">
                        <i class="fas fa-play"></i> Run
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#" data-section="analyze">
                        <i class="fas fa-chart-line"></i> Analyze
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#" data-section="export">
                        <i class="fas fa-download"></i> Export
                    </a>
                </li>
            </ul>
            
            <!-- User Controls -->
            <div class="navbar-nav ms-auto">
                <div class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                        <i class="fas fa-user"></i> Project
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#" id="saveProject">Save Project</a></li>
                        <li><a class="dropdown-item" href="#" id="loadProject">Load Project</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="#" id="newProject">New Project</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content Area -->
    <main class="main-content" id="mainContent">
        <!-- Home Section -->
        <section id="homeSection" class="content-section active">
            <div class="container mt-5">
                <div class="row">
                    <div class="col-12">
                        <h1 class="display-4">Welcome to Simulacra</h1>
                        <p class="lead">Urban simulation platform for research and analysis</p>
                    </div>
                </div>
                
                <!-- Recent Projects -->
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-folder-open"></i> Recent Projects</h5>
                            </div>
                            <div class="card-body" id="recentProjects">
                                <!-- Populated by JavaScript -->
                            </div>
                        </div>
                    </div>
                    
                    <!-- Quick Actions -->
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-zap"></i> Quick Actions</h5>
                            </div>
                            <div class="card-body">
                                <div class="d-grid gap-2">
                                    <button class="btn btn-primary" id="newSimulationBtn">
                                        <i class="fas fa-plus"></i> New Simulation
                                    </button>
                                    <button class="btn btn-secondary" id="loadProjectBtn">
                                        <i class="fas fa-folder-open"></i> Load Project
                                    </button>
                                    <button class="btn btn-info" id="viewExamplesBtn">
                                        <i class="fas fa-eye"></i> View Examples
                                    </button>
                                    <a href="#" class="btn btn-outline-primary" id="documentationBtn">
                                        <i class="fas fa-book"></i> Documentation
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Template Gallery -->
                <div class="row mt-4">
                    <div class="col-12">
                        <h3>Simulation Templates</h3>
                        <div class="row" id="templateGallery">
                            <!-- Populated by JavaScript -->
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Setup Section (Wizard) -->
        <section id="setupSection" class="content-section">
            <!-- Setup wizard content will be loaded here -->
        </section>

        <!-- Run Section (Dashboard) -->
        <section id="runSection" class="content-section">
            <!-- Real-time dashboard will be loaded here -->
        </section>

        <!-- Analyze Section -->
        <section id="analyzeSection" class="content-section">
            <!-- Analysis tools will be loaded here -->
        </section>

        <!-- Export Section -->
        <section id="exportSection" class="content-section">
            <!-- Export tools will be loaded here -->
        </section>
    </main>

    <!-- JavaScript Libraries -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <!-- Custom JavaScript -->
    <script src="{{ url_for('static', filename='js/unified_interface.js') }}"></script>
</body>
</html>
```

### 2.2 JavaScript Application Framework

```javascript
// src/visualization/static/js/unified_interface.js

class SimulacraApp {
    constructor() {
        this.currentSection = 'home';
        this.socket = io();
        this.state = {
            currentProject: null,
            configuration: null,
            simulation: null
        };
        
        this.setupWizard = new SetupWizard();
        this.dashboard = new SimulationDashboard();
        this.analysisTools = new AnalysisTools();
        this.exportCenter = new ExportCenter();
        
        this.init();
    }
    
    init() {
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
                const section = e.target.dataset.section;
                this.showSection(section);
            });
        });
        
        // Handle quick action buttons
        document.getElementById('newSimulationBtn').addEventListener('click', () => {
            this.startNewSimulation();
        });
        
        document.getElementById('loadProjectBtn').addEventListener('click', () => {
            this.showLoadProjectDialog();
        });
        
        document.getElementById('viewExamplesBtn').addEventListener('click', () => {
            this.showTemplateGallery();
        });
    }
    
    setupSocketHandlers() {
        // Real-time simulation updates
        this.socket.on('simulation_update', (data) => {
            if (this.currentSection === 'run') {
                this.dashboard.updateSimulationData(data);
            }
        });
        
        // Configuration validation results
        this.socket.on('validation_result', (data) => {
            this.setupWizard.handleValidationResult(data);
        });
        
        // Export completion notifications
        this.socket.on('export_complete', (data) => {
            this.exportCenter.handleExportComplete(data);
        });
    }
    
    async loadInitialData() {
        try {
            // Load recent projects
            const projects = await this.apiCall('/api/projects');
            this.displayRecentProjects(projects);
            
            // Load template gallery
            const templates = await this.apiCall('/api/templates');
            this.displayTemplateGallery(templates);
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('Error loading application data', 'error');
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
            case 'setup':
                this.setupWizard.initialize();
                break;
            case 'run':
                this.dashboard.initialize();
                break;
            case 'analyze':
                this.analysisTools.initialize();
                break;
            case 'export':
                this.exportCenter.initialize();
                break;
        }
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
        
        if (projects.length === 0) {
            container.innerHTML = '<p class="text-muted">No recent projects</p>';
            return;
        }
        
        const projectsHtml = projects.map(project => `
            <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                <div>
                    <h6 class="mb-0">${project.name}</h6>
                    <small class="text-muted">${project.agents} agents, ${project.duration} months</small>
                </div>
                <button class="btn btn-sm btn-outline-primary" onclick="app.loadProject('${project.id}')">
                    Load
                </button>
            </div>
        `).join('');
        
        container.innerHTML = projectsHtml;
    }
    
    displayTemplateGallery(templates) {
        const container = document.getElementById('templateGallery');
        
        const templatesHtml = templates.map(template => `
            <div class="col-md-3 mb-3">
                <div class="card template-card" data-template-id="${template.id}">
                    <div class="card-body">
                        <h6 class="card-title">${template.name}</h6>
                        <p class="card-text small">${template.description}</p>
                        <div class="d-flex justify-content-between">
                            <span class="badge bg-secondary">${template.category}</span>
                            <button class="btn btn-sm btn-primary" onclick="app.useTemplate('${template.id}')">
                                Use
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = templatesHtml;
    }
    
    async useTemplate(templateId) {
        try {
            const template = await this.apiCall(`/api/templates/${templateId}`);
            this.state.configuration = new SimulationConfiguration(template.configuration);
            this.showSection('setup');
            this.setupWizard.loadConfiguration(this.state.configuration);
        } catch (error) {
            console.error('Error loading template:', error);
            this.showNotification('Error loading template', 'error');
        }
    }
    
    showNotification(message, type = 'info') {
        // Simple notification system
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
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

// Configuration object for the setup wizard
class SimulationConfiguration {
    constructor(data = {}) {
        this.cityName = data.cityName || "New City";
        this.citySize = data.citySize || "medium";
        this.districts = data.districts || [];
        this.buildings = data.buildings || {
            residential: 10,
            commercial: 5,
            industrial: 3
        };
        
        this.totalAgents = data.totalAgents || 100;
        this.populationMix = data.populationMix || {
            balanced: 0.7,
            vulnerable: 0.3
        };
        this.behavioralParams = data.behavioralParams || {
            riskPreference: "normal",
            addictionVulnerability: 0.4,
            economicStress: 0.5,
            impulsivityRange: [0.2, 0.8]
        };
        
        this.durationMonths = data.durationMonths || 12;
        this.roundsPerMonth = data.roundsPerMonth || 8;
        this.updateInterval = data.updateInterval || 1.0;
        
        this.economicConditions = data.economicConditions || {
            unemploymentRate: 0.08,
            rentInflation: 0.02,
            economicShocks: "mild",
            jobMarket: "balanced"
        };
        
        this.dataCollection = data.dataCollection || {
            agentMetrics: true,
            populationStats: true,
            lifeEvents: true,
            actionHistory: true,
            exportData: true
        };
    }
    
    toDict() {
        return {
            cityName: this.cityName,
            citySize: this.citySize,
            districts: this.districts,
            buildings: this.buildings,
            totalAgents: this.totalAgents,
            populationMix: this.populationMix,
            behavioralParams: this.behavioralParams,
            durationMonths: this.durationMonths,
            roundsPerMonth: this.roundsPerMonth,
            updateInterval: this.updateInterval,
            economicConditions: this.economicConditions,
            dataCollection: this.dataCollection
        };
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.app = new SimulacraApp();
});
```

## Phase 3: Setup Wizard Implementation (Week 3-4)

### 3.1 Setup Wizard Framework

```javascript
// src/visualization/static/js/setup_wizard.js

class SetupWizard {
    constructor() {
        this.currentStep = 0;
        this.steps = ['city', 'population', 'simulation', 'review'];
        this.configuration = null;
        this.validationResults = {};
    }
    
    initialize() {
        this.loadWizardTemplate();
        this.setupEventHandlers();
        this.showStep(0);
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
                                        <div>City</div>
                                    </div>
                                </div>
                                <div class="col-3 text-center">
                                    <div class="step-indicator" data-step="1">
                                        <i class="fas fa-users"></i>
                                        <div>Population</div>
                                    </div>
                                </div>
                                <div class="col-3 text-center">
                                    <div class="step-indicator" data-step="2">
                                        <i class="fas fa-cogs"></i>
                                        <div>Simulation</div>
                                    </div>
                                </div>
                                <div class="col-3 text-center">
                                    <div class="step-indicator" data-step="3">
                                        <i class="fas fa-check"></i>
                                        <div>Review</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Step Content -->
                        <div class="card">
                            <div class="card-body">
                                <div id="stepContent">
                                    <!-- Step content loaded here -->
                                </div>
                                
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
    }
    
    showStep(stepIndex) {
        this.currentStep = stepIndex;
        this.updateProgressIndicator();
        this.updateNavigationButtons();
        
        const stepContent = document.getElementById('stepContent');
        
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
    }
    
    showCityConfigurationStep(container) {
        container.innerHTML = `
            <h4>Step 1: City Configuration</h4>
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
                                       value="${this.configuration?.cityName || 'New City'}">
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">City Size</label>
                                <div class="btn-group d-flex" role="group">
                                    <input type="radio" class="btn-check" name="citySize" id="sizeSmall" value="small">
                                    <label class="btn btn-outline-primary" for="sizeSmall">Small</label>
                                    
                                    <input type="radio" class="btn-check" name="citySize" id="sizeMedium" value="medium" checked>
                                    <label class="btn btn-outline-primary" for="sizeMedium">Medium</label>
                                    
                                    <input type="radio" class="btn-check" name="citySize" id="sizeLarge" value="large">
                                    <label class="btn btn-outline-primary" for="sizeLarge">Large</label>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Map Preview</label>
                                <div id="cityMapPreview" class="border p-3" style="height: 200px;">
                                    <small class="text-muted">Interactive city map will appear here</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-map"></i> Districts</h6>
                        </div>
                        <div class="card-body">
                            <div id="districtsList">
                                <!-- Districts list will be populated here -->
                            </div>
                            <button class="btn btn-sm btn-outline-primary" id="addDistrictBtn">
                                <i class="fas fa-plus"></i> Add District
                            </button>
                        </div>
                    </div>
                    
                    <div class="card mt-3">
                        <div class="card-header">
                            <h6><i class="fas fa-building"></i> Buildings</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-2">
                                <label class="form-label">Residential</label>
                                <div class="d-flex align-items-center">
                                    <input type="range" class="form-range flex-grow-1" min="1" max="50" value="10" id="residentialCount">
                                    <span class="ms-2" id="residentialValue">10</span>
                                </div>
                            </div>
                            <div class="mb-2">
                                <label class="form-label">Commercial</label>
                                <div class="d-flex align-items-center">
                                    <input type="range" class="form-range flex-grow-1" min="1" max="20" value="5" id="commercialCount">
                                    <span class="ms-2" id="commercialValue">5</span>
                                </div>
                            </div>
                            <div class="mb-2">
                                <label class="form-label">Industrial</label>
                                <div class="d-flex align-items-center">
                                    <input type="range" class="form-range flex-grow-1" min="1" max="15" value="3" id="industrialCount">
                                    <span class="ms-2" id="industrialValue">3</span>
                                </div>
                            </div>
                            
                            <hr>
                            
                            <div class="row">
                                <div class="col-6">
                                    <small>🎰 Casinos: <span id="casinosCount">2</span></small>
                                </div>
                                <div class="col-6">
                                    <small>🍺 Liquor Stores: <span id="liquorStoresCount">5</span></small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.setupCityConfigurationHandlers();
    }
    
    setupCityConfigurationHandlers() {
        // Real-time updates for building counts
        ['residential', 'commercial', 'industrial'].forEach(type => {
            const slider = document.getElementById(`${type}Count`);
            const display = document.getElementById(`${type}Value`);
            
            slider.addEventListener('input', (e) => {
                display.textContent = e.target.value;
                this.updateBuildingCounts();
            });
        });
        
        // Add district functionality
        document.getElementById('addDistrictBtn').addEventListener('click', () => {
            this.addDistrict();
        });
        
        // City name validation
        document.getElementById('cityName').addEventListener('blur', () => {
            this.validateCurrentStep();
        });
    }
    
    async nextStep() {
        // Validate current step before proceeding
        const isValid = await this.validateCurrentStep();
        if (!isValid) {
            return;
        }
        
        // Save current step data
        this.saveCurrentStepData();
        
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
        const stepData = this.getCurrentStepData();
        
        try {
            const response = await app.apiCall(`/api/validate/${this.steps[this.currentStep]}`, 'POST', stepData);
            this.validationResults[this.steps[this.currentStep]] = response;
            
            if (!response.valid) {
                this.showValidationErrors(response.errors, response.warnings);
                return false;
            }
            
            if (response.warnings && response.warnings.length > 0) {
                this.showValidationWarnings(response.warnings);
            }
            
            return true;
        } catch (error) {
            console.error('Validation error:', error);
            app.showNotification('Validation error occurred', 'error');
            return false;
        }
    }
    
    showValidationErrors(errors, warnings = []) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger';
        
        let content = '<strong>Configuration Errors:</strong><ul>';
        errors.forEach(error => {
            content += `<li>${error}</li>`;
        });
        content += '</ul>';
        
        if (warnings.length > 0) {
            content += '<strong>Warnings:</strong><ul>';
            warnings.forEach(warning => {
                content += `<li>${warning}</li>`;
            });
            content += '</ul>';
        }
        
        alertDiv.innerHTML = content;
        
        const stepContent = document.getElementById('stepContent');
        stepContent.insertBefore(alertDiv, stepContent.firstChild);
    }
    
    updateProgressIndicator() {
        document.querySelectorAll('.step-indicator').forEach((indicator, index) => {
            if (index <= this.currentStep) {
                indicator.classList.add('active');
            } else {
                indicator.classList.remove('active');
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
            const nextStepName = this.steps[this.currentStep + 1];
            nextBtn.innerHTML = `Next: ${nextStepName.charAt(0).toUpperCase() + nextStepName.slice(1)} <i class="fas fa-arrow-right"></i>`;
            nextBtn.className = 'btn btn-primary';
        }
    }
}
```

This implementation roadmap provides the foundation for building the unified Simulacra interface. Each phase builds incrementally on the existing infrastructure while adding the new functionality outlined in the design specification.

## Next Steps

1. **Start with Phase 1**: Implement the core infrastructure and state management
2. **Extend existing dashboard**: Build on the existing `demo_realtime_visualization.py` 
3. **Integrate with current analytics**: Leverage the existing metrics and export systems
4. **Test incrementally**: Each phase should be tested before moving to the next

The roadmap is designed to minimize disruption to existing functionality while progressively adding the unified interface capabilities. 