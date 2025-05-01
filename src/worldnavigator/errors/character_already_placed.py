class CharacterAlreadyPlacedError(Exception):
  """
  Exception raised when a character is already placed in a location.

  This error is raised when attempting to add a character to a location
  where that character is already present.
  """

  def __init__(self, character_name: str, location_name: str, message: str = None):
    self.character_name = character_name
    self.location_name = location_name

    if message is None:
      message = f'Character "{character_name}" is already placed in location "{location_name}"'
    else:
      message += f'\nCharacter name: "{character_name}"'
      message += f'\nLocation name: "{location_name}"'

    self.message = message
    super().__init__(self.message)
