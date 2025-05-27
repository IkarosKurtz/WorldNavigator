from typing import TYPE_CHECKING, List, Dict, Union

from worldnavigator.core.world_time import Time, WorldTime
from worldnavigator.errors import DuplicatedLocationError, LocationNotFoundError
from worldnavigator.errors.character_already_present import CharacterAlreadyPresentError

if TYPE_CHECKING:
  from worldnavigator.locations.base_location import Location
  from worldnavigator.core.character import GameCharacter


class World:
  """
  Represents a world composed of connected locations.

  The World class serves as a container and manager for Location objects. It provides
  methods for adding, removing, and retrieving locations, as well as tracking characters
  within the world's locations.

  The world automatically monitors population changes by subscribing to the ``character_added``
  and ``character_removed`` events from its locations.
  """

  def __init__(self, *, name: str, initial_time: Time = Time()):
    """
    :param str name: The name of the world.
    :param list[int] initial_time: The initial time of the world. See :ref:`~worldnavigator.core.world_time.WorldTime` for more information.
    """
    self._name = name
    self._locations: Dict[str, 'Location'] = {}
    self._total_characters: list['GameCharacter'] = []
    self._population = 0
    self._character_entrypoint: 'Location' = None

    self._time = WorldTime(initial_time)

  #################################################
  ################### Properties ##################
  #################################################

  @property
  def name(self) -> str:
    """
    Name of the world
    """
    return self._name

  @property
  def locations(self) -> List['Location']:
    """
    A list with all the locations in the world
    """
    return list(self._locations.values())

  @property
  def time(self) -> WorldTime:
    """
    Manager from the world time
    """
    return self._time

  #################################################
  ################ Private Methods ################
  #################################################

  def _character_added(self, name: str, location: str):
    self._population += 1

  def _character_removed(self, name: str, location: str):
    self._population -= 1

  #################################################
  ################ Public Methods #################
  #################################################

  def population(self) -> str:
    """
    Get a string with the number of characters in the world

    :return: String saying how many characters are in the world
    """
    return f'"{self._population}" characters'

  def add_location(self, location: 'Location') -> None:
    """
    Add a new location to the world

    :param Location location: The new location to add

    :raise DuplicatedLocationError: If the location is already in the world
    """
    if location.name in self._locations:
      raise DuplicatedLocationError(f'Location "{location.name}" is already in the world.')

    location.on('character_added', self._character_added)
    location.on('character_removed', self._character_removed)
    self._locations[location.name] = location

  def remove_location(self, location_name: str) -> 'Location':
    """
    Remove some location with his name

    :return: The removed location
    :raise LocationNotFoundError: If the location is not found in the world
    """
    if location_name not in self._locations:
      raise LocationNotFoundError(location_name)

    return self._locations.pop(location_name)

  def get_location(self, location_name: str) -> 'Location':
    """
    Get a location by it's name

    :return: The location
    :raise LocationNotFoundError: If the location is not found in the world
    """
    if location_name not in self._locations:
      raise LocationNotFoundError(location_name)

    return self._locations[location_name]

  def where_is(self, character: 'GameCharacter') -> str:
    """
    Determines where a specific character is located.

    :param GameCharacter character: The character to find the location of.

    :return: The location of the character.
    """

    for location in self._locations.values():
      if character in location.characters:
        return f'"{character.name}" is in "{location.name}"'

    return f'"{character.name}" is not found in the world.'

  def character_entrypoint(self, location: Union[str, 'Location']) -> None:
    """
    Set spawn point for characters, this means when you use :py:meth:`~World.add_character` it will be moved to this location, if not set, you can't add characters.

    :param Union[str, Location] location: The location to set as the spawn point.

    :raises LocationNotFoundError: If the location is not found in the world.
    """
    if isinstance(location, str):
      location = self.get_location(location)

    self._character_entrypoint = location

  def add_character(self, character: 'GameCharacter') -> None:
    """
    Add a character to the world, the character will be on the ``character_entrypoint`` location, use :py:meth:`~World.character_entrypoint`.

    :param GameCharacter character: The character to add.

    :raises ValueError: If the character entrypoint is not set.
    :raises CharacterAlreadyPresentError: If the character is already in the world.
    """
    if self._character_entrypoint is None:
      raise ValueError('No character entrypoint defined')

    # We don't want to add the same character twice
    if character in self._total_characters:
      raise CharacterAlreadyPresentError(f'Character "{character.name}" is already in the world.')

    self._total_characters.append(character)
    self._character_entrypoint.add_character(character)

  def move_character(self, character: 'GameCharacter', location: Union[str, 'Location']) -> bool:
    """
    Use this method to move a character to a different location. This is the recommended way to move characters.

    .. attention:: 

      You can also do it in the old way, that consists in get the location you want
      to move and the current location, and use :py:meth:`~worldnavigator.locations.base_location.Location.add_character`
      for the current location and :py:meth:`~worldnavigator.locations.base_location.Location.remove_character` for the new one.

    :param GameCharacter character: The character to move.
    :param Union[str, Location] location: The location to move the character to.

    :return: True if the character was moved, False if the character was not moved.
    :raises LocationNotFoundError: If the location is not found in the world.
    :raises CharacterAlreadyPresentError: If the character is already in the location.
    """
    if isinstance(location, str):
      location = self.get_location(location)

    if location.condition_pipeline.handle().denied:
      return False

    last_location = character.current_location

    if last_location is not None:
      last_location = self.get_location(last_location)

    # Why do you want to move a character to the same location?
    if last_location.name == location.name:
      raise CharacterAlreadyPresentError(f'Character "{character.name}" is already in "{location.name}"')

    last_location.remove_character(character)

    location.add_character(character)
    return True
