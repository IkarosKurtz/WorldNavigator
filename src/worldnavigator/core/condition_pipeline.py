from dataclasses import replace

from worldnavigator.types.types import BaseCondition, ConditionPipelineContext


class ConditionalPipeline(BaseCondition):
  """
  Head of conditional pipeline, used to chain conditions together.

  This class is in other classes like :class:`Location <worldnavigator.locations.base_location.Location>`,
  so you can chain conditions that needs to be checked when player is moved to that location.
  """

  def __init__(self):
    """
    Initializes the conditional pipeline head.
    """
    super().__init__()
    self._context: ConditionPipelineContext = ConditionPipelineContext()

  def handle(self) -> ConditionPipelineContext:
    """
    Executes the entire pipeline chain iteratively.

    :return: The final context after all conditions have been handled.
    """
    current = self._next_condition
    while current is not None:
      if not current.handle(self._context):
        self._context.denied = True
        break

      current = current._next_condition

    # We need to reset the context for future calls, but we want to return the result
    context_copy = replace(self._context)

    # Reset the context for the next handle() call
    self._context = ConditionPipelineContext()
    return context_copy

  def __call__(self, *args: BaseCondition) -> "ConditionalPipeline":
    """
    Bulk set the conditions in the pipeline.
    This method resets the current chain before adding new conditions.

    :param BaseCondition args: The conditions to add to the pipeline.
    :return: The head of the conditional pipeline (self).
    """
    # Reset the next condition if it exists
    self._next_condition = None

    for arg in args:
      self += arg

    return self

  def __add__(self, other: BaseCondition) -> "ConditionalPipeline":
    """
    Append a new condition to the end of the pipeline chain and return the head (self).

    This allows fluent chaining while keeping the reference to the head of the pipeline.
    Example: pipeline + cond1 + cond2

    :param BaseCondition other: The next condition to append to the pipeline.
    :return: The head of the conditional pipeline.
    :raises TypeError: If the other object is not a BaseCondition.
    """
    if not isinstance(other, BaseCondition):
      raise TypeError(f'Expected BaseCondition, got "{type(other).__name__}"')

    # Traverse to the end of the chain
    last_node = self
    while last_node._next_condition is not None:
      last_node = last_node._next_condition

    last_node._next_condition = other
    return self
