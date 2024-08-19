from typing import Optional


class LocationBackground:
  def __init__(self, day: str, afternoon: str = None, night: str = None):
    self.day: str = day
    self.afternoon: str = afternoon if afternoon is not None else day
    self.night: str = night if night is not None else day

  def get_backgrounds(self) -> str:
    return (self.day, self.afternoon, self.night)

  def get_background(self, time: tuple[int, int]) -> str:
    hour, minute = time

    if 7 <= hour < 17:
      return self.day
    elif 17 <= hour < 19:
      return self.afternoon
    else:
      return self.night


class BasicLocation(LocationBackground):
  def __init__(self,
              name: str,
              background_day: str,
              background_afternoon: str = None,
              background_night: str = None):
    super().__init__(background_day, background_afternoon, background_night)

    self.name = name
    self.characters: list[str] = []
    self.sub_locations: list['BasicLocation'] = []
    self.parent_location: Optional['BasicLocation'] = None

  def add_character(self, character: str) -> None:
    self.characters.append(character)

  def remove_character(self, character: str) -> None:
    self.characters.remove(character)

  def add_sub_location(self, sub_location: 'BasicLocation') -> None:
    self.sub_locations.append(sub_location)

    sub_location.parent_location = self

  def add_sub_locations(self, sub_locations: list['BasicLocation']) -> None:
    self.sub_locations.extend(sub_locations)

    for sub_location in sub_locations:
      sub_location.parent_location = self

  def sub_locations_here(self) -> str:
    return [
      sb.name for sb in self.sub_locations
    ]

  def who_is_here(self) -> str:
    return ', '.join(self.characters)

  def __str__(self) -> str:
    sub_locations = '\n\t'.join(str(sl) for sl in self.sub_locations)
    return f"Location: {self.name}\nSub Locations: {sub_locations}\n"

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
  def __init__(self,
              name: str,
              background_day: str,
              background_afternoon: str = None,
              background_night: str = None):
    super().__init__(name, background_day, background_afternoon, background_night)


class Building(BasicLocation):
  def __init__(self,
              name: str,
              background_day: str,
              background_afternoon: str = None,
              background_night: str = None):
    super().__init__(name, background_day, background_afternoon, background_night)


class GenericConnection(BasicLocation):
  def __init__(self,
              name: str,
              background_day: str,
              background_afternoon: str = None,
              background_night: str = None):
    super().__init__(name, background_day, background_afternoon, background_night)


class Town(BasicLocation):
  def __init__(self, name: str):
    super().__init__(name, ' ')

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

  def get_location(self, location_name: str, location: BasicLocation | None = None) -> BasicLocation:
    if location is None:
      location = self

    if location.name == location_name:
      return location

    a = None

    for sub_location in location.sub_locations:
      a = self.get_location(location_name, sub_location)

      if a is not None:
        return a

  def get_characters(self, location: BasicLocation | None = None) -> list[str]:
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
