# Simulacra Development Roadmap

## Current Status
✅ **Phase 1: Foundation** - Agent architecture with behavioral economics
✅ **Phase 2: Decision Making** - Multi-component utility system with dual-process cognition

## Next Development Phases

### Phase 3: Environment Implementation (Next Priority)

#### 3.1 City Structure
- [x] Create `City` class with districts and spatial layout
- [x] Implement `District` class with wealth levels and characteristics
- [x] Create `Plot` system for spatial locations
- [x] Add coordinate system and distance calculations

#### 3.2 Building Types
- [x] **ResidentialBuilding**: Apartments, houses, shelters
  - Housing units with rent/quality
  - Mood/stress modifiers based on quality
- [x] **LiquorStore**: Alcohol sales
  - Price variations by district
  - Cue generation for nearby agents
- [x] **Casino**: Gambling venues
  - Different games with house edges
  - Near-miss mechanics
- [x] **Employer**: Job locations
  - Job openings with requirements
  - Salary and stress levels
- [x] **PublicSpace**: Parks, streets
  - Begging locations
  - Rest and recovery venues

#### 3.3 Environmental Cue System
- [x] Spatial cue generation based on proximity
- [x] Cue intensity based on distance and agent state

### Phase 4: Action Execution System

#### 4.1 Action Outcomes
- [x] Implement outcome generation for each action type
- [x] Add stochastic elements (gambling wins/losses, begging income)
- [x] Create outcome → state update pipeline
- [x] Handle action failures and constraints

#### 4.2 State Updates from Actions
- [x] **Work**: Income, stress, performance tracking
- [x] **Drink**: Addiction progression, habit reinforcement
- [x] **Gamble**: Win/loss tracking, near-miss effects
- [x] **Rest**: Recovery mechanics
- [x] **Housing/Job Search**: Success probabilities

#### 4.3 Movement System
- [x] Agent movement between plots
- [x] Time costs for movement
- [x] Location-based action availability

### Phase 5: Simulation Loop

#### 5.1 Time Management
- [x] Monthly simulation cycle
- [x] Action round system within months
- [x] Start/end of month events (rent, salary)
- [x] Time progression mechanics

#### 5.2 Population Management
- [x] Initialize diverse agent population
- [x] Handle multiple agents efficiently
- [x] Agent lifecycle (potential for death/departure)
- [x] New agent introduction

#### 5.3 Economic System
- [x] City-wide economic parameters
- [x] Job market dynamics
- [x] Housing market availability
- [x] Price fluctuations

### Phase 6: Advanced Analytics

#### 6.1 Behavioral Analysis Tools
- [ ] Pattern recognition in agent behaviors
- [ ] Clustering analysis of agent types
- [ ] Behavioral trajectory analysis

#### 6.2 Intervention Analysis
- [ ] Policy intervention effects measurement
- [ ] Economic shock impact analysis
- [ ] Treatment program effectiveness

### Phase 7: Data Collection & Analysis ✅

#### 7.1 Metrics System ✅
- [x] Agent-level metrics (wealth, addiction progression)
- [x] Population-level statistics
- [x] Behavioral pattern tracking
- [x] Economic indicators

#### 7.2 History Tracking ✅
- [x] Detailed agent histories
- [x] Action sequences
- [x] State trajectories
- [x] Life event logging

#### 7.3 Export Capabilities ✅
- [x] CSV export for analysis
- [x] JSON serialization for full state
- [x] Statistical summaries

### Phase 8: Visualization

#### 8.1 Real-time Visualization
- [ ] City map with agent locations
- [ ] Agent state indicators
- [ ] Building occupancy
- [ ] Heat maps (stress, addiction, wealth)

#### 8.2 Analysis Plots
- [ ] Time series of key metrics
- [ ] Distribution plots
- [ ] Agent trajectory visualization
- [ ] Network graphs

#### 8.3 Interactive Dashboard
- [ ] Parameter adjustment
- [ ] Simulation control
- [ ] Agent inspection
- [ ] Scenario comparison

### Phase 9: Advanced Features

#### 9.1 Intervention System
- [ ] Policy interventions (addiction treatment, housing programs)
- [ ] Environmental changes (new casinos, job opportunities)
- [ ] Economic shocks
- [ ] Measure intervention effects

#### 9.2 Scenario Engine
- [ ] Predefined scenarios
- [ ] Parameter sweeps
- [ ] A/B testing framework
- [ ] Reproducible experiments

#### 9.3 Calibration Tools
- [ ] Parameter tuning utilities
- [ ] Validation against real-world data
- [ ] Sensitivity analysis
- [ ] Model diagnostics

## Implementation Priority Order

### Immediate Next Steps (Phase 3.1-3.2)
1. Create basic `City` and `District` classes
2. Implement `Plot` system with building placement
3. Create core building types (start with `ResidentialBuilding` and `LiquorStore`)
4. Test spatial mechanics and building interactions

### Short Term (Phase 4)
1. Implement action execution for core actions (Work, Drink, Rest)
2. Create outcome → state update pipeline
3. Test action cycles with environment

### Medium Term (Phase 5)
1. Build monthly simulation loop
2. Handle multiple agents
3. Add economic dynamics

### Long Term (Phases 6-9)
1. Comprehensive data collection
2. Visualization tools
3. Advanced analysis features

## Technical Considerations

### Architecture Principles
- **Modularity**: Each phase builds on previous work
- **Testability**: Unit tests for each component
- **Performance**: Profile and optimize as agent count grows
- **Extensibility**: Easy to add new buildings, actions, mechanics

### Key Integration Points
- Environment ↔ Agent: Cue generation, action availability
- Action → Outcome → State: Clear update pipeline
- Time → Events: Monthly cycles trigger updates
- Data → Analysis: Comprehensive tracking from start

### Risk Mitigation
- Start simple, add complexity gradually
- Test each phase thoroughly before moving on
- Keep performance in mind from the start
- Document assumptions and parameters

## Success Metrics

### Phase Completion Criteria
- All unit tests passing
- Integration tests demonstrate expected behaviors
- Performance benchmarks met
- Documentation updated

### Behavioral Validation
- Agents show addiction progression
- Environmental cues trigger appropriate responses
- Economic pressures affect decisions

### System Goals
- 100+ agents running smoothly
- 12+ month simulations complete without errors
- Data suitable for analysis

This roadmap provides a clear path forward while maintaining flexibility to adjust based on discoveries during implementation. 