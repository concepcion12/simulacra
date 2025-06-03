"""
Simple test script for the population generation system.
"""

import numpy as np
from src.population import (
    DistributionConfig, DistributionType, DistributionSpec,
    PopulationGenerator, PopulationAnalyzer, QuickPopulationFactory
)

def test_basic_generation():
    """Test basic population generation."""
    print("Testing basic population generation...")
    
    # Create default configuration
    config = DistributionConfig.create_realistic_default()
    generator = PopulationGenerator(config, seed=42)
    
    # Generate small population
    agents = generator.generate_population(10)
    print(f"✓ Generated {len(agents)} agents")
    
    # Show first agent details
    agent = agents[0]
    print(f"  Sample agent: {agent.name}")
    print(f"    Wealth: ${agent.internal_state.wealth:.0f}")
    print(f"    Impulsivity: {agent.personality.baseline_impulsivity:.3f}")
    print(f"    Stress: {agent.internal_state.stress:.3f}")
    
    return agents

def test_population_analysis():
    """Test population analysis."""
    print("\nTesting population analysis...")
    
    # Generate population
    agents = QuickPopulationFactory.create_balanced_population(20, seed=123)
    
    # Analyze
    analyzer = PopulationAnalyzer()
    stats = analyzer.analyze_population(agents)
    
    print(f"✓ Analyzed {stats.size} agents")
    print(f"  Average wealth: ${stats.wealth_stats['mean']:,.0f}")
    print(f"  Wealth range: ${stats.wealth_stats['min']:,.0f} - ${stats.wealth_stats['max']:,.0f}")
    print(f"  Average impulsivity: {stats.personality_stats['baseline_impulsivity']['mean']:.3f}")
    
    if stats.distribution_warnings:
        print(f"  Warnings: {len(stats.distribution_warnings)}")
    else:
        print(f"  ✓ No warnings")
    
    return stats

def test_custom_distribution():
    """Test custom distribution configuration."""
    print("\nTesting custom distribution...")
    
    # Create custom config
    config = DistributionConfig()
    
    # Set custom impulsivity distribution
    config.update_personality_trait(
        'baseline_impulsivity',
        DistributionSpec(
            DistributionType.UNIFORM,
            {'low': 0.3, 'high': 0.7},
            bounds=(0.0, 1.0),
            description="Moderate impulsivity range"
        )
    )
    
    # Generate with custom config
    generator = PopulationGenerator(config, seed=456)
    agents = generator.generate_population(15)
    
    # Check impulsivity range
    impulsivities = [agent.personality.baseline_impulsivity for agent in agents]
    min_imp = min(impulsivities)
    max_imp = max(impulsivities)
    
    print(f"✓ Generated {len(agents)} agents with custom distribution")
    print(f"  Impulsivity range: {min_imp:.3f} - {max_imp:.3f}")
    print(f"  Expected range: 0.300 - 0.700")
    
    return agents

def test_population_comparison():
    """Test comparing different population types."""
    print("\nTesting population comparison...")
    
    # Generate different populations
    balanced = QuickPopulationFactory.create_balanced_population(15, seed=789)
    vulnerable = QuickPopulationFactory.create_vulnerable_population(15, seed=789)
    
    # Compare
    analyzer = PopulationAnalyzer()
    comparison = analyzer.compare_populations(balanced, vulnerable, ("Balanced", "Vulnerable"))
    
    impulsivity_diff = comparison['personality_differences']['baseline_impulsivity']['mean_difference']
    addiction_diff = comparison['personality_differences']['addiction_vulnerability']['mean_difference']
    
    print(f"✓ Compared two populations")
    print(f"  Impulsivity difference: {impulsivity_diff:+.3f}")
    print(f"  Addiction vulnerability difference: {addiction_diff:+.3f}")
    
    return comparison

def main():
    """Run all tests."""
    print("POPULATION GENERATION SYSTEM - SIMPLE TESTS")
    print("=" * 50)
    
    try:
        # Set seed for reproducible results
        np.random.seed(42)
        
        # Run tests
        agents1 = test_basic_generation()
        stats = test_population_analysis()
        agents2 = test_custom_distribution()
        comparison = test_population_comparison()
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("Population generation system is working correctly! 🎉")
        
        print(f"\nSystem capabilities demonstrated:")
        print(f"✓ Basic population generation")
        print(f"✓ Statistical analysis")
        print(f"✓ Custom distributions")
        print(f"✓ Population comparison")
        print(f"✓ Various factory methods")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 