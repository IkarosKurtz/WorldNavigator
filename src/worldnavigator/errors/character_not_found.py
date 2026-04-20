class CharacterNotFoundError(Exception):
  """
  Exception raised when a character is not found in the selected location.

  This error is raised when attempting to access a character that does not exist
  in the selected location.
  """

  def __init__(self, message: str = "Character not found."):
    self.message = message
    super().__init__(self.message)
