import json
from classes import BasicLocation, Corridor, Room, Street, Building, LocationType, World


class WorldParser:
  def __init__(self) -> None:
    self._types = {
      "B": Building,
      "R": Room,
      "S": Street,
      "C": Corridor,
    }

  def _get_class(self, type: str):
    return self._types[type]

  def unpack(self, path: str) -> World:
    with open(path, 'r', encoding='utf-8') as f:
      json_name = f.name
      data: dict[str, dict] = json.load(f)

    world_name = json_name.split('.')[0]

    world = World(world_name)

    for i in LocationType.list():
      world.loc_categories[i] = []

    def wrapper(data: dict[str, dict]):
      locations = []

      for key, value in data.items():
        if key.count('-') != 1:
          continue

        location_type, location_name = key.split('-')

        if location_type not in LocationType.list():
          raise ValueError(f"Unknown location type: {location_type}")

        day_bg = value.get('day', None)

        if day_bg is None:
          raise ValueError(f"Missing day background for {key}")

        afternoon_bg = value.get('afternoon', day_bg)

        night_bg = value.get('night', day_bg)

        location_cls = self._get_class(location_type)

        location: BasicLocation = location_cls(location_name, day_bg, afternoon_bg, night_bg)

        world.loc_categories[location.type.value].append(location)

        if (referencial_links := value.get('to', None)) is not None:
          location._referencial_link = referencial_links

        sub_locations = wrapper(value)

        if sub_locations is None:
          continue

        location.add_sub_locations(sub_locations)
        locations.append(location)

      return locations

    world.add_sub_locations(wrapper(data))

    def link_references(location: BasicLocation):
      if location._referencial_link is not None:
        for referencial_link in location._referencial_link:
          if referencial_link.count('-') != 1:
            raise ValueError(f"Invalid referencial link: {referencial_link}")

          location_type, location_name = referencial_link.split('-')

          if location_type not in LocationType.list():
            raise ValueError(f"Unknown location type: {location_type}")

          referenced_location = world.get_location(location_name, location_type)

          if referenced_location is None:
            raise ValueError(f"Referenced location not found: {referencial_link}")

          location.add_referenced_sub_location(referenced_location)

      for sub_location in location.sub_locations:
        link_references(sub_location)

    link_references(world)

    return world


if __name__ == "__main__":
  parser = WorldParser()
  world = parser.unpack('nexis.json')

  def wrap(cls: BasicLocation):
    for location in cls.sub_locations:
      if len(location.sub_locations) > 0:
        wrap(location)

      print(location.name)

  wrap(world)

  print(world.get_location('School', 'B').sub_locations_here())
  # print(world.loc_categories)
  # school = world.get_location('School')
  # print(school.sub_locations_here())
  # print(parser.get_locations(world))
