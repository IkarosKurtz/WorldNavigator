import random
from typing import Callable, Dict

from worldnavigator.types.typed_dicts import WeatherConditionsDict, GeneratedWeatherDict
from worldnavigator.types.types import Weather


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
      'Sunny': ['Cloudy', 'Rainy'],
      'Cloudy': ['Sunny', 'Rainy', 'Stormy', 'Snowy'],
      'Rainy': ['Cloudy', 'Stormy'],
      'Stormy': ['Rainy', 'Cloudy'],
      'Snowy': ['Cloudy'],
    }

    self._current_weather: GeneratedWeatherDict = {}
    self._weather_steps: list[GeneratedWeatherDict] = []

    self._thunder_prob = 0.125
    self._weather_change_listener: Callable[[GeneratedWeatherDict, list[GeneratedWeatherDict]], None] = None
    self._thunder_listener: Callable[[], None] = None

  #################################################
  ################### Properties ##################
  #################################################

  @property
  def current_weather(self) -> GeneratedWeatherDict:
    """
    Get the current weather.
    """
    return self._current_weather

  @property
  def weather_steps(self) -> list[GeneratedWeatherDict]:
    """
    Get the weather steps remaining to be processed.
    """
    return self._weather_steps

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

  def listen_for_weather_change(self, callback: Callable[[GeneratedWeatherDict, list[GeneratedWeatherDict]], None]) -> None:
    """
    Listen for the weather change, and call the callback with the current weather and the weather steps.

    :param Callable[[GeneratedWeatherDict, list[GeneratedWeatherDict]], None] callback: The callback to call with the current weather and the weather steps.
    """
    self._weather_change_listener = callback

  def listen_for_thunder(self, callback: Callable[[], None]) -> None:
    """
    Listen for the thunder, and call the callback.

    :param Callable[[], None] callback: The callback to call when thunder is thrown.
    """
    self._thunder_listener = callback

  def simulate_weather_with_transitions(self, total_duration: int, last_weather: Weather = 'Sunny') -> list[GeneratedWeatherDict]:
    """
    Simulates weather over a specified duration with transitions between states.

    Generates a list of hourly weather data points, simulating transitions
    between different weather states randomly chosen from allowed possibilities.

    :param int total_duration: The total number of hours to simulate.
    :param Weather last_weather: The initial weather state to start the simulation from. Defaults to ``Sunny``.

    :return: A list of dictionaries, where each dictionary represents the weather 
             conditions for one hour. Each dictionary contains the ``weather`` state 
             (e.g., ``Cloudy``) and a ``data`` dictionary with ``temperature``, ``humidity``, 
             ``wind``, and ``clouds`` values for that hour.
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
      new_weather = random.choice(self._posible_transitions[current_weather])
      final_conditions = self._generate_weather(new_weather)

      # Perform the transition
      transition_gen = self._transition_weather(current_conditions, final_conditions, transition_duration)

      timestamps.extend(transition_gen)

      # Update for the next transition
      current_conditions = final_conditions
      remaining_period -= transition_duration
      current_weather = new_weather

    return timestamps

  def update_weather(self) -> None:
    """
    Update the weather by generating a new weather condition and adding it to the list of weather steps or iterating over the list.
    """
    print(f'WEATHER: {self._current_weather}')
    print(f'WEATHER STEPS: {self._weather_steps}')
    last_weather = self._current_weather.get('weather', None)

    # TODO: Fix this, for some reason it skips the last current weather
    # when weather steps is empty
    if len(self._weather_steps) > 0:
      self._current_weather = self._weather_steps.pop(0)

      if self._current_weather['weather'] == 'Stormy' and random.random() < self._thunder_prob and self._thunder_listener:
        self._thunder_listener()

      if (last_weather is None or last_weather != self._current_weather['weather']) and self._weather_change_listener:
        self._weather_change_listener(self._current_weather, self._weather_steps)
      return

    print('NEW WEATHER STEPS')
    current_weather = self._current_weather.get('weather', 'Sunny')
    current_conditions = self._generate_weather(current_weather)

    transition_duration = random.randint(2, 6)

    new_weather = random.choice(self._posible_transitions[current_weather])
    final_conditions = self._generate_weather(new_weather)

    transition_gen = self._transition_weather(current_conditions, final_conditions, transition_duration)

    self._weather_steps.extend(transition_gen[1:])
    self._current_weather = transition_gen[0]

    if (last_weather is None or last_weather != self._current_weather['weather']) and self._weather_change_listener:
      self._weather_change_listener(self._current_weather, self._weather_steps)

    if self._current_weather['weather'] == 'Stormy' and random.random() < self._thunder_prob and self._thunder_listener:
      self._thunder_listener()

  def override_weather(self, current_weather: Weather, next_weather: Weather, duration: int) -> None:
    """
    Override the current weather, and set the next weather after the duration.
    This will trigger the listener for the weather change.

    :param Weather current_weather: The current weather to override.
    :param Weather next_weather: The next weather to set after the duration.
    :param int duration: The duration of the override.
    """
    current_conditions = self._generate_weather(current_weather)
    next_conditions = self._generate_weather(next_weather)

    transition_gen = self._transition_weather(current_conditions, next_conditions, duration)

    self._weather_steps.extend(transition_gen[1:])
    self._current_weather = transition_gen[0]

    if self._weather_change_listener:
      self._weather_change_listener(self._current_weather, self._weather_steps)

  def throw_thunder(self) -> None:
    """
    Trigger the thunder listener, is just a helper method to trigger the thunder listener, 
    doesn't have any other functionality.	
    """
    if self._thunder_listener:
      self._thunder_listener()

  #################################################
  ################ Dunder Methods #################
  #################################################

  def __getstate__(self):
    """
    Function for compatibility with pickle, used for renpy save/load.
    """
    state = self.__dict__.copy()

    del state['_weather_change_listener']
    del state['_thunder_listener']

    print(f'Saving weather: {state}')

    return state

  def __setstate__(self, state):
    """
    Function for compatibility with pickle, used for renpy save/load.
    """
    cw = state.pop('_current_weather')
    ws = state.pop('_weather_steps')
    self.__dict__.update(state)

    self._weather_change_listener = None
    self._thunder_listener = None
    self._current_weather = cw
    self._weather_steps = ws

    print(f'Loading weather2: {self.__dict__}')
    print(f'Loading weather: {state}')
