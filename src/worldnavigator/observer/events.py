from typing import Literal, TypedDict


EventName = Literal['character_added', 'character_removed']


class CharacterAddedEvent(TypedDict):
  name: str
  location: str


class CharacterRemovedEvent(TypedDict):
  name: str
  location: str
