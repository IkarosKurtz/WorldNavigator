from worldnavigator.observer import Observer
from worldnavigator.typed_dicts import BackgroundsDict


class LocationBackground:
  """ 
  Base clase for all backgrounds and their management.
  For now it only accepts day, afternoon and night backgrounds, but I planing to add more or even add custom backgrounds.
  """

  def __init__(self, backgrounds: BackgroundsDict):
    day_background = backgrounds.get('day', None)
    if day_background is None:
      raise ValueError('Day background is required')

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
    return self._day

  @property
  def afternoon(self) -> str:
    return self._afternoon

  @property
  def night(self) -> str:
    return self._night

  #################################################
  ################ Public Methods #################
  #################################################

  def get_backgrounds(self) -> str:
    return (self.day, self.afternoon, self.night)

  def retrieve_scene_background(self, time: tuple[int, int]) -> str:
    hour, minute = time

    if 7 <= hour < 17:
      return self.day
    elif 17 <= hour < 19:
      return self.afternoon
    else:
      return self.night


class Location(Observer):
  """
  A location from the world, it can be any kind of location.
  """

  def __init__(self,
               *,
               name: str,
               backgrounds: BackgroundsDict,
               objects: list = None,
               is_indoor: bool = False):
    super().__init__()
    self._name = name
    self._backgrounds = LocationBackground(backgrounds)
    self._objects = objects if objects is not None else []
    self._is_indoor = is_indoor

    self._connections: dict[str, 'Location'] = {}
    self._characters: list[str] = []

  def __str__(self) -> str:
    return f'Location({self.name}, backgrounds={self.backgrounds}, objects={self.objects}, is_indoor={self.is_indoor})'

  def __repr__(self) -> str:
    return self.__str__()

  #################################################
  ################### Properties ##################
  #################################################

  @property
  def name(self) -> str:
    return self._name

  @property
  def backgrounds(self) -> LocationBackground:
    return self._backgrounds

  @property
  def objects(self) -> list:
    return self._objects

  @property
  def is_indoor(self) -> bool:
    return self._is_indoor

  @property
  def connections(self) -> dict[str, 'Location']:
    return self._connections

  @property
  def characters(self) -> list[str]:
    return self._characters

  #################################################
  ################ Public Methods #################
  #################################################

  def get_location(self, location_name: str) -> 'Location':
    if location_name not in self._connections:
      raise ValueError(f"Location {location_name} does not exist")

    return self._connections[location_name]

  def get_locations(self) -> list['Location']:
    return list(self._connections.values())

  def connect_with(self, other_location: 'Location') -> None:
    if other_location.name in self.connections:
      raise ValueError(f"Location {other_location.name} is already connected to {self.name}")

    self._connections[other_location.name] = other_location

  def disconnect_from(self, other_location: 'Location') -> None:
    if other_location.name not in self.connections:
      raise ValueError(f"Location {other_location.name} is not connected to {self.name}")

    self.connections.pop(other_location.name)

  def add_object(self, obj: str):
    self._objects.append(obj)

  def remove_object(self, obj: str):
    self._objects.remove(obj)

  def add_character(self, character: str) -> None:
    if character in self._characters:
      raise ValueError(f'Character {character} is already in {self.name}')

    self.trigger('character_added', {'name': character, 'location': self.name})
    self._characters.append(character)

  def remove_character(self, character: str) -> None:
    if character not in self._characters:
      raise ValueError(f'Character {character} is not in {self.name}')

    self.trigger('character_removed', {'name': character, 'location': self.name})
    self._characters.remove(character)

  def who_is_here(self) -> str:
    return ', '.join(self._characters)
