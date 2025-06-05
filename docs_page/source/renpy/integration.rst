Setup
==============

Installation
------------

WorldNavigator provides a dedicated package for seamless integration with Ren'Py. You can download the latest version of this package from our official repository.

1. Download the latest version of the package from `here`_.
2. Unzip the package and copy all files from the ``worldnavigator`` folder into your Ren'Py project's ``game`` folder.
3. That's it! Installation complete.

.. _here: https://github.com/IkarosKurtz/WorldNavigator/releases

Integration
-----------

After installing the package, there are additional steps required depending on whether you're using a new or existing project.

New Project
^^^^^^^^^^^

When starting a new project, you'll notice a ``special_labels.rpy`` file in your ``game`` folder. This file contains special labels that control WorldNavigator's behavior. For more information, see :doc:`/source/renpy/components/labels`.

Within this file, you'll find a label called ``after_load`` which isn't defined when you initially create a project. If you don't plan to implement custom save functionality, you can safely ignore this file. However, it's important to understand that **this label is essential for properly initializing WorldNavigator with your save data**, as explained in the :ref:`After Load Label` section.

The ``after_load`` label is a powerful hook that Ren'Py automatically executes immediately after loading a saved game, before returning control to the saved position. This strategic timing provides a critical opportunity to reinitialize systems, reconstruct state that may not persist through saves, update variables between game versions, or synchronize with external services.

.. code-block:: renpy

  label after_load:
    python:
      register_basic_listeners() # Sets up important listeners and other core functionality

    return

The :py:func:`register_basic_listeners` function is essential for WorldNavigator to function properly. You must call it in your
``start`` label, and then jump to the ``beginning`` special label. See :ref:`Beginning Label` to understand why this sequence is important.

.. code-block:: renpy

  label start:
    python:
      register_basic_listeners() # Sets up important listeners and other core functionality

    jump beginning # Jumps to the main loop of the WorldNavigator system

After completing this setup, you need to define your visual assets. As explained in :ref:`World Parser`, you must define backgrounds for each location in your `JSON` world file. If you used the :doc:`/source/editor/worldnavigator_editor`, the backgrounds correspond to what you specified in the `Add Location` form. Define these backgrounds as you would in any standard Ren'Py project.

Example:

.. code-block:: json

  // my_world.world.json
  {
    "name": "My World",
    "locations": [
      {
        "name": "School",
        "is_indoor": false,
        "backgrounds": {
          "day": "bg school",
          "night": "bg school_night"
        },
        "connected_locations": ["Main Entrance"]
      },
      {
        "name": "Main Entrance",
        "is_indoor": true,
        "backgrounds": {
          "day": "bg main_entrance",
          "night": "bg main_entrance_night"
        },
        "connected_locations": []
      }
    ]
  }

You must define your Ren'Py background images using exactly the same names as specified in your World file:

.. code-block:: renpy

  define bg school = "bg_school"
  define bg school_night = "bg_school_night"
  define bg main_entrance = "bg_main_entrance"
  define bg main_entrance_night = "bg_main_entrance_night"

Next, create the special label ``story`` which serves as the main entry point for your narrative content. See :ref:`Story Label` for detailed information.

.. code-block:: renpy

  label story:
    if character_is_selected(e):
      $ world_time.freeze_time() # Freeze time while Eileen is talking
      
      e "It's raining outside..."
      e "I just hope it stops raining soon. I need to go outside."
      e "..."

      $ selected_char = None # Critical line - resets the selected character to prevent dialogue loops
      $ world_time.unfreeze_time()

    return

An important consideration is character definition. While Ren'Py uses the `Character` class, WorldNavigator uses :py:class:`~worldnavigator.core.character.GameCharacter`. You must modify your character definitions accordingly.

The ``GameCharacter`` class is a wrapper around Ren'Py's `Character` class, providing additional functionality while maintaining compatibility. See :ref:`Character` for comprehensive details.

.. code-block:: renpy

  define e = GameCharacter("Eileen")
  define mc = GameCharacter("player", dynamic=True)

Existing Project
^^^^^^^^^^^^^^^^

When integrating WorldNavigator into an existing project, follow the same steps outlined for new projects, with special attention to modifying your ``start`` label. You must call the :func:`register_basic_listeners` function and then jump to the ``beginning`` special label.

For the ``after_load`` label, you have two options:

1. If you already have this label defined, add the call to :func:`register_basic_listeners` and remove the label from ``special_labels.rpy``
   
2. If you don't have this label defined, you can use the one provided in ``special_labels.rpy``
