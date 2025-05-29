from dataclasses import dataclass, field
from threading import Event, Thread
import time
from typing import Callable, Literal, Tuple

from worldnavigator.weather.weather import WorldWeather

DateFormat = Literal[
  'DD/MM/YYYY',
  'MM/DD/YYYY',
  'YYYY/MM/DD',
  'DD-MM-YYYY',
  'MM-DD-YYYY',
  'YYYY-MM-DD',
]

ClockFormat = Literal[
  '12:00',
  '24:00',
]


@dataclass
class Time:
  hours: int = field(default=12)
  minutes: int = field(default=0)


class WorldTime:
  """
  Used to handle the time in the world, essential for weather and changing backgrounds.

  The initial time is set to 12:00, the hours are in 24-hour format, this can't be changed,
  but you can change the initial time.
  """

  def __init__(self, initial_time: Time = Time()) -> None:
    """
    :param list[int] initial_time: The initial time of the world, default is 12:00
    """
    self._clock = initial_time
    self._thread: Thread = None
    self._time_amount = 5
    self._freeze_time = Event()
    self._freeze_time.set()

    self._time_listener: Callable[[Time], None] = None
    self._date_listener: Callable[[list[int]], None] = None

    self._weather = WorldWeather()

    self._date = [29, 5, 2025]

    self._months = [
      ('January', 31),
      ('February', 28),
      ('March', 31),
      ('April', 30),
      ('May', 31),
      ('June', 30),
      ('July', 31),
      ('August', 31),
      ('September', 30),
      ('October', 31),
      ('November', 30),
      ('December', 31)
    ]

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

  @property
  def weather(self) -> WorldWeather:
    """
    Get the weather of the world.
    """
    return self._weather

  #################################################
  ################ Private Methods ################
  #################################################

  def _update_time(self) -> None:
    """
    Updates the time in the background.

    This is called every second, so it's important to keep it as light as possible.
    """
    self._clock.minutes += self._time_amount
    surplus = abs(60 - self._clock.minutes)

    if self._clock.minutes >= 60:
      self._clock.hours += 1

      # Change weather
      self._weather.update_weather()

      self._clock.minutes = surplus

    if self._clock.hours >= 24:
      self._clock.hours = 0
      self._date[0] += 1

      max_days = self._months[self._date[1] - 1][1]
      if self._date[0] > max_days:
        self._date[0] = 1
        self._date[1] += 1

      if self._date[1] > 12:
        self._date[1] = 1
        self._date[2] += 1

      if self._date_listener:
        self._date_listener(self._date)

    if self._time_listener:
      self._time_listener(self._clock)

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

  def listen_for_time(self, callback: Callable[[Time], None]) -> None:
    """
    Listen for the time, and call the callback with the current time, when time is updated.

    :param Callable[[Time], None] callback: The callback to call with the current time.
    """
    self._time_listener = callback

  def listen_for_date(self, callback: Callable[[list[int]], None]) -> None:
    """
    Listen for the date, and call the callback with the current date, when a new day starts.

    :param Callable[[list[int]], None] callback: The callback to call with the current date.
    """
    self._date_listener = callback

  def show_clock(self, format: ClockFormat = 'HH:MM') -> str:
    """
    Get the current time, in the format specified

    :param ClockFormat format: The format of the time to return. By default it's 'HH:MM'.

    :return: The current time in the desired format
    """
    hours = self._clock.hours if self._clock.hours >= 10 else f'0{self._clock.hours}'
    minutes = self._clock.minutes if self._clock.minutes >= 10 else f'0{self._clock.minutes}'

    if format == '12:00':
      am_pm = "AM" if self._clock.hours < 12 else "PM"
      display_hours = hours if self._clock.hours <= 12 else f'{self._clock.hours - 12:02d}'

      return f'{display_hours}:{minutes} {am_pm}'
    elif format == '24:00':
      return f'{hours}:{minutes}'
    else:
      return f'{hours}:{minutes}'

  def show_date(self, format: DateFormat = 'MM/DD/YYYY', full_month: bool = False) -> str:
    """
    Get the current date, in the format specified

    :param DateFormat format: The format of the date to return. By default it's 'MM/DD/YYYY'.

    :return: The current date in the format specified
    """
    day = self._date[0]
    month = self._date[1]
    year = self._date[2]

    if full_month:
      month = self._months[month - 1][0]

    formats = {
      'DD-MM-YYYY': f'{day}-{month}-{year}',
      'DD/MM/YYYY': f'{day}/{month}/{year}',
      'MM-DD-YYYY': f'{month}-{day}-{year}',
      'MM/DD/YYYY': f'{month}/{day}/{year}',
      'YYYY-MM-DD': f'{year}-{month}-{day}',
      'YYYY/MM/DD': f'{year}/{month}/{day}'
    }

    return formats.get(format, f'{month}/{day}/{year}')

  def get_time(self) -> Tuple[int, int]:
    """
    Get the current time.

    :return: The current time.
    """
    return (self._clock.hours, self._clock.minutes)

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

    self._weather.update_weather()

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

  def override_time(self, hours: int, minutes: int) -> None:
    """
    Override the current time, **is important to know that hours are in 24-hour format**,
    even if you use the 12:00 format in the :py:meth:`~worldnavigator.core.world_time.WorldTime.show_clock` method.

    This will trigger the listener for the time.

    :param int hours: The hours to override the time to. Must be between 0 and 23.
    :param int minutes: The minutes to override the time to. Must be between 0 and 59.
    """
    if 0 <= hours <= 23:
      self._clock.hours = hours
    else:
      raise ValueError(f"Hours must be between 0 and 23, got {hours}")

    if 0 <= minutes <= 59:
      self._clock.minutes = minutes
    else:
      raise ValueError(f"Minutes must be between 0 and 59, got {minutes}")

    if self._time_listener:
      self._time_listener(self._clock)

  def override_date(self, *, day: int = None, month: int = None, year: int = None) -> None:
    """
    Override the current date, this will trigger the listener for the date.

    :param int day: The day to override the date to.
    :param int month: The month to override the date to.
    :param int year: The year to override the date to.
    """
    if month:
      if 1 <= month <= 12:
        self._date[1] = month
      else:
        raise ValueError(f"Month must be between 1 and 12, got {month}")

    if day:
      max_days = self._months[self._date[1] - 1][1]

      if 1 <= day <= max_days:
        self._date[0] = day
      else:
        raise ValueError(f"Day must be between 1 and {max_days} for month {self._months[month - 1][0]}, got {day}")

    if year:
      self._date[2] = year
