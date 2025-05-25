from unittest import TestCase

from worldnavigator.core.character import GameCharacter
from worldnavigator.locations.base_location import Location
from worldnavigator.errors import CharacterAlreadyPresentError, CharacterNotFoundError, DuplicatedLocationError, LocationNotFoundError, MissingDayBackgroundError


class LocationTest(TestCase):
  def test_location_creation(self):
    """
    Test that a location can be created with the correct properties.

    Arrange:
      - Prepare background dictionaries and object lists

    Act:
      - Create Location instances with different configurations

    Assert:
      - Verify location properties are set correctly
      - Verify MissingDayBackgroundError is raised when day background is missing
    """
    # Test basic creation
    location = Location(
        name="Classroom",
        backgrounds={'day': 'bg_classroom_day'},
        is_indoor=True
    )

    self.assertEqual(location.name, "Classroom")
    self.assertTrue(location.is_indoor)
    self.assertEqual(location.backgrounds.day, "bg_classroom_day")
    self.assertEqual(len(location.objects), 0)
    self.assertEqual(len(location.connections), 0)
    self.assertEqual(len(location.characters), 0)

    # Test missing day background
    with self.assertRaises(MissingDayBackgroundError) as context:
      Location(
          name="Invalid",
          backgrounds={'night': 'bg_night_only'},
          is_indoor=False
      )

    self.assertEquals(str(context.exception), 'Missing day background for location "Invalid"')

  def test_location_connections(self):
    """
    Test connecting and disconnecting locations.

    Arrange:
      - Create multiple locations

    Act:
      - Connect locations with each other
      - Attempt invalid connections
      - Disconnect locations

    Assert:
      - Verify connections are established correctly
      - Verify proper errors are raised for invalid operations
      - Verify disconnections work correctly
    """
    classroom = Location(name="Classroom", backgrounds={'day': 'bg_classroom'})
    hallway = Location(name="Hallway", backgrounds={'day': 'bg_hallway'})
    office = Location(name="Office", backgrounds={'day': 'bg_office'})

    # Test connecting locations
    classroom.connect_with(hallway)
    self.assertIn("Hallway", classroom.connections)
    self.assertEqual(id(classroom.connections["Hallway"]), id(hallway))

    # Test get_location
    self.assertEqual(id(classroom.get_location("Hallway")), id(hallway))

    # Test get_locations
    self.assertEqual(classroom.get_locations(), [hallway])

    # Test duplicate connection
    with self.assertRaises(DuplicatedLocationError) as context:
      classroom.connect_with(hallway)

    self.assertEquals(str(context.exception), 'Location "Hallway" is already connected to "Classroom"')

    # Test connecting multiple locations
    classroom.connect_with(office)
    self.assertEqual(len(classroom.connections), 2)
    self.assertIn("Office", classroom.connections)

    # Test disconnecting
    classroom.disconnect_from("Hallway")
    self.assertNotIn("Hallway", classroom.connections)
    self.assertEqual(len(classroom.connections), 1)

    # Test disconnecting non-existent location
    with self.assertRaises(LocationNotFoundError) as context:
      classroom.disconnect_from("Non-existent")

    self.assertEquals(str(context.exception), 'Location "Non-existent" not found')

    # Test getting non-existent location
    with self.assertRaises(LocationNotFoundError) as context:
      classroom.get_location("Non-existent")

    self.assertEquals(str(context.exception), 'Location "Non-existent" not found')

  def test_character_management(self):
    """
    Test adding, removing, and querying characters in a location.

    Arrange:
      - Create a location
      - Set up event tracking

    Act:
      - Add characters to the location
      - Query who is in the location
      - Remove characters from the location
      - Attempt invalid operations

    Assert:
      - Verify characters are added correctly
      - Verify who_is_here returns correct string
      - Verify characters are removed correctly
      - Verify proper errors are raised for invalid operations
      - Verify events are triggered correctly
    """
    cafeteria = Location(name="Cafeteria", backgrounds={'day': 'bg_cafeteria'})

    # Track triggered events
    events_triggered = []

    def event_tracker(**data):
      events_triggered.append((data['name'], data['location']))

    cafeteria.on('character_added', event_tracker)
    cafeteria.on('character_removed', event_tracker)

    # Test initial state
    self.assertEqual(len(cafeteria.characters), 0)
    self.assertEqual(cafeteria.who_is_here(), '')

    student1 = GameCharacter("Student1")
    teacher = GameCharacter("Teacher")

    # Test adding characters
    cafeteria.add_character(student1)
    cafeteria.add_character(teacher)

    self.assertEqual(len(cafeteria.characters), 2)
    self.assertIn(student1, cafeteria.characters)
    self.assertIn(teacher, cafeteria.characters)

    # Test who_is_here
    self.assertEqual(cafeteria.who_is_here(), "Student1, Teacher")

    # Test adding duplicate character
    with self.assertRaises(CharacterAlreadyPresentError) as context:
      cafeteria.add_character(student1)

    self.assertEqual(str(context.exception), 'Character "Student1" is already in "Cafeteria"')

    # Test removing character
    cafeteria.remove_character(student1)

    self.assertEqual(len(cafeteria.characters), 1)
    self.assertNotIn(student1, cafeteria.characters)
    self.assertIn(teacher, cafeteria.characters)

    student2 = GameCharacter("Student2")

    # Test removing non-existent character
    with self.assertRaises(CharacterNotFoundError) as context:
      cafeteria.remove_character(student2)

    self.assertEqual(str(context.exception), 'Character "Student2" is not in "Cafeteria"')

    # Test events were triggered
    self.assertEqual(len(events_triggered), 3)  # 2 adds + 1 remove
    self.assertEqual(events_triggered[0], ("Student1", "Cafeteria"))
    self.assertEqual(events_triggered[1], ("Teacher", "Cafeteria"))
    self.assertEqual(events_triggered[2], ("Student1", "Cafeteria"))
