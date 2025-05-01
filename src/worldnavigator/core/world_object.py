from typing import Callable, Generic, TypeVar

V = TypeVar('V', bound=str)


class WorldObject(Generic[V]):
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
  ################ Public Methods #################
  #################################################

  def register_interaction(self, kind: V, func: Callable):
    self._interactions_func[kind] = func

  def interact(self, kind: V):
    if kind not in self._interactions_func:
      raise ValueError(f'Interaction "{kind}" not found')

    self._interactions_func[kind]()
