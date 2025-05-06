class LocationNotFoundError(Exception):
  """
  Exception raised when a location is not found in the selected location.

  This error is raised when attempting to access a location that does not exist in the selected location.
  """

  def __init__(self, location_name: str, message: str = None):
    self.location_name = location_name

    if message is None:
      message = f'Location "{location_name}" not found'
    else:
      message += f'\nLocation: "{location_name}"'

    self.message = message
    super().__init__(self.message)
