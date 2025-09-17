"""Tests for the population generation system."""

from simulacra.population import (
    DistributionConfig,
    DistributionType,
    DistributionSpec,
    PopulationGenerator,
    PopulationAnalyzer,
    QuickPopulationFactory,
)


def test_basic_generation():
    """Verify that population generation produces the expected number of agents."""
    config = DistributionConfig.create_realistic_default()
    generator = PopulationGenerator(config, seed=42)

    agents = generator.generate_population(10)
    assert len(agents) == 10

    agent = agents[0]
    assert agent.internal_state.wealth > 0
    assert 0.0 <= agent.personality.baseline_impulsivity <= 1.0
    assert 0.0 <= agent.internal_state.stress <= 1.0


def test_population_analysis():
    """Ensure population statistics are computed correctly."""
    agents = QuickPopulationFactory.create_balanced_population(20, seed=123)
    analyzer = PopulationAnalyzer()
    stats = analyzer.analyze_population(agents)

    assert stats.size == len(agents)
    assert stats.wealth_stats["mean"] > 0
    assert "baseline_impulsivity" in stats.personality_stats
    assert stats.distribution_warnings == []


def test_custom_distribution():
    """Check that custom distribution parameters are honored."""
    config = DistributionConfig()
    config.update_personality_trait(
        "baseline_impulsivity",
        DistributionSpec(
            DistributionType.UNIFORM,
            {"low": 0.3, "high": 0.7},
            bounds=(0.0, 1.0),
            description="Moderate impulsivity range",
        ),
    )
    generator = PopulationGenerator(config, seed=456)
    agents = generator.generate_population(15)

    impulsivities = [a.personality.baseline_impulsivity for a in agents]
    assert min(impulsivities) >= 0.3
    assert max(impulsivities) <= 0.7


def test_population_comparison():
    """Validate comparison metrics between two populations."""
    balanced = QuickPopulationFactory.create_balanced_population(15, seed=789)
    vulnerable = QuickPopulationFactory.create_vulnerable_population(15, seed=789)
    analyzer = PopulationAnalyzer()
    comparison = analyzer.compare_populations(
        balanced, vulnerable, ("Balanced", "Vulnerable")
    )

    assert "personality_differences" in comparison
    diff = comparison["personality_differences"]
    assert "baseline_impulsivity" in diff
    assert "addiction_vulnerability" in diff
