import pytest
from typing import TypedDict
from worldnavigator.core.character import GameCharacter

class SampleData(TypedDict):
  health: int
  inventory: list[str]

def get_status(character: GameCharacter):
  return f"{character.name} is healthy"

class TestGameCharacter:
  def test_character_creation(self):
    """
    Test basic character creation.
    
    Arrange:
      - Define character name.
    
    Act:
      - Create GameCharacter instance.
    
    Assert:
      - Verify name and default values.
    """
    # Arrange
    name = "Hero"

    # Act
    char = GameCharacter(name=name)

    # Assert
    assert char.name == name
    assert char.current_location is None
    assert char.data == {}

  def test_character_with_data(self):
    """
    Test character creation with extra data and methods.
    
    Arrange:
      - Define data dictionary with attributes and a function.
    
    Act:
      - Create GameCharacter instance with data.
    
    Assert:
      - Verify attributes are in data.
      - Verify function is bound as a method.
    """
    # Arrange
    data = {
      "health": 100,
      "get_status": get_status
    }

    # Act
    char = GameCharacter(name="Warrior", data=data)
    
    # Assert
    assert char.data["health"] == 100
    assert hasattr(char, "get_status")
    assert char.get_status() == "Warrior is healthy"

  def test_current_location_property(self):
    """
    Test the current_location getter and setter.

    Arrange:
      - Create a GameCharacter instance.

    Act:
      - Set the current_location property.

    Assert:
      - Verify the property returns the assigned value.
    """
    # Arrange
    char = GameCharacter(name="Explorer")

    # Act
    char.current_location = "Cave"

    # Assert
    assert char.current_location == "Cave"

  def test_character_equality(self):
    """
    Test character equality logic.

    Arrange:
      - Create multiple characters with same and different names.

    Act:
      - Compare characters using equality operator.

    Assert:
      - Verify characters with same name are equal.
      - Verify character is equal to its name string.
      - Verify different characters are not equal.
    """
    # Arrange
    char1 = GameCharacter(name="Twin")
    char2 = GameCharacter(name="Twin")
    char3 = GameCharacter(name="Other")
    
    # Act & Assert
    assert char1 == char2
    assert char1 == "Twin"
    assert char1 != char3
    assert char1 != 123

  def test_character_string_representation(self):
    """
    Test __str__ and __repr__ methods.

    Arrange:
      - Create a character with specific data.

    Act:
      - Get string and repr representations.

    Assert:
      - Verify they match the expected format.
    """
    # Arrange
    char = GameCharacter(name="Bob", data={"age": 20})
    expected = 'GameCharacter(name="Bob", data="{\'age\': 20}")'

    # Act & Assert
    assert str(char) == expected
    assert repr(char) == expected

  def test_character_renpy_mocking(self):
    """
    Test RenPy compatibility logic in Python environment.

    Arrange:
      - Create a character in standard environment.

    Act:
      - Check RenPy-specific attribute 'c'.

    Assert:
      - Verify 'c' is None and calling the character returns None.
    """
    # Arrange & Act
    char = GameCharacter(name="RenPyChar")

    # Assert
    assert char.c is None
    assert char() is None

  def test_pickle_compatibility(self):
    """
    Test __getstate__ and __setstate__ for serialization.

    Arrange:
      - Create and configure a character instance.

    Act:
      - Get its state and apply it to a new instance.

    Assert:
      - Verify the state is correctly restored in the new instance.
    """
    # Arrange
    char = GameCharacter(name="Serializable", data={"score": 50})
    char.current_location = "Start"
    
    # Act
    state = char.__getstate__()
    new_char = GameCharacter(name="Temp")
    new_char.__setstate__(state)
    
    # Assert
    assert new_char.name == "Serializable"
    assert new_char.current_location == "Start"
    assert new_char.data["score"] == 50
