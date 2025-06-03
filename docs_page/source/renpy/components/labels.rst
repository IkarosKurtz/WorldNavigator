Special Labels
==============
To use WorldNavigator correctly, you need to understand several special labels and ensure you ``do not remove others``.

There is one essential label: `story`_, which is where the magic happens. This is where you define your story, while everything else like weather, interface, background updates, etc. is handled by another label called `beginning`_.

There are two additional special labels used by Ren'Py. If you want to add WorldNavigator to your project and you have already modified `after_load`_ or `start`_, you'll need to add a single function to initialize everything: :py:func:`register_basic_listeners`.

.. warning:: 

  Using :py:func:`register_basic_listeners` is mandatory. Without it, your game will crash because this function sets up the basic listeners for WorldNavigator.

.. _after_load: https://www.renpy.org/doc/html/label.html#special-labels

.. _start: https://www.renpy.org/doc/html/label.html#special-labels


.. _story:

Story Label
-----------
You can define your narrative content within this label.

For example, if you want to create a ``chapter 1``, you can add all the dialogues for your first chapter here. This label is called multiple times - specifically, each time the player changes location or completes a chapter/dialogue sequence.

.. attention:: 

  It's important to use ``return`` at the end of the label. The `beginning`_ label handles the game's logic, and when you return from the story label, control loops back to the beginning label, which will then call your story label again.

Example:

.. code-block:: renpy

  image eileen_1:
    "eileen_1.png"
    zoom 1.5

  image eileen_2:
    "eileen_2.png"
    zoom 1.5

  define e = GameCharacter("Eileen")

  label story:
    if character_is_selected(e):
      $ world_time.freeze_time() # Freeze time while Eileen is talking
      
      e "It's raining outside..."
      e "I just hope it stops raining soon. I need to go outside."
      e "..."

      $ selected_char = None # This is an important line - it resets the selected character. Without this, dialogues would repeat endlessly.
      $ world_time.unfreeze_time()

    return

In the example above, you can see that dialogue only appears when Eileen is the selected character. See :py:func:`character_is_selected` and :doc:`/source/renpy/components/variables` for more information.

For better code organization, you can create separate labels for different story chapters:

.. code-block:: renpy

  image eileen_1:
    "eileen_1.png"
    zoom 1.5

  image eileen_2:
    "eileen_2.png"
    zoom 1.5

  define e = GameCharacter("Eileen")

  label chapter1:
    $ world_time.freeze_time() # Freeze time during dialogue

    e "It's raining outside..."
    e "I just hope it stops raining soon. I need to go outside."
    e "..."

    $ selected_char = None # Reset the selected character to prevent dialogue loops
    $ world_time.unfreeze_time()

    return # Returning control to the calling label is crucial

  label story:
    if character_is_selected(e):
      call chapter1

    return 

This modular approach allows you to organize your narrative into separate chapters. When the story label calls chapter1, it waits for that label to complete before continuing execution. After chapter1 returns, the story label continues and eventually returns to the main game loop.

.. attention:: 

  It's essential to use ``call`` and ``return`` rather than ``jump``. The system needs to return to the main loop label, and if you use ``jump``, execution will not return to the main loop unless you explicitly jump back to the beginning label after your chapter.

.. _beginning:

Beginning Label
---------------
This label handles the game's core logic. It updates the weather, displays the interface, and serves as the main loop. When you start the game, execution enters here first. Everything is updated and then control passes to the story label using Ren'Py's `call`_ statement. When the story label returns, the beginning label is called again, continuing the loop.

If you understand how this works, you can customize the logic to suit your needs. **However, be careful: the world_info screen must be displayed, as it updates time and weather. If you don't show it, time and weather will not be updated correctly.**

Here is the code for the beginning label:

.. code-block:: renpy

  label beginning:
    $ change_weather_expression()

    show screen world_info
    scene expression change_bg_expression() with fadeIn

    call screen location_selector(current_location.characters, list(current_location.connections.values()))

    call story

    jump beginning


.. _call: https://www.renpy.org/doc/html/label.html#call-statement

After Load Label
----------------
This label is implemented by Ren'Py and is called when a game is loaded from save files. WorldNavigator implements this label to set up your world. If you already use this label in your project, simply add :py:func:`register_basic_listeners` to your existing implementation.

After Load label implementation:

.. code-block:: renpy

  label after_load:
    python:
      register_basic_listeners()

    return

Start Label
-----------
This label is implemented by Ren'Py and is called when starting a new game. WorldNavigator does not implement this label automatically, so you need to implement it yourself.

You should use this label to set up your world - add characters to locations, add objects, and configure other initial game state.

Example:

.. code-block:: renpy

  label start:
    python:
      register_basic_listeners()

      world.time.adjust_time(10) # 1 second equals 10 game minutes
      # Additional setup code...

    jump beginning # This is crucial - you must jump to the beginning label to start the main game loop.
