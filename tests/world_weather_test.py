from unittest import TestCase
import random

from worldnavigator.weather.weather import WorldWeather


class WorldWeatherTest(TestCase):
  def setUp(self):
    """Set up test environment before each test method."""
    # Fix the random seed for consistent test results
    random.seed(42)
    self.weather_system = WorldWeather()

  def test_weather_initialization(self):
    """
    Test that WorldWeather is initialized with the correct weather conditions and transition rules.

    Arrange:
      - Initialize a WorldWeather object

    Act:
      - Access the weather conditions and transition rules

    Assert:
      - Verify all expected weather types exist
      - Verify each weather type has the required properties (temperature, humidity, wind, clouds)
      - Verify transition rules exist for each weather type
    """
    # Test weather conditions exist
    self.assertIn('Sunny', self.weather_system._weather)
    self.assertIn('Cloudy', self.weather_system._weather)
    self.assertIn('Rainy', self.weather_system._weather)
    self.assertIn('Stormy', self.weather_system._weather)
    self.assertIn('Snowy', self.weather_system._weather)

    # Test weather properties
    for weather_type in ['Sunny', 'Cloudy', 'Rainy', 'Stormy', 'Snowy']:
      self.assertIn('temperature', self.weather_system._weather[weather_type])
      self.assertIn('humidity', self.weather_system._weather[weather_type])
      self.assertIn('wind', self.weather_system._weather[weather_type])
      self.assertIn('clouds', self.weather_system._weather[weather_type])

    # Test transition rules
    self.assertIn(self.weather_system._posible_transitions['Cloudy'](), ['Sunny', 'Rainy', 'Stormy', 'Snowy'])
    self.assertIn(self.weather_system._posible_transitions['Sunny'](), ['Cloudy', 'Rainy'])
    self.assertIn(self.weather_system._posible_transitions['Rainy'](), ['Cloudy', 'Stormy'])

  def test_generate_weather(self):
    """
    Test the internal _generate_weather method produces valid weather conditions.

    Arrange:
      - Initialize a WorldWeather object

    Act:
      - Generate weather conditions for different weather types

    Assert:
      - Verify the generated conditions have the expected keys
      - Verify the values are within the expected ranges
    """
    for weather_type in ['Sunny', 'Cloudy', 'Rainy', 'Stormy', 'Snowy']:
      conditions = self.weather_system._generate_weather(weather_type)

      # Check that all required keys exist
      self.assertIn('weather', conditions)
      self.assertIn('temperature', conditions)
      self.assertIn('humidity', conditions)
      self.assertIn('wind', conditions)
      self.assertIn('clouds', conditions)

      # Check that the weather type is correct
      self.assertEqual(conditions['weather'], weather_type)

      # Check that values are within the expected ranges
      min_temp, max_temp = self.weather_system._weather[weather_type]['temperature']
      self.assertTrue(min_temp <= conditions['temperature'] <= max_temp)

      min_humidity, max_humidity = self.weather_system._weather[weather_type]['humidity']
      self.assertTrue(min_humidity <= conditions['humidity'] <= max_humidity)

      min_wind, max_wind = self.weather_system._weather[weather_type]['wind']
      self.assertTrue(min_wind <= conditions['wind'] <= max_wind)

      min_clouds, max_clouds = self.weather_system._weather[weather_type]['clouds']
      self.assertTrue(min_clouds <= conditions['clouds'] <= max_clouds)

  def test_interpolate(self):
    """
    Test the _interpolate method correctly calculates intermediate values.

    Arrange:
      - Initialize a WorldWeather object

    Act:
      - Call _interpolate with various input parameters

    Assert:
      - Verify the interpolated values are calculated correctly
    """
    # Test start of interpolation
    self.assertAlmostEqual(
        self.weather_system._interpolate(10, 20, 0, 10),
        10.0
    )

    # Test middle of interpolation
    self.assertAlmostEqual(
        self.weather_system._interpolate(10, 20, 5, 10),
        15.0
    )

    # Test end of interpolation
    self.assertAlmostEqual(
        self.weather_system._interpolate(10, 20, 10, 10),
        20.0
    )

    # Test with negative values
    self.assertAlmostEqual(
        self.weather_system._interpolate(-10, 10, 5, 10),
        0.0
    )

  def test_transition_weather(self):
    """
    Test the _transition_weather method generates correct transition steps.

    Arrange:
      - Initialize a WorldWeather object
      - Define initial and final weather conditions

    Act:
      - Generate a weather transition over a specified duration

    Assert:
      - Verify the correct number of steps is generated
      - Verify the first and last steps have values close to initial and final conditions
      - Verify the intermediate values show a progression
    """
    initial_conditions = {
        'weather': 'Sunny',
        'temperature': 30.0,
        'humidity': 20.0,
        'wind': 5.0,
        'clouds': 10.0
    }

    final_conditions = {
        'weather': 'Rainy',
        'temperature': 15.0,
        'humidity': 80.0,
        'wind': 15.0,
        'clouds': 90.0
    }

    duration = 5  # 5-hour transition

    steps = self.weather_system._transition_weather(
        initial_conditions, final_conditions, duration
    )

    # Check the number of steps
    self.assertEqual(len(steps), duration)

    # Check first step is close to initial conditions but already transitioning
    first_step = steps[0]
    self.assertEqual(first_step['weather'], 'Rainy')
    # First step should have moved 1/5 of the way from initial to final
    self.assertAlmostEqual(first_step['temperature'], 27.0)  # 30 + (15 - 30) * (1/5)

    # Check last step is at final conditions
    last_step = steps[-1]
    self.assertEqual(last_step['weather'], 'Rainy')
    self.assertAlmostEqual(last_step['temperature'], 15.0)
    self.assertAlmostEqual(last_step['humidity'], 80.0)
    self.assertAlmostEqual(last_step['wind'], 15.0)
    self.assertAlmostEqual(last_step['clouds'], 90.0)

  def test_simulate_weather_with_transitions(self):
    """
    Test the simulate_weather_with_transitions method generates a valid weather simulation.

    Arrange:
      - Initialize a WorldWeather object

    Act:
      - Simulate weather over a specified duration

    Assert:
      - Verify the correct number of hourly data points is generated
      - Verify each data point has the required properties
    """
    # Test with fixed duration
    total_duration = 24  # 24 hours
    initial_weather = 'Sunny'

    hourly_weather = self.weather_system.simulate_weather_with_transitions(
        total_duration, initial_weather
    )

    # Check the total number of hours
    self.assertEqual(len(hourly_weather), total_duration)

    # Check each hour's data has the required structure
    for hour_data in hourly_weather:
      self.assertIn('weather', hour_data)
      self.assertIn('temperature', hour_data)
      self.assertIn('humidity', hour_data)
      self.assertIn('wind', hour_data)
      self.assertIn('clouds', hour_data)

  def test_simulate_weather_with_custom_duration(self):
    """
    Test weather simulation with different durations.

    Arrange:
      - Initialize a WorldWeather object

    Act:
      - Simulate weather with very short, medium, and long durations

    Assert:
      - Verify the correct number of hourly data points is generated in each case
    """
    # Test short duration
    short_duration = 3
    short_simulation = self.weather_system.simulate_weather_with_transitions(short_duration)
    self.assertEqual(len(short_simulation), short_duration)

    # Test medium duration
    medium_duration = 48
    medium_simulation = self.weather_system.simulate_weather_with_transitions(medium_duration)
    self.assertEqual(len(medium_simulation), medium_duration)

    # Test long duration
    long_duration = 168  # One week
    long_simulation = self.weather_system.simulate_weather_with_transitions(long_duration)
    self.assertEqual(len(long_simulation), long_duration)

  def test_simulate_weather_with_different_start_conditions(self):
    """
    Test weather simulation with different starting weather conditions.

    Arrange:
      - Initialize a WorldWeather object

    Act:
      - Simulate weather starting from different weather types

    Assert:
      - Verify the simulation works for all starting weather types
    """
    duration = 24

    for initial_weather in ['Sunny', 'Cloudy', 'Rainy', 'Stormy', 'Snowy']:
      # Reset random seed for consistent results in each test
      random.seed(42)

      simulation = self.weather_system.simulate_weather_with_transitions(
          duration, initial_weather
      )

      self.assertEqual(len(simulation), duration)
