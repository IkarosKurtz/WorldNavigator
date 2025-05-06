import inspect
from typing import Callable, Generic, Tuple, TypeVar, get_args, get_type_hints

from worldnavigator.errors import EventNotFound, IsNotAFunctionError


EventType = TypeVar('EventType')
EventName = TypeVar('EventName', bound=str)

BASIC_TYPES = (int, float, str, bool)


class WorldObject(Generic[EventType, EventName]):
  """
  A world object is an object that can be found in a location, like a pencil, book, bed, etc.

  WorldObject serves as the base class for all interactive objects within the world navigation system.
  It provides a flexible interaction mechanism that allows defining custom interactions for each object.

  Examples:
  ```python
  # Create a simple book object
  Events = Literal["read", "open"]
  book = WorldObject[Events]("Ancient Book")

  # Register interactions
  book.register_interaction("read", lambda: print("You read the mysterious text..."))
  book.register_interaction("open", lambda: print("The book creaks as you open it"))

  # Interact with the object
  book.interact("read")  # Outputs: You read the mysterious text...
  ```

  Generic Parameter:
  - V: A Literal type with the possible interactions for the specific WorldObject implementation.
  """

  def __init__(self, name: str):
    self._name = name
    self._interactions_func: dict[str, Callable] = {}

  #################################################
  ################### Properties ##################
  #################################################

  @property
  def name(self) -> str:
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
  ################### Properties ##################
  #################################################

  @property
  def events(self) -> list[str]:
    self._define_hints()

    return list(self._hints_of.keys())

  #################################################
  ################ Public Methods #################
  #################################################

  def register_interaction(self, kind: EventName, func: Callable) -> None:
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
        raise ValueError(f'Misssing parameter "{key}" in function "{func.__name__}" for event "{kind}"')
      param_type = param_type.annotation

      if inspect.Parameter.empty == param_type:
        raise ValueError(f'Parameter "{key}" has no type, it must be "{param_type.__name__}"')

      value_type, _ = self._extract_metadata(value)
      if param_type != value_type:
        raise ValueError(f'Type of "{key}" is "{value_type.__name__}" and was expected to be "{param_type.__name__}"')

    self._interactions_func[kind] = func

  def interact(self, kind: EventName, **payload) -> None:
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
