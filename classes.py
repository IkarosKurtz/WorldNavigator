from enums import LocationType
from typing import Optional


class LocationBackground:
  """ 
  Base clase for all backgrounds and their management.
  For now it only accepts day, afternoon and night backgrounds, but I planing to add more or even add custom backgrounds.
  """

  def __init__(self, day: str, afternoon: Optional[str] = None, night: Optional[str] = None):
    self.day: str = day
    self.afternoon: str = afternoon if afternoon is not None else day
    self.night: str = night if night is not None else day

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


class BasicLocation(LocationBackground):
  """
  Basic class for all locations, this class manage their basic methods and properties.
  """

  def __init__(self,
              name: str,
              background_day: str,
              background_afternoon: Optional[str] = None,
              background_night: Optional[str] = None):
    super().__init__(background_day, background_afternoon, background_night)
    self.name = name
    self.is_indoor: bool = False
    self.type: Optional[LocationType] = None

    self.parent_location: Optional['BasicLocation'] = None
    self._referencial_link: Optional[str] = None

    self.characters: list[str] = []
    self.sub_locations: list['BasicLocation'] = []
    self.referenced_locations: list['BasicLocation'] = []

  def add_character(self, character: str) -> None:
    self.characters.append(character)

  def remove_character(self, character: str) -> None:
    self.characters.remove(character)

  def add_sub_location(self, sub_location: 'BasicLocation') -> None:
    self.sub_locations.append(sub_location)

    sub_location.parent_location = self

  def add_referenced_sub_location(self, sub_location: 'BasicLocation') -> None:
    self.referenced_locations.append(sub_location)

  def add_sub_locations(self, sub_locations: list['BasicLocation']) -> None:
    self.sub_locations.extend(sub_locations)

    for sub_location in sub_locations:
      sub_location.parent_location = self

  def sub_locations_here(self) -> str:
    return [
      sb.name for sb in self.referenced_locations + self.sub_locations
    ]

  def who_is_here(self) -> str:
    return ', '.join(self.characters)

  def all_sub_locations(self) -> list['BasicLocation']:
    return self.referenced_locations + self.sub_locations

  def __str__(self) -> str:
    parent_name = self.parent_location.name if self.parent_location is not None else 'None'
    return f"Location({self.name}, type={self.type.value}, parent={parent_name}, no_sub_locations={len(self.sub_locations)})"

  def __repr__(self) -> str:
    return self.name

  def __iter__(self):
    self._location_idx = 0
    return self

  def __next__(self):
    if len(self.sub_locations) == 0:
      raise StopIteration

    if self._location_idx >= len(self.sub_locations):
      raise StopIteration

    location = self.sub_locations[self._location_idx]
    self._location_idx += 1

    return location


class Room(BasicLocation):
  """ Just a Room class, is intended to be used inside a Building """

  def __init__(self,
              name: str,
              background_day: str,
              background_afternoon: Optional[str] = None,
              background_night: Optional[str] = None):
    super().__init__(name, background_day, background_afternoon, background_night)
    self.is_indoor = True
    self.type = LocationType.Room


class Building(BasicLocation):
  """ Just a Building class, is intended to see the outside of a Building, not inside """

  def __init__(self,
              name: str,
              background_day: str,
              background_afternoon: Optional[str] = None,
              background_night: Optional[str] = None):
    super().__init__(name, background_day, background_afternoon, background_night)
    self.type = LocationType.Building


class Street(BasicLocation):
  """ Just a Street class, is intended to be used as a conection between Buildings and more Streets """

  def __init__(self,
              name: str,
              background_day: str,
              background_afternoon: Optional[str] = None,
              background_night: Optional[str] = None):
    super().__init__(name, background_day, background_afternoon, background_night)
    self.type = LocationType.Street


class Corridor(BasicLocation):
  """ Just a Corridor class, is intended to be used as a conection between Rooms and more Corridors """

  def __init__(self,
              name: str,
              background_day: str,
              background_afternoon: Optional[str] = None,
              background_night: Optional[str] = None):
    super().__init__(name, background_day, background_afternoon, background_night)
    self.is_indoor = True
    self.type = LocationType.Corridor


class World(BasicLocation):
  """
  This class is where all the locations are stored, you can get a location and where is some character.
  You can't actually be in this location, for obvious reasons.
  """

  def __init__(self, name: str):
    super().__init__(name, ' ')
    self.type = LocationType.World
    self.loc_categories = {}
    self.all_locations: list[BasicLocation] = []

  def _rec(self, loc: BasicLocation, character: str):
    if character in loc.characters:
      return f"{character} is in {loc.name}"

    a = None

    for sub_location in loc.sub_locations:
      a = self._rec(sub_location, character)

      if a is not None:
        return a

  def __str__(self) -> str:
    sub_locations = '\t\t'.join(str(sl) for sl in self.sub_locations)
    return f"Location: {self.name}\n\tSub Locations: {sub_locations}"

  def __repr__(self) -> str:
    return super().__str__()

  def get_location(self, location_name: str, location_type: str, location: Optional[BasicLocation] = None) -> Optional[BasicLocation]:
    search_list = self.loc_categories.get(location_type, [])

    if len(search_list) == 0:
      return None

    for location in search_list:
      if location.name == location_name:
        return location

  def get_location_by_name(self, location_name: str) -> BasicLocation | None:
    for location in self.all_locations:
      if location.name == location_name:
        return location

  def get_characters(self, location: Optional[BasicLocation] = None) -> list[str]:
    characters = {}

    if location is None:
      location = self

    if len(location.characters) > 0:
      characters[location.name] = location.characters

    for sub_location in location.sub_locations:
      characters.update(self.get_characters(sub_location))

    return characters

  def where_is(self, character: str) -> str:
    return self._rec(self, character)
