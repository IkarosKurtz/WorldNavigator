Assets and Variables
====================

WorldNavigator uses various assets and variables to function properly. While these assets can be replaced with your own, it's important to note that most audio files are designed to be looped for a seamless experience.

Sounds and Effects (SFX)
------------------------

WorldNavigator includes several predefined ambient sounds that create immersive atmospheres. These sounds are implemented using Ren'Py's `partial playback`_ feature for seamless looping. If you wish to replace these sounds with your own, we recommend either:

1. Using the same partial playback method for looping
2. Creating pre-looped audio files

When creating looped audio, we recommend using `.ogg` format rather than `.mp3`, as MP3 files often introduce imperceptible silence at the beginning of playback, which can disrupt the seamless loop experience.

.. _partial playback: https://www.renpy.org/doc/html/audio.html#partial-playback

.. code-block:: renpy

  # Rain sounds
  define rain_sound.soft_rain = "<from 47.356 to 489.012>mod_assets/sfx/rain/soft_rain.mp3"
  define rain_sound.soft_indoor_rain = "<from 20.149 to 53.877>mod_assets/sfx/rain/soft_indoor_rain.mp3"
  define rain_sound.hard_rain = "<from 19.447 to 63.843>mod_assets/sfx/rain/hard_rain.mp3"
  define rain_sound.hard_indoor_rain = "<from 216.959 to 752.292>mod_assets/sfx/rain/hard_indoor_rain.mp3"
  define thunder_sound = "mod_assets/sfx/rain/thunder.mp3"

These sounds are designed to play in loops within the specified time ranges. The sound library includes:

- Soft rain (outdoor) - Gentle rainfall ambient sound for outdoor scenes
- Soft rain (indoor) - Subtle rainfall sound as heard from inside buildings
- Heavy rain (outdoor) - Intense rainfall for stormy outdoor scenes
- Heavy rain (indoor) - Heavy rainfall as heard from inside buildings
- Thunder - One-time effect that plays during stormy weather

Utility Variables
-----------------

WorldNavigator defines several key utility variables that are essential for proper functionality:

.. code-block:: renpy

  define fadeIn = Fade(0, 0, 0.5)  # Transition used to fade backgrounds
  define selected_char = None  # Currently selected character

The ``fadeIn`` transition can be customized to any other Ren'Py transition according to your preferences. However, the ``selected_char`` variable is critical to the core functionality of WorldNavigator, as it's used internally by the :py:func:`character_is_selected` function. This function is essential when implementing character dialogue interactions. For more information on functions, see :doc:`/source/renpy/components/functions`.

Weather Configuration
---------------------

WorldNavigator's sophisticated weather system is controlled by a dictionary that defines various weather conditions and how they affect both indoor and outdoor environments:

.. code-block:: python

  define weather_config = {
    'Rainy': {
      'indoor': {'screen': None, 'music': rain_sound.soft_indoor_rain, 'volume': 1.2},
      'outdoor': {'screen': 'rain', 'music': rain_sound.soft_rain, 'volume': 1.0},
    },
    'Stormy': {
      'indoor': {'screen': None, 'music': rain_sound.hard_indoor_rain, 'volume': 0.65},
      'outdoor': {'screen': 'stormy', 'music': rain_sound.hard_rain, 'volume': 0.7},
    },
    'Snowy': {
      'indoor': {'screen': None, 'music': None, 'volume': 0.0},
      'outdoor': {'screen': 'snow', 'music': None, 'volume': 0.0},
    },
  }

This configuration system allows you to define for each weather type (Rainy, Stormy, Snowy):

- The visual screen effects to display (or None for no effect)
- The ambient sounds to play (linked to the sound definitions above)
- The appropriate volume level for the sound effects

Each weather type has distinct settings for both indoor and outdoor environments, allowing for a highly immersive experience as characters move between locations.

