import sys
from typing import Any, Callable, Generic, Optional, TypeVar
from types import MethodType

ExtraData = TypeVar('ExtraData', dict, None)


class GameCharacter(Generic[ExtraData]):
  """
  A class that represents a character in the world. Characters are stored in each location where they are present.

  This class allows you to define a character with custom data such as inventory, stats, etc. Use the ``data`` parameter to pass a
  dictionary with the information you want to store. You can then access this data through ``<obj>.data['key']``.
  If you're using Python, it's recommended to use a :py:class:`TypedDict` to define your data structure for better
  autocompletion support.

  When storing functions in the data dictionary, the functions are bound to the class itself, not to the ``data``
  dictionary. Therefore, you cannot access them using ``<obj>.data['my_function']()``. Instead, access the function
  directly with ``<obj>.my_function()``. Every function will always receive as first argument the character itself.

  Generic Parameter:
    - **ExtraData**: Class with inheritance from :py:class:`TypedDict` or ``None``. Is used to support autocompletion \
      for ``data`` dictionary.

  .. attention::

    If you are using Ren'Py, this class functions identically to the ``Character`` class from `Ren'Py`_.

    .. _Ren'Py: https://www.renpy.org/doc/html/dialogue.html#defining-character-objects
  """

  def __init__(self, name: str, data: Optional[ExtraData] = None, **kwargs: dict[str, Any]):
    """ 
    :param str name: The name of the character.
    :param ExtraData data: Extra data to store in the character, like inventory, stats, etc.
    :param bool dynamic: This is used for Ren'Py compatibility, \
      this means ``Character`` will have dynamic parameter to True. See `Ren'Py`_ for more information.
    :param dict[str, Any] kwargs: The keyword arguments define in `Ren'Py`_.

     .. _Ren'Py: https://www.renpy.org/doc/html/dialogue.html#defining-character-objects
    """
    self.name: str = name
    self._renpy_kwargs: dict[str, Any] = kwargs

    if 'renpy' in sys.modules:
      self.c = Character(name, **self._renpy_kwargs)  # type: ignore
    else:
      self.c = None

    self._current_location: str = None

    self._data: ExtraData = {}

    if data is None:
      return

    for key, value in data.items():
      if isinstance(value, Callable):
        setattr(self, key, MethodType(value, self))
        continue

      self._data[key] = value

  #################################################
  ################### Properties ##################
  #################################################

  @property
  def current_location(self) -> str:
    return self._current_location

  @current_location.setter
  def current_location(self, location: str):
    self._current_location = location

  @property
  def data(self) -> ExtraData:
    return self._data

  #################################################
  ################ Dunder Methods #################
  #################################################

  def __call__(self, *args, **kwargs):
    """
    This dunder method is used for Ren'Py compatibility, it allows you to call the character like normal.

    .. code-block:: renpy

      define human = GameCharacter("Human")

      label start:

        human "Hello, world!"
    """
    if self.c is not None:
      return self.c(*args, **kwargs)

  def __getattr__(self, item):
    if item in self.__dict__:
      return self.__dict__[item]

    if self.c is not None and hasattr(self.c, item):
      return getattr(self.c, item)

    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")

  def __eq__(self, value: object) -> bool:
    if isinstance(value, GameCharacter):
      return self.name == value.name
    elif isinstance(value, str):
      return self.name == value

    return False

  def __str__(self):
    return f'GameCharacter(name="{self.name}", data="{self.data}")'

  def __repr__(self):
    return self.__str__()

  def __getstate__(self):
    """
    Function for compatibility with pickle, used for renpy save/load.
    """
    state = self.__dict__.copy()

    print(f'Saving character: {state}')

    return state

  def __setstate__(self, state):
    """
    Function for compatibility with pickle, used for renpy save/load.
    """
    self.__dict__.update(state)

    print(f'Loading character: {state}')
