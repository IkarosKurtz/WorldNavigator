import random

import pytest

from worldnavigator.weather.weather import WorldWeather


class TestWorldWeather:
  @pytest.fixture(autouse=True)
  def setup(self):
    """Set up test environment before each test method."""
    # Fix the random seed for consistent test results
    random.seed(42)
    self.weather_system = WorldWeather()

  def test_weather_initialization(self):
    """
    Test that WorldWeather is initialized with the correct weather conditions and transition rules.

    Arrange:
      - Initialize a WorldWeather object.

    Act:
      - Access the weather conditions and transition rules.

    Assert:
      - Verify all expected weather types exist.
      - Verify each weather type has the required properties.
      - Verify transition rules exist for each weather type.
    """
    # Arrange & Act
    weather = self.weather_system._weather
    transitions = self.weather_system._posible_transitions

    # Assert
    assert "Sunny" in weather
    assert "Cloudy" in weather
    assert "Rainy" in weather

    for weather_type in ["Sunny", "Cloudy", "Rainy"]:
      assert "temperature" in weather[weather_type]
      assert "humidity" in weather[weather_type]

    assert transitions["Sunny"] == ["Cloudy", "Rainy"]

    self.weather_system.update_weather()

    for key in ["clouds", "humidity", "temperature", "weather", "wind"]:
      assert key in self.weather_system.current_weather

    assert isinstance(self.weather_system.weather_steps, list)

    for key in ["clouds", "humidity", "temperature", "weather", "wind"]:
      assert key in self.weather_system.weather_steps[0]

  def test_weather_update_and_callback(self):
    """
    Test that the update_weather method correctly updates the current weather and triggers callbacks.

    Arrange:
      - Initialize a WorldWeather object.
      - Define a callback function to capture weather updates.

    Act:
      - Register the callback and call update_weather.

    Assert:
      - Verify the current weather is updated to a valid weather type.
      - Verify the callback is triggered with the new weather conditions.
    """
    # Arrange
    captured_weather = {}

    def weather_callback(new_weather, rest_of_conditions):
      captured_weather.update(new_weather)

    self.weather_system.listen_for_weather_change(weather_callback)

    captured_thunder = False

    def thunder_callback():
      nonlocal captured_thunder
      captured_thunder = True

    self.weather_system.listen_for_thunder(thunder_callback)

    # Act
    self.weather_system.update_weather()

    # Assert
    assert self.weather_system.current_weather["weather"] in ["Sunny", "Cloudy", "Rainy"]
    assert captured_weather == self.weather_system.current_weather

    # Act
    self.weather_system.throw_thunder()

    # Assert
    assert captured_thunder is True

  def test_generate_weather(self):
    """
    Test the internal _generate_weather method produces valid weather conditions.

    Arrange:
      - Initialize a WorldWeather object.

    Act:
      - Generate weather conditions for different weather types.

    Assert:
      - Verify the generated conditions have the expected keys.
      - Verify the values are within the expected ranges defined in the config.
    """
    # Arrange
    weather_type = "Sunny"

    # Act
    conditions = self.weather_system._generate_weather(weather_type)

    # Assert
    assert conditions["weather"] == weather_type
    min_temp, max_temp = self.weather_system._weather[weather_type]["temperature"]
    assert min_temp <= conditions["temperature"] <= max_temp

  def test_interpolate(self):
    """
    Test the _interpolate method correctly calculates intermediate values.

    Arrange:
      - Initialize a WorldWeather object.

    Act:
      - Call _interpolate with various input parameters.

    Assert:
      - Verify the interpolated values match mathematical expectations.
    """
    # Arrange & Act & Assert
    # Start of interpolation
    assert self.weather_system._interpolate(10, 20, 0, 10) == pytest.approx(10.0)
    # Middle of interpolation
    assert self.weather_system._interpolate(10, 20, 5, 10) == pytest.approx(15.0)
    # End of interpolation
    assert self.weather_system._interpolate(10, 20, 10, 10) == pytest.approx(20.0)

  def test_transition_weather(self):
    """
    Test the _transition_weather method generates correct transition steps.

    Arrange:
      - Initialize a WorldWeather object.
      - Define initial and final weather conditions and transition duration.

    Act:
      - Generate a weather transition.

    Assert:
      - Verify the correct number of steps is generated.
      - Verify values show a progression from initial to final state.
    """
    # Arrange
    initial = {"weather": "Sunny", "temperature": 30.0, "humidity": 20.0, "wind": 5.0, "clouds": 10.0}
    final = {"weather": "Rainy", "temperature": 15.0, "humidity": 80.0, "wind": 15.0, "clouds": 90.0}
    duration = 5

    # Act
    steps = self.weather_system._transition_weather(initial, final, duration)

    # Assert
    assert len(steps) == duration
    assert steps[-1]["temperature"] == pytest.approx(15.0)
    assert steps[0]["temperature"] < 30.0  # Should have started decreasing

  def test_simulate_weather_with_transitions(self):
    """
    Test the simulate_weather_with_transitions method generates a valid weather simulation.

    Arrange:
      - Initialize a WorldWeather object.

    Act:
      - Simulate weather over a specified duration (24 hours).

    Assert:
      - Verify the correct number of hourly data points is generated.
      - Verify each data point has the required weather properties.
    """
    # Arrange
    total_duration = 24

    # Act
    hourly_weather = self.weather_system.simulate_weather_with_transitions(total_duration, "Sunny")

    # Assert
    assert len(hourly_weather) == total_duration
    for hour_data in hourly_weather:
      assert "weather" in hour_data
      assert "temperature" in hour_data

  def test_simulate_weather_with_custom_duration(self):
    """
    Test weather simulation with different durations.

    Arrange:
      - Initialize a WorldWeather object.

    Act:
      - Simulate weather with short and medium durations.

    Assert:
      - Verify the returned list length matches the requested duration.
    """
    # Arrange
    durations = [3, 48]

    # Act & Assert
    for d in durations:
      simulation = self.weather_system.simulate_weather_with_transitions(d)
      assert len(simulation) == d

  def test_simulate_weather_with_different_start_conditions(self):
    """
    Test weather simulation starting from different weather types.

    Arrange:
      - Initialize a WorldWeather object.

    Act:
      - Simulate weather starting from various types (Sunny, Rainy, etc.).

    Assert:
      - Verify the simulation works without errors for all starting types.
    """
    # Arrange
    duration = 10
    weather_types = ["Sunny", "Cloudy", "Rainy"]

    # Act & Assert
    for weather_type in weather_types:
      simulation = self.weather_system.simulate_weather_with_transitions(duration, weather_type)
      assert len(simulation) == duration

  def test_weather_override_weather(self):
    """
    Test that the override_current_weather method correctly sets the current weather, and the override_next_weather method correctly sets the next weather.

    Arrange:
      - Initialize a WorldWeather object.
      - Define a custom weather and duration.
      - Define next weather conditions and duration.


    Act:
      - Override the current weather with the custom condition.
    """
    # Arrange
    weather_type = "Rainy"
    duration = 5

    next_weather_type = "Sunny"
    next_duration = 3

    captured_weather = {}

    def weather_callback(new_weather, rest_of_conditions):
      captured_weather.update(new_weather)

    self.weather_system.listen_for_weather_change(weather_callback)

    # Act
    self.weather_system.override_current_weather(weather_type, duration)

    # Assert
    assert self.weather_system.current_weather["weather"] == "Rainy"
    assert len(self.weather_system.weather_steps) == duration - 1
    assert captured_weather["weather"] == "Rainy"

    self.weather_system.override_next_weather(next_weather_type, next_duration)

    assert len(self.weather_system.weather_steps) != duration - 1
    assert self.weather_system.weather_steps[-1]["weather"] == "Sunny"

  def test_set_weather_manually(self):
    """
    Test that the set_weather method correctly sets the weather steps and triggers callbacks.

    Arrange:
      - Initialize a WorldWeather object.
      - Define a list of custom weather steps.

    Act:
      - Set the weather manually with the custom steps.

    Assert:
      - Verify the current weather and weather steps match the custom steps.
    """
    # Arrange
    custom_weather_steps = self.weather_system.simulate_weather_with_transitions(4, "Cloudy")

    captured_weather = {}

    def weather_callback(new_weather, rest_of_conditions):
      captured_weather.update(new_weather)

    self.weather_system.listen_for_weather_change(weather_callback)

    # Act
    self.weather_system.set_weather(custom_weather_steps)

    # Assert
    assert self.weather_system.current_weather == custom_weather_steps[0]
    assert self.weather_system.weather_steps == custom_weather_steps[1:]
    assert captured_weather == custom_weather_steps[0]

  def test_weather_transitions_validity(self):
    """
    Test that the weather transitions follow the defined rules.

    Arrange:
      - Initialize a WorldWeather object.

    Act:
      - Simulate multiple weather updates.

    Assert:
      - Verify that each new weather condition is a valid transition from the previous one.
    """
    # Arrange
    self.weather_system.override_current_weather("Sunny", 3)
    previous_weather = self.weather_system.current_weather["weather"]

    captured_weather = False
    captured_thunder = False

    def weather_callback(new_weather, rest_of_conditions):
      nonlocal captured_weather
      captured_weather = True

    def thunder_callback():
      nonlocal captured_thunder
      captured_thunder = True

    self.weather_system.listen_for_weather_change(weather_callback)
    self.weather_system.listen_for_thunder(thunder_callback)

    # Act & Assert
    for i in range(10):
      self.weather_system.update_weather()
      current_weather = self.weather_system.current_weather["weather"]
      valid_transitions = self.weather_system._posible_transitions[previous_weather]

      # When current weather runs out of transitions, it should randomly pick a new weather type from the possible transitions of the previous weather
      if i == 2:
        assert current_weather in valid_transitions
      previous_weather = current_weather

    assert captured_weather
    assert captured_thunder
