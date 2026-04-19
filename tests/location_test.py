from typing import Annotated, Literal

import pytest
from pytest_mock import MockerFixture

from worldnavigator.core.character import GameCharacter
from worldnavigator.core.world_object import WorldObject
from worldnavigator.decorators.function_decorators import evaluate_events
from worldnavigator.errors import (
  CharacterAlreadyPresentError,
  CharacterNotFoundError,
  DuplicatedLocationError,
  LocationNotFoundError,
)
from worldnavigator.locations.base_location import Location, LocationBackground
from worldnavigator.types.types import Params

# --- Mock Classes for Testing ---


@evaluate_events
class MockEvents:
  use: Annotated[str, Params(), "Use the object."]
  another_event: Annotated[str, Params(is_other=bool), "Another event for testing."]


MockEventsName = Literal["use", "another_event"]


class MockObject(WorldObject[MockEvents, MockEventsName]):
  def __init__(self):
    super().__init__("Mock Object")
    self.register_interaction("use", self._use)
    self.register_interaction("another_event", self._another_event)

  def _use(self):
    return "You used the mock object."

  def _another_event(self, is_other: bool):
    return f"Another event triggered with is_other={is_other}"


# --- Tests for WorldObject ---


class TestLocation:
  def test_location_creation_standard_python(self):
    """
    Test that a location can be created in a standard Python environment.

    Arrange:
      - Define location name and description
      - Prepare background data (optional in Python)

    Act:
      - Create Location instances with and without backgrounds

    Assert:
      - Verify name and description are set correctly
      - Verify backgrounds default to 'default_day_background' when missing in Python mode
    """
    # Arrange
    name = "Classroom"
    description = "A place where students learn."

    # Act
    location = Location(
      name=name,
      description=description,
      is_indoor=False,
    )
    location_with_bg = Location(name="Office", description="A workspace.", backgrounds={"day": "my_bg.png"})

    # Assert
    assert location.name == name
    assert location.description == description
    assert location.is_indoor is False
    assert location.backgrounds.day == "default_day_background"
    assert location_with_bg.backgrounds.day == "default_day_background"

  def test_location_creation_renpy(self, mocker: MockerFixture):
    """
    Test that a location requires backgrounds when running in RenPy.

    Arrange:
      - Mock sys.modules using pytest-mock to simulate RenPy environment
      - Prepare valid and invalid background data

    Act:
      - Create Location with valid backgrounds
      - Attempt to create Location without backgrounds or missing 'day' key

    Assert:
      - Verify backgrounds are correctly assigned when valid
      - Verify ValueError is raised when backgrounds are missing or invalid
    """
    # Arrange
    mocker.patch.dict("sys.modules", {"renpy": True})
    valid_bg = {"day": "gym_day.png", "night": "gym_night.png"}

    # Act
    location = Location(
      name="Gym",
      description="A place to train.",
      backgrounds=valid_bg,
    )

    # Assert
    assert location.backgrounds.day == "gym_day.png"
    assert location.is_indoor
    assert location.backgrounds.night == "gym_night.png"

    # Act & Assert (Error cases)
    with pytest.raises(ValueError, match='must have a "day" background when running in RenPy'):
      Location(name="Invalid", description="No backgrounds", backgrounds=None)

    with pytest.raises(ValueError, match='must have a "day" background when running in RenPy'):
      Location(name="MissingDayRenPy", description="Testing RenPy validation.", backgrounds={"night": "only_night.png"})

  def test_location_connections(self):
    """
    Test connecting and disconnecting locations.

    Arrange:
      - Create multiple location instances

    Act:
      - Connect locations with each other
      - Attempt to connect already connected locations
      - Disconnect locations

    Assert:
      - Verify connections are established correctly in the dictionary
      - Verify DuplicatedLocationError is raised for already connected locations
      - Verify LocationNotFoundError is raised for disconnecting non-existent connections
    """
    # Arrange
    classroom = Location(name="Classroom", description="A place to learn.")
    hallway = Location(name="Hallway", description="A long hallway.")

    # Act (Connect)
    classroom.connect_with(hallway)

    # Assert (Connect)
    assert "Hallway" in classroom.connections
    assert classroom.get_location("Hallway") == hallway
    assert hallway in classroom.get_locations()

    # Act & Assert (Duplicate)
    with pytest.raises(DuplicatedLocationError, match="already connected"):
      classroom.connect_with(hallway)

    # Act (Disconnect)
    classroom.disconnect_from("Hallway")

    # Assert (Get after disconnect)
    with pytest.raises(LocationNotFoundError):
      classroom.get_location("Hallway")

    # Assert (Disconnect)
    assert "Hallway" not in classroom.connections
    with pytest.raises(LocationNotFoundError):
      classroom.disconnect_from("Hallway")

  def test_character_management(self):
    """
    Test adding, removing, and querying characters in a location.

    Arrange:
      - Create a location and character instances
      - Set up event tracking using a spy/mock

    Act:
      - Add characters to the location
      - Remove a character from the location

    Assert:
      - Verify characters are present in the location's list
      - Verify who_is_here returns a correct comma-separated string
      - Verify character's current_location property is updated
      - Verify proper errors are raised for invalid operations (duplicate add, non-existent remove)
    """
    # Arrange
    cafeteria = Location(name="Cafeteria", description="A place to eat.")
    student = GameCharacter("Student")
    teacher = GameCharacter("Teacher")

    # Act (Add)
    cafeteria.add_character(student)
    cafeteria.add_character(teacher)

    # Assert (Add)
    assert student in cafeteria.characters
    assert teacher in cafeteria.characters
    assert student.current_location == "Cafeteria"
    assert "Student, Teacher" == cafeteria.who_is_here()

    # Act & Assert (Duplicate)
    with pytest.raises(CharacterAlreadyPresentError):
      cafeteria.add_character(student)

    # Act (Remove)
    cafeteria.remove_character(student)

    # Assert (Remove)
    assert student not in cafeteria.characters
    assert teacher in cafeteria.characters
    assert "Teacher" == cafeteria.who_is_here()

    # Act & Assert (Non-existent remove)
    with pytest.raises(CharacterNotFoundError):
      cafeteria.remove_character(student)

  def test_object_management(self):
    """
    Test adding and retrieving objects in a location.

    Arrange:
      - Create a location and a WorldObject instance

    Act:
      - Add the object to the location
      - Retrieve the object by name

    Assert:
      - Verify the object is stored in the location's objects dictionary
      - Verify get_object returns the correct instance
      - Verify KeyError is raised when trying to retrieve a non-existent object
    """
    # Arrange
    library = Location(name="Library", description="A quiet place with books.")

    mock = MockObject()  # Using MockObject for testing purposes

    # Act (Add)
    library.add_object(mock)

    # Assert (Add & Retrieve)
    assert "Mock Object" in library.objects
    retrieved_object = library.get_object("Mock Object")
    assert retrieved_object == mock

    # Act (Remove object)
    library.remove_object("Mock Object")

    # Assert (Non-existent)
    with pytest.raises(KeyError, match='Object "Mock Object" not found'):
      library.get_object("Mock Object")


class TestLocationBackground:
  def test_background_creation(self):
    """
    Test that LocationBackground correctly initializes with various background configurations.

    Arrange:
      - Create background configurations with different combinations of day/afternoon/night

    Act:
      - Initialize LocationBackground instances with these configurations

    Assert:
      - Verify backgrounds are set correctly
      - Verify default values are applied when backgrounds are not specified
    """
    # Arrane & Act (Only day specified)
    bg_day_only = LocationBackground({"day": "bg_day"})

    # Assert
    assert bg_day_only.day == "bg_day"
    assert bg_day_only.afternoon == "bg_day"  # Should default to day
    assert bg_day_only.night == "bg_day"  # Should default to day

    # Arrange & Act (backgrounds specified)
    bg_all = LocationBackground({"day": "bg_day", "afternoon": "bg_afternoon", "night": "bg_night"})

    # Assert
    assert bg_all.day == "bg_day"
    assert bg_all.afternoon == "bg_afternoon"
    assert bg_all.night == "bg_night"

    # Assert
    assert bg_all.get_backgrounds() == ("bg_day", "bg_afternoon", "bg_night")
    assert str(bg_all) == '(Day: "bg_day", Afternoon: "bg_afternoon", Night: "bg_night")'

  def test_retrieve_scene_background(self):
    """
    Test that the correct background is retrieved based on the time of day.

    Arrange:
      - Create a LocationBackground with different backgrounds for different times

    Act:
      - Call retrieve_scene_background with different times

    Assert:
      - Verify the correct background is returned for each time period
    """
    # Arrange
    bg = LocationBackground({"day": "bg_day", "afternoon": "bg_afternoon", "night": "bg_night"})

    # Assert (Morning)
    # Test morning/day (7:00 - 16:59)
    assert bg.retrieve_scene_background((7, 0)) == "bg_day"
    assert bg.retrieve_scene_background((12, 30)) == "bg_day"
    assert bg.retrieve_scene_background((16, 59)) == "bg_day"

    # Assert (Afternoon)
    # Test afternoon (17:00 - 18:59)
    assert bg.retrieve_scene_background((17, 0)) == "bg_afternoon"
    assert bg.retrieve_scene_background((18, 30)) == "bg_afternoon"
    assert bg.retrieve_scene_background((18, 59)) == "bg_afternoon"

    # Assert (Night)
    # Test night (19:00 - 6:59)
    assert bg.retrieve_scene_background((19, 0)) == "bg_night"
    assert bg.retrieve_scene_background((23, 45)) == "bg_night"
    assert bg.retrieve_scene_background((0, 0)) == "bg_night"
    assert bg.retrieve_scene_background((6, 59)) == "bg_night"
