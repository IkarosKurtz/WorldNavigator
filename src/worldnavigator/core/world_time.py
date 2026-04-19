from dataclasses import dataclass, field
from threading import Thread
from typing import Callable, Literal, Tuple

DateFormat = Literal[
  "DD/MM/YYYY",
  "MM/DD/YYYY",
  "YYYY/MM/DD",
  "DD-MM-YYYY",
  "MM-DD-YYYY",
  "YYYY-MM-DD",
]

ClockFormat = Literal[
  "12:00",
  "24:00",
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

  def __init__(self, initial_time: Time = Time(), amount_of_time: int = 5) -> None:
    """
    :param WorldWeather weather: The weather of the world.
    :param Time initial_time: The initial time of the world, default is 12:00
    :param int amount_of_time: The amount of time (in minutes) that passes each second, default is 5
    """
    self._clock = initial_time
    self._thread: Thread = None
    self._time_amount = amount_of_time

    self._time_listener: Callable[[Time], None] = None
    self._date_listener: Callable[[list[int]], None] = None

    self._date = [29, 5, 2025]

    self._months = [
      ("January", 31),
      ("February", 28),
      ("March", 31),
      ("April", 30),
      ("May", 31),
      ("June", 30),
      ("July", 31),
      ("August", 31),
      ("September", 30),
      ("October", 31),
      ("November", 30),
      ("December", 31),
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

  #################################################
  ################ Private Methods ################
  #################################################

  #################################################
  ################ Public Methods #################
  #################################################

  def update_time(self) -> None:
    """
    Updates the time in the background.

    This is called every second, so it's important to keep it as light as possible.
    """
    self._clock.minutes += self._time_amount
    surplus = abs(60 - self._clock.minutes)

    if self._clock.minutes >= 60:
      self._clock.hours += 1

      # Change weather

      self._clock.minutes = surplus

    if self._clock.hours >= 24:
      self._clock.hours = 0
      self._date[0] += 1

      # Update date
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

  def show_clock(self, format: ClockFormat = "24:00") -> str:
    """
    Get the current time, in the format specified

    :param ClockFormat format: The format of the time to return. By default it's '24:00'.

    :return: The current time in the desired format
    """
    hours = self._clock.hours if self._clock.hours >= 10 else f"0{self._clock.hours}"
    minutes = self._clock.minutes if self._clock.minutes >= 10 else f"0{self._clock.minutes}"

    if format == "12:00":
      am_pm = "AM" if self._clock.hours < 12 else "PM"
      display_hours = hours if self._clock.hours <= 12 else f"{self._clock.hours - 12:02d}"

      return f"{display_hours}:{minutes} {am_pm}"
    elif format == "24:00":
      return f"{hours}:{minutes}"

  def show_date(self, format: DateFormat = "DD/MM/YYYY", full_month: bool = False) -> str:
    """
    Get the current date, in the format specified

    :param DateFormat format: The format of the date to return. By default it's 'DD/MM/YYYY'.
    :param bool full_month: Whether to show the full month name instead of the number.

    :return: The current date in the format specified
    """
    day = self._date[0]
    month = self._date[1]
    year = self._date[2]

    if full_month:
      month = self._months[month - 1][0]

    day = day if day >= 10 else f"0{day}"
    month = month if isinstance(month, str) or month >= 10 else f"0{month}"

    formats = {
      "DD-MM-YYYY": f"{day}-{month}-{year}",
      "DD/MM/YYYY": f"{day}/{month}/{year}",
      "MM-DD-YYYY": f"{month}-{day}-{year}",
      "MM/DD/YYYY": f"{month}/{day}/{year}",
      "YYYY-MM-DD": f"{year}-{month}-{day}",
      "YYYY/MM/DD": f"{year}/{month}/{day}",
    }

    return formats.get(format, f"{month}/{day}/{year}")

  def get_time(self) -> Tuple[int, int]:
    """
    Get the current time.

    :return: The current time.
    """
    return (self._clock.hours, self._clock.minutes)

  def adjust_time(self, amount: int) -> None:
    """
    Adjust the amount of time that passes each second.

    :param int amount: The amount of time (in minutes) that passes each second.

    >>> world.time.adjust_time(5)
    >>> # 1 real time second = 5 game minutes
    """
    self._time_amount = amount

  def override_time(self, hours: int, minutes: int = None) -> None:
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

    if minutes is not None and 0 <= minutes <= 59:
      self._clock.minutes = minutes
    elif minutes is None:
      self._clock.minutes = 0
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

    if self._date_listener:
      self._date_listener(self._date)

  #################################################
  ################ Dunder Methods #################
  #################################################

  def __getstate__(self):
    """
    Function for compatibility with pickle, used for renpy save/load.
    """
    state = self.__dict__.copy()
    hour, minute = self.get_time()

    del state["_thread"]
    del state["_time_listener"]
    del state["_date_listener"]
    del state["_clock"]
    state["_clock"] = {"hours": hour, "minutes": minute}
    print(f"Saving time: {state}")

    return state

  def __setstate__(self, state):
    """
    Function for compatibility with pickle, used for renpy save/load.
    """
    clock = state.pop("_clock")
    self.__dict__.update(state)
    print(f"Loading time: {state}")

    self._clock = Time(clock["hours"], clock["minutes"])

    self._time_listener = None
    self._date_listener = None
    self._threads = 0

    self._thread = None
