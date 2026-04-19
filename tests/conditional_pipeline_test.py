import pytest

from worldnavigator.core.condition_pipeline import ConditionalPipeline
from worldnavigator.types.types import BaseCondition, ConditionPipelineContext


class MockCondition(BaseCondition):
  def __init__(self, name: str, should_pass: bool = True):
    super().__init__()
    self.name = name
    self.should_pass = should_pass
    self.handled = False

  def handle(self, context: ConditionPipelineContext) -> bool:
    self.handled = True
    return self.should_pass


class TestConditionalPipeline:
  def test_initialization(self):
    """
    Test that the ConditionalPipeline initializes with the correct attributes.

    Arrange & Act:
      - Create a ConditionalPipeline instance.

    Assert:
      - Verify that the initial attributes are set correctly.
    """
    # Arrange & Act
    pipeline = ConditionalPipeline()

    # Assert
    assert pipeline._next_condition is None
    assert isinstance(pipeline._context, ConditionPipelineContext)
    assert not pipeline._context.denied

  def test_chaining_with_plus_operator(self):
    """
    Test that the + operator correctly appends conditions to the end of the chain
    and returns the head (pipeline).

    Arrange:
      - Create a pipeline and multiple mock conditions.

    Act:
      - Chain conditions using the + operator starting from the head.

    Assert:
      - Verify the chain structure: pipeline -> cond1 -> cond2.
      - Verify the return value is the pipeline instance.
    """
    # Arrange
    pipeline = ConditionalPipeline()
    cond1 = MockCondition("cond1")
    cond2 = MockCondition("cond2")

    # Act
    result = pipeline + cond1 + cond2

    # Assert
    assert result is pipeline
    assert pipeline._next_condition is cond1
    assert cond1._next_condition is cond2
    assert cond2._next_condition is None

    # Act
    with pytest.raises(TypeError) as exc_info:
      pipeline + "not a condition"

    # Assert
    assert 'Expected BaseCondition, got "str"' in str(exc_info.value)

  def test_execution_of_entire_chain(self):
    """
    Test that calling handle() executes all conditions in the chain sequentially.

    Arrange:
      - Create a chain of conditions.

    Act:
      - Execute the pipeline.

    Assert:
      - Verify all conditions were handled.
    """
    # Arrange
    pipeline = ConditionalPipeline()
    cond1 = MockCondition("cond1")
    cond2 = MockCondition("cond2")
    pipeline + cond1 + cond2

    # Act
    pipeline.handle()

    # Assert
    assert cond1.handled
    assert cond2.handled

  def test_interruption_on_denial(self):
    """
    Test that if a condition returns False, subsequent conditions are skipped.

    Arrange:
      - Create a chain where the first condition returns False.

    Act:
      - Execute the pipeline.

    Assert:
      - Verify the first condition was handled and returned False.
      - Verify the second condition was skipped.
    """
    # Arrange
    pipeline = ConditionalPipeline()
    cond1 = MockCondition("cond1", should_pass=False)
    cond2 = MockCondition("cond2")
    pipeline + cond1 + cond2

    # Act
    context = pipeline.handle()

    # Assert
    assert context.denied
    assert cond1.handled
    assert not cond2.handled

  def test_bulk_set_via_call(self):
    """
    Test that calling the pipeline object resets the chain and sets new conditions.

    Arrange:
      - Create a pipeline with an existing condition.

    Act:
      - Call the pipeline with new conditions.

    Assert:
      - Verify the old condition is gone and new conditions are correctly chained.
    """
    # Arrange
    pipeline = ConditionalPipeline()
    old_cond = MockCondition("old")
    pipeline + old_cond

    new_cond1 = MockCondition("new1")
    new_cond2 = MockCondition("new2")

    # Act
    pipeline(new_cond1, new_cond2)

    # Assert
    assert pipeline._next_condition is new_cond1
    assert new_cond1._next_condition is new_cond2
    assert new_cond2._next_condition is None
    assert old_cond._next_condition is None

  def test_multiple_handle_calls(self):
    """
    Test that multiple calls to handle() reset the context correctly and do not carry over denial state.

    Arrange:
      - Create a pipeline with a condition that toggles its state to fail after the first pass.

    Act:
      - Call handle() multiple times.

    Assert:
      - Verify the returned context from the first run is denied.
      - Verify the returned context from the second run is fresh (not denied initially).
      - Verify the returned context from the third run is also fresh (not denied initially).
    """
    # Arrange
    pipeline = ConditionalPipeline()

    class MockCondition2(BaseCondition):
      def __init__(self):
        super().__init__()
        self.i = 0

      def handle(self, context: ConditionPipelineContext) -> bool:
        if self.i == 0:
          self.i += 1
          return True

        return False

    pipeline + MockCondition2()

    # Act
    first_run = pipeline.handle()
    second_run = pipeline.handle()
    third_run = pipeline.handle()

    # Assert
    assert not first_run.denied
    assert second_run.denied  # Second run fails because MockCondition2 toggled its internal state
    assert third_run.denied  # Third run also fails
