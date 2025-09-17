# Population Generation Guide

This guide explains the different ways to create agent populations for simulations.

## Quick Generation
Use `QuickPopulationFactory` for simple scenarios:
```python
from simulacra.population.population_generator import QuickPopulationFactory
agents = QuickPopulationFactory.create_balanced_population(50)
```

## Custom Generation
For fine grained control use `PopulationGenerator` with a `DistributionConfig`:
```python
from simulacra.population.population_generator import PopulationGenerator
from simulacra.population.distribution_config import DistributionConfig
config = DistributionConfig.create_realistic_default()
generator = PopulationGenerator(config)
agents = generator.generate_population(100)
```

