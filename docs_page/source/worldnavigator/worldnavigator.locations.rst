Location
=========

.. autoclass:: worldnavigator.locations.base_location.Location
   :members:
   :special-members: __call__
   :show-inheritance:
   :undoc-members:

Location Backgrounds
---------------------

Class to manage background for locations. Store backgrounds and provide a simple way to get the background for a specific time of day.

.. autoclass:: worldnavigator.locations.base_location.LocationBackground
   :members:
   :show-inheritance:
   :undoc-members:

.. code-block:: python

   from worldnavigator.locations import Location

   shop = Location(
      name='Shop',
      backgrounds={
        'day': 'day_bg',
        'afternoon': 'afternoon_bg',
        'night': 'night_bg',
      },
      is_indoor=True
   )

   print(shop.backgrounds.retrieve_scene_background([12, 0]))

.. code-block:: bash

   > day_bg

.. code-block:: python

   from worldnavigator.locations import Location

   shop = Location(
      name='Shop',
      backgrounds={
        'day': 'day_bg',
        'afternoon': 'afternoon_bg',
        'night': 'night_bg',
      },
      is_indoor=True
   )

   print(shop.backgrounds.retrieve_scene_background([17, 0]))

.. code-block:: bash

   > afternoon_bg

.. code-block:: python

   from worldnavigator.locations import Location

   shop = Location(
      name='Shop',
      backgrounds={
        'day': 'day_bg',
        'afternoon': 'afternoon_bg',
        'night': 'night_bg',
      },
      is_indoor=True
   )

   print(shop.backgrounds.retrieve_scene_background([21, 0]))

.. code-block:: bash

   > night_bg

