from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


BASIC_TYPES = (int, float, str, bool)
"""
Basic types that can be used in the :class:`Params` class.

For now only this basic types are allowed, but maybe in the future there will be more.

- ``int``: An integer number.
- ``float``: A floating-point number.
- ``str``: A string.
- ``bool``: A boolean value.
"""

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

  This constructor accepts any number of keyword arguments, which are stored as
  a dictionary for later retrieval.

  .. code-block:: python

    from worldnavigator.types import Params

    class MyEvents:
      hear: Annotated[str, Params(time=float, topic=str)]

  .. attention::

    Only :py:data:`~worldnavigator.types.types.BASIC_TYPES` are allowed as parameter types.

  """

  def __init__(self, **params):
    """
    :param dict[str, Union[Tuple[type, str], type]] params: Arbitrary keyword arguments representing parameters and their types.
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


@dataclass
class ConditionPipelineContext:
  denied: bool = False


class BaseCondition(ABC):
  """
  Basic class for a condition in the conditional pipeline.

  This class can be used to create conditions that can be used in :class:`Location <worldnavigator.locations.base_location.Location>`, and others.
  It is used in the :class:`ConditionalPipeline <worldnavigator.core.condition_pipeline.ConditionalPipeline>` class.
  """

  def __init__(self) -> None:
    super().__init__()
    self._next_condition: 'BaseCondition' = None

  def handle_next(self, context: ConditionPipelineContext):
    """
    Handles the next condition in the pipeline, if it exists.
    """
    if (self._next_condition is not None and not context.denied):
      self._next_condition.handle(context)

  @abstractmethod
  def handle(self, context: ConditionPipelineContext):
    """
    Handles the condition you want to implement, can be check player inventory, check weather, check stats, etc.

    :param ConditionPipelineContext context: The context from the pipeline head, used to know if the chain was denied.
    """
    pass

  def __add__(self, other):
    """
    Link this condition to the next condition in the pipeline.

    :param BaseCondition other: The next condition in the pipeline.
    :return: The next condition in the pipeline.
    """
    self._next_condition = other
    return other

  def __str__(self) -> str:
    return f'{self.__class__.__name__}(next_condition={self._next_condition})'

  def __repr__(self) -> str:
    return self.__str__()
