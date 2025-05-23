Core
====

The Core module forms the foundation of the WorldNavigator framework. It provides the essential classes and functions needed to create, parse, and interact with virtual worlds.

World
-----

.. automodule:: worldnavigator.core.world
   :members:
   :show-inheritance:
   :undoc-members:

World Parser
------------

.. automodule:: worldnavigator.core.world_parser
   :members:
   :show-inheritance:
   :undoc-members:

WorldObject
-----------

.. automodule:: worldnavigator.core.world_object
   :members:
   :show-inheritance:
   :undoc-members:

Examples

.. code-block:: python

   from typing import Annotated, Literal
   from worldnavigator.core import WorldObject
   from worldnavigator.decorators import evaluate_events
   from worldnavigator.types import Params


   @evaluate_events  # Used to check if the events have the correct format
   class MyEvents:
     read: Annotated[str, Params(time=float)]


   # Event names are optional, but it's good practice to use them to avoid typos
   # You will get an error if something is wrong
   Events = Literal['read', 'open']

   book = WorldObject[MyEvents, Events]('Ancient Book')
   # If 'Events' is not needed, pass None instead, otherwise you will get an error
   # book = WorldObject[MyEvents, None]('Ancient Book')


   def read(time: float):
     print(f'Ancient Book was read for {time} seconds')


   book.register_interaction('read', read)

   book.interact('read', time=24.53)

.. code-block:: text

   > Ancient Book was read for 24.53 seconds

It is important to ensure that types, parameters, and definitions are correctly specified, otherwise errors will occur.
If you don't provide a proper type in ``Params(time=...)``, you will get an error. Always specify the type like this:
``Params(time=float)``, ``Params(time=int)``, ``Params(time=str)``, etc. Only :py:data:`~worldnavigator.types.types.BASIC_TYPES` are allowed.

When you interact and send data like this:

.. code-block:: python

   ...

   book.interact('read', time=24.53)

You will get an error if the value is not the correct type for the parameter. You will also get an error if the parameter name is incorrect or not defined in the `Params` class. All of these validations are also applied to callbacks in the ``register_interaction`` method.

.. caution:: 

   Type and parameter checking occurs only at runtime, not during static type checking, due to implementation limitations.
