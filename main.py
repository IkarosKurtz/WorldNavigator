
from typing import Optional
import json


class BasicLocation:
  def __init__(self, name: str, background_day: str = None, background_night: str = None):
    self.name = name
    self.characters: list[str] = []
    self.sub_locations: list['BasicLocation'] = []
    self.parent_location: Optional['BasicLocation'] = None

    self.background_day: Optional[str] = background_day
    self.background_night: Optional[str] = background_night

  def add_character(self, character: str) -> None:
    self.characters.append(character)

  def remove_character(self, character: str) -> None:
    self.characters.remove(character)

  def add_sub_location(self, sub_location: 'BasicLocation') -> None:
    self.sub_locations.append(sub_location)
    sub_location.parent_location = self

  def sub_locations_here(self) -> str:
    return [
      sb.name for sb in self.sub_locations
    ]

  def who_is_here(self) -> str:
    return 'Characters: \n' + '\n'.join(self.characters)

  def __str__(self) -> str:
    return f"Location: {self.name}\n{self.who_is_here()}"


class Room(BasicLocation):
  def __init__(self, name: str, background_day: str = None, background_night: str = None):
    super().__init__(name, background_day, background_night)


class Building(BasicLocation):
  def __init__(self, name: str, background_day: str = None, background_night: str = None):
    super().__init__(name, background_day, background_night)

  def rooms_here(self) -> str:
    return 'Rooms: \n' + '\n'.join([room.name for room in self.sub_locations])


class GenericConnection(BasicLocation):
  def __init__(self, name: str, background_day: str = None, background_night: str = None):
    super().__init__(name, background_day, background_night)


class GenericStuff:
  def __init__(self, name: str):
    self.name = name

  def __str__(self):
    return self.name


class Town(BasicLocation):
  def __init__(self, name: str):
    super().__init__(name)

  def buildings_here(self) -> str:
    return 'Buildings: \n' + '\n'.join([building.name for building in self.sub_locations])

  def where_is(self, character: str) -> str:
    for building in self.sub_locations:
      if character in building.characters:
        return f"{character} is in {building.name}"
      for room in building.sub_locations:
        if character in room.characters:
          return f"{character} is in {room.name}"

    return f"{character} is not in any building"


if __name__ == "__main__":
  nexuz = Town("Nexuz")
  building1 = Building("Building 1")

  bedroom = Room("Bedroom")

  bed = GenericStuff("Bed")
  dresser = GenericStuff("Dresser")

  kitchen = Room("Kitchen")

  fridge = GenericStuff("Fridge")
  stove = GenericStuff("Stove")
  sink = GenericStuff("Sink")

  building1.add_sub_location(bedroom)
  building1.add_sub_location(kitchen)

  bedroom.add_sub_location(bed)
  bedroom.add_sub_location(dresser)

  kitchen.add_sub_location(fridge)
  kitchen.add_sub_location(stove)
  kitchen.add_sub_location(sink)

  building2 = Building("Building 2")

  office = Room("Office")

  desk = GenericStuff("Desk")

  office.add_sub_location(desk)

  office.add_character("John")

  bathroom = Room("Bathroom")

  toilet = GenericStuff("Toilet")
  sink = GenericStuff("Sink")
  shower = GenericStuff("Shower")

  bathroom.add_sub_location(toilet)
  bathroom.add_sub_location(sink)
  bathroom.add_sub_location(shower)

  nexuz.add_sub_location(building1)
  nexuz.add_sub_location(building2)

  print(nexuz.buildings_here())
  print(nexuz.where_is("John"))
