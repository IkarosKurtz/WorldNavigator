import json
from classes import BasicLocation, Corridor, Room, Street, Town, Building, LocationType


class WorldParser:
  def __init__(self, path: str) -> None:
    self._path = path

    self._types = {
      "T": Town,
      "B": Building,
      "R": Room,
      "S": Street,
      "C": Corridor,
    }

  def _get_class(self, type: str):
    if type in self._types:
      return self._types[type]

    raise ValueError(f"Unknown type: {type}")

  def get_locations(self, location: BasicLocation) -> list[BasicLocation]:
    locations = []

    for sbl in location:
      if len(sbl.sub_locations) > 0:
        locations.extend(self.get_locations(sbl))

      locations.append(sbl)

    return locations

  def unpack(self) -> Town:
    with open(self._path, 'r', encoding='utf-8') as f:
      data: dict[str, dict] = json.load(f)

    loc_categories = {
      key: []
      for key in LocationType.list()
    }

    def link_references(t: Town):
      all_locations = [s for s in self.get_locations(t) if s._to is not None]
      print(all_locations)

      for loc in all_locations:
        for to in loc._to:
          clean_to = to.split('-')[1]
          sub_loc = t.get_location(clean_to)
          print(f'Linking {loc.name} to {sub_loc.name}')

          loc.add_sub_location(sub_loc)

    def wrapper(data: dict[str, dict]):
      locations = []
      for key, value in data.items():
        if any(key.startswith(t) for t in self._types):

          if (day := value.get('day', None)) is None:
            raise ValueError(f"Missing day background for {key}")

          day = value['day']
          afternoon = value.get('afternoon', day)
          night = value.get('night', day)

          type, name = key.split('-')
          location = self._get_class(type)(name, day, afternoon, night)

          loc_categories[location.type.value].append(location)

          if (to := value.get('to', None)) is not None:
            location._to = to

          more = wrapper(value)

          if more is not None:
            location.add_sub_locations(more)

            locations.append(location)

        continue

      return locations

    town = None
    for key, value in data.items():
      if key.startswith("T"):
        town = Town(key.split('-')[1])

      town.add_sub_locations(wrapper(value))
      town.loc_categories = loc_categories

      link_references(town)

      return town


if __name__ == "__main__":
  parser = WorldParser("schema.json")
  world = parser.unpack()

  # for location in world:
  # print(location.name)
  # print(world.loc_categories)
  # print(parser.get_locations(world))
  school = world.get_location('School')
  print(school.sub_locations_here())
