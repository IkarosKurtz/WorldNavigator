import json as JSON
from typing import Union

from worldnavigator.core.world import World
from worldnavigator.locations.base_location import Location
from worldnavigator.types.typed_dicts import LocationDict
from worldnavigator.errors import NoLocationsFoundError


class WorldParser:
  """
  A utility class for parsing different world data formats and creating World objects.

  This class provides static methods to parse world data from different file formats
  and create a fully connected World object with properly configured Location objects.

  Currently supported formats:
    - **SceneGraph**: A JSON format with locations and connections between them
    - **WorldNest**: (In development) An alternative world description format
  """

  @classmethod
  def scene_graph_parser(cls, json: Union[dict, str]) -> World:
    """
    Parse a JSON with SceneGraph format.

    :param Union[dict, str] json: The JSON string to parse or the path to the JSON file.
    """
    if isinstance(json, str):
      with open(json, 'r', encoding='utf-8') as f:
        json = JSON.load(f)

    locations: list[LocationDict] = json.get('locations', [])
    if len(locations) == 0:
      raise NoLocationsFoundError('No locations found in the provided world data')

    world_name = json.get('name', 'World')

    world = World(name=world_name)

    # First we create all the locations
    for location in locations:
      new_location = Location(
        name=location.get('name', 'Unknown'),
        backgrounds=location.get('backgrounds', {}),
        objects=location.get('objects', {}),
        is_indoor=location.get('is_indoor', False)
      )

      world.add_location(new_location)

    # Then we connect all the locations
    for location in locations:
      location_name = location.get('name', 'Unknown')
      location_object = world.get_location(location_name)

      connected_locations = location.get('connected_locations', [])

      for connected_location in connected_locations:
        if isinstance(connected_location, dict):
          target_name = connected_location.get('name')
          one_way = connected_location.get('one_way', False)
        else:
          target_name = connected_location
          one_way = False

        connected_location_object = world.get_location(target_name)
        location_object.connect_with(connected_location_object)

        if not one_way:
          connected_location_object.connect_with(location_object)

    return world

  @classmethod
  def world_nest_parser(cls, json: Union[dict, str]):
    """
    Parse a JSON with WorldNest format.

    :param Union[dict, str] json: The JSON string to parse or the path to the JSON file.
    """
    pass
