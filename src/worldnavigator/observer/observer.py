from typing import Callable, Literal, get_type_hints, overload

from worldnavigator.observer.events import EventName, CharacterAddedEvent, CharacterRemovedEvent


class Observer:
  """
  An observer is an object that can trigger events and listen to them.

  It is used to notify other objects about changes in the world.
  """

  def __init__(self):
    self.events: dict[EventName, Callable] = {}

  @overload
  def on(self, event_name: Literal['character_added'], func: Callable[[CharacterAddedEvent], None]) -> None:
    ...

  @overload
  def on(self, event_name: Literal['character_removed'], func: Callable[[CharacterRemovedEvent], None]) -> None:
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
    ...

  @overload
  def trigger(self, event_name: Literal['character_removed'], data: CharacterRemovedEvent) -> None:
    ...

  def trigger(self, event_name: EventName, data: dict) -> object:
    """
    Trigger an event with the given data.

    :param EventName event_name: The name of the event to trigger.
    :param dict data: The data to pass to the event.
    """
    if event_name not in self.events:
      raise ValueError("Evento no registrado")

    func = self.events[event_name]

    types_hints = get_type_hints(func)
    for key, value in types_hints.items():
      if key not in data:
        raise ValueError(f'Falta argumento "{key}" en evento "{event_name}"')

      if not isinstance(data[key], value):
        raise ValueError(f'Argumento "{key}" en evento "{event_name}" debe ser de tipo "{value}"')

    return func(**data)
