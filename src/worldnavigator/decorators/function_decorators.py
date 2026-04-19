import inspect
from typing import Annotated, Any, get_args, get_origin

from worldnavigator.types.types import Params
from worldnavigator.utils.functions import is_valid_prop_value


def evaluate_events(cls: Any):
  """
  Check if the provided events class has the correct format for a WorldObject.

  This decorator function inspects the attributes of the given class to ensure that
  each event is properly annotated with the expected types. It verifies that each
  event attribute is of type ``Annotated`` with a base type of ``str`` and that the
  associated metadata is an instance of the `Params` class.

  Example:

  .. code-block:: python

    from worldnavigator.types import Params
    from worldnavigator.decorators import evaluate_events

    @evaluate_events # Check if the class has the correct format
    class MyEvents:
        hear: Annotated[str, Params(time=float, topic=str)]

  :return: The original class if all validations pass.
  :raises ValueError: If any event attribute does not conform to the expected format.
  """
  # Check each attribute for annotations
  for attr_name, attr_type in inspect.get_annotations(cls).items():
    # Each attribute must be an Annotated
    if get_origin(attr_type) is not Annotated:
      raise ValueError(f'Event "{attr_name}" must be typed with Annotated')

    base_type, *metadata = get_args(attr_type)

    description = None
    if len(metadata) > 1:
      description = metadata[1]
      params = metadata[0]
    else:
      params = metadata[0]

    if base_type is not str:
      raise ValueError(f'Event "{attr_name}" must be a string (Annotated[str, ...])')

    if not isinstance(params, Params):
      raise ValueError(f'Event "{attr_name}" must have Params metadata (Annotated[str, Params(...)])')

    if description is not None and not isinstance(description, str):
      raise ValueError(f'Description for event "{attr_name}" must be a string')

    for key, value in params.params.items():
      if not is_valid_prop_value(value):
        raise ValueError(
          f'Invalid metadata for "{key}" in attribute "{attr_name}". Must be a basic type or (basic type, str)'
        )

  return cls
