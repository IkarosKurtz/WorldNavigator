from typing import TYPE_CHECKING, Dict, List, Tuple, Optional

from worldnavigator.core.condition_pipeline import ConditionalPipeline
from worldnavigator.errors import CharacterAlreadyPresentError, CharacterNotFoundError, DuplicatedLocationError, LocationNotFoundError
from worldnavigator.errors.missing_day_bg import MissingDayBackgroundError
from worldnavigator.observer import Observer
from worldnavigator.types.typed_dicts import BackgroundsDict

if TYPE_CHECKING:
  from worldnavigator.core.character import GameCharacter
  from worldnavigator.core.world_object import WorldObject


class LocationBackground:
  """
  Manages the different background images for a location based on the time of day.

  This class handles the storage and retrieval of background images for different times
  of day (morning, afternoon, night). It provides a time-based background retrieval system
  that automatically selects the appropriate background image based on the current in-game time.

  The day background is required, while afternoon and night backgrounds are optional and
  will default to the day background if not specified.
  """

  def __init__(self, backgrounds: BackgroundsDict):
    day_background = backgrounds.get('day', None)

    self._day: str = day_background
    self._afternoon: str = backgrounds.get('afternoon', self.day)
    self._night: str = backgrounds.get('night', self.day)

  def __str__(self):
    return f'(Day: "{self.day}", Afternoon: "{self.afternoon}", Night: "{self.night}")'

  def __repr__(self):
    return self.__str__()

  #################################################
  ################### Properties ##################
  #################################################

  @property
  def day(self) -> str:
    """Returns the day background."""
    return self._day

  @property
  def afternoon(self) -> str:
    """Returns the afternoon background."""
    return self._afternoon

  @property
  def night(self) -> str:
    """Returns the night background."""
    return self._night

  #################################################
  ################ Public Methods #################
  #################################################

  def get_backgrounds(self) -> Tuple[str, str, str]:
    """
    Returns a tuple of all backgrounds (day, afternoon, night).

    :return: A tuple containing the day, afternoon, and night backgrounds.
    """
    return (self.day, self.afternoon, self.night)

  def retrieve_scene_background(self, time: Tuple[int, int]) -> str:
    """
    Retrieves the appropriate background based on the current in-game time.

    :param Tuple[int, int] time: A tuple representing the current hour and minute.
    :return: The background image for the current time of day.
    """
    hour, minute = time

    if 7 <= hour < 17:
      return self.day
    elif 17 <= hour < 19:
      return self.afternoon
    else:
      return self.night


class Location(Observer):
  """
  Represents a location within a world that can be connected to other locations.

  A Location is a basic building block of a World. It can contain characters and objects,
  and connects to other locations to form a navigable environment. Each location can have
  different background images for day and night conditions, and can be designated as indoor
  or outdoor.
  """

  def __init__(self,
               *,
               name: str,
               backgrounds: BackgroundsDict,
               objects: Optional[dict[str, 'WorldObject']] = None,
               is_indoor: bool = False):
    """
    :param str name: The name of the location.
    :param BackgroundsDict backgrounds: A dictionary containing the backgrounds for different times of day.
    :param Optional[Dict[str, WorldObject]] objects: A dictionary of objects present in the location (optional).
    :param bool is_indoor: A boolean indicating if the location is indoors (default is False).

    :raises MissingDayBackgroundError: If the day background is not provided.
    """
    super().__init__()
    self._name = name

    if backgrounds.get('day', None) is None:
      raise MissingDayBackgroundError(self._name)

    self._backgrounds = LocationBackground(backgrounds)
    self._objects: dict[str, 'WorldObject'] = objects if objects is not None else {}
    self._is_indoor = is_indoor

    self._condition_pipeline = ConditionalPipeline()

    self._connections: dict[str, 'Location'] = {}
    self._characters: list['GameCharacter'] = []

  #################################################
  ################### Properties ##################
  #################################################

  @property
  def name(self) -> str:
    """Returns the name of the location."""
    return self._name

  @property
  def backgrounds(self) -> LocationBackground:
    """Returns the LocationBackground instance for the location."""
    return self._backgrounds

  @property
  def objects(self) -> Dict[str, 'WorldObject']:
    """Returns the objects present in the location."""
    return self._objects

  @property
  def is_indoor(self) -> bool:
    """Returns whether the location is indoors."""
    return self._is_indoor

  @property
  def connections(self) -> Dict[str, 'Location']:
    """Returns the connections to other locations."""
    return self._connections

  @property
  def characters(self) -> List['GameCharacter']:
    """Returns the characters present in the location."""
    return self._characters

  @property
  def condition_pipeline(self) -> ConditionalPipeline:
    """Returns the conditional pipeline for the location."""
    return self._condition_pipeline

  #################################################
  ################ Public Methods #################
  #################################################

  def get_location(self, location_name: str) -> 'Location':
    """
    Retrieves a connected location by name.

    :param str location_name: The name of the location to retrieve.

    :return: The connected Location instance.
    :raises LocationNotFoundError: If the location is not found in the connections.
    """
    if location_name not in self._connections:
      raise LocationNotFoundError(location_name)

    return self._connections[location_name]

  def get_locations(self) -> List['Location']:
    """
    Returns a list of all connected locations.

    :return: A list of connected Location instances.
    """
    return list(self._connections.values())

  def connect_with(self, other_location: 'Location') -> None:
    """
    Connects this location with another location.

    :param Location other_location: The location to connect with.
    :raises DuplicatedLocationError: If the locations are already connected.
    """
    if other_location.name in self.connections:
      raise DuplicatedLocationError(f'Location "{other_location.name}" is already connected to "{self.name}"')

    self._connections[other_location.name] = other_location

  def disconnect_from(self, location_name: str) -> None:
    """
    Disconnects this location from another location.

    :param str location_name: The name of the location to disconnect from.
    :raises LocationNotFoundError: If the location is not found in the connections.
    """
    if location_name not in self.connections:
      raise LocationNotFoundError(location_name)

    self.connections.pop(location_name)

  def add_object(self, obj: 'WorldObject'):
    """
    Adds an object to the location.

    :param WorldObject obj: The WorldObject to add.
    """
    self._objects[obj.name] = obj

  def remove_object(self, obj_name: str) -> 'WorldObject':
    """
    Removes an object from the location.

    :param str obj_name: The name of the object to remove.
    :raises KeyError: If the object is not found in the location.

    :return: The removed WorldObject.
    """
    return self._objects.pop(obj_name)

  def get_object(self, obj_name: str) -> 'WorldObject':
    """
    Retrieves an object from the location by name.

    :param str obj_name: The name of the object to retrieve.
    :raises KeyError: If the object is not found in the location.

    :return: The WorldObject instance.
    """
    return self._objects[obj_name]

  def add_character(self, character: 'GameCharacter') -> None:
    """
    Adds a character to the location.

    :param GameCharacter character: The Character to add.

    :raises CharacterAlreadyPresentError: If the character is already in the location.
    """
    if character in self._characters:
      raise CharacterAlreadyPresentError(f'Character "{character.name}" is already in "{self.name}"')

    character.current_location = self.name

    self.trigger('character_added', {'name': character.name, 'location': self.name})
    self._characters.append(character)

  def remove_character(self, character: 'GameCharacter') -> None:
    """
    Removes a character from the location.

    :param GameCharacter character: The Character to remove.

    :raises CharacterNotFoundError: If the character is not found in the location.
    """
    if character not in self._characters:
      raise CharacterNotFoundError(f'Character "{character.name}" is not in "{self.name}"')

    self.trigger('character_removed', {'name': character.name, 'location': self.name})
    self._characters.remove(character)

  def who_is_here(self) -> str:
    """
    Returns a string listing all characters currently in the location.

    :return: A comma-separated string of character names.
    """
    return ', '.join([character.name for character in self._characters])

  #################################################
  ################ Dunder Methods #################
  #################################################

  def __str__(self) -> str:
    return f'Location("{self.name}", backgrounds="{self.backgrounds}", objects="{self.objects}", is_indoor="{self.is_indoor}")'

  def __repr__(self) -> str:
    return self.__str__()
