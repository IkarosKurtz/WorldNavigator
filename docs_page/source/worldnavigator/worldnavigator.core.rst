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

Character
------------

.. automodule:: worldnavigator.core.character
   :members:
   :show-inheritance:
   :undoc-members:

Examples in Python
******************

  .. code-block:: python

      from typing import TypedDict
      from worldnavigator.core import GameCharacter


      # This class is optional, but it's recommended to use it to avoid typos,
      # probably doesn't work in Ren'Py
      class MyData(TypedDict):
         inventory: list[str]
         health: int
         damage: int


      my_data: MyData = {
         'damage': 10,
         'health': 100,
         'inventory': ['sword', 'shield']
      }

      human = GameCharacter[MyData]("Human", data=my_data)
      # If you're not using a TypedDict, you can remove the brackets
      # human = GameCharacter("Human", data=my_data)

      print(f"Character name: {human.name}")
      print(f"Health: {human.data['health']}")
      print(f"Damage: {human.data['damage']}")
      print(f"Inventory: {human.data['inventory']}")

  Output:

  .. code-block:: text

      > Character name: Human
      > Health: 100
      > Damage: 10
      > Inventory: ['sword', 'shield']

  .. code-block:: python

      from typing import Callable, TypedDict
      from worldnavigator.core import GameCharacter


      # This class is optional, but it's recommended to use it to avoid typos,
      # probably doesn't work in Ren'Py
      class MyData(TypedDict):
         inventory: list[str]
         health: int
         damage: int

         print_stats: Callable[[], None]


      def print_stats(character: GameCharacter[MyData]):
         print(f"Character name: {character.name}")
         print(f"Health: {character.data['health']}")
         print(f"Damage: {character.data['damage']}")
         print(f"Inventory: {character.data['inventory']}")


      my_data: MyData = {
         'damage': 10,
         'health': 100,
         'inventory': ['sword', 'shield'],
         'print_stats': print_stats
      }

      human = GameCharacter[MyData]("Human", data=my_data)
      # If you're not using a TypedDict, you can remove the brackets
      # human = GameCharacter("Human", data=my_data)

      human.print_stats()

  Output:

  .. code-block:: text

      > Character name: Human
      > Health: 100
      > Damage: 10
      > Inventory: ['sword', 'shield']

Example in Ren'Py
*****************

.. code-block:: renpy

   define human = GameCharacter("Human")

   label start:

      human "Hello, world!"

.. code-block:: renpy

   define human = GameCharacter("Human", data={"inventory": ["sword", "shield"]})

   label start:

      $ inventory = ', '.join(human.data["inventory"])

      human "I have stored: [inventory]"

WorldObject
-----------

.. automodule:: worldnavigator.core.world_object
   :members:
   :show-inheritance:
   :undoc-members:

Examples
********

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


Condition Pipeline
------------------

A condition pipeline is the head of the conditions that will check all of the conditions before something, for example when player is moved to a location.

Use this pipeline is easy, for :class:`Location <worldnavigator.locations.base_location.Location>` class, you can do this:
``location.condition_pipeline(<your conditions>)``, and it will check all of the conditions before player is moved to that location.

Below is an example of how to use it, in a raw code, but just replace ``pipe`` with ``location.condition_pipeline``.

To create a custom condition, you need to inherit from :class:`BaseCondition <worldnavigator.types.types.BaseCondition>` and implement the ``handle`` method, this method will receive a :class:`ConditionPipelineContext <worldnavigator.types.types.ConditionPipelineContext>` object, that contains the current context of the pipeline.

.. code-block:: python

   from worldnavigator.types import BaseCondition

   current_wheatear = 'sunny'

   class CustomCondition(BaseCondition):
      # context = ConditionPipelineContext
      def handle(self, context):
         if current_wheatear == 'sunny':
            # This will execute the next condition in the pipeline
            self.handle_next(context)
            return

         # This will stop the pipeline from executing the next condition
         # basically, will brake the chain of conditions
         context.denied = True

This custom condition can be used in a location (and for now is the only way to use it), see the examples in :ref:`here <pipeline_examples>`.

.. automodule:: worldnavigator.core.condition_pipeline
   :members:
   :show-inheritance:
   :undoc-members:

.. _pipeline_examples:

Example in Python
*****************

.. code-block:: python

   from typing import TypedDict
   from worldnavigator.core import GameCharacter, WorldParser
   from worldnavigator.types import BaseCondition
   from worldnavigator.types.types import ConditionPipelineContext


   # This class is optional, but it's recommended to use it to avoid typos, probably doesn't work in Ren'Py
   class MyData(TypedDict):
      inventory: list[str]


   my_data: MyData = {
      'inventory': []
   }

   human = GameCharacter[MyData]("Human", data=my_data)

   world = WorldParser.scene_graph_parser(f'./examples/worlds/nexis.world.json')


   class HasSword(BaseCondition):
      def handle(self, context: ConditionPipelineContext):
         if 'student_card' in human.data['inventory']:
            self.handle_next(context)
            return

         context.denied = True


   world.character_entrypoint('Main Entrance')
   world.add_character(human)
   print(f'Current location: {human.current_location}')

   school = world.get_location('School')

   school.condition_pipeline(
      HasSword()
   )

   was_moved = world.move_character(human, school)
   print(f'Was moved: {was_moved}')

   print(f'Current location: {human.current_location}')


Output:

.. code-block:: text

   > Current location: Main Entrance
   > Was moved: False
   > Current location: Main Entrance

Example in Ren'Py
*****************

.. code-block:: renpy

   ...
   
   define location = Location('School')

   label start:
      python:
         class WeatherCondition(BaseCondition):
            def handle(self):
               if world.time.time_of_day != 'night':
                  return

               self.handle_next()


         location.condition_pipeline(
            WeatherCondition()
         )
      
      ...

WorldTime
---------

.. automodule:: worldnavigator.core.world_time
   :members:
   :show-inheritance:
   :undoc-members:
