class MissingDayBackgroundError(Exception):
  """
  Exception raised when a day background is missing for a location.

  This error is raised when the world parser detects that a location
  doesn't have the required background for daytime.

  :param str location_name: Name of the location missing the day background
  :param str message: Error message with details
  """

  def __init__(self, location_name: str, message: str = None):
    self.location_name = location_name
    if message is None:
      message = f'Missing day background for location "{location_name}"'
    else:
      message += f'\n\n Location name: "{location_name}"'

    self.message = message
    super().__init__(self.message)
