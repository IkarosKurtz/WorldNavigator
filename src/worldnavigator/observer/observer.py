from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Literal, Union, overload

from worldnavigator.errors.is_not_a_function import IsNotAFunctionError
from worldnavigator.observer.events import EventName
from worldnavigator.utils.functions import is_a_valid_function

if TYPE_CHECKING:
  from worldnavigator.core.character import GameCharacter
  from worldnavigator.locations.base_location import Location

# Allow users to use their own event names
CustomEventName = Union[EventName, str]


class Observer:
  """
  Implements the Observer pattern for event handling in the WorldNavigator system.

  Provides a foundation for objects that need to emit events and
  respond to events from other objects. It allows for type-safe event registration
  and triggering with proper argument validation.

  This class is used as a base for objects like :class:`Location <worldnavigator.locations.base_location.Location>`
  and :class:`World <worldnavigator.core.world.World>` that need to communicate state changes
  (such as characters being added or removed) to other components of the system.
  """

  def __init__(self):
    """
    Initializes the Observer instance.

    This constructor sets up an empty dictionary to hold event listeners,
    mapping event names to their corresponding callback functions.
    """
    self._events: Dict[str, List[Callable]] = defaultdict(list)

  @overload
  def on(self, event_name: Literal["character_added"], func: Callable[[GameCharacter, Location], None]) -> None:
    """
    Registers a callback function for the 'character_added' event.

    :param event_name: The name of the event to listen to.
    :param func: The function to call when the event is triggered.
    """
    ...

  @overload
  def on(self, event_name: Literal["character_removed"], func: Callable[[GameCharacter, Location], None]) -> None:
    """
    Registers a callback function for the 'character_removed' event.

    :param event_name: The name of the event to listen to.
    :param func: The function to call when the event is triggered.
    """
    ...

  def on(self, event_name: CustomEventName, func: Callable) -> None:
    """
    Listen to an event and call the given function when it is triggered.

    :param CustomEventName event_name: The name of the event to listen to.
    :param Callable func: The function to call when the event is triggered.
    """
    if not is_a_valid_function(func):
      raise IsNotAFunctionError(f"The provided callback for event '{event_name}' is not a valid function.")

    if func not in self._events[event_name]:
      self._events[event_name].append(func)

  @overload
  def trigger(self, event_name: Literal["character_added"], data: GameCharacter, location: Location) -> None:
    """
    Triggers the 'character_added' event with the provided data.

    :param event_name: The name of the event to trigger.
    :param data: The data associated with the event.
    """
    ...

  @overload
  def trigger(self, event_name: Literal["character_removed"], data: GameCharacter, location: Location) -> None:
    """
    Triggers the 'character_removed' event with the provided data.

    :param event_name: The name of the event to trigger.
    :param data: The data associated with the event.
    """
    ...

  def trigger(self, event_name: CustomEventName, *data: Any) -> None:
    """
    Trigger an event with the given data and notify all registered listeners.

    This method checks if the event is registered and validates the data
    against the expected types before calling the registered callback functions.
    It supports multiple listeners per event.

    :param CustomEventName event_name: The name of the event to trigger.
    :param Any data: The positional arguments to pass to the event listeners.
    """
    if event_name not in self._events:
      return

    for func in self._events[event_name]:
      func(*data)
