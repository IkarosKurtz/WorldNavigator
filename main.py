
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
    return ', '.join(self.characters)

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


class GenericStuff(BasicLocation):
  def __init__(self, name: str):
    super().__init__(name)
    self.name = name

  def __str__(self):
    return self.name


class Town(BasicLocation):
  def __init__(self, name: str):
    super().__init__(name)

  def buildings_here(self) -> str:
    return 'Buildings: \n' + '\n'.join([building.name for building in self.sub_locations])

  def _rec(self, location: BasicLocation, character: str):
    print(location.name, location.characters)
    if character in location.characters:
      return f"{character} is in {location.name}"

    a = None

    if location.sub_locations is None:
      return None

    for sub_location in location.sub_locations:
      a = self._rec(sub_location, character)

      if a is not None:
        return a

  def where_is(self, character: str) -> str:
    return self._rec(self, character)


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

  building2.add_sub_location(office)
  building2.add_sub_location(bathroom)

  nexuz.add_sub_location(building1)
  nexuz.add_sub_location(building2)

  current_location = nexuz
  while True:
    someone = f', aquí se encuentra {current_location.who_is_here()}' if len(
      current_location.characters) > 0 else ', aquí no hay nadie'

    print(current_location.sub_locations_here())

    print(f'Estas en {current_location.name} {someone}')
    print('Puedes ir a: ')
    for i, sub_location in enumerate(current_location.sub_locations):
      print(f'{i + 1}. {sub_location.name}')

    if current_location.parent_location is not None:
      print('0. Regresar')

    to = input('> ')

    try:
      to = int(to) - 1

      print(to)

      if to == -1:
        current_location = current_location.parent_location
        continue

      current_location = current_location.sub_locations[to]
    except:
      continue
