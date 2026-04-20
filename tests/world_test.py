import pytest

from worldnavigator.core import World
from worldnavigator.core.character import GameCharacter
from worldnavigator.errors import CharacterAlreadyPresentError, DuplicatedLocationError, LocationNotFoundError
from worldnavigator.locations import Location
from worldnavigator.types.types import BaseCondition


class TestWorld:
  def test_world_creation(self):
    """
    Test that a world can be created with the correct name.

    Arrange:
      - Define a world name.

    Act:
      - Create a new World instance.

    Assert:
      - Verify the world is created with the correct name.
      - Verify the world starts with no locations.
      - Verify initial population is zero.
    """
    # Arrange
    name = "Nexis"

    # Act
    world = World(name=name)

    # Assert
    assert world.name == name
    assert len(world.locations) == 0
    assert world.population() == '"0" characters'

  def test_add_location(self):
    """
    Test adding locations to the world.

    Arrange:
      - Create a new world.
      - Create sample Location instances.

    Act:
      - Add locations to the world.

    Assert:
      - Verify locations are added correctly to the locations list.
      - Verify DuplicatedLocationError is raised when adding the same location twice.
    """
    # Arrange
    world = World(name="Nexis")
    school = Location(name="School", description="School", backgrounds={"day": "bg school"}, is_indoor=False)
    club_room = Location(name="Club Room", description="Club", backgrounds={"day": "bg club_day"}, is_indoor=True)

    # Act
    world.add_location(school)
    world.add_location(club_room)

    # Assert
    assert len(world.locations) == 2
    assert school in world.locations
    assert club_room in world.locations

    # Act & Assert (Duplicate)
    with pytest.raises(DuplicatedLocationError):
      world.add_location(school)

  def test_remove_location(self):
    """
    Test removing locations from the world.

    Arrange:
      - Create a new world.
      - Add a location to the world.

    Act:
      - Remove the location from the world by name.

    Assert:
      - Verify the correct location object is returned.
      - Verify the location is removed from the world.
      - Verify LocationNotFoundError is raised for non-existent locations.
    """
    # Arrange
    world = World(name="Nexis")
    school = Location(name="School", description="School", backgrounds={"day": "bg school"})
    world.add_location(school)

    # Act
    removed_location = world.remove_location("School")

    # Assert
    assert removed_location == school
    assert len(world.locations) == 0

    # Act & Assert (Non-existent)
    with pytest.raises(LocationNotFoundError):
      world.remove_location("Non-existent Location")

  def test_entry_point(self):
    """
    Test setting the character entry point in the world.

    Arrange:
      - Create a new world.
      - Create a location to set as the entry point.

    Act:
      - Set the character entry point to the location.

    Assert:
      - Verify the entry point is set correctly.
      - Verify LocationNotFoundError is raised when setting an entry point to a non-existent location.
    """
    # Arrange
    world = World(name="Nexis")
    school = Location(name="School", description="School", backgrounds={"day": "bg school"})
    world.add_location(school)

    # Act
    world.character_entrypoint("School")

    # Assert
    assert world._character_entrypoint == school

    # Act
    with pytest.raises(LocationNotFoundError) as exc_info:
      world.character_entrypoint("Non-existent Location")

    # Assert (Non-existent)
    assert 'Location "Non-existent Location" not found' in str(exc_info.value)

  def test_get_location(self):
    """
    Test retrieving locations from the world by name.

    Arrange:
      - Create a world and add a location.

    Act:
      - Retrieve the location by name.

    Assert:
      - Verify the correct location instance is returned.
      - Verify LocationNotFoundError is raised for invalid names.
    """
    # Arrange
    world = World(name="Nexis")
    school = Location(name="School", description="Desc", backgrounds={"day": "bg school"})
    world.add_location(school)

    # Act
    retrieved_location = world.get_location("School")

    # Assert
    assert retrieved_location == school

    # Act & Assert (Non-existent)
    with pytest.raises(LocationNotFoundError):
      world.get_location("Non-existent Location")

  def test_character_population_tracking(self):
    """
    Test that the world correctly tracks total population.

    Arrange:
      - Create a world with locations.
      - Create a character instance.

    Act:
      - Add and remove the character from a location.

    Assert:
      - Verify population count updates correctly after addition and removal.
    """
    # Arrange
    world = World(name="Nexis")
    school = Location(name="School", description="Desc", backgrounds={"day": "bg school"})
    world.add_location(school)
    student = GameCharacter("Student")

    # Act & Assert (Initial)
    assert world.population() == '"0" characters'

    # Act (Add)
    school.add_character(student)

    # Assert (Add)
    assert world.population() == '"1" characters'

    # Act (Remove)
    school.remove_character(student)

    # Assert (Remove)
    assert world.population() == '"0" characters'

  def test_character_movement(self):
    """
    Test moving characters between locations.

    Arrange:
      - Create a world with multiple locations.
      - Set an entry point and add characters.

    Act:
      - Move characters using the move_character method.

    Assert:
      - Verify the character's location is updated in the world state.
      - Verify appropriate errors are raised for invalid moves.
    """
    # Arrange
    world = World(name="Nexis")
    l1 = Location(name="L1", description="D1", backgrounds={"day": "bg1"})
    l2 = Location(name="L2", description="D2", backgrounds={"day": "bg2"})
    world.add_location(l1)
    world.add_location(l2)
    char = GameCharacter("Player")

    # Act
    with pytest.raises(ValueError) as exc_info:
      world.add_character(char)

    # Assert (Not entry point)
    assert str(exc_info.value) == "No character entrypoint defined"

    # Act
    world.character_entrypoint(l1)
    world.add_character(char)
    world.move_character(char, "L2")

    # Assert
    assert char.current_location == "L2"
    assert world.where_is(char) == '"Player" is in "L2"'
    assert world.where_are_everyone().strip() == '"Player" is in "L2"'

    # Act & Assert (Invalid move to current)
    with pytest.raises(CharacterAlreadyPresentError):
      world.move_character(char, "L2")

    # Act & Assert (Add twice)
    with pytest.raises(CharacterAlreadyPresentError):
      world.add_character(char)

  def test_player_movement(self):
    """
    Test moving a player character between locations.

    Arrange:
      - Create a world with multiple locations.
      - Set an entry point and add a player character.

    Act:
      - Move the player character to a different location.

    Assert:
      - Verify the player's current location is updated correctly.
      - Verify the where_is and where_are_everyone methods reflect the new location.
    """
    # Arrange
    world = World(name="Nexis")
    l1 = Location(name="L1", description="D1", backgrounds={"day": "bg1"})
    l2 = Location(name="L2", description="D2", backgrounds={"day": "bg2"})
    world.add_location(l1)
    world.add_location(l2)
    player = GameCharacter("Player")

    # Act
    world.add_player(player, l2)
    world.move_player(l1)

    # Assert
    assert player.current_location == "L1"
    assert len(l1.characters) == 0
    assert world.player_current_location == l1
    assert (
      world.where_is(player) == '"Player" is not found in the world.'
    )  # Because player is not a "NPC" character the world doesn't track it in the total characters list
    assert world.where_are_everyone().strip() == ""

  def test_where_is_character(self):
    """
    Test finding a character's location string.

    Arrange:
      - Create a world and add a character to a location.

    Act:
      - Query the location of the character.

    Assert:
      - Verify the returned string matches the expected location format.
      - Verify the message for non-existent characters.
    """
    # Arrange
    world = World(name="Nexis")
    loc = Location(name="Room", description="Desc", backgrounds={"day": "bg"})
    world.add_location(loc)
    char = GameCharacter("Hero")
    loc.add_character(char)

    # Act
    result = world.where_is(char)

    # Assert
    assert result == '"Hero" is in "Room"'
    assert world.where_is(GameCharacter("Ghost")) == '"Ghost" is not found in the world.'

  def test_conditional_pipeline_to_move_character(self):
    """
    Test the conditional pipeline for moving characters.

    Arrange:
      - Create a world with multiple locations.
      - Define a custom condition that checks character data.
      - Link the condition to a location's pipeline.

    Act:
      - Attempt to move the character when the condition is NOT met.
      - Attempt to move the character when the condition IS met.

    Assert:
      - Verify the character does NOT move (returns False) when the condition fails.
      - Verify the character moves successfully (returns True) when the condition passes.
    """
    # Arrange
    world = World(name="Nexis")
    l1 = Location(name="L1", description="D1", backgrounds={"day": "bg1"})
    l2 = Location(name="L2", description="D2", backgrounds={"day": "bg2"})
    char = GameCharacter("Player", data={"can_move": False})

    class CustomCondition(BaseCondition):
      def handle(self, context):
        if char.data["can_move"]:
          return True

        return False

    l2.condition_pipeline + CustomCondition()
    world.add_location(l1)
    world.add_location(l2)
    world.character_entrypoint(l1)
    world.add_character(char)

    # Act
    res = world.move_character(char, l2)

    # Assert
    assert not res, "Character should not move when condition is not met"

    # Act (Change condition)
    char.data["can_move"] = True

    res = world.move_character(char, l2)

    # Assert
    assert res, "Character should move when condition is met"
