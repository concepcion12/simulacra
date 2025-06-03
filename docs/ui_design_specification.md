# Simulacra Unified UI Design Specification

## Executive Summary

This document outlines the design for a unified web-based interface for the Simulacra simulation platform. The interface will provide a complete workflow from simulation setup through execution to data analysis and export, building on the existing real-time dashboard infrastructure.

## Current State Assessment

### Existing Infrastructure ✅
- **Real-time Dashboard**: Flask/SocketIO web interface with live visualization
- **Analytics System**: Comprehensive metrics collection and export (CSV, JSON, reports)  
- **Population Generation**: Sophisticated agent creation with configurable distributions
- **Simulation Engine**: Complete city/agent/building simulation system
- **Data Export**: Multiple export formats and statistical reporting

### Current Gaps 🔧
- No integrated setup/configuration interface
- No unified workflow management 
- Limited scenario management capabilities
- No guided simulation configuration UI
- Export functionality scattered across different interfaces

## UI Architecture Overview

### Technology Stack
- **Frontend**: Enhanced HTML5/CSS3/JavaScript (building on existing dashboard)
- **Backend**: Flask with SocketIO (existing infrastructure)
- **Visualization**: D3.js for city maps, Chart.js for metrics (existing)
- **Styling**: Bootstrap 5 with custom dark theme (existing)
- **Real-time**: WebSocket communication (existing)

### Application Structure
```
Unified Simulacra Interface
├── 1. Welcome & Project Management
├── 2. Simulation Setup Wizard
├── 3. Real-time Execution Dashboard  
├── 4. Data Analysis & Visualization
└── 5. Export & Reporting Center
```

## Detailed UI Design

### 1. Welcome & Project Management Screen

**Purpose**: Entry point for managing simulation projects and scenarios

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ 🏙️ Simulacra - Urban Simulation Platform               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📋 Recent Projects          📁 Quick Actions           │
│  ┌─────────────────────┐    ┌─────────────────────┐     │
│  │ • Urban Study #1    │    │ 🆕 New Simulation  │     │
│  │ • Addiction Research│    │ 📁 Load Project    │     │
│  │ • Economic Impact   │    │ 📊 View Examples   │     │
│  │ • Policy Test       │    │ 📖 Documentation   │     │
│  └─────────────────────┘    └─────────────────────┘     │
│                                                         │
│  🎯 Simulation Templates                                │
│  ┌─────────────┬─────────────┬─────────────┬───────────┐ │
│  │ 🏘️ Basic    │ 🍺 Addiction│ 💰 Economic │ 🏛️ Policy │ │
│  │ Urban Study │ Research    │ Inequality  │ Testing   │ │
│  └─────────────┴─────────────┴─────────────┴───────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- Project management (save/load simulation configurations)
- Template library with pre-configured scenarios
- Recent projects history
- Documentation and help access

### 2. Simulation Setup Wizard

**Purpose**: Guided configuration of all simulation parameters

**Layout**: Multi-step wizard with progress indicator

#### Step 1: City Configuration
```
┌─────────────────────────────────────────────────────────┐
│ Step 1/4: City Configuration                            │
│ ●━━━○━━━○━━━○                                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🏙️ City Layout                    📊 District Setup   │
│  ┌─────────────────────┐          ┌─────────────────┐   │
│  │ City Name: [______] │          │ Districts: 3    │   │
│  │ Size: ●Small ○Med  │          │ ┌─────────────┐ │   │
│  │       ○Large       │          │ │ Downtown    │ │   │
│  │                    │          │ │ Wealth: ███ │ │   │
│  │ Map Preview:       │          │ │ Size: ██    │ │   │
│  │ ┌────────────────┐ │          │ └─────────────┘ │   │
│  │ │ [Visual Map]   │ │          │ + Add District  │   │
│  │ │                │ │          └─────────────────┘   │
│  │ └────────────────┘ │                                │
│  └─────────────────────┘                              │
│                                                         │
│  🏢 Building Configuration                              │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Residential: [████████████████]        80%        │ │
│  │ Commercial:  [██████]                  30%        │ │  
│  │ Industrial:  [████]                    20%        │ │
│  │ 🎰 Casinos: 2  🍺 Liquor Stores: 5  🏭 Employers: 8│ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  [← Back]                               [Next: Agents →]│
└─────────────────────────────────────────────────────────┘
```

#### Step 2: Population Configuration
```
┌─────────────────────────────────────────────────────────┐
│ Step 2/4: Population Configuration                      │
│ ○━━━●━━━○━━━○                                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  👥 Population Size & Composition                       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Total Agents: [100] ▲▼                             │ │
│  │                                                     │ │
│  │ 📊 Population Mix:                                  │ │
│  │ Balanced:     [████████████████] 70%               │ │
│  │ Vulnerable:   [████████]         30%               │ │
│  │ High-Income:  [████]             15%               │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  🧠 Behavioral Parameters                              │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Risk Preference:     Normal ●  High ○  Custom ○    │ │
│  │ Addiction Vulnerability: [████████] 40%            │ │
│  │ Economic Stress:     [██████████] 50%              │ │
│  │ Impulsivity Range:   [████] 20% - 80%              │ │
│  │                                                     │ │
│  │ 🎲 Advanced Config   📊 Preview Population         │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  [← Back]                        [Next: Simulation →]  │
└─────────────────────────────────────────────────────────┘
```

#### Step 3: Simulation Parameters
```
┌─────────────────────────────────────────────────────────┐
│ Step 3/4: Simulation Parameters                         │
│ ○━━━○━━━●━━━○                                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ⏱️ Time Configuration                                  │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Duration: [12] months                               │ │
│  │ Rounds per Month: [8] ▲▼                           │ │
│  │ Update Interval: [1.0] seconds                      │ │
│  │                                                     │ │
│  │ ⏰ Estimated Runtime: ~15 minutes                   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  💰 Economic Conditions                                 │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Base Unemployment: [8%] ████                        │ │
│  │ Rent Inflation:    [2%] ██                          │ │
│  │ Economic Shocks:   ○None ●Mild ○Severe              │ │
│  │ Job Market:        ○Tight ●Balanced ○Loose          │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  📊 Data Collection                                     │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ ☑️ Individual Agent Metrics                         │ │
│  │ ☑️ Population-level Statistics                      │ │
│  │ ☑️ Life Events Tracking                             │ │
│  │ ☑️ Action History Logging                           │ │
│  │ ☑️ Export Data (CSV, JSON, Reports)                │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  [← Back]                            [Review Setup →]  │
└─────────────────────────────────────────────────────────┘
```

#### Step 4: Review & Launch
```
┌─────────────────────────────────────────────────────────┐
│ Step 4/4: Review & Launch                               │
│ ○━━━○━━━○━━━●                                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📋 Configuration Summary                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ City: "Demo City" (3 districts, 45 buildings)       │ │
│  │ Population: 100 agents (70% balanced, 30% vulnerable│ │
│  │ Duration: 12 months (8 rounds/month)               │ │
│  │ Analytics: Full tracking enabled                    │ │
│  │ Storage: ~/simulacra_data/demo_20240315_1430       │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  ⚡ Pre-flight Checks                                   │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ ✅ City configuration valid                         │ │
│  │ ✅ Population parameters within bounds              │ │
│  │ ✅ Sufficient housing/employment capacity           │ │
│  │ ✅ Analytics system ready                           │ │
│  │ ✅ Export directory accessible                      │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  💾 Save Configuration As: [Demo Setup] [Save Template]│ │
│                                                         │ │
│  [← Back]      [🚀 Launch Simulation]     [💾 Save Only]│
└─────────────────────────────────────────────────────────┘
```

### 3. Real-time Execution Dashboard (Enhanced)

**Purpose**: Monitor and control running simulation (extends existing dashboard)

**Key Enhancements**:
- **Simulation Control Panel**: Enhanced controls for pause/resume/speed adjustment
- **Scenario Intervention Panel**: Add economic shocks, policy changes during runtime
- **Agent Inspector**: Click any agent to see detailed state and history
- **Alert System**: Notifications for significant events or threshold breaches
- **Export Controls**: One-click data export during simulation

**Layout Enhancement**:
```
┌─────────────────────────────────────────────────────────┐
│ 🏙️ Simulacra - Live Simulation Dashboard               │
├─────────────────────────────────────────────────────────┤
│ ⏱️ Month 8/12  ●Running  👥 98 agents  📊 Data: 45MB    │
├─────────────────────────────────────────────────────────┤
│                                  │                      │
│  [Existing Map View]             │  🎛️ Controls         │
│  [Agent positions,               │  ⏸️ ⏵️ ⏹️ 🔄        │
│   building states,               │  Speed: [████░░]     │
│   heat maps...]                  │                      │
│                                  │  🚨 Interventions    │
│                                  │  💰 Economic Shock   │
│                                  │  🏠 Housing Program  │
│                                  │                      │
│                                  │                      │
│                                  │  📤 Quick Export     │
│                                  │  📊 📈 📋 💾        │
├─────────────────────────────────────────────────────────┤
│ [Live Metrics Panels - Employment, Wealth, Addiction...] │
└─────────────────────────────────────────────────────────┘
```

### 4. Data Analysis & Visualization

**Purpose**: Comprehensive post-simulation analysis tools

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ 📊 Simulation Analysis - Demo Study Results             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📈 Overview Dashboard                                   │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Key Findings:                                       │ │
│  │ • Employment: 85% → 72% (13% decline)               │ │
│  │ • Addiction Rate: 15% → 28% (87% increase)          │ │
│  │ • Homelessness: 5% → 18% (260% increase)            │ │
│  │ • Wealth Inequality (Gini): 0.34 → 0.52             │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  🔍 Analysis Tools                                      │
│  ┌──────────────┬──────────────┬──────────────┬─────────┐│
│  │📊 Population│ 👤 Individual│ 🎯 Behavioral│ 💰 Econ ││
│  │ Trends       │ Trajectories │ Patterns     │ Metrics ││
│  │              │              │              │         ││
│  │ [Chart View] │ [Agent View] │ [Pattern ID] │ [Stats] ││
│  └──────────────┴──────────────┴──────────────┴─────────┘│
│                                                          │
│  📋 Interactive Data Table                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │Agent ID  │Final Wealth │ Addiction │ Employment     │ │
│  │ A001     │ $847        │ High      │ Unemployed     │ │
│  │ A002     │ $2,341      │ None      │ Employed       │ │
│  │ ...      │ ...         │ ...       │ ...            │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  [Filter Controls] [Sort Options] [Export Selected]     │
└─────────────────────────────────────────────────────────┘
```

### 5. Export & Reporting Center

**Purpose**: Unified data export and report generation

**Features**:
- **Export Templates**: Pre-configured export packages for common research needs
- **Custom Exports**: Choose specific data subsets and formats
- **Report Generator**: Automated statistical and visual reports
- **Data Validation**: Verify export completeness and quality
- **Sharing Tools**: Generate shareable URLs for datasets

## Navigation & Workflow

### Primary Navigation
```
┌─────────────────────────────────────────────────────────┐
│ [🏠 Home] [⚙️ Setup] [▶️ Run] [📊 Analyze] [📤 Export] │
└─────────────────────────────────────────────────────────┘
```

### State Management
- **Session Persistence**: Save intermediate progress
- **Undo/Redo**: Configuration changes
- **Templates**: Save/load common configurations
- **Workspaces**: Organize multiple simulation projects

## Technical Implementation Plan

### Phase 1: Core Infrastructure (2-3 weeks)
1. **Navigation Framework**: Implement multi-section SPA structure
2. **State Management**: Centralized configuration and simulation state
3. **Template System**: Save/load functionality for configurations
4. **Enhanced Backend**: Extend existing Flask app with setup endpoints

### Phase 2: Setup Wizard (3-4 weeks)
1. **City Configuration UI**: Interactive city/district builder
2. **Population Configuration**: Enhanced population parameter controls
3. **Simulation Parameters**: Time, economic, analytics configuration
4. **Pre-flight Validation**: Configuration checking and warnings

### Phase 3: Enhanced Dashboard (2-3 weeks)
1. **Intervention Controls**: Runtime scenario modification
2. **Agent Inspector**: Detailed agent state viewer
3. **Alert System**: Event notifications and threshold monitoring
4. **Quick Export**: One-click data export during simulation

### Phase 4: Analysis Tools (3-4 weeks)
1. **Analysis Dashboard**: Post-simulation data exploration
2. **Interactive Visualizations**: Charts, tables, and filtering tools
3. **Pattern Detection**: Automated behavioral pattern identification
4. **Comparison Tools**: Multi-simulation comparison capabilities

### Phase 5: Export & Reporting (2-3 weeks)
1. **Export Center**: Unified export interface
2. **Report Templates**: Automated report generation
3. **Data Validation**: Export verification tools
4. **Sharing Features**: Dataset sharing and collaboration tools

## User Experience Flow

### Typical User Journey
1. **Start**: User opens Simulacra interface
2. **Setup**: Choose template or create custom simulation
3. **Configure**: Step-by-step wizard guides through all parameters
4. **Validate**: Pre-flight checks ensure valid configuration
5. **Execute**: Real-time dashboard monitors simulation progress
6. **Intervene**: Optional runtime modifications to test scenarios
7. **Analyze**: Comprehensive post-simulation data exploration
8. **Export**: Generate reports and export data for further analysis
9. **Share**: Save configuration as template for future use

### Design Principles
- **Guided Workflow**: Clear step-by-step progression
- **Progressive Disclosure**: Show complexity only when needed
- **Immediate Feedback**: Real-time validation and preview
- **Discoverability**: Intuitive navigation and help system
- **Flexibility**: Power users can access advanced features
- **Persistence**: Never lose work, always save progress

## Success Metrics

### Usability Goals
- **Setup Time**: < 5 minutes for basic simulation
- **Error Rate**: < 2% invalid configurations reach execution
- **Learning Curve**: New users productive within 30 minutes
- **Data Access**: All simulation data accessible within 3 clicks

### Technical Goals
- **Performance**: UI responsive < 200ms for all interactions
- **Reliability**: Zero data loss during simulation execution
- **Compatibility**: Works in all modern browsers
- **Scalability**: Support simulations up to 1000 agents

## Future Enhancements

### Advanced Features (Post-MVP)
- **Collaborative Workspaces**: Multi-user simulation configuration
- **A/B Testing Framework**: Automated scenario comparison
- **Machine Learning Integration**: Predictive analytics and optimization
- **Cloud Deployment**: Scalable cloud-based simulation execution
- **API Access**: Programmatic access for researchers
- **Plugin System**: Custom extensions and analysis tools

This unified interface will transform Simulacra from a powerful but complex toolkit into an accessible, end-to-end simulation platform suitable for researchers, policymakers, and educators at all technical levels. 

