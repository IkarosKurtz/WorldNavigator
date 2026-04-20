class CharacterAlreadyPresentError(Exception):
  """
  Exception raised when a character is already present in a location.

  This error is raised when attempting to add a character to a location
  where that character is already present.
  """

  def __init__(self, message: str = "Character already present in this location."):
    self.message = message
    super().__init__(self.message)
