from threading import Event, Thread
import time


class WorldTime:
  """
  Used to handle the time in the world, essential for weather and changing backgrounds.

  The initial time is set to 12:00, the hours are in 24-hour format, this can't be changed,
  but you can change the initial time.
  """

  def __init__(self, initial_time: list[int] = [12, 0]) -> None:
    """
    :param list[int] initial_time: The initial time of the world, default is 12:00
    """
    self._clock = initial_time
    self._thread: Thread = None
    self._time_amount = 5
    self._freeze_time = Event()
    self._freeze_time.set()

  #################################################
  ################### Properties ##################
  #################################################

  @property
  def amount_of_time(self) -> int:
    """
    The amount of time (in minutes) that passes each second.
    default is 5, so 1 real time second = 5 game minutes.
    """
    return self._time_amount

  #################################################
  ################ Private Methods ################
  #################################################

  def _update_time(self) -> None:
    """
    Updates the time in the background.

    This is called every second, so it's important to keep it as light as possible.
    """
    self._clock[1] += self._time_amount
    surplus = abs(60 - self._clock[1])

    if self._clock[1] >= 60:
      self._clock[0] += 1
      self._clock[1] = surplus

    if self._clock[0] >= 24:
      self._clock[0] = 0

  def _update_time_thread(self) -> None:
    """
    Thread that updates the time in the background.
    """
    print('Starting time thread')
    while True:
      self._freeze_time.wait()

      self._update_time()

      time.sleep(1)

  #################################################
  ################ Public Methods #################
  #################################################

  def show_clock(self) -> str:
    """
    Get the current time in the format 'HH:MM', remember that the hours are in 24-hour format.

    :return: The current time in the format 'HH:MM'
    """
    hours = self._clock[0] if self._clock[0] >= 10 else f'0{self._clock[0]}'
    minutes = self._clock[1] if self._clock[1] >= 10 else f'0{self._clock[1]}'

    return f'{hours}:{minutes}'

  def start_time(self) -> None:
    """
    Start the time thread, this is used to update the time in the background.

    Has two implementations depending where it's called, from Ren'Py or Python.
    For Ren'Py it's using ``renpy.invoke_in_thread``, for Python it's using the ``Thread`` class,
    they basically do the same thing.
    """
    if 'renpy' in globals():
      renpy.invoke_in_thread(self._update_time_thread)  # type: ignore
    else:
      self._thread = Thread(target=self._update_time_thread, daemon=True)
      self._thread.start()

  def adjust_time(self, amount: int) -> None:
    """
    Adjust the amount of time that passes each second.

    :param int amount: The amount of time (in minutes) that passes each second.

    >>> world.time.adjust_time(5)
    >>> # 1 real time second = 5 game minutes
    """
    self._time_amount = amount

  def freeze_time(self) -> None:
    """
    Freeze the time, so it doesn't change, this also stops weather from changing.
    """
    self._freeze_time.clear()

  def unfreeze_time(self) -> None:
    """
    Unfreeze the time, so it can change again, this also starts weather from changing.
    """
    self._freeze_time.set()

  def is_time_frozen(self) -> bool:
    """
    Check if the time has been frozen, helpful for checking if the weather should change.
    """
    return not self._freeze_time.is_set()
