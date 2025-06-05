# Simulacra Project Guidelines

This document provides guidelines and instructions for working with the Simulacra project codebase.

## Project Structure

- `src/`: Core source code for the simulation platform
- `tests/`: Test suite and test utilities
- `docs/`: Project documentation and guides
- `examples/`: Example scripts and demos
- `simulacra_projects/`: Project-specific configurations and data

## Code Style and Conventions

1. **Python Code Style**
   - Follow PEP 8 guidelines
   - Use type hints for all function parameters and return values
   - Maximum line length: 100 characters
   - Use descriptive variable names that reflect their purpose
   - Include docstrings for all classes and functions

2. **File Organization**
   - Keep related functionality in the same module
   - Use clear, descriptive file names
   - Place new features in appropriate subdirectories under `src/`

3. **Testing Requirements**
   - All new code must include unit tests
   - Test files should mirror the structure of the source code
   - Use pytest fixtures for common test setup
   - Maintain test coverage above 80%

## Pull Request Guidelines

When creating a pull request:

1. **Title Format**
   - Use present tense ("Add feature" not "Added feature")
   - Keep it concise but descriptive
   - Start with a verb

2. **Description Requirements**
   - Clearly describe the changes made
   - Reference any related issues
   - Include testing instructions
   - Note any breaking changes

3. **Code Review Process**
   - All PRs require at least one review
   - Address all review comments
   - Ensure all tests pass before merging

## Development Workflow

1. **Running Tests**
   ```bash
   pytest
   ```

2. **Local Development**
   - Use virtual environment
   - Install development dependencies: `pip install -e .[dev]`
   - Run linting: `flake8 src tests`

3. **Documentation**
   - Update relevant documentation when adding features
   - Include docstring examples for public APIs
   - Keep README.md and docs/ up to date

## Performance Considerations

1. **Simulation Performance**
   - Profile code before optimization
   - Use appropriate data structures
   - Consider memory usage for large simulations
   - Utilize threading where appropriate

2. **Visualization**
   - Optimize real-time rendering
   - Use efficient data structures for visualization
   - Consider memory usage for large datasets

## Security Guidelines

1. **Data Handling**
   - Never commit sensitive data
   - Use environment variables for configuration
   - Validate all user inputs
   - Sanitize data before visualization

2. **API Security**
   - Validate all API inputs
   - Use appropriate authentication
   - Implement rate limiting where necessary

## Programmatic Checks

Before submitting any changes, ensure:

1. All tests pass: `pytest`
2. Code style is correct: `flake8 src tests`
3. Type checking passes: `mypy src`
4. Documentation builds: `sphinx-build docs/ docs/_build/`

## Additional Notes

- Keep the codebase modular and maintainable
- Document complex algorithms and design decisions
- Consider backward compatibility when making changes
- Use meaningful commit messages 