from typing import Literal


BASIC_TYPES = (int, float, str, bool)

Weather = Literal[
  'Sunny',
  'Cloudy',
  'Rainy',
  'Stormy',
  'Snowy',
]
"""
A type representing all possible weather states in the :class:`WorldWeather <worldnavigator.weather.weather.WorldWeather>` class.

- ``Sunny``: A weather with no clouds and a clear sky but with high temperatures.
- ``Cloudy``: A weather with clouds covering the sky, but not necessarily rain.
- ``Rainy``: A weather with clouds and light rain, without thunderstorms.
- ``Stormy``: A weather with clouds and heavy rain, with possibility of thunderstorms.
- ``Snowy``: A weather with clouds and falling snow, lower temperatures.
"""


class Params:
  """
  A class used to declare parameters for events of an object.

  This class allows the definition of parameters with their types for event handling
  in a structured way. It can be used to annotate event attributes in classes.

  .. code-block:: python

    from worldnavigator.types import Params

    class MyEvents:
      hear: Annotated[str, Params(time=float, topic=str)]


  :param **params: Arbitrary keyword arguments representing parameters and their types.
  """

  def __init__(self, **params):
    """
    Initializes the Params class with the given parameters.

    This constructor accepts any number of keyword arguments, which are stored as
    a dictionary for later retrieval.

    :param **params: Arbitrary keyword arguments representing parameters and their types.
    """
    self._params = params

  @property
  def items(self):
    """
    Returns the items of the parameters as a view of (key, value) pairs.

    This property provides a convenient way to access the parameters stored in the instance.

    :return: A view of the parameters' items as (key, value) pairs.
    """
    return self._params.items()

  #################################################
  ################### Properties ##################
  #################################################

  @property
  def params(self):
    """
    Returns the parameters stored in the instance.

    This property allows access to the entire dictionary of parameters.

    :return: A dictionary of parameters.
    """
    return self._params

  def __str__(self):
    """
    Returns a string representation of the parameters.

    This method provides a human-readable format of the parameters stored in the
    instance.

    :return: A string representation of the parameters.
    """
    return str(self._params)

  def __repr__(self):
    """
    Returns a string representation of the Params instance.

    This method is used for debugging and logging purposes, providing a clear
    representation of the Params object.

    :return: A string representation of the Params instance.
    """
    return self.__str__()
