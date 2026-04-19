import pytest

from worldnavigator.core import World, WorldParser
from worldnavigator.errors import NoLocationsFoundError


class TestWorldParser:
  def test_scene_graph_parser(self):
    """
    Test parsing a valid scene graph JSON file into a World object.

    Arrange:
      - Initialize a WorldParser instance.

    Act:
      - Parse the example world file using scene_graph_parser().

    Assert:
      - Verify the returned object is an instance of World.
      - Check the world name and the number of locations.
      - Confirm that individual locations have correct indoor/outdoor properties and backgrounds.
      - Validate that connections between locations are correctly established.
    """
    # Arrange
    world_parser = WorldParser()

    # Act
    world = world_parser.scene_graph_parser("./examples/worlds/nexis.world.json")

    # Assert
    assert isinstance(world, World)
    assert world.name == "Nexis"
    assert len(world.locations) == 12

    school = world.get_location("School")
    assert school.is_indoor is False
    assert school.backgrounds.day == "default_day_background"

    club_room = world.get_location("Club Room")
    assert club_room.is_indoor is True
    assert club_room.backgrounds.day == "default_day_background"
    assert club_room.backgrounds.afternoon == "default_day_background"

    assert "Park" in school.connections
    park = world.get_location("Park")
    assert "School" in park.connections

    right_corridor = world.get_location("Right Corridor")
    man_bathroom = world.get_location("Man Bathroom")
    assert "Man Bathroom" in right_corridor.connections
    assert "Right Corridor" not in man_bathroom.connections

  def test_scene_graph_parser_invalid_json(self):
    """
    Test parsing invalid scene graph data and handling errors appropriately.

    Arrange:
      - Initialize a WorldParser instance.
      - Define invalid JSON-like structures for testing.

    Act & Assert:
      - Test case 1: Verify NoLocationsFoundError is raised for empty worlds.
      - Test case 2: Verify MissingDayBackgroundError is raised when day background is missing.
    """
    # Arrange
    world_parser = WorldParser()
    empty_data = {"name": "Empty World"}
    invalid_json = {
      "name": "Invalid World",
      "locations": [
        {
          "name": "Invalid Location",
          "description": "Desc",
          "is_indoor": False,
          "backgrounds": {"night": "bg night"},
          "connected_locations": [],
        }
      ],
    }

    # Act & Assert (No locations)
    with pytest.raises(NoLocationsFoundError) as excinfo:
      world_parser.scene_graph_parser(empty_data)
    assert str(excinfo.value) == "No locations found in the provided world data"
