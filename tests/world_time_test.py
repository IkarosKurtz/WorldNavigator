import pytest

from worldnavigator.core.world_time import WorldTime


class TestWorldTime:
  @pytest.fixture(autouse=True)
  def setup(self):
    self.world_time = WorldTime()

  def test_initialization(self):
    """
    Test that WorldTime initializes with the correct default values.

    Arrange & Act:
      - Create an instance of WorldTime.

    Assert:
      - Verify that amount_of_time is set to 5.
      - Verify that the initial time is set to 12:00.
    """
    # Arrange & Act
    world_time = self.world_time

    # Assert
    assert world_time.amount_of_time == 5
    assert world_time.show_clock() == "12:00"
    assert world_time.show_clock("12:00") == "12:00 PM"
    assert world_time.show_date("DD/MM/YYYY") == "29/05/2025"
    assert world_time.show_date("DD/MM/YYYY", True) == "29/May/2025"
    assert world_time.show_date("DD-MM-YYYY") == "29-05-2025"
    assert world_time.show_date("MM-DD-YYYY") == "05-29-2025"
    assert world_time.show_date("MM/DD/YYYY") == "05/29/2025"
    assert world_time.show_date("YYYY-MM-DD") == "2025-05-29"
    assert world_time.show_date("YYYY/MM/DD") == "2025/05/29"

    assert world_time.get_time() == (12, 0)

  def test_adjust_time_amount(self):
    """
    Test that the adjust_time method correctly updates the time amount.

    Arrange:
      - Create an instance of WorldTime.

    Act:
      - Call adjust_time with a new amount.

    Assert:
      - Verify that the amount_of_time is updated to the new value.
    """
    # Arrange & Act
    self.world_time.adjust_time(10)  # This should set the time amount to 10 minutes per second

    # Assert
    assert self.world_time.amount_of_time == 10
    assert self.world_time.get_time() == (12, 0)
    assert self.world_time.show_clock() == "12:00"

    # Act
    self.world_time.update_time()  # This should add 10 minutes

    # Assert
    assert self.world_time.show_clock() == "12:10"
    assert self.world_time.get_time() == (12, 10)

  def test_update_time(self):
    """
    Test that the update_time method correctly updates the time and handles overflow.

    Arrange:
      - Set the time to 23:55.
      - Set the time to 22:55.

    Act:
      - Call update_time with an amount that causes minutes to overflow.

    Assert:
      - Verify that the hours and minutes are updated correctly after overflow.
    """
    # Arrange
    self.world_time.override_time(23, 55)

    # Act
    self.world_time.update_time()  # This should add 5 minutes, causing overflow

    # Assert
    assert self.world_time.show_clock() == "00:00"  # Time should reset to 00:00 after overflow

    # Arrange
    self.world_time.override_time(22, 55)

    # Act
    self.world_time.update_time()  # This should add 5 minutes

    # Assert
    assert self.world_time.show_clock() == "23:00"  # Time should be 23:00

    # Arrange & Act
    self.world_time.override_time(23)  # This should set time to 23:00

    # Assert
    assert self.world_time.show_clock() == "23:00"

    # Arrange & Act
    with pytest.raises(ValueError) as exc_info:
      self.world_time.override_time(25, 0)

    # Assert
    assert "Hours must be between 0 and 23, got 25" == str(exc_info.value)

    # Arrange & Act
    with pytest.raises(ValueError) as exc_info:
      self.world_time.override_time(23, 60)

    # Assert
    assert "Minutes must be between 0 and 59, got 60" == str(exc_info.value)

  def test_update_date(self):
    """
    Test that the update_time method correctly updates the date and handles overflow.

    Arrange:
      - Set the date to January 31st.
      - Set the date to December 31st.

    Act:
      - Call update_time with an amount that causes day to overflow.

    Assert:
      - Verify that the day, month, and year are updated correctly after overflow.
    """
    # Arrange
    self.world_time.override_date(day=31, month=1, year=2024)
    self.world_time.override_time(23, 55)  # Set time to 23:55 to cause day overflow

    # Act
    self.world_time.update_time()  # This should add 5 minutes, causing day overflow

    # Assert
    assert self.world_time.show_date() == "01/02/2024"  # Date should be February 1st after overflow

    # Arrange
    self.world_time.override_date(day=31, month=12, year=2024)
    self.world_time.override_time(23, 55)  # Set time to 23:55 to cause day and month overflow

    # Act
    self.world_time.update_time()  # This should add 5 minutes, causing day and month overflow

    # Assert
    assert self.world_time.show_date() == "01/01/2025"  # Date should be January 1st of the next year after overflow

    # Arrange & Act
    with pytest.raises(ValueError) as exc_info:
      self.world_time.override_date(day=30, month=2, year=2024)

    # Assert
    assert "Day must be between 1 and 28 for month February, got 30" == str(exc_info.value)

    # Arrange & Act
    with pytest.raises(ValueError) as exc_info:
      self.world_time.override_date(day=1, month=13, year=2024)

    # Assert
    assert "Month must be between 1 and 12, got 13" == str(exc_info.value)

  def test_time_update_callbacks(self):
    """
    Test that time and date listeners are called correctly when time and date are updated.

    Arrange:
      - Create mock listener functions for time and date updates.

    Act:
      - Set the time and date listeners.
      - Update the time and date.

    Assert:
      - Verify that the listeners were called with the correct parameters.
    """
    # Arrange
    time_listener_called = False
    date_listener_called = False

    def time_listener(time):
      nonlocal time_listener_called
      time_listener_called = True
      assert time.hours == 12
      assert time.minutes == 0

    def date_listener(date):
      nonlocal date_listener_called
      date_listener_called = True
      assert date == [29, 5, 2025]

    # Act
    self.world_time.listen_for_time(time_listener)
    self.world_time.listen_for_date(date_listener)

    self.world_time.override_time(12, 0)  # This should trigger the time listener
    self.world_time.override_date(day=29, month=5, year=2025)  # This should trigger the date listener

    # Assert
    assert time_listener_called
    assert date_listener_called

    # Arrange
    time_listener_called = False
    date_listener_called = False

    # Act
    def time_listener(time):
      nonlocal time_listener_called
      time_listener_called = True

    def date_listener(date):
      nonlocal date_listener_called
      date_listener_called = True

    self.world_time.listen_for_time(time_listener)
    self.world_time.listen_for_date(date_listener)
    self.world_time.update_time()  # This should trigger the time listener and update the date if needed

    # Assert
    assert time_listener_called

    # Arrange
    time_listener_called = False
    self.world_time.override_time(23, 55)  # Set time to 23:55

    # Act
    self.world_time.update_time()  # This should add 5 minutes, causing day overflow

    # Assert
    assert time_listener_called
    assert date_listener_called
