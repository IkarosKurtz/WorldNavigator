# WorldNavigator - Agent Guidelines

This document provides guidelines for AI coding agents working on the WorldNavigator project.

## Project Overview

WorldNavigator is a Python library for creating navigable world simulations with weather systems. It's designed for game development, particularly for Ren'Py visual novels. The project simulates locations, character movement, and dynamic weather conditions.

## Build & Test Commands

### Running Tests

The project uses Python's built-in `unittest` framework:

```bash
# Run all tests
python -m unittest discover -s tests -p "*_test.py"

# Run a single test file
python -m unittest tests.world_test

# Run a specific test class
python -m unittest tests.world_test.WorldTest

# Run a specific test method
python -m unittest tests.world_test.WorldTest.test_world_creation

# Verbose output
python -m unittest discover -s tests -p "*_test.py" -v
```

### Building Documentation

```bash
# Install dev dependencies first
pip install -e ".[dev]"

# Build Sphinx documentation
cd docs_page
sphinx-build -b html source _build/html
```

### Package Build

```bash
# Install build tools
pip install build

# Build distribution
python -m build
```

## Code Style Guidelines

### General Principles

- **Python Version**: Requires Python 3.11+
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use reStructuredText (reST) format for all public methods
- **Testing**: Write unit tests using AAA pattern (Arrange, Act, Assert)

### Import Style

Follow this import order with blank lines between groups:

1. Standard library imports
2. Third-party imports (e.g., `rich`)
3. Local application imports

**Use `TYPE_CHECKING` for circular dependencies:**

```python
from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:
    from worldnavigator.core.character import GameCharacter
```

**Example:**
```python
from typing import TYPE_CHECKING, List, Dict, Union
import random

from rich.console import Console

from worldnavigator.errors import LocationNotFoundError
from worldnavigator.observer.observer import Observer

if TYPE_CHECKING:
    from worldnavigator.locations.base_location import Location
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `WorldWeather`, `GameCharacter`)
- **Functions/Methods**: snake_case (e.g., `add_character`, `get_location`)
- **Private Methods**: Prefix with single underscore (e.g., `_character_added`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_TEMPERATURE`)
- **Type Aliases**: PascalCase (e.g., `Weather`, `LocationType`)

### Type Annotations

Always use type hints. Import from `typing` module:

```python
def add_location(self, location: 'Location') -> None:
    """Add a new location to the world"""
    pass

def get_location(self, location_name: str) -> 'Location':
    """Get a location by name"""
    pass

def where_is(self, character: 'GameCharacter') -> str:
    """Find where a character is located"""
    pass
```

Use generic types for collections:
```python
from typing import List, Dict, Tuple, Optional, Union

_locations: Dict[str, 'Location'] = {}
_total_characters: List['GameCharacter'] = []
```

### Docstring Format

Use reStructuredText format with proper parameter and return documentation:

```python
def move_character(self, character: 'GameCharacter', location: Union[str, 'Location']) -> bool:
    """
    Use this method to move a character to a different location.

    :param GameCharacter character: The character to move.
    :param Union[str, Location] location: The location to move the character to.

    :return: True if the character was moved, False otherwise.
    :raises LocationNotFoundError: If the location is not found in the world.
    :raises CharacterAlreadyPresentError: If the character is already in the location.
    """
    pass
```

### Error Handling

- Create custom exception classes for domain-specific errors
- All custom exceptions should inherit from `Exception`
- Provide clear error messages with context

**Example:**
```python
class LocationNotFoundError(Exception):
    """Exception raised when a location is not found."""
    
    def __init__(self, location_name: str, message: str = None):
        if message is None:
            message = f'Location "{location_name}" not found'
        super().__init__(message)
```

**Raise exceptions with context:**
```python
if location_name not in self._locations:
    raise LocationNotFoundError(location_name)
```

### Class Structure

Organize class code in this order:

1. Class docstring
2. `__init__` method
3. Properties (with `@property` decorator)
4. Private methods (prefixed with `_`)
5. Public methods
6. Dunder methods (e.g., `__str__`, `__repr__`, `__getstate__`)

**Use comment sections to separate:**
```python
#################################################
################### Properties ##################
#################################################

#################################################
################ Private Methods ################
#################################################

#################################################
################ Public Methods #################
#################################################

#################################################
################ Dunder Methods #################
#################################################
```

### Testing Standards

Write tests using the AAA pattern with clear docstrings:

```python
def test_add_location(self):
    """
    Test adding locations to the world.

    Arrange:
      - Create a new world
      - Create sample locations

    Act:
      - Add locations to the world

    Assert:
      - Verify locations are added correctly
      - Verify duplicate location raises error
    """
    # Arrange
    world = World(name='Nexis')
    location = Location(name='School', backgrounds={'day': 'bg'}, is_indoor=False)
    
    # Act
    world.add_location(location)
    
    # Assert
    self.assertEqual(len(world.locations), 1)
```

## Project Structure

```
src/worldnavigator/
├── core/           # Core world, character, and time management
├── locations/      # Location classes and background handling
├── weather/        # Weather simulation system
├── observer/       # Event system for location/character events
├── errors/         # Custom exception classes
├── types/          # Type definitions and TypedDicts
├── utils/          # Utility functions
└── decorators/     # Function decorators
```

## Important Rules

1. **Commit Messages**: Must be in English (enforced by .cursorrules)
2. **No External Dependencies**: Core functionality uses only standard library (except `rich` for CLI)
3. **Pickle Compatibility**: Implement `__getstate__` and `__setstate__` for Ren'Py save/load support
4. **Event-Driven**: Use the Observer pattern for character/location events

## Common Patterns

### Observer Pattern for Events
```python
location.on('character_added', self._character_added)
location.on('character_removed', self._character_removed)
```

### Flexible Input Types
Accept both string names and object instances:
```python
def move_character(self, character: 'GameCharacter', location: Union[str, 'Location']):
    if isinstance(location, str):
        location = self.get_location(location)
```

### Property-Based Access
Use properties for read-only access to internal state:
```python
@property
def name(self) -> str:
    """Name of the world"""
    return self._name
```

---

When in doubt, refer to existing code in `src/worldnavigator/core/` for examples.
