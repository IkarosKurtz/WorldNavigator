class IsNotAFunctionError(Exception):
  """
  Exception raised when the listener is not a normal function.

  This error is raised when user don't use a function like a valid listener.
  """

  def __init__(self, message: str = "Your listener is not the correct type"):
    self.message = message
    super().__init__(self.message)
