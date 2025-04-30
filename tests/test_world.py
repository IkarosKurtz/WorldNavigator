from rich.console import Console
from rich.pretty import pprint

from worldnavigator.core import WorldParser

console = Console()


def test_world_parser():
  """Test the WorldParser functionality."""
  worldparser = WorldParser()
  world = worldparser.scene_graph_parser('../nexis.world.json')

  corridor = world.get_location('Left Corridor')
  corridor.add_character('Monika')
  pprint(corridor)

  return world


if __name__ == "__main__":
  test_world_parser()
