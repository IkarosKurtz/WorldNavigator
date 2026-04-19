import functools
from typing import Callable, Union

from worldnavigator.types.types import BASIC_TYPES


def is_valid_prop_value(value: Union[type, tuple[type, str]]) -> bool:
  """
  Check if the provided value from :class:`Params <worldnavigator.types.types.Params>`  is a basic type or a tuple with the correct types.

  This function validates whether the given value is either a :py:data:`~worldnavigator.types.types.BASIC_TYPES`
  or a tuple consisting of a type and a description string. It is used to ensure that the parameters
  defined in the :class:`Params <worldnavigator.types.types.Params>` class conform to expected types.

  :param Union[type, tuple[type, str]] value: The value to validate, which can be a type or a tuple
                                         containing a type and a description.

  :return: True if the value is correctly defined as a basic type or a valid tuple; otherwise, False.
  """
  if isinstance(value, type) and issubclass(value, BASIC_TYPES):
    return True

  if isinstance(value, tuple) and len(value) == 2:
    type_part, description = value

    return isinstance(type_part, type) and issubclass(type_part, BASIC_TYPES) and isinstance(description, str)

  return False


def is_a_valid_function(func: Callable) -> bool:
  if not callable(func):
    return False

  if isinstance(func, functools.partial):
    return False

  if getattr(func, "__name__", None) == "<lambda>":
    return False

  return True
