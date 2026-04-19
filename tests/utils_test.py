import functools

from worldnavigator.utils.functions import is_a_valid_function, is_valid_prop_value


class TestUtils:
  def test_is_valid_prop_value(self):
    """
    Test the is_valid_prop_value function that checks if a value is a valid property type for Params class.

    Arrange:
      - Define a set of valid and invalid values to test.

    Act & Assert:
      - For each valid value, assert that is_valid_prop_value returns True.
      - For each invalid value, assert that is_valid_prop_value returns False.
    """

    # Arrange
    valid_values = [
      str,
      int,
      bool,
      float,
      (str, "A string type"),
      (int, "An integer type"),
      (bool, "A boolean type"),
      (float, "A float type"),
    ]

    # Act & Assert
    for value in valid_values:
      assert is_valid_prop_value(value), f"Expected {value} to be valid"

    invalid_values = [
      list,
      dict,
      (list, "A list type"),
      (dict, "A dict type"),
      (str, 123),  # Invalid because description is not a string
      (int, None),  # Invalid because description is not a string
      (bool, 456),  # Invalid because description is not a string
      (float, []),  # Invalid because description is not a string
      "Not a type or tuple",
      (str,),  # Invalid because it's a tuple but does not have two elements
      (str, "A string type", "Extra element"),  # Invalid because it has more than two elements
    ]

    for value in invalid_values:
      assert not is_valid_prop_value(value), f"Expected {value} to be invalid"

  def test_is_valid_function(self):
    """
    Test the is_a_valid_function function that checks if a given function is a valid callable.

    Arrange:
      - Define a set of valid and invalid functions to test.

    Act & Assert:
      - For each valid function, assert that is_a_valid_function returns True.
      - For each invalid function, assert that is_a_valid_function returns False.
    """

    # Arrange
    def valid_function1():
      pass

    invalid_function1 = "Not a function"
    invalid_function2 = lambda x: x  # noqa: E731
    invalid_function3 = functools.partial(valid_function1)

    # Act & Assert
    assert is_a_valid_function(valid_function1), "Expected valid_function1 to be a valid function"
    assert not is_a_valid_function(invalid_function1), "Expected invalid_function1 to be an invalid function"
    assert not is_a_valid_function(invalid_function2), "Expected invalid_function2 to be an invalid function"
    assert not is_a_valid_function(invalid_function3), "Expected invalid_function3 to be an invalid function"
