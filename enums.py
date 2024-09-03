from enum import Enum


class LocationType(Enum):
  """ Diferent types of locations that can be found in the world/schema. """
  Room = 'R'
  Corridor = 'C'
  Building = 'B'
  Street = 'S'
  World = 'W'

  @classmethod
  def list(cls) -> list[str]:
    return [e.value for e in cls if e != LocationType.World]
