from unittest import TestCase

from worldnavigator.core import World, WorldParser
from worldnavigator.errors import MissingDayBackgroundError, NoLocationsFoundError


class WorldParserTest(TestCase):
  def test_scene_graph_parser(self):
    """
    Test parsing a valid scene graph JSON file into a World object.

    **Arrange**
        - Initialize a :class:`WorldParser` instance.

    **Act**
        - Parse the example world file using `scene_graph_parser()`.

    **Assert**
        - Verify the returned object is an instance of :class:`World`.
        - Check the world name and the number of locations.
        - Confirm that individual locations have correct indoor/outdoor properties and backgrounds.
        - Validate that connections between locations are correctly established.
        - Test that one-way connections are handled appropriately.
    """
    world_parser = WorldParser()
    world = world_parser.scene_graph_parser('./examples/worlds/nexis.world.json')

    self.assertIsInstance(world, World)
    self.assertEqual(world.name, 'Nexis')

    self.assertEqual(len(world.locations), 12)

    school = world.get_location('School')
    self.assertFalse(school.is_indoor)
    self.assertEqual(school.backgrounds.day, 'bg school')

    club_room = world.get_location('Club Room')
    self.assertTrue(club_room.is_indoor)
    self.assertEqual(club_room.backgrounds.day, 'bg club_day')
    self.assertEqual(club_room.backgrounds.afternoon, 'bg club_afternoon')

    self.assertIn('Park', school.connections)
    park = world.get_location('Park')
    self.assertIn('School', park.connections)

    right_corridor = world.get_location('Right Corridor')
    man_bathroom = world.get_location('Man Bathroom')
    self.assertIn('Man Bathroom', right_corridor.connections)
    self.assertNotIn('Right Corridor', man_bathroom.connections)

    left_corridor = world.get_location('Left Corridor')
    self.assertEqual(len(left_corridor.connections), 4)
    self.assertIn('Club Room', left_corridor.connections)
    self.assertIn('Classroom 2', left_corridor.connections)
    self.assertIn('Classroom 3', left_corridor.connections)
    self.assertIn('Main Entrance', left_corridor.connections)

    classroom2 = world.get_location('Classroom 2')
    closet = world.get_location('Closet')
    self.assertIn('Closet', classroom2.connections)
    self.assertNotIn('Left Corridor', closet.connections)

  def test_scene_graph_parser_invalid_json(self):
    """
    Test parsing invalid scene graph data and handling errors appropriately.

    **Arrange**
        - Initialize a :class:`WorldParser` instance.
        - Define invalid JSON-like structures for testing.

    **Act & Assert**
        - Test case 1: Parsing JSON with no locations.
            - Ensure :class:`NoLocationsFoundError` is raised.
            - Validate the error message.
        - Test case 2: Location missing a 'day' background.
            - Ensure :class:`MissingDayBackgroundError` is raised.
            - Validate the error message includes the affected location name.
    """
    world_parser = WorldParser()

    with self.assertRaises(NoLocationsFoundError) as context:
      world_parser.scene_graph_parser({'name': 'Empty World'})
    self.assertEqual(str(context.exception), 'No locations found in the provided world data')

    invalid_json = {
        'name': 'Invalid World',
        'locations': [
            {
                'name': 'Invalid Location',
                'is_indoor': False,
                'backgrounds': {'night': 'bg night'},
                'connected_locations': []
            }
        ]
    }

    with self.assertRaises(MissingDayBackgroundError) as context:
      world_parser.scene_graph_parser(invalid_json)
    self.assertEqual(str(context.exception), 'Missing day background for location "Invalid Location"')
