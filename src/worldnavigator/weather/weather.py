import random


class WorldWeather:
  """
  Manages and simulates weather conditions and transitions within the world.

  This class simulates weather patterns over time, including transitions between
  different weather states like Sunny, Cloudy, Rainy, Stormy, and Snowy.

  The simulation proceeds in steps, generating a list of weather conditions for each hour
  over a specified total duration.
  """

  def __init__(self) -> None:
    self.weather = {
        'Sunny': {'temperature': (25, 35), 'humidity': (10, 30), 'wind': (0, 10), 'clouds': (0, 20)},
        'Cloudy': {'temperature': (15, 25), 'humidity': (40, 60), 'wind': (5, 15), 'clouds': (60, 100)},
        'Rainy': {'temperature': (10, 20), 'humidity': (70, 90), 'wind': (10, 20), 'clouds': (80, 100)},
        'Stormy': {'temperature': (8, 18), 'humidity': (80, 100), 'wind': (20, 40), 'clouds': (90, 100)},
        'Snowy': {'temperature': (-5, 5), 'humidity': (60, 80), 'wind': (5, 15), 'clouds': (70, 100)}
    }

    self.posible_transitions = {
        'Sunny': ['Cloudy', 'Rainy'],
        'Cloudy': ['Sunny', 'Rainy', 'Stormy', 'Snowy'],
        'Rainy': ['Cloudy', 'Stormy'],
        'Stormy': ['Rainy', 'Cloudy'],
        'Snowy': ['Cloudy']
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

  def _transition_weather(self, initial_conditions: dict, final_conditions: dict, duration_period: str):
    steps = []
    for hour in range(duration_period):
      temperature = self._interpolate(
          initial_conditions['temperature'], final_conditions['temperature'], hour, duration_period)
      humidity = self._interpolate(
          initial_conditions['humidity'], final_conditions['humidity'], hour, duration_period)
      wind = self._interpolate(
          initial_conditions['wind'], final_conditions['wind'], hour, duration_period)
      clouds = self._interpolate(
          initial_conditions['clouds'], final_conditions['clouds'], hour, duration_period)

      steps.append({
        'weather': final_conditions['weather'],
        'data': {
          'temperature': temperature,
          'humidity': humidity,
          'wind': wind,
          'clouds': clouds
        }
      })

    return steps

  def simulate_weather_with_transitions(self, total_duration: int, last_weather: str = 'Sunny') -> list[dict[str, dict]]:
    """
    Simulates weather over a specified duration with transitions between states.

    Generates a list of hourly weather data points, simulating transitions
    between different weather states randomly chosen from allowed possibilities.

    :param total_duration: The total number of hours to simulate.
    :param last_weather: The initial weather state to start the simulation from. Defaults to 'Sunny'.
    :return: A list of dictionaries, where each dictionary represents the weather 
             conditions for one hour. Each dictionary contains the 'weather' state 
             (e.g., 'Cloudy') and a 'data' dictionary with 'temperature', 'humidity', 
             'wind', and 'clouds' values for that hour.
    """
    current_conditions = self._generate_weather(last_weather)
    remaining_period = total_duration
    current_weather = last_weather

    timestamps = []

    while remaining_period > 0:
      # Define the duration of the next transition
      transition_duration = random.randint(2, 6)

      if (remaining_period - transition_duration) < 0:
        transition_duration = remaining_period

      # Choose the next weather
      new_weather = random.choice(self.posible_transitions[current_weather])
      final_conditions = self._generate_weather(new_weather)

      # Perform the transition
      transition_gen = self._transition_weather(current_conditions, final_conditions, transition_duration)

      timestamps.extend(transition_gen)

      # Update for the next transition
      current_conditions = final_conditions
      remaining_period -= transition_duration
      current_weather = new_weather

    return timestamps
