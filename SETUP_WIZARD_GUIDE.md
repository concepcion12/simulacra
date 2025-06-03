# Simulacra Setup Wizard - Complete Guide

The setup wizard is now fully implemented! Here's what you can do with the completed functionality:

## 🚀 Quick Start

1. **Start the unified interface:**
   ```bash
   python start_unified_interface.py
   ```

2. **Open your browser:**
   Navigate to `http://localhost:5000`

3. **Start the setup wizard:**
   Click "New Simulation" or navigate to the Setup section

## ✨ Completed Features

### Step 1: City Configuration
- ✅ **City naming and sizing**
- ✅ **Building configuration sliders:**
  - Residential buildings (1-50)
  - Commercial buildings (1-20) 
  - Industrial buildings (1-15)
  - Casinos (0-10)
  - Liquor stores (0-15)
- ✅ **Real-time capacity calculations:**
  - Housing capacity (5 units per residential building)
  - Employment capacity estimates
  - Total building count
- ✅ **Live validation** with immediate feedback

### Step 2: Population Configuration  
- ✅ **Population size control** (1-1000 agents)
- ✅ **Population mix sliders:**
  - Balanced vs Vulnerable populations
  - Auto-balancing percentages
- ✅ **Behavioral parameters:**
  - Risk preference (Low/Normal/High)
  - Addiction vulnerability (0-100%)
  - Economic stress levels (0-100%)
- ✅ **Live population preview** showing agent distribution

### Step 3: Simulation Parameters ⭐ NEW!
- ✅ **Time configuration:**
  - Duration (1-60 months)
  - Rounds per month (1-16)
  - Update interval (0.1-5.0 seconds)
  - **Real-time runtime estimation**
- ✅ **Economic conditions:**
  - Unemployment rate (1-25%)
  - Rent inflation (0-10%)
  - Economic shock severity (None/Mild/Moderate/Severe)
  - Job market conditions (Tight/Balanced/Loose)
- ✅ **Data collection options:**
  - Individual agent metrics
  - Population-level statistics
  - Life events tracking
  - Action history logging
  - Export data toggle

### Step 4: Review & Launch ⭐ NEW!
- ✅ **Complete configuration summary** with organized sections
- ✅ **Pre-flight validation checks:**
  - City configuration validation
  - Housing capacity warnings
  - Population mix verification
  - Data collection status
  - Performance optimization alerts
- ✅ **Configuration management:**
  - Save configurations with custom names
  - Option to save as reusable templates
  - Preview full configuration as JSON
- ✅ **Simulation launch** with error handling

## 🛠️ Technical Features

### Real-time Validation
- All steps validate input as you type/adjust sliders
- Immediate error highlighting and helpful warnings
- Progress indicator shows completion status

### Smart Defaults
- Pre-configured templates for different research scenarios:
  - Basic Urban Study
  - Addiction Research
  - Economic Inequality Study
  - Policy Testing Environment

### State Management
- Configuration persists as you move between steps
- Can navigate back/forward freely
- Auto-saves progress

### Runtime Estimation
The wizard calculates estimated runtime based on:
- Total simulation rounds (duration × rounds per month)
- Agent count impact on performance
- Shows time in seconds/minutes/hours appropriately

## 📊 Pre-flight Checks

The review step runs comprehensive validation:

✅ **Success indicators:**
- City configuration is valid
- Sufficient housing capacity
- Population mix sums to 100%
- Data collection enabled
- Performance optimized

⚠️ **Warnings (non-blocking):**
- Housing capacity may be insufficient
- Large simulations may be slow
- No data collection enabled

❌ **Errors (must fix):**
- City name is required
- Population mix must sum to 100%

## 🎯 Next Steps

After completing the setup wizard:

1. **Configuration is automatically saved** as a project
2. **Click "Launch Simulation"** to proceed to the Run dashboard
3. **Monitor progress** in real-time
4. **Access analysis tools** after simulation completes
5. **Export results** in multiple formats

## 🔧 Advanced Usage

### Custom Templates
You can save any configuration as a template for future use by checking "Save as template" in the review step.

### Configuration Import/Export
The preview button shows the full JSON configuration that can be copied and shared.

### API Integration
All wizard functionality is backed by REST APIs:
- `/api/validate/{step}` - Real-time validation
- `/api/projects` - Project management
- `/api/templates` - Template library
- `/api/simulation/start` - Launch simulations

## 🎨 User Experience

The setup wizard provides:
- **Progressive disclosure** - Complexity revealed as needed
- **Visual feedback** - Sliders, badges, and live updates
- **Contextual help** - Tooltips and recommendations
- **Error prevention** - Validation before allowing progression
- **Flexibility** - Jump between steps freely

Ready to create your first simulation? Just run `python start_unified_interface.py` and dive in! 🚀 