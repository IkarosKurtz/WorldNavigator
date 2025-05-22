import inspect
from typing import Any, Callable, Generic, Tuple, TypeVar, get_args, get_type_hints

from worldnavigator.errors import EventNotFound, IsNotAFunctionError


EventType = TypeVar('EventType', bound=object)
EventName = TypeVar('EventName', bound=str)

BASIC_TYPES = (int, float, str, bool)


class WorldObject(Generic[EventType, EventName]):
  """
  A world object is an object that can be found in a location, like a pencil, book, bed, etc.

  WorldObject serves as the base class for all interactive objects within the world navigation system.
  It provides a flexible interaction mechanism that allows defining custom interactions for each object.

  Generic Parameter:
    - EventType: Class with the definitions of the events for the specific WorldObject implementation.
    - EventName: A Literal type with the possible interactions for the specific WorldObject implementation.
  """

  def __init__(self, name: str):
    self._name = name
    self._interactions_func: dict[str, Callable] = {}

  #################################################
  ################### Properties ##################
  #################################################

  @property
  def events(self) -> list[str]:
    """
    List of event names
    """
    self._define_hints()

    return list(self._hints_of.keys())

  @property
  def name(self) -> str:
    """
    Name of the Object
    """
    return self._name

  #################################################
  ################ Private Methods ################
  #################################################

  def _define_hints(self) -> None:
    """
    Extract all the data from EventType type, is used for data validation in functions and payloads 
    """
    if not hasattr(self, 'hints'):
      self._V_type = get_args(self.__orig_class__)[0]
      self._events_class_name = self._V_type.__name__
      self._hints_of = get_type_hints(self._V_type, include_extras=True)

  def _extract_metadata(self, value) -> Tuple[type, str]:
    if isinstance(value, tuple):
      value_type, value_description = value
    else:
      value_type = value
      value_description = None

    return (value_type, value_description)

  #################################################
  ################ Public Methods #################
  #################################################

  def register_interaction(self, kind: EventName, func: Callable) -> None:
    """
    Register an interaction/callback to be called when the event is triggered with ``interact`` method.

    :param EventName kind: The name of the event to listen to.
    :param Callable func: The function to call when the event is triggered.
    """
    self._define_hints()

    # We need to know what event we want to listen
    event_type = self._hints_of.get(kind, None)

    if event_type is None:
      raise EventNotFound(f'Event "{kind}" is not defined in your "{self._events_class_name}" class')

    if not callable(func):
      raise IsNotAFunctionError(f'Interaction "{kind}" is not callable')

    if func.__name__ == '<lambda>':
      raise IsNotAFunctionError(f'Interaction "{kind}" is a lambda function')

    # We need all the data from the event, same thing for func
    _, *metadata = get_args(event_type)
    func_metadata = inspect.signature(func)
    params = dict(func_metadata.parameters.items())
    metadata_item: dict = dict(metadata[0].items)

    if len(params) == 0 and len(metadata_item) != 0:
      raise ValueError(f'Function "{func.__name__}" has no parameters, expected "{str(list(metadata_item.keys()))}"')

    # We have to be sure that func definition has all the parameters
    # from the defined event
    for key, value in params.items():
      value = value.annotation
      event_type = metadata_item.get(key, None)

      if event_type is None:
        raise ValueError(f'Unexpected parameter "{key}" in function "{func.__name__}" for event "{kind}"')

      param_type, _ = self._extract_metadata(event_type)
      if inspect.Parameter.empty == value:
        raise ValueError(f'Parameter "{key}" has no type, it must be "{param_type.__name__}"')

      if param_type != value:
        raise ValueError(f'Type of "{key}" is "{value.__name__}" and was expected to be "{param_type.__name__}"')

    for key, value in metadata_item.items():
      param_type = params.get(key, None)

      if param_type is None:
        raise ValueError(f'Missing parameter "{key}" in function "{func.__name__}" for event "{kind}"')
      param_type = param_type.annotation

      if inspect.Parameter.empty == param_type:
        raise ValueError(f'Parameter "{key}" has no type, it must be "{param_type.__name__}"')

      value_type, _ = self._extract_metadata(value)
      if param_type != value_type:
        raise ValueError(f'Type of "{key}" is "{value_type.__name__}" and was expected to be "{param_type.__name__}"')

    self._interactions_func[kind] = func

  def interact(self, kind: EventName, **payload: dict[str, Any]) -> None:
    """
    Interact with this object by triggering a specific event, passing the data as keyword arguments.

    :param EventName kind: The name of the event to trigger.
    :param dict[str, Any] payload: The data to pass to the event.
    """
    func = self._interactions_func.get(kind, None)

    if func is None:
      raise EventNotFound(
        f'Event "{kind}" is not defined in your "{self._events_class_name}" class or is not register yet.')

    # We need to check if payload has the correct data for the listener
    params = inspect.signature(func).parameters
    params_values = dict(params.items())

    for key, value in payload.items():
      if key not in params_values:
        raise ValueError(f'Unexpected data "{key}" for event "{kind}"')

      value_type = type(value).__name__

      expected_type = params_values[key].annotation.__name__
      if value_type != expected_type:
        raise ValueError(f'Type of "{key}" must be {expected_type}')

    func(**payload)
