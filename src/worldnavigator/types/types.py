BASIC_TYPES = (int, float, str, bool)


class Params:
  def __init__(self, **params):
    self._params = params

  @property
  def items(self):
    return self._params.items()

  @property
  def params(self):
    return self._params

  def __str__(self):
    return str(self._params)

  def __repr__(self):
    return self.__str__()
