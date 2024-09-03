import random
from typing import Generator


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
