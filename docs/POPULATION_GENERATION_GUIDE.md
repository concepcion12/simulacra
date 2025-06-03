# Population Generation System Guide

This guide shows how to use the robust population generation system in Simulacra to create diverse agent populations with configurable distributions.

## Quick Start

### 1. Generate a Basic Population

```python
from src.population import QuickPopulationFactory

# Generate 100 balanced agents
agents = QuickPopulationFactory.create_balanced_population(100, seed=42)

# Generate vulnerable population (higher addiction risk, financial stress)
vulnerable_agents = QuickPopulationFactory.create_vulnerable_population(50, seed=123)

# Generate maximally diverse population
diverse_agents = QuickPopulationFactory.create_diverse_population(75, seed=456)
```

### 2. Analyze Your Population

```python
from src.population import PopulationAnalyzer

analyzer = PopulationAnalyzer()
stats = analyzer.analyze_population(agents)

print(f"Population size: {stats.size}")
print(f"Average wealth: ${stats.wealth_stats['mean']:,.0f}")
print(f"Average impulsivity: {stats.personality_stats['baseline_impulsivity']['mean']:.3f}")

# Check for warnings
if stats.distribution_warnings:
    for warning in stats.distribution_warnings:
        print(f"⚠️ {warning}")
```

### 3. Get Population Overview

```python
overview = analyzer.get_distribution_overview(agents)

print(f"Financial stress rate: {overview['summary']['financial_stress_rate']:.1%}")
print(f"High-risk profiles: {overview['summary']['high_risk_rate']:.1%}")
print(f"Wealth inequality (Gini): {overview['summary']['wealth_inequality_gini']:.3f}")
```

## Advanced Configuration

### Custom Distribution Configuration

```python
from src.population import DistributionConfig, DistributionType, DistributionSpec, PopulationGenerator

# Create custom configuration
config = DistributionConfig()

# Customize personality traits
config.update_personality_trait(
    'baseline_impulsivity',
    DistributionSpec(
        DistributionType.BIMODAL,
        {'mean1': 0.2, 'std1': 0.1, 'mean2': 0.8, 'std2': 0.1, 'weight1': 0.7},
        bounds=(0.0, 1.0),
        description="Mostly cautious with some very impulsive agents"
    )
)

# Customize economic distributions
config.update_economic_distribution(
    DistributionSpec(
        DistributionType.LOGNORMAL,
        {'mean': 6.5, 'sigma': 0.8},
        bounds=(200, 50000),
        description="Lower median wealth with long tail"
    )
)

# Generate population with custom config
generator = PopulationGenerator(config, seed=789)
agents = generator.generate_population(200)
```

### Available Distribution Types

1. **NORMAL**: `{'mean': 0.5, 'std': 0.2}`
2. **UNIFORM**: `{'low': 0.0, 'high': 1.0}`
3. **BETA**: `{'alpha': 2.0, 'beta': 3.0}`
4. **LOGNORMAL**: `{'mean': 7.0, 'sigma': 0.5}`
5. **BIMODAL**: `{'mean1': 0.3, 'std1': 0.1, 'mean2': 0.7, 'std2': 0.1, 'weight1': 0.6}`
6. **CATEGORICAL**: `{'categories': ['A', 'B', 'C'], 'probabilities': [0.5, 0.3, 0.2]}`
7. **FIXED**: `{'value': 0.5}`

### Stratified Population Generation

```python
# Create different population strata
working_class_config = DistributionConfig.create_realistic_default()
vulnerable_config = DistributionConfig.create_vulnerable_population()
wealthy_config = DistributionConfig.create_realistic_default()

# Adjust wealthy group
wealthy_config.update_economic_distribution(
    DistributionSpec(DistributionType.LOGNORMAL, {'mean': 8.5, 'sigma': 0.3}, bounds=(20000, 200000))
)

# Define strata proportions
strata_proportions = {
    'working_class': 0.70,
    'vulnerable': 0.20,
    'wealthy': 0.10
}

strata_configs = {
    'working_class': working_class_config,
    'vulnerable': vulnerable_config,
    'wealthy': wealthy_config
}

# Generate stratified population
generator = PopulationGenerator(working_class_config, seed=555)
mixed_population = generator.generate_stratified_population(
    300, strata_proportions, strata_configs
)
```

## Population Analysis and Review

### Compare Populations

```python
# Compare two different populations
comparison = analyzer.compare_populations(
    population1, population2, 
    ("Original", "Modified")
)

# Check key differences
impulsivity_diff = comparison['personality_differences']['baseline_impulsivity']['mean_difference']
wealth_diff = comparison['economic_differences']['wealth']['mean_difference']

print(f"Impulsivity difference: {impulsivity_diff:+.3f}")
print(f"Wealth difference: ${wealth_diff:+,.0f}")
```

### Get Agent Profiles

```python
# Get detailed profiles for sample agents
profiles = analyzer.get_agent_profiles_summary(agents, 10)

for profile in profiles:
    print(f"{profile['name']}:")
    print(f"  Wealth: {profile['economic_situation']['wealth']}")
    print(f"  Impulsivity: {profile['personality_summary']['impulsivity']}")
    print(f"  Addiction Risk: {profile['personality_summary']['addiction_vulnerability']}")
```

### Export Data for Analysis

```python
# Create DataFrame for advanced analysis
df = analyzer.create_dataframe(agents)

# Examine correlations
print(f"Wealth vs Stress correlation: {df['wealth'].corr(df['stress']):.3f}")
print(f"Impulsivity vs Addiction vulnerability: {df['baseline_impulsivity'].corr(df['addiction_vulnerability']):.3f}")

# Export analysis report
analyzer.export_analysis_report(agents, "population_report.txt")
```

## Configuration Management

### Save and Load Configurations

```python
# Save configuration for reuse
config.save_to_file("my_population_config.json")

# Load configuration later
loaded_config = DistributionConfig.load_from_file("my_population_config.json")

# Use loaded configuration
new_generator = PopulationGenerator(loaded_config, seed=999)
new_agents = new_generator.generate_population(100)
```

### Pre-built Configurations

```python
# Realistic balanced population
realistic_config = DistributionConfig.create_realistic_default()

# Maximum diversity population
diverse_config = DistributionConfig.create_diverse_population()

# Vulnerable population (high addiction risk, financial stress)
vulnerable_config = DistributionConfig.create_vulnerable_population()
```

## Complete Workflow Example

```python
from src.population import *

# 1. Define your simulation requirements
print("Creating population for urban addiction simulation...")

# 2. Create custom configuration
config = DistributionConfig.create_realistic_default()

# Adjust for urban setting with higher stress
config.initial_stress = DistributionSpec(
    DistributionType.BETA, 
    {'alpha': 3.0, 'beta': 2.0},
    bounds=(0.1, 0.8),
    description="Higher urban stress levels"
)

# 3. Generate population
generator = PopulationGenerator(config, seed=42)
population = generator.generate_population(500)

# 4. Analyze and validate
analyzer = PopulationAnalyzer()
stats = analyzer.analyze_population(population)
overview = analyzer.get_distribution_overview(population)

print(f"Generated {stats.size} agents")
print(f"Financial stress rate: {overview['summary']['financial_stress_rate']:.1%}")
print(f"High-risk profiles: {overview['summary']['high_risk_rate']:.1%}")

# 5. Check for issues
if stats.distribution_warnings:
    print("⚠️ Issues found:")
    for warning in stats.distribution_warnings:
        print(f"  - {warning}")
else:
    print("✅ Population looks good!")

# 6. Save for simulation
# Your population is now ready to use in your simulation!
```

## Tips for Good Population Generation

### 1. Start with Realistic Defaults
```python
config = DistributionConfig.create_realistic_default()
# Modify only what you need
```

### 2. Always Review Generated Populations
```python
stats = analyzer.analyze_population(agents)
if stats.distribution_warnings:
    # Address warnings before proceeding
    pass
```

### 3. Use Appropriate Distribution Types
- **Personality traits**: Beta or Normal distributions
- **Wealth**: Lognormal for realistic wealth inequality
- **Binary traits**: Beta with appropriate skew
- **Categories**: Categorical with realistic proportions

### 4. Set Reasonable Bounds
```python
DistributionSpec(
    DistributionType.NORMAL,
    {'mean': 0.5, 'std': 0.2},
    bounds=(0.0, 1.0),  # Prevent impossible values
    description="Bounded normal distribution"
)
```

### 5. Test with Small Populations First
```python
# Test with 50 agents first
test_agents = generator.generate_population(50)
test_stats = analyzer.analyze_population(test_agents)

# If good, scale up
final_agents = generator.generate_population(1000)
```

### 6. Use Seeds for Reproducibility
```python
# Always use seeds for reproducible results
generator = PopulationGenerator(config, seed=42)
```

### 7. Save Your Configurations
```python
# Save working configurations
config.save_to_file("working_population_config.json")
```

## Validation Checklist

Before using your population in simulation:

- [ ] No agents can't afford monthly expenses (unless intended)
- [ ] Personality trait distributions look reasonable
- [ ] Wealth distribution reflects intended inequality
- [ ] High-risk profile rate is appropriate for your study
- [ ] No extreme outliers unless intended
- [ ] Configuration saved for reproducibility

## Common Use Cases

### Academic Research
- Use realistic defaults with documentation of all parameters
- Save all configurations and seeds
- Generate control populations for comparison

### Policy Testing
- Create vulnerable populations to test interventions
- Use stratified populations to represent real demographics
- Focus on financial stress and addiction vulnerability

### System Testing
- Use diverse populations to stress-test your simulation
- Generate edge cases with extreme configurations
- Test with various population sizes

The population generation system gives you complete control over agent characteristics while ensuring statistical validity and reproducibility. Start simple, analyze your results, and iterate to create the perfect population for your simulation needs! 