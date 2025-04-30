from typing import Callable, Generic, TypeVar

V = TypeVar('V', bound=str)


class WorldObject(Generic[V]):
  """
  A world object is an object that can be found in a location, like an pencil, book, bed, etc.

  It can be interacted with any way you like.
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
  ################ Public Methods #################
  #################################################

  def register_interaction(self, kind: V, func: Callable):
    self._interactions_func[kind] = func

  def interact(self, kind: V):
    if kind not in self._interactions_func:
      raise ValueError(f'No se encuentra la interacción "{kind}"')

    self._interactions_func[kind]()
