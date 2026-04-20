class DuplicatedLocationError(Exception):
  """
  Exception raised when a location is added to a world with the same name.

  This error is raised when attempting to add a location to a world
  where that location is already present.
  """

  def __init__(self, message: str = "The location is already connected."):
    self.message = message
    super().__init__(self.message)
