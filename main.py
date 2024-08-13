
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

  def _rec(self, location: BasicLocation, character: str):
    print(location.name, location.characters)
    if character in location.characters:
      return f"{character} is in {location.name}"

    a = None

    for sub_location in location.sub_locations:
      a = self._rec(sub_location, character)

      if a is not None:
        return a

  def get_location(self, location_name: str, location: BasicLocation = None) -> BasicLocation:
    if location is None:
      location = self

    print(location.name, location.characters)
    if location.name == location_name:
      return location

    a = None

    for sub_location in location.sub_locations:
      a = self.get_location(location_name, sub_location)

      if a is not None:
        return a

  def where_is(self, character: str) -> str:
    return self._rec(self, character)


if __name__ == "__main__":
  nexis = Town('Nexis (ネクシス)')

  school = Building("School", "bg school")

  main_entrance = Room("Main Entrance", "bg main_entrance")
  left_corridor = GenericConnection("Left Corridor", "bg left_corridor")
  right_corridor = GenericConnection("Right Corridor", "bg right_corridor")

  club_room = Room("Club Room", "bg club_day", "bg club_afternoon")
  classroom_2 = Room("Classroom 2", "bg class_room_day", "bg class_room_afternoon")
  classroom_3 = Room("Classroom 3", "bg class_room_day", "bg class_room_afternoon")

  closet = Room("Closet", "bg closet")

  classroom_2.add_sub_location(closet)

  left_corridor.add_sub_location(club_room)
  left_corridor.add_sub_location(classroom_2)
  left_corridor.add_sub_location(classroom_3)

  man_bathroom = Room("Man Bathroom", "bg man_bathroom")
  woman_bathroom = Room("Woman Bathroom", "bg woman_bathroom")

  right_corridor.add_sub_location(man_bathroom)
  right_corridor.add_sub_location(woman_bathroom)

  main_entrance.add_sub_location(left_corridor)
  main_entrance.add_sub_location(right_corridor)

  nexis.add_sub_location(school)

  nexis.get_location('Club Room').add_character('Monika')

  print(nexis.where_is("Monika"))

  current_location = club_room
  while True:
    someone = f', aquí se encuentra {current_location.who_is_here()}' if len(
      current_location.characters) > 0 else ', aquí no hay nadie'

    print(current_location.choices)

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
