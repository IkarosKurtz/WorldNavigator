from unittest import TestCase

from worldnavigator.core import World
from worldnavigator.core.character import GameCharacter
from worldnavigator.errors import CharacterAlreadyPresentError, CharacterNotFoundError, DuplicatedLocationError, LocationNotFoundError
from worldnavigator.locations import Location


class WorldTest(TestCase):
  def test_world_creation(self):
    """
    Test that a world can be created with the correct name.

    Act:
      - Create a new World instance with a name

    Assert:
      - Verify the world is created with the correct name
      - Verify the world starts with no locations
    """
    world = World(name='Nexis')

    self.assertEqual(world.name, 'Nexis')
    self.assertEqual(len(world.locations), 0)

    self.assertEqual(world.population(), '"0" characters')

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
      - Verify trying to add a duplicate location raises ValueError
    """
    world = World(name='Nexis')

    # Create test locations
    school = Location(
        name='School',
        backgrounds={'day': 'bg school'},
        is_indoor=False
    )

    club_room = Location(
        name='Club Room',
        backgrounds={'day': 'bg club_day', 'afternoon': 'bg club_afternoon'},
        is_indoor=True
    )

    # Add locations to world
    world.add_location(school)
    world.add_location(club_room)

    # Verify locations were added
    self.assertEqual(len(world.locations), 2)
    self.assertIn(school, world.locations)
    self.assertIn(club_room, world.locations)

    # Test adding duplicate location
    with self.assertRaises(DuplicatedLocationError) as context:
      world.add_location(school)

    self.assertEqual(str(context.exception), 'Location "School" is already in the world.')

  def test_remove_location(self):
    """
    Test removing locations from the world.

    Arrange:
      - Create a new world
      - Add a location to the world

    Act:
      - Remove the location from the world

    Assert:
      - Verify the location is removed
      - Verify trying to remove a non-existent location raises LocationNotFoundError
    """
    world = World(name='Nexis')

    # Create and add a test location
    school = Location(
        name='School',
        backgrounds={'day': 'bg school'},
        is_indoor=False
    )
    world.add_location(school)

    # Remove the location
    removed_location = world.remove_location('School')

    # Verify location was removed
    self.assertEqual(removed_location, school)
    self.assertEqual(len(world.locations), 0)

    # Test removing non-existent location
    with self.assertRaises(LocationNotFoundError) as context:
      world.remove_location('Non-existent Location')

    self.assertEqual(str(context.exception), 'Location "Non-existent Location" not found')

  def test_get_location(self):
    """
    Test retrieving locations from the world by name.

    Arrange:
      - Create a new world
      - Add a location to the world

    Act:
      - Get the location by name

    Assert:
      - Verify the correct location is returned
      - Verify trying to get a non-existent location raises LocationNotFoundError
    """
    world = World(name='Nexis')

    # Create and add a test location
    school = Location(
        name='School',
        backgrounds={'day': 'bg school'},
        is_indoor=False
    )
    world.add_location(school)

    # Get the location
    retrieved_location = world.get_location('School')

    # Verify correct location was returned
    self.assertEqual(id(retrieved_location), id(school))

    # Test getting non-existent location
    with self.assertRaises(LocationNotFoundError) as context:
      world.get_location('Non-existent Location')

    self.assertEqual(str(context.exception), 'Location "Non-existent Location" not found')

  def test_character_population_tracking(self):
    """
    Test that the world correctly tracks the total population as characters are added and removed.

    Arrange:
      - Create a new world
      - Add locations to the world

    Act:
      - Add characters to locations
      - Remove characters from locations

    Assert:
      - Verify population count updates correctly when characters are added
      - Verify population count updates correctly when characters are removed
    """
    world = World(name='Nexis')

    # Create and add test locations
    school = Location(
        name='School',
        backgrounds={'day': 'bg school'},
        is_indoor=False
    )

    club_room = Location(
        name='Club Room',
        backgrounds={'day': 'bg club_day'},
        is_indoor=True
    )

    world.add_location(school)
    world.add_location(club_room)

    # Initial population should be 0
    self.assertEqual(world.population(), '"0" characters')

    student1 = GameCharacter("Student1")
    teacher = GameCharacter("Teacher")
    student2 = GameCharacter("Student2")

    # Add characters to locations
    school.add_character(student1)
    school.add_character(teacher)
    club_room.add_character(student2)

    # Population should be 3
    self.assertEqual(world.population(), '"3" characters')

    # Raise error when adding duplicate character
    with self.assertRaises(CharacterAlreadyPresentError) as context:
      school.add_character(student1)

    self.assertEqual(str(context.exception), 'Character "Student1" is already in "School"')

    # Remove a character
    school.remove_character(student1)

    # Population should be 2
    self.assertEqual(world.population(), '"2" characters')

    # Remove all remaining characters
    school.remove_character(teacher)
    club_room.remove_character(student2)

    # Population should be 0
    self.assertEqual(world.population(), '"0" characters')

    # Raise error when removing non-existent character
    with self.assertRaises(CharacterNotFoundError) as context:
      club_room.remove_character(student2)

    self.assertEqual(str(context.exception), 'Character "Student2" is not in "Club Room"')

  def test_character_movement(self):
    """
    Test moving characters between locations using the move_character method.

    Arrange:
      - Create a new world
      - Add locations to the world
      - Add characters to locations
      - Set up the character entry point

    Act:
      - Move characters between locations using the move_character method

    Assert:
      - Verify characters are correctly moved between locations
      - Verify character's current_location property is updated
      - Verify trying to move a character to its current location raises CharacterAlreadyPresentError
      - Verify trying to move a character to a non-existent location raises LocationNotFoundError
    """
    world = World(name='Nexis')

    # Create and add test locations
    school = Location(
        name='School',
        backgrounds={'day': 'bg school'},
        is_indoor=False
    )

    club_room = Location(
        name='Club Room',
        backgrounds={'day': 'bg club_day'},
        is_indoor=True
    )

    library = Location(
        name='Library',
        backgrounds={'day': 'bg library'},
        is_indoor=True
    )

    world.add_location(school)
    world.add_location(club_room)
    world.add_location(library)

    # Set character entry point
    world.character_entrypoint(school)

    # Create and add characters
    student1 = GameCharacter("Student1")
    teacher = GameCharacter("Teacher")

    # Add characters to the world
    world.add_character(student1)
    world.add_character(teacher)

    # Initial location check
    self.assertEqual(student1.current_location, 'School')
    self.assertEqual(teacher.current_location, 'School')
    self.assertEqual(world.where_is(student1), '"Student1" is in "School"')

    # Move student1 to club_room
    world.move_character(student1, 'Club Room')

    # Verify student1 was moved to club_room
    self.assertEqual(student1.current_location, 'Club Room')
    self.assertEqual(world.where_is(student1), '"Student1" is in "Club Room"')

    # Move student1 to library
    world.move_character(student1, library)

    # Verify student1 was moved to library
    self.assertEqual(student1.current_location, 'Library')
    self.assertEqual(world.where_is(student1), '"Student1" is in "Library"')

    # Verify teacher is still in school
    self.assertEqual(teacher.current_location, 'School')
    self.assertEqual(world.where_is(teacher), '"Teacher" is in "School"')

    # Test moving to non-existent location
    with self.assertRaises(LocationNotFoundError):
      world.move_character(student1, 'Non-existent Location')

    # Test moving to current location (should raise error)
    with self.assertRaises(CharacterAlreadyPresentError) as context:
      world.move_character(student1, library)

    self.assertEqual(str(context.exception), 'Character "Student1" is already in "Library"')

  def test_where_is_character(self):
    """
    Test finding a character's location in the world.

    Arrange:
      - Create a new world
      - Add locations to the world
      - Add characters to different locations

    Act:
      - Query for characters' locations

    Assert:
      - Verify correct locations are returned for each character
      - Verify appropriate message is returned for non-existent characters
      - Verify location updates when a character moves
    """
    world = World(name='Nexis')

    # Create and add test locations
    school = Location(
        name='School',
        backgrounds={'day': 'bg school'},
        is_indoor=False
    )

    club_room = Location(
        name='Club Room',
        backgrounds={'day': 'bg club_day'},
        is_indoor=True
    )

    world.add_location(school)
    world.add_location(club_room)

    student1 = GameCharacter("Student1")
    teacher = GameCharacter("Teacher")
    student2 = GameCharacter("Student2")

    # Add characters to locations
    school.add_character(student1)
    school.add_character(teacher)
    club_room.add_character(student2)

    # Test finding characters
    self.assertEqual(world.where_is(student1), '"Student1" is in "School"')
    self.assertEqual(world.where_is(teacher), '"Teacher" is in "School"')
    self.assertEqual(world.where_is(student2), '"Student2" is in "Club Room"')

    unknown = GameCharacter("Unknown")

    # Test finding non-spawned character
    self.assertEqual(world.where_is(unknown), '"Unknown" is not found in the world.')

    # Test character movement
    school.remove_character(student1)
    club_room.add_character(student1)

    # Verify location was updated
    self.assertEqual(world.where_is(student1), '"Student1" is in "Club Room"')
