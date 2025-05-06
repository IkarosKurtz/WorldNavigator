from typing import TypedDict


class BackgroundsDict(TypedDict):
  day: str
  night: str
  afternoon: str


class LocationDict(TypedDict):
  name: str
  is_indoor: bool
  backgrounds: BackgroundsDict
  connected_locations: list[str]


class WorldDict(TypedDict):
  locations: list[LocationDict]
