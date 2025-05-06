import inspect
from typing import Annotated, Any, get_args, get_origin

from worldnavigator.types import Params
from worldnavigator.utils import is_valid_prop_value


def evaluate_events(cls: Any):
  """
  Check if your events class has the correct format for a WorldObject.

  :param Any cls: Your events class
  """
  # Check each attribute for annotations
  for attr_name, attr_type in inspect.get_annotations(cls).items():
    # Each attribute must be a Annotated
    if get_origin(attr_type) is not Annotated:
      raise ValueError(f'Event "{attr_name}" be typed with Annotated')

    base_type, *metadata = get_args(attr_type)
    if base_type.__name__ != 'str':
      raise ValueError(f'Event "{attr_name}" must be a string (Annotated[str, ...])')

    # We only care about the first metadata item
    metadata_item = metadata[0]

    # We need to check if Params is defined
    if not isinstance(metadata_item, Params):
      raise ValueError(f'Event "{attr_name}" must have Params metadata (Annotated[str, Params(...)])')

    for key, value in metadata_item.items:
      if not is_valid_prop_value(value):
        raise ValueError(
          f'Invalid metadata for "{key}" in attribute "{attr_name}". Must be a basic type or (basic type, str)')

  return cls
