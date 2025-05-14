from typing import TypedDict
from worldnavigator.types.types import Weather


class BackgroundsDict(TypedDict):
  """
  Dictionary containing backgrounds for different times of the day.
  """
  day: str
  night: str
  afternoon: str


class LocationDict(TypedDict):
  """
  Dictionary representing a location with its name and characteristics.
  """
  name: str
  is_indoor: bool
  backgrounds: BackgroundsDict
  connected_locations: list[str]


class WorldDict(TypedDict):
  """
  Dictionary containing a list of locations in the world.
  """
  locations: list[LocationDict]


class WeatherConditionsDict(TypedDict):
  """
  Dictionary representing weather conditions.
  """
  temperature: tuple[int, int]
  humidity: tuple[int, int]
  wind: tuple[int, int]
  clouds: tuple[int, int]


class GeneratedWeatherDict(TypedDict):
  """
  Dictionary representing generated weather with its parameters.
  """
  weather: Weather
  temperature: int
  humidity: int
  wind: int
  clouds: int
