
from typing import Annotated, Literal
from worldnavigator.core import WorldObject
from worldnavigator.decorators import evaluate_events
from worldnavigator.types import Params


@evaluate_events
class Events:
  sat: Annotated[str, Params(name=(str, 'Nombre del personaje'))]
  read: Annotated[str, Params(name=(str, 'Nombre del personaje'), duration=float)]


EventNames = Literal['sat', 'read']

chair = WorldObject[Events, EventNames]('Chair')
