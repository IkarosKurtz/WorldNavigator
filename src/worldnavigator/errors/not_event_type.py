class NotEventTypeError(Exception):
  """
  Exception raised when a WorldObject does not have a valid EventType defined.

  This error is raised when attempting to define a WorldObject without a valid EventType.
  """

  def __init__(self, classname: str):
    self.message = f'The object "{classname}" does not have a valid EventType defined. Please make sure to define an EventType for this object.'
    super().__init__(self.message)
