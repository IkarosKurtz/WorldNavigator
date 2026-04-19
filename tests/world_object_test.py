from typing import Annotated, Literal

import pytest

from worldnavigator.core.world_object import WorldObject, WorldObjectResult
from worldnavigator.decorators.function_decorators import evaluate_events
from worldnavigator.errors import IsNotAFunctionError
from worldnavigator.errors.event_not_found import EventNotFound
from worldnavigator.errors.not_event_type import NotEventTypeError
from worldnavigator.types.types import Params

# --- Mock Classes for Testing ---


@evaluate_events
class ValidEvents:
  touch: Annotated[str, Params(force=int), "Touch the object"]
  look: Annotated[str, Params()]


ValidEventsName = Literal["touch", "look"]


class MockObject(WorldObject[ValidEvents, ValidEventsName]):
  def __init__(self):
    super().__init__("MockItem")


# --- Tests for WorldObject ---


class TestWorldObject:
  def test_initialization(self):
    """
    Test basic initialization of a WorldObject.

    Arrange:
      - Create a MockObject instance.

    Act:
      - Access initialization properties.

    Assert:
      - Verify name and events list are correct.
    """
    # Arrange
    obj = MockObject()

    # Assert
    assert obj.name == "MockItem"
    assert "touch" in obj.events
    assert "look" in obj.events

  def test_initialization_without_events(self):
    """
    Test initialization of a WorldObject without defining events.

    Arrange:
      - Create a class without events and attempt to instantiate it.

    Act & Assert:
      - Verify that NotEventTypeError is raised due to missing EventType.
    """
    # Arrange & Act & Assert
    with pytest.raises(NotEventTypeError) as exc_info:

      class NoEventsObject(WorldObject):
        def __init__(self):
          super().__init__("NoEventsItem")

      NoEventsObject()

    assert (
      'The object "NoEventsObject" does not have a valid EventType defined. Please make sure to define an EventType for this object.'
      == str(exc_info.value)
    )

  def test_register_interaction_success(self):
    """
    Test successful registration of an interaction.

    Arrange:
      - Create a MockObject and a valid handler function.

    Act:
      - Register the interaction for the "touch" event.

    Assert:
      - Verify that the interaction is stored in the internal dictionary.
    """
    # Arrange
    obj = MockObject()

    def handle_touch(force: int):
      return WorldObjectResult(success=True)

    # Act
    obj.register_interaction("touch", handle_touch)

    # Assert
    assert "touch" in obj._interactions_func

  def test_register_interaction_fails_with_lambda(self):
    """
    Test that registering a lambda function raises IsNotAFunctionError.

    Arrange:
      - Create a MockObject.

    Act & Assert:
      - Attempt to register a lambda and verify IsNotAFunctionError is raised.
    """
    # Arrange
    obj = MockObject()

    # Act & Assert
    with pytest.raises(IsNotAFunctionError):
      obj.register_interaction("look", lambda: WorldObjectResult(True))

  def test_register_interaction_fails_with_partial(self):
    """
    Test that registering a partial function raises IsNotAFunctionError.

    Arrange:
      - Create a partial function using functools.

    Act & Assert:
      - Attempt to register the partial function and verify IsNotAFunctionError.
    """
    # Arrange
    import functools

    obj = MockObject()

    def handle_look():
      return WorldObjectResult(success=True)

    partial_func = functools.partial(handle_look)

    # Act & Assert
    with pytest.raises(IsNotAFunctionError):
      obj.register_interaction("look", partial_func)

  def test_register_interaction_param_mismatch(self):
    """
    Test that parameter mismatch between Event and Function raises ValueError.

    Arrange:
      - Prepare functions with wrong names or types.

    Act & Assert:
      - Attempt to register invalid handlers and verify ValueError.
    """
    # Arrange
    obj = MockObject()

    def wrong_name(power: int):
      return WorldObjectResult(success=True)

    def wrong_type(force: str):
      return WorldObjectResult(success=True)

    # Act & Assert
    with pytest.raises(ValueError):
      obj.register_interaction("touch", wrong_name)

    with pytest.raises(ValueError, match='Type of "force" is "str" and was expected to be "int"'):
      obj.register_interaction("touch", wrong_type)

  def test_interact_execution(self):
    """
    Test successful execution of an interaction.

    Arrange:
      - Register a valid interaction handler.

    Act:
      - Trigger the interaction via 'interact' method.

    Assert:
      - Verify the result matches expectations.
    """
    # Arrange
    obj = MockObject()

    def handle_touch(force: int):
      return WorldObjectResult(success=True, result=f"Touch with {force}N")

    obj.register_interaction("touch", handle_touch)

    # Act
    res = obj.interact("touch", force=10)

    # Assert
    assert res.success is True
    assert res.result == "Touch with 10N"

  def test_interact_validation(self):
    """
    Test that 'interact' validates payload types before execution.

    Arrange:
      - Register a valid interaction.

    Act & Assert:
      - Call interact with unexpected data and verify ValueError.
      - Call interact with wrong type and verify ValueError.
    """
    # Arrange
    obj = MockObject()

    def handle_touch(force: int):
      return WorldObjectResult(success=True)

    obj.register_interaction("touch", handle_touch)

    # Act & Assert
    with pytest.raises(ValueError, match='Unexpected data "extra"'):
      obj.interact("touch", force=10, extra="oops")

    with pytest.raises(ValueError, match='Type of "force" must be int'):
      obj.interact("touch", force="hard")

  def test_register_non_existent_event(self):
    """
    Test that registering an event not in the EventType class raises EventNotFound.

    Arrange:
      - Create a MockObject.

    Act & Assert:
      - Attempt to register a non-existent event and verify EventNotFound.
    """
    # Arrange
    obj = MockObject()

    # Act & Assert
    with pytest.raises(EventNotFound, match='Event "non_existent" is not defined'):
      obj.register_interaction("non_existent", lambda x: None)

  def test_interact_with_unregistered_event(self):
    """
    Test that interacting with an event that hasn't been registered raises EventNotFound.

    Arrange:
      - Create an object without registering handlers.

    Act & Assert:
      - Attempt to interact and verify EventNotFound.
    """
    # Arrange
    obj = MockObject()

    # Act & Assert
    with pytest.raises(EventNotFound, match="is not register yet"):
      obj.interact("touch", force=5)

  def test_interact_exception_handling(self):
    """
    Test that exceptions during interaction are caught and returned in WorldObjectResult.

    Arrange:
      - Register a handler that raises an exception.

    Act:
      - Trigger the interaction.

    Assert:
      - Verify the result indicates failure and contains the error message.
    """
    # Arrange
    obj = MockObject()

    def failing_func(force: int):
      raise RuntimeError("Something went wrong")

    obj.register_interaction("touch", failing_func)

    # Act
    res = obj.interact("touch", force=10)

    # Assert
    assert res.success is False
    assert "Something went wrong" in str(res.result)
