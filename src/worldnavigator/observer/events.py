from typing import Literal, TypedDict


EventName = Literal['character_added', 'character_removed']
"""
A type representing the names of events that can occur in the system.

This type is a literal that restricts the event names to two specific strings:
- 'character_added': Indicates that a character has been added to a location.
- 'character_removed': Indicates that a character has been removed from a location.
"""


class CharacterAddedEvent(TypedDict):
  """
  A dictionary representing the event data for when a character is added.
  """
  name: str
  location: str


class CharacterRemovedEvent(TypedDict):
  """
  A dictionary representing the event data for when a character is removed.
  """
  name: str
  location: str
