from threading import Event, Thread
import time


class WorldTime:
  def __init__(self) -> None:
    self._clock = [6, 48]
    self._thread: Thread = None
    self._time_amount = 1
    self._freeze_time = Event()
    self._freeze_time.set()

  #################################################
  ################ Private Methods ################
  #################################################

  def _update_time(self) -> None:
    self._clock[1] += self._time_amount
    surplus = abs(60 - self._clock[1])

    if self._clock[1] >= 60:
      self._clock[0] += 1
      self._clock[1] = surplus

    if self._clock[0] >= 24:
      self._clock[0] = 0

  def _update_time_thread(self) -> None:
    print('Starting time thread')
    while True:
      self._freeze_time.wait()

      self._update_time()

      time.sleep(1)

  #################################################
  ################### Properties ##################
  #################################################

  @property
  def amount_of_time(self) -> int:
    return self._time_amount

  #################################################
  ################ Public Methods #################
  #################################################

  def show_clock(self):
    hours = self._clock[0] if self._clock[0] >= 10 else f'0{self._clock[0]}'
    minutes = self._clock[1] if self._clock[1] >= 10 else f'0{self._clock[1]}'

    return f'{hours}:{minutes}'

  def start_time(self) -> None:
    if 'renpy' in globals():
      renpy.invoke_in_thread(self._update_time_thread)  # type: ignore
    else:
      self._thread = Thread(target=self._update_time_thread, daemon=True)
      self._thread.start()

  def change_time(self, amount: int) -> None:
    self._time_amount = amount

  def freeze_time(self) -> None:
    self._freeze_time.clear()

  def unfreeze_time(self) -> None:
    self._freeze_time.set()

  def is_time_frozen(self) -> bool:
    return not self._freeze_time.is_set()
