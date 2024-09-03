from enum import Enum


class LocationType(Enum):
  Room = 'R'
  Corridor = 'C'
  Building = 'B'
  Street = 'S'
  World = 'W'

  @classmethod
  def list(cls) -> list[str]:
    return [e.value for e in cls if e != LocationType.World]
