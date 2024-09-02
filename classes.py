import math
import random
import time
from typing import Generator, Optional


class LocationBackground:
  def __init__(self, day: str, afternoon: str = None, night: str = None):
    self.day: str = day
    self.afternoon: str = afternoon if afternoon is not None else day
    self.night: str = night if night is not None else day

  def get_backgrounds(self) -> str:
    return (self.day, self.afternoon, self.night)

  def get_background(self, time: tuple[int, int]) -> str:
    hour, minute = time

    if 7 <= hour < 17:
      return self.day
    elif 17 <= hour < 19:
      return self.afternoon
    else:
      return self.night


class BasicLocation(LocationBackground):
  def __init__(self,
              name: str,
              background_day: str,
              background_afternoon: str = None,
              background_night: str = None):
    super().__init__(background_day, background_afternoon, background_night)

    self.name = name
    self.characters: list[str] = []
    self.sub_locations: list['BasicLocation'] = []
    self.parent_location: Optional['BasicLocation'] = None

  def add_character(self, character: str) -> None:
    self.characters.append(character)

  def remove_character(self, character: str) -> None:
    self.characters.remove(character)

  def add_sub_location(self, sub_location: 'BasicLocation') -> None:
    self.sub_locations.append(sub_location)

    sub_location.parent_location = self

  def add_sub_locations(self, sub_locations: list['BasicLocation']) -> None:
    self.sub_locations.extend(sub_locations)

    for sub_location in sub_locations:
      sub_location.parent_location = self

  def sub_locations_here(self) -> str:
    return [
      sb.name for sb in self.sub_locations
    ]

  def who_is_here(self) -> str:
    return ', '.join(self.characters)

  def __str__(self) -> str:
    sub_locations = '\n\t'.join(str(sl) for sl in self.sub_locations)
    return f"Location: {self.name}\nSub Locations: {sub_locations}\n"

  def __repr__(self) -> str:
    return self.name

  def __iter__(self):
    self._location_idx = 0
    return self

  def __next__(self):
    if len(self.sub_locations) == 0:
      raise StopIteration

    if self._location_idx >= len(self.sub_locations):
      raise StopIteration

    location = self.sub_locations[self._location_idx]
    self._location_idx += 1

    return location


class Room(BasicLocation):
  def __init__(self,
              name: str,
              background_day: str,
              background_afternoon: str = None,
              background_night: str = None):
    super().__init__(name, background_day, background_afternoon, background_night)


class Building(BasicLocation):
  def __init__(self,
              name: str,
              background_day: str,
              background_afternoon: str = None,
              background_night: str = None):
    super().__init__(name, background_day, background_afternoon, background_night)


class GenericConnection(BasicLocation):
  def __init__(self,
              name: str,
              background_day: str,
              background_afternoon: str = None,
              background_night: str = None):
    super().__init__(name, background_day, background_afternoon, background_night)


class Town(BasicLocation):
  def __init__(self, name: str):
    super().__init__(name, ' ')

  def _rec(self, loc: BasicLocation, character: str):
    if character in loc.characters:
      return f"{character} is in {loc.name}"

    a = None

    for sub_location in loc.sub_locations:
      a = self._rec(sub_location, character)

      if a is not None:
        return a

  def __str__(self) -> str:
    sub_locations = '\t\t'.join(str(sl) for sl in self.sub_locations)
    return f"Location: {self.name}\n\tSub Locations: {sub_locations}"

  def __repr__(self) -> str:
    return super().__str__()

  def get_location(self, location_name: str, location: BasicLocation | None = None) -> BasicLocation:
    if location is None:
      location = self

    if location.name == location_name:
      return location

    a = None

    for sub_location in location.sub_locations:
      a = self.get_location(location_name, sub_location)

      if a is not None:
        return a

  def get_characters(self, location: BasicLocation | None = None) -> list[str]:
    characters = {}

    if location is None:
      location = self

    if len(location.characters) > 0:
      characters[location.name] = location.characters

    for sub_location in location.sub_locations:
      characters.update(self.get_characters(sub_location))

    return characters

  def where_is(self, character: str) -> str:
    return self._rec(self, character)


class WorldWeather:
  def __init__(self) -> None:
    self.weather = {
        'Sunny': {'temperature': (25, 35), 'humidity': (10, 30), 'wind': (0, 10), 'clouds': (0, 20)},
        'Cloudy': {'temperature': (15, 25), 'humidity': (40, 60), 'wind': (5, 15), 'clouds': (60, 100)},
        'Rainy': {'temperature': (10, 20), 'humidity': (70, 90), 'wind': (10, 20), 'clouds': (80, 100)},
        'Stormy': {'temperature': (8, 18), 'humidity': (80, 100), 'wind': (20, 40), 'clouds': (90, 100)},
        'Snowy': {'temperature': (-5, 5), 'humidity': (60, 80), 'wind': (5, 15), 'clouds': (70, 100)}
    }

  def _interpolate(self, initial_value: float, final_value: float, step: int, max_steps: int) -> float:
    return initial_value + (final_value - initial_value) * (step / max_steps)

  def _generate_weather(self, weather) -> None:
    conditions = self.weather[weather]
    temperature = random.uniform(*conditions['temperature'])
    humidity = random.uniform(*conditions['humidity'])
    wind = random.uniform(*conditions['wind'])
    clouds = random.uniform(*conditions['clouds'])
    return {'weather': weather, 'temperature': temperature, 'humidity': humidity, 'wind': wind, 'clouds': clouds}

  def transition_weather(self, initial_conditions: dict, final_conditions: dict, duration_minutes: str):
    for hour in range(duration_minutes):
      temperature = self._interpolate(
          initial_conditions['temperature'], final_conditions['temperature'], hour, duration_minutes)
      humidity = self._interpolate(
          initial_conditions['humidity'], final_conditions['humidity'], hour, duration_minutes)
      wind = self._interpolate(
          initial_conditions['wind'], final_conditions['wind'], hour, duration_minutes)
      clouds = self._interpolate(
          initial_conditions['clouds'], final_conditions['clouds'], hour, duration_minutes)
      print(
          f"Hour {hour*2}: Weather: {final_conditions['weather']}, Temperature: {temperature:.2f}°C, Humidity: {humidity:.2f}%, Wind: {wind:.2f} km/h, Clouds: {clouds:.2f}%")

      yield {
          'weather': final_conditions['weather'],
          'temperature': temperature,
          'humidity': humidity,
          'wind': wind,
          'clouds': clouds
      }

  def simulate_weather_with_transitions(self, total_duration_minutes: int, last_weather: str = 'Sunny') -> Generator[str, None, None]:
    current_conditions = self._generate_weather(last_weather)
    remaining_minutes = total_duration_minutes

    while remaining_minutes > 0:
      # Define the duration of the next transition
      transition_duration = random.randint(30, 60)  # Example transition from 1 to 4 hours (30 to 240 minutes)

      # Choose the next weather
      new_weather = random.choice(list(self.weather.keys()))
      final_conditions = self._generate_weather(new_weather)

      # Perform the transition
      transition_gen = self.transition_weather(current_conditions, final_conditions, transition_duration)

      for transition in transition_gen:
        yield transition

      # Update for the next transition
      current_conditions = final_conditions
      remaining_minutes -= transition_duration


if __name__ == "__main__":
  world_weather = WorldWeather()
  gen = world_weather.simulate_weather_with_transitions(720)

  print(next(gen))
  print(next(gen))

  for _ in range(1000):
    print(next(gen))
