Functions
=========

WorldNavigator provides several helpful functions, some of which are required for specific purposes.

Helper Functions
----------------

.. py:function:: character_is_selected(character: GameCharacter) -> bool

  Checks if the specified character is currently selected by the player.
  This is particularly useful when you want to display dialogues for a specific character in a location.

  :param GameCharacter character: The character to check for selection.

  :return: True if the character is selected, False otherwise.

  Example:

  .. code-block:: renpy

    label story:
      if character_is_selected(e):
        e "Hello, how are you?"

.. py:function:: show_toast(message: str, title: str = "Information", duration: int = 2.3, toast_type: str = 0)

  Displays a toast-like notification on the screen, similar to those in web applications.
  There are 5 types of toast notifications:

  - ``0``: Informative
  - ``1``: Alert
  - ``2``: Warning
  - ``3``: Danger
  - ``4``: Debug

  :param str message: The message text to display.
  :param str title: The title of the toast notification (defaults to "Information").
  :param float duration: How long the toast should remain visible in seconds.
  :param int toast_type: The type of toast notification (0-4).
  
  Example:

  .. code-block:: renpy

    label chapter1:
      $ show_toast("Time has been frozen", "Time Freeze", toast_type=1)

      # You can also use the screen to display the toast
      # show expression toast("Time has been frozen", "Time Freeze", toast_type=1)

      e "It's boring here. Have you ever felt like time moves slower sometimes?"

Required Functions
--------------------

.. py:function:: register_basic_listeners()

  This function must be called in both the ``after_load`` and ``start`` labels.
  It sets up the essential event listeners required for WorldNavigator to function properly.
  Without calling this function, your game will not work correctly.

