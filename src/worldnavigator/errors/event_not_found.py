class EventNotFound(Exception):
  """
  Exception raised when interaction name is not found in the selected object.

  This error is raised when attempting to triger a unexistent interaction in the selected object.
  """

  def __init__(self, message: str = 'Interaction not found'):
    self.message = message
    super().__init__(self.message)
