from worldnavigator.types import BASIC_TYPES


def is_valid_prop_value(value: type | tuple[type, str]) -> bool:
  """
  Check if the provided value from :class:`Params <worldnavigator.types.types.Params>`  is a basic type or a tuple with the correct types.

  This function validates whether the given value is either a :py:data:`~worldnavigator.types.types.BASIC_TYPES`
  or a tuple consisting of a type and a description string. It is used to ensure that the parameters
  defined in the :class:`Params <worldnavigator.types.types.Params>` class conform to expected types.

  :param type | tuple[type, str] value: The value to validate, which can be a type or a tuple
                                         containing a type and a description.

  :return: True if the value is correctly defined as a basic type or a valid tuple; otherwise, False.
  """
  if isinstance(value, type) and issubclass(value, BASIC_TYPES):
    return True

  if isinstance(value, tuple) and len(value) == 2:
    type_part, description = value

    return isinstance(type_part, type) and issubclass(type_part, BASIC_TYPES) and isinstance(description, str)

  return False
