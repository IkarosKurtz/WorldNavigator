Events
======

There is a list of predefined events for locations, like ``character_added``, ``character_removed``, etc. You can listen to these events to react to changes in some locations, for example, when a character enters a room.


.. autodata:: worldnavigator.observer.events.EventName


Example of use of the events:

.. code-block:: python
  
  from worldnavigator.locations import Location

  shop = Location(
    name="Shop",
    backgrounds={
      "day": "day_bg",
    },
    is_indoor=True
  )

  shop.on('character_added', lambda name, location: print(f'Character {name} added to {location}'))

  shop.add_character('Mike')

.. code-block:: bash

  > Character Mike added to Shop

Events Parameters
-----------------

.. automodule:: worldnavigator.observer.events
  :members:
  :show-inheritance:
  :exclude-members: EventName
  :undoc-members:
