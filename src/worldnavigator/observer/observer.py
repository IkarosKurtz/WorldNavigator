from typing import Callable, Literal, get_type_hints, overload

from worldnavigator.observer.events import EventName, CharacterAddedEvent, CharacterRemovedEvent


class Observer:
  """
  Implements the Observer pattern for event handling in the WorldNavigator system.

  The :class:`Observer` class provides a foundation for objects that need to emit events and 
  respond to events from other objects. It allows for type-safe event registration
  and triggering with proper argument validation.

  This class is used as a base for objects like :class:`Locations` and :class:`World` that need to
  communicate state changes (such as characters being added or removed) to other
  components of the system.
  """

  def __init__(self):
    """
    Initializes the Observer instance.

    This constructor sets up an empty dictionary to hold event listeners,
    mapping event names to their corresponding callback functions.
    """
    self.events: dict[EventName, Callable] = {}

  @overload
  def on(self, event_name: Literal['character_added'], func: Callable[[CharacterAddedEvent], None]) -> None:
    """
    Registers a callback function for the 'character_added' event.

    :param event_name: The name of the event to listen to.
    :param func: The function to call when the event is triggered.
    """
    ...

  @overload
  def on(self, event_name: Literal['character_removed'], func: Callable[[CharacterRemovedEvent], None]) -> None:
    """
    Registers a callback function for the 'character_removed' event.

    :param event_name: The name of the event to listen to.
    :param func: The function to call when the event is triggered.
    """
    ...

  def on(self, event_name: EventName, func: Callable) -> None:
    """
    Listen to an event and call the given function when it is triggered.

    :param EventName event_name: The name of the event to listen to.
    :param Callable func: The function to call when the event is triggered.
    """
    self.events[event_name] = func

  @overload
  def trigger(self, event_name: Literal['character_added'], data: CharacterAddedEvent) -> None:
    """
    Triggers the 'character_added' event with the provided data.

    :param event_name: The name of the event to trigger.
    :param data: The data associated with the event.
    """
    ...

  @overload
  def trigger(self, event_name: Literal['character_removed'], data: CharacterRemovedEvent) -> None:
    """
    Triggers the 'character_removed' event with the provided data.

    :param event_name: The name of the event to trigger.
    :param data: The data associated with the event.
    """
    ...

  def trigger(self, event_name: EventName, data: dict) -> object:
    """
    Trigger an event with the given data.

    This method checks if the event is registered and validates the data
    against the expected types before calling the registered callback function.

    :param EventName event_name: The name of the event to trigger.
    :param dict data: The data to pass to the event.

    :return: The result of the callback function.
    :raises ValueError: If the event is not registered or if the data does not match the expected types.
    """
    if event_name not in self.events:
      raise ValueError('Event not registered')

    func = self.events[event_name]

    types_hints = get_type_hints(func)
    for key, value in types_hints.items():
      if key not in data:
        raise ValueError(f'Missing argument "{key}" in event "{event_name}"')

      if not isinstance(data[key], value):
        raise ValueError(f'Argument "{key}" in event "{event_name}" must be of type "{value}"')

    return func(**data)
