class NoLocationsFoundError(Exception):
  """
  Exception raised when no locations are found during parsing.

  This error is raised when the world parser doesn't detect any locations
  in the provided world data.
  """

  def __init__(self, message: str = "No locations found in the world data"):
    self.message = message
    super().__init__(self.message)
