from worldnavigator.errors import DuplicatedLocationError, LocationNotFoundError
from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:
  from worldnavigator.locations.base_location import Location


class World:
  """
  Represents a world composed of connected locations.

  The World class serves as a container and manager for Location objects. It provides
  methods for adding, removing, and retrieving locations, as well as tracking characters
  within the world's locations.

  The world automatically monitors population changes by subscribing to the ``character_added``
  and ``character_removed`` events from its locations.
  """

  def __init__(self, *, name: str):
    self._name = name
    self._locations: Dict[str, 'Location'] = {}
    self._population = 0

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

  def where_is(self, character: str) -> str:
    """
    Determines where a specific character is located.

    :param str character: The character to find the location of.

    :return: The location of the character.
    """

    for location in self._locations.values():
      if character in location.characters:
        return f'"{character}" is in "{location.name}"'

    return f'"{character}" is not found in the world.'
