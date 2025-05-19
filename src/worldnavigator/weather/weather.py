import random
from typing import Callable, Dict, Iterator

from worldnavigator.types import WeatherConditionsDict, GeneratedWeatherDict, Weather


class WorldWeather:
  """
  Manages and simulates weather conditions and transitions within the world.

  This class simulates weather patterns over time, including transitions between
  different weather states like Sunny, Cloudy, Rainy, Stormy, and Snowy.

  The simulation proceeds in steps, generating a list of weather conditions for each hour
  over a specified total duration.
  """

  def __init__(self) -> None:
    self._weather: Dict[Weather, WeatherConditionsDict] = {
        'Sunny': {'temperature': (25, 35), 'humidity': (10, 30), 'wind': (0, 10), 'clouds': (0, 20)},
        'Cloudy': {'temperature': (15, 25), 'humidity': (40, 60), 'wind': (5, 15), 'clouds': (60, 100)},
        'Rainy': {'temperature': (10, 20), 'humidity': (70, 90), 'wind': (10, 20), 'clouds': (80, 100)},
        'Stormy': {'temperature': (8, 18), 'humidity': (80, 100), 'wind': (20, 40), 'clouds': (90, 100)},
        'Snowy': {'temperature': (-5, 5), 'humidity': (60, 80), 'wind': (5, 15), 'clouds': (70, 100)}
    }

    self._posible_transitions: Dict[Weather, Callable[[], str]] = {
        'Sunny': lambda: random.choice(['Cloudy', 'Rainy']),
        'Cloudy': lambda: random.choice(['Sunny', 'Rainy', 'Stormy', 'Snowy']),
        'Rainy': lambda: random.choice(['Cloudy', 'Stormy']),
        'Stormy': lambda: random.choice(['Rainy', 'Cloudy']),
        'Snowy': lambda: random.choice(['Cloudy'])
      }

  #################################################
  ################ Private Methods ################
  #################################################

  def _interpolate(self, initial_value: float, final_value: float, step: int, max_steps: int) -> float:
    """
    Interpolates between two values based on the current step and total steps.

    :param float initial_value: The starting value for interpolation.
    :param float final_value: The ending value for interpolation.
    :param int step: The current step in the interpolation process.
    :param int max_steps: The total number of steps for interpolation.

    :return: The interpolated value.
    """
    return initial_value + (final_value - initial_value) * (step / max_steps)

  def _generate_weather(self, weather: Weather) -> GeneratedWeatherDict:
    """
    Generates random weather conditions based on the specified weather state.

    :param Weather weather: The weather state for which to generate conditions.

    :return: A dictionary containing the weather state and its associated conditions.
    """
    conditions = self._weather[weather]
    temperature = random.uniform(*conditions['temperature'])
    humidity = random.uniform(*conditions['humidity'])
    wind = random.uniform(*conditions['wind'])
    clouds = random.uniform(*conditions['clouds'])
    return {'weather': weather, 'temperature': temperature, 'humidity': humidity, 'wind': wind, 'clouds': clouds}

  def _transition_weather(self, initial_conditions: GeneratedWeatherDict, final_conditions: GeneratedWeatherDict, duration_period: int) -> list[GeneratedWeatherDict]:
    """
    Generates a list of weather conditions during a transition period.

    :param GeneratedWeatherDict initial_conditions: The initial weather conditions.
    :param GeneratedWeatherDict final_conditions: The final weather conditions after the transition.
    :param int duration_period: The duration of the transition in hours.

    :return: A list of dictionaries representing the weather conditions for each hour during the transition.
    """
    steps = []
    for hour in range(1, duration_period + 1):
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
        'temperature': temperature,
        'humidity': humidity,
        'wind': wind,
        'clouds': clouds
      })

    return steps

  #################################################
  ################ Public Methods #################
  #################################################

  def simulate_weather_with_transitions(self, total_duration: int, last_weather: Weather = 'Sunny') -> list[GeneratedWeatherDict]:
    """
    Simulates weather over a specified duration with transitions between states.

    Generates a list of hourly weather data points, simulating transitions
    between different weather states randomly chosen from allowed possibilities.

    :param int total_duration: The total number of hours to simulate.
    :param Weather last_weather: The initial weather state to start the simulation from. Defaults to 'Sunny'.

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
      new_weather = self._posible_transitions[current_weather]()
      final_conditions = self._generate_weather(new_weather)

      # Perform the transition
      transition_gen = self._transition_weather(current_conditions, final_conditions, transition_duration)

      timestamps.extend(transition_gen)

      # Update for the next transition
      current_conditions = final_conditions
      remaining_period -= transition_duration
      current_weather = new_weather

    return timestamps

  def start(self) -> Iterator[GeneratedWeatherDict]:
    """
    Starts the continuous weather simulation as a generator.

    This method will yield the weather conditions for each hour continuously
    without needing to call the simulation function repeatedly.

    :return: An iterator that yields the weather conditions for each hour.
    """
    current_conditions = self._generate_weather('Sunny')
    current_weather: Weather = 'Sunny'

    while True:  # Loop indefinitely until stopped externally
      # Define the duration of the next transition
      transition_duration = random.randint(2, 6)

      # Choose the next weather
      new_weather = self._posible_transitions[current_weather]()
      final_conditions = self._generate_weather(new_weather)

      # Perform the transition
      transition_gen = self._transition_weather(current_conditions, final_conditions, transition_duration)

      for step in transition_gen:
        yield step  # Yield each step of the transition

      # Update for the next transition
      current_conditions = final_conditions
      current_weather = new_weather
