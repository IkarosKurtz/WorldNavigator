from worldnavigator.types.types import BaseCondition


class ConditionalPipeline(BaseCondition):
  """
  Head of conditional pipeline, used to chain conditions together.

  This class is in other classes like :class:`Location <worldnavigator.locations.base_location.Location>`, so you can chain conditions that needs to be checked when player is moved to that location.
  """

  def __init__(self):
    self._next_condition: BaseCondition = None

  def __call__(self, *args: list[BaseCondition]):
    current_node = self

    for arg in args:
      current_node += arg

  def handle(self):
    self.handle_next()
