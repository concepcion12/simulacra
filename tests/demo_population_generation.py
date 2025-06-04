"""
Demonstration of the Population Generation System for Simulacra.

This script shows how to:
1. Generate diverse agent populations with configurable distributions
2. Review and analyze generated populations
3. Adjust distribution parameters
4. Compare different population configurations
5. Save/load population configurations

Usage:
    python demo_population_generation.py
"""

import numpy as np
import json
from typing import List
from pathlib import Path

from src.population import (
    DistributionConfig, DistributionType, DistributionSpec,
    PopulationGenerator, PopulationAnalyzer, QuickPopulationFactory
)
from src.agents.agent import Agent


def demonstrate_basic_population_generation():
    """Demonstrate basic population generation with default settings."""
    print("=" * 60)
    print("BASIC POPULATION GENERATION DEMONSTRATION")
    print("=" * 60)
    
    # Create a realistic default configuration
    config = DistributionConfig.create_realistic_default()
    generator = PopulationGenerator(config, seed=42)
    
    # Generate a small test population
    print("\n1. Generating test population (50 agents)...")
    agents = generator.generate_population(50)
    
    print(f"✓ Generated {len(agents)} agents")
    print(f"  Sample agent: {agents[0].name} (Wealth: ${agents[0].internal_state.wealth:.0f})")
    
    # Analyze the population
    analyzer = PopulationAnalyzer()
    stats = analyzer.analyze_population(agents)
    
    print(f"\n2. Population Analysis:")
    print(f"  Average wealth: ${stats.wealth_stats['mean']:,.0f}")
    print(f"  Wealth range: ${stats.wealth_stats['min']:,.0f} - ${stats.wealth_stats['max']:,.0f}")
    print(f"  Average impulsivity: {stats.personality_stats['baseline_impulsivity']['mean']:.3f}")
    print(f"  Average addiction vulnerability: {stats.personality_stats['addiction_vulnerability']['mean']:.3f}")
    
    if stats.distribution_warnings:
        print(f"\n  Warnings:")
        for warning in stats.distribution_warnings:
            print(f"    ⚠️  {warning}")
    else:
        print(f"  ✓ No distribution warnings")
    
    return agents, stats


def demonstrate_custom_distributions():
    """Demonstrate creating custom distribution configurations."""
    print("\n" + "=" * 60)
    print("CUSTOM DISTRIBUTION CONFIGURATION")
    print("=" * 60)
    
    # Create a custom configuration
    config = DistributionConfig()
    
    # Customize personality traits for a more extreme population
    config.update_personality_trait(
        'baseline_impulsivity',
        DistributionSpec(
            DistributionType.BIMODAL,
            {'mean1': 0.2, 'std1': 0.1, 'mean2': 0.8, 'std2': 0.1, 'weight1': 0.7},
            bounds=(0.0, 1.0),
            description="Bimodal impulsivity: mostly cautious with some very impulsive agents"
        )
    )
    
    # Create a wealth inequality scenario
    config.update_economic_distribution(
        DistributionSpec(
            DistributionType.BIMODAL,
            {'mean1': 6.0, 'std1': 0.3, 'mean2': 9.0, 'std2': 0.3, 'weight1': 0.8},
            bounds=(100, 200000),
            description="Wealth inequality: poor majority with wealthy minority"
        )
    )
    
    print("1. Custom Configuration Created:")
    print("   - Bimodal impulsivity distribution")
    print("   - Wealth inequality simulation")
    
    # Generate population with custom config
    generator = PopulationGenerator(config, seed=123)
    agents = generator.generate_population(100)
    
    # Analyze the custom population
    analyzer = PopulationAnalyzer()
    stats = analyzer.analyze_population(agents)
    overview = analyzer.get_distribution_overview(agents)
    
    print(f"\n2. Custom Population Analysis:")
    print(f"  Population size: {stats.size}")
    print(f"  Wealth inequality (Gini): {overview['summary']['wealth_inequality_gini']:.3f}")
    print(f"  Financial stress rate: {overview['summary']['financial_stress_rate']:.1%}")
    print(f"  High-risk profile rate: {overview['summary']['high_risk_rate']:.1%}")
    
    # Show extreme agents
    print(f"\n3. Notable Agents:")
    print(f"  Wealthiest: {overview['extremes']['wealthiest_agent']}")
    print(f"  Most stressed: {overview['extremes']['most_stressed_agent']}")
    print(f"  Most impulsive: {overview['extremes']['most_impulsive_agent']}")
    
    return agents, config


def demonstrate_population_comparison():
    """Demonstrate comparing different population types."""
    print("\n" + "=" * 60)
    print("POPULATION COMPARISON")
    print("=" * 60)
    
    # Generate different population types
    print("1. Generating different population types...")
    
    balanced_pop = QuickPopulationFactory.create_balanced_population(80, seed=42)
    vulnerable_pop = QuickPopulationFactory.create_vulnerable_population(80, seed=42)
    diverse_pop = QuickPopulationFactory.create_diverse_population(80, seed=42)
    
    print(f"   ✓ Balanced population: {len(balanced_pop)} agents")
    print(f"   ✓ Vulnerable population: {len(vulnerable_pop)} agents")  
    print(f"   ✓ Diverse population: {len(diverse_pop)} agents")
    
    # Compare populations
    analyzer = PopulationAnalyzer()
    
    print("\n2. Comparing Balanced vs Vulnerable populations:")
    comparison = analyzer.compare_populations(
        balanced_pop, vulnerable_pop, 
        ("Balanced", "Vulnerable")
    )
    
    # Show key differences
    impulsivity_diff = comparison['personality_differences']['baseline_impulsivity']['mean_difference']
    addiction_vuln_diff = comparison['personality_differences']['addiction_vulnerability']['mean_difference']
    wealth_diff = comparison['economic_differences']['wealth']['mean_difference']
    
    print(f"   Impulsivity difference: {impulsivity_diff:+.3f}")
    print(f"   Addiction vulnerability difference: {addiction_vuln_diff:+.3f}")
    print(f"   Wealth difference: ${wealth_diff:+,.0f}")
    
    print("\n3. Comparing Balanced vs Diverse populations:")
    comparison2 = analyzer.compare_populations(
        balanced_pop, diverse_pop,
        ("Balanced", "Diverse")
    )
    
    # Show diversity metrics
    balanced_stats = analyzer.analyze_population(balanced_pop)
    diverse_stats = analyzer.analyze_population(diverse_pop)
    
    print(f"   Impulsivity std deviation:")
    print(f"     Balanced: {balanced_stats.personality_stats['baseline_impulsivity']['std']:.3f}")
    print(f"     Diverse:  {diverse_stats.personality_stats['baseline_impulsivity']['std']:.3f}")
    
    return balanced_pop, vulnerable_pop, diverse_pop


def demonstrate_stratified_population():
    """Demonstrate creating stratified populations with mixed characteristics."""
    print("\n" + "=" * 60)
    print("STRATIFIED POPULATION GENERATION")
    print("=" * 60)
    
    # Create a mixed population
    print("1. Creating mixed population with different strata...")
    
    mixed_pop = QuickPopulationFactory.create_mixed_population(
        size=120,
        vulnerable_proportion=0.25,  # 25% vulnerable agents
        seed=789
    )
    
    print(f"   ✓ Generated {len(mixed_pop)} agents")
    print(f"   - Expected vulnerable agents: {int(120 * 0.25)}")
    print(f"   - Expected balanced agents: {int(120 * 0.75)}")
    
    # Analyze the mixed population
    analyzer = PopulationAnalyzer()
    stats = analyzer.analyze_population(mixed_pop)
    overview = analyzer.get_distribution_overview(mixed_pop)
    
    print(f"\n2. Mixed Population Analysis:")
    print(f"   High-risk profile rate: {overview['summary']['high_risk_rate']:.1%}")
    print(f"   Average addiction vulnerability: {overview['summary']['addiction_vulnerability_mean']:.3f}")
    print(f"   Financial stress rate: {overview['summary']['financial_stress_rate']:.1%}")
    
    # Show agent profiles sample
    profiles = analyzer.get_agent_profiles_summary(mixed_pop, 5)
    print(f"\n3. Sample Agent Profiles:")
    for i, profile in enumerate(profiles):
        print(f"   Agent {i+1}: {profile['name']}")
        print(f"     Wealth: {profile['economic_situation']['wealth']} " + 
              f"(Expenses: {profile['economic_situation']['monthly_expenses']})")
        print(f"     Impulsivity: {profile['personality_summary']['impulsivity']}, " +
              f"Addiction Risk: {profile['personality_summary']['addiction_vulnerability']}")
    
    return mixed_pop


def demonstrate_configuration_management():
    """Demonstrate saving and loading configurations."""
    print("\n" + "=" * 60)
    print("CONFIGURATION MANAGEMENT")
    print("=" * 60)
    
    # Create a custom configuration
    config = DistributionConfig.create_vulnerable_population()
    
    # Modify it further
    config.update_personality_trait(
        'gambling_bias_strength',
        DistributionSpec(
            DistributionType.BETA,
            {'alpha': 3.0, 'beta': 1.5},  # Higher gambling bias
            bounds=(0.2, 1.0),
            description="Enhanced gambling bias for vulnerable population"
        )
    )
    
    print("1. Created and modified configuration")
    
    # Save configuration
    config_path = "population_config_vulnerable_enhanced.json"
    config.save_to_file(config_path)
    print(f"   ✓ Saved configuration to {config_path}")
    
    # Load configuration
    loaded_config = DistributionConfig.load_from_file(config_path)
    print(f"   ✓ Loaded configuration from {config_path}")
    
    # Verify they're the same by generating identical populations
    gen1 = PopulationGenerator(config, seed=999)
    gen2 = PopulationGenerator(loaded_config, seed=999)
    
    pop1 = gen1.generate_population(20)
    pop2 = gen2.generate_population(20)
    
    # Check if first agent's wealth is identical (should be with same seed)
    wealth_match = abs(pop1[0].internal_state.wealth - pop2[0].internal_state.wealth) < 0.01
    print(f"   ✓ Configuration consistency verified: {wealth_match}")
    
    # Show configuration summary
    print(f"\n2. Configuration Summary:")
    summary = config.get_summary()
    for category, items in summary.items():
        if isinstance(items, dict):
            print(f"   {category}:")
            for key, value in list(items.items())[:3]:  # Show first 3
                print(f"     {key}: {value}")
        else:
            print(f"   {category}: {items}")
    
    # Cleanup
    Path(config_path).unlink(missing_ok=True)
    
    return config


def demonstrate_interactive_adjustment():
    """Demonstrate interactive parameter adjustment workflow."""
    print("\n" + "=" * 60)
    print("INTERACTIVE PARAMETER ADJUSTMENT WORKFLOW")
    print("=" * 60)
    
    # Start with default configuration
    config = DistributionConfig.create_realistic_default()
    generator = PopulationGenerator(config, seed=42)
    analyzer = PopulationAnalyzer()
    
    print("1. Initial Population (Default Configuration):")
    pop_v1 = generator.generate_population(100)
    stats_v1 = analyzer.analyze_population(pop_v1)
    
    print(f"   Financial stress rate: {analyzer.get_distribution_overview(pop_v1)['summary']['financial_stress_rate']:.1%}")
    print(f"   Average impulsivity: {stats_v1.personality_stats['baseline_impulsivity']['mean']:.3f}")
    
    # Simulate user wanting to increase financial pressure
    print("\n2. Adjusting parameters to increase financial pressure...")
    
    # Lower wealth and higher expenses
    config.update_economic_distribution(
        DistributionSpec(
            DistributionType.LOGNORMAL,
            {'mean': 6.5, 'sigma': 0.7},  # Lower wealth
            bounds=(50, 20000),
            description="Reduced initial wealth"
        ),
        DistributionSpec(
            DistributionType.NORMAL,
            {'mean': 900, 'std': 150},  # Higher expenses
            bounds=(600, 1500),
            description="Increased living expenses"
        )
    )
    
    # Generate new population with adjusted parameters
    generator.update_config(config)
    pop_v2 = generator.generate_population(100)
    stats_v2 = analyzer.analyze_population(pop_v2)
    
    print("3. Adjusted Population Results:")
    overview_v2 = analyzer.get_distribution_overview(pop_v2)
    print(f"   Financial stress rate: {overview_v2['summary']['financial_stress_rate']:.1%}")
    print(f"   Average wealth: ${overview_v2['summary']['mean_wealth']:,.0f}")
    
    # Compare the two versions
    comparison = analyzer.compare_populations(pop_v1, pop_v2, ("Original", "Adjusted"))
    wealth_change = comparison['economic_differences']['wealth']['mean_difference']
    
    print(f"\n4. Parameter Adjustment Results:")
    print(f"   Wealth change: ${wealth_change:+,.0f}")
    print(f"   Financial stress increased: {overview_v2['summary']['financial_stress_rate'] - analyzer.get_distribution_overview(pop_v1)['summary']['financial_stress_rate']:+.1%}")
    
    # Show warnings if any
    if stats_v2.distribution_warnings:
        print(f"   New warnings:")
        for warning in stats_v2.distribution_warnings:
            print(f"     ⚠️  {warning}")
    
    return pop_v1, pop_v2


def demonstrate_export_and_analysis():
    """Demonstrate exporting analysis reports."""
    print("\n" + "=" * 60)
    print("ANALYSIS EXPORT AND REPORTING")
    print("=" * 60)
    
    # Generate a diverse population for analysis
    diverse_pop = QuickPopulationFactory.create_diverse_population(150, seed=555)
    analyzer = PopulationAnalyzer()
    
    print(f"1. Generated diverse population of {len(diverse_pop)} agents for analysis")
    
    # Export detailed analysis report
    report_path = "population_analysis_report.txt"
    analyzer.export_analysis_report(diverse_pop, report_path)
    print(f"   ✓ Exported detailed analysis to {report_path}")
    
    # Create DataFrame for further analysis
    df = analyzer.create_dataframe(diverse_pop)
    print(f"   ✓ Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
    
    # Show some interesting correlations
    print(f"\n2. Interesting Population Correlations:")
    print(f"   Wealth vs Stress: {df['wealth'].corr(df['stress']):.3f}")
    print(f"   Impulsivity vs Addiction Vulnerability: {df['baseline_impulsivity'].corr(df['addiction_vulnerability']):.3f}")
    print(f"   Self-Control vs Stress: {df['self_control_resource'].corr(df['stress']):.3f}")
    
    # Show distribution of risk factors
    high_risk_count = df['high_risk_profile'].sum()
    financial_stress_count = df['financial_stress'].sum()
    
    print(f"\n3. Risk Factor Distribution:")
    print(f"   High-risk personality profiles: {high_risk_count}/{len(df)} ({high_risk_count/len(df):.1%})")
    print(f"   Financial stress cases: {financial_stress_count}/{len(df)} ({financial_stress_count/len(df):.1%})")
    
    # Cleanup
    Path(report_path).unlink(missing_ok=True)
    
    return df


def demonstrate_complete_workflow():
    """Demonstrate a complete population generation workflow."""
    print("\n" + "=" * 60)
    print("COMPLETE POPULATION GENERATION WORKFLOW")
    print("=" * 60)
    
    print("Scenario: Setting up a simulation with 200 agents representing")
    print("a mixed urban population with economic stress factors.")
    
    # Step 1: Define requirements
    print("\n1. Define Population Requirements:")
    print("   - 200 total agents")
    print("   - 70% balanced working class")
    print("   - 20% economically vulnerable")
    print("   - 10% high-income resilient")
    
    # Step 2: Create stratified configuration
    print("\n2. Creating Stratified Population Configuration...")
    
    # Define three population strata
    working_class_config = DistributionConfig.create_realistic_default()
    working_class_config.update_economic_distribution(
        DistributionSpec(DistributionType.LOGNORMAL, {'mean': 7.2, 'sigma': 0.4}, bounds=(800, 15000))
    )
    
    vulnerable_config = DistributionConfig.create_vulnerable_population()
    vulnerable_config.update_economic_distribution(
        DistributionSpec(DistributionType.LOGNORMAL, {'mean': 6.0, 'sigma': 0.6}, bounds=(200, 5000))
    )
    
    resilient_config = DistributionConfig.create_realistic_default()
    resilient_config.update_economic_distribution(
        DistributionSpec(DistributionType.LOGNORMAL, {'mean': 8.5, 'sigma': 0.3}, bounds=(15000, 100000))
    )
    # Lower addiction vulnerability for resilient group
    resilient_config.update_personality_trait(
        'addiction_vulnerability',
        DistributionSpec(DistributionType.BETA, {'alpha': 1.0, 'beta': 5.0}, bounds=(0.0, 0.4))
    )
    
    # Step 3: Generate stratified population
    print("\n3. Generating Stratified Population...")
    
    generator = PopulationGenerator(working_class_config, seed=777)
    
    strata_proportions = {
        'working_class': 0.70,
        'vulnerable': 0.20,
        'resilient': 0.10
    }
    
    strata_configs = {
        'working_class': working_class_config,
        'vulnerable': vulnerable_config,
        'resilient': resilient_config
    }
    
    final_population = generator.generate_stratified_population(
        200, strata_proportions, strata_configs
    )
    
    print(f"   ✓ Generated {len(final_population)} agents")
    
    # Step 4: Analyze and validate
    print("\n4. Analyzing Final Population...")
    
    analyzer = PopulationAnalyzer()
    final_stats = analyzer.analyze_population(final_population)
    final_overview = analyzer.get_distribution_overview(final_population)
    
    print(f"   Population size: {final_stats.size}")
    print(f"   Average wealth: ${final_overview['summary']['mean_wealth']:,.0f}")
    print(f"   Wealth inequality (Gini): {final_overview['summary']['wealth_inequality_gini']:.3f}")
    print(f"   Financial stress rate: {final_overview['summary']['financial_stress_rate']:.1%}")
    print(f"   High-risk profile rate: {final_overview['summary']['high_risk_rate']:.1%}")
    
    # Step 5: Validation checks
    print("\n5. Validation Results:")
    if final_stats.distribution_warnings:
        print("   Warnings found:")
        for warning in final_stats.distribution_warnings:
            print(f"     ⚠️  {warning}")
    else:
        print("   ✓ No distribution warnings - population looks good!")
    
    print(f"   ✓ Ready for simulation with {len(final_population)} agents")
    
    return final_population


def main():
    """Run all demonstrations."""
    print("SIMULACRA POPULATION GENERATION SYSTEM DEMONSTRATION")
    print("This demo shows the complete population generation workflow.")
    
    # Set random seed for reproducible results
    np.random.seed(42)
    
    try:
        # Run demonstrations
        basic_agents, basic_stats = demonstrate_basic_population_generation()
        custom_agents, custom_config = demonstrate_custom_distributions()
        balanced, vulnerable, diverse = demonstrate_population_comparison()
        mixed_pop = demonstrate_stratified_population()
        saved_config = demonstrate_configuration_management()
        v1_pop, v2_pop = demonstrate_interactive_adjustment()
        analysis_df = demonstrate_export_and_analysis()
        final_population = demonstrate_complete_workflow()
        
        # Final summary
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("\nSummary of Generated Populations:")
        print(f"  - Basic population: {len(basic_agents)} agents")
        print(f"  - Custom population: {len(custom_agents)} agents")
        print(f"  - Comparison populations: {len(balanced)} + {len(vulnerable)} + {len(diverse)} agents")
        print(f"  - Mixed stratified population: {len(mixed_pop)} agents")
        print(f"  - Final simulation-ready population: {len(final_population)} agents")
        
        print(f"\nTotal agents generated: {len(basic_agents) + len(custom_agents) + len(balanced) + len(vulnerable) + len(diverse) + len(mixed_pop) + len(final_population)}")
        
        print("\nNext steps:")
        print("  1. Choose a population configuration that fits your simulation needs")
        print("  2. Adjust distributions as needed using the demonstrated methods")
        print("  3. Generate your final population for simulation")
        print("  4. Use the analyzer to validate before running simulation")
        
        print("\nPopulation generation system is ready for use! 🎉")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
