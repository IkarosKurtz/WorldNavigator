from typing import Annotated

import pytest

from worldnavigator.decorators.function_decorators import evaluate_events
from worldnavigator.types.types import Params


class TestEvaluateEvents:
  def test_decorator_accepts_valid_class(self):
    """
    Test that the decorator accepts a correctly formatted events class.

    Arrange:
      - Define a class with correct Annotated and Params structure.

    Act:
      - Apply the @evaluate_events decorator to the class.

    Assert:
      - Verify that the class definition is successful without raising errors.
    """

    # Act & Assert
    @evaluate_events
    class TestClass:
      event: Annotated[str, Params(a=int), "desc"]

  def test_decorator_raises_error_if_params_missing(self):
    """
    Test that the decorator enforces Params metadata is present.

    Arrange:
      - Define a class using Annotated but missing Params metadata.

    Act:
      - Apply the @evaluate_events decorator.

    Assert:
      - Verify that ValueError is raised with the appropriate message.
    """
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:

      @evaluate_events
      class Invalid1:
        event: Annotated[str, "description only"]

    assert 'Event "event" must have Params metadata (Annotated[str, Params(...)])' == str(exc_info.value)

  def test_decorator_raises_error_if_params_wrong_position(self):
    """
    Test that the decorator enforces Params metadata is in the correct position.

    Arrange:
      - Define a class where Params is not the second argument of Annotated.

    Act:
      - Apply the @evaluate_events decorator.

    Assert:
      - Verify that ValueError is raised with the appropriate message.
    """
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:

      @evaluate_events
      class Invalid2:
        event: Annotated[str, "desc", Params(a=int)]

    assert 'Event "event" must have Params metadata (Annotated[str, Params(...)])' == str(exc_info.value)

  def test_decorator_validates_base_type(self):
    """
    Test that the decorator ensures the base type of the event is 'str'.

    Arrange:
      - Define a class with an event typed as int instead of str.

    Act:
      - Apply the @evaluate_events decorator.

    Assert:
      - Verify that ValueError is raised confirming only strings are allowed as event base types.
    """
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:

      @evaluate_events
      class InvalidType:
        event: Annotated[int, Params()]

    assert 'Event "event" must be a string (Annotated[str, ...])' == str(exc_info.value)

  def test_decorator_validates_metadata_values(self):
    """
    Test that Params content is validated to contain only basic types.

    Arrange:
      - Define a class with an event using complex types (dict) in Params.

    Act:
      - Apply the @evaluate_events decorator.

    Assert:
      - Verify that ValueError is raised due to invalid metadata types.
    """
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:

      @evaluate_events
      class InvalidParams:
        event: Annotated[str, Params(data=dict)]

    assert 'Invalid metadata for "data" in attribute "event". Must be a basic type or (basic type, str)' in str(
      exc_info.value
    )

  def test_decorator_wrong_event_type(self):
    """
    Test that the decorator raises an error if an event is not annotated with Annotated.

    Arrange:
      - Define a class with an event that is not using Annotated.

    Act:
      - Apply the @evaluate_events decorator.

    Assert:
      - Verify that ValueError is raised with the appropriate message.
    """
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:

      @evaluate_events
      class InvalidEventType:
        event: str

    assert 'Event "event" must be typed with Annotated' == str(exc_info.value)

  def test_decorator_description_must_be_string(self):
    """
    Test that the decorator raises an error if the description is not a string.

    Arrange:
      - Define a class with an event that has a non-string description.

    Act:
      - Apply the @evaluate_events decorator.

    Assert:
      - Verify that ValueError is raised with the appropriate message.
    """
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:

      @evaluate_events
      class InvalidDescription:
        event: Annotated[str, Params(a=int), 123]

    assert 'Description for event "event" must be a string' == str(exc_info.value)

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:

      @evaluate_events
      class InvalidDescription:
        event: Annotated[str, Params(a=int), str]

    assert 'Description for event "event" must be a string' == str(exc_info.value)
