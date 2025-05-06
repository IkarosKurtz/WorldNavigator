from worldnavigator.types import BASIC_TYPES


def is_valid_prop_value(value: type | tuple[type, str]) -> bool:
  """
  Check if value from Params, is a basic type or a tuple with the correct types.

  :param type | tuple[type, str] value:
  :return: If this prop is correctly defined
  """
  if isinstance(value, type) and issubclass(value, BASIC_TYPES):
    return True

  if isinstance(value, tuple) and len(value) == 2:
    type_part, description = value

    return isinstance(type_part, type) and issubclass(type_part, BASIC_TYPES) and isinstance(description, str)

  return False
