import time
from typing import TypedDict

from worldnavigator.core import GameCharacter, WorldParser
from worldnavigator.types import BaseCondition
from worldnavigator.types.types import ConditionPipelineContext


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

world = WorldParser.scene_graph_parser(f'./examples/worlds/nexis.world.json')
world.character_entrypoint('Main Entrance')
world.time.adjust_time(20)
world.time.start_time()


# def weather():
#   while True:
#     time.sleep(1)
#     print(world.time.weather.current_weather)


# thread = Thread(target=weather, daemon=True)
# thread.start()

time.sleep(3)
print(world.time.show_clock())


class HasSword(BaseCondition):
  def handle(self, context: ConditionPipelineContext):
    if 'sword' in human.data['inventory']:
      self.handle_next(context)
      return

    context.denied = True


class IsPassTwelve(BaseCondition):
  def handle(self, context: ConditionPipelineContext):
    if world.time.get_time()[0] >= 10:
      self.handle_next(context)
      return

    context.denied = True


class IsSunny(BaseCondition):
  def handle(self, context: ConditionPipelineContext):
    if world.time.weather.current_weather['weather'] == 'Sunny':
      self.handle_next(context)
      return

    context.denied = True


world.add_character(human)
print(human.current_location)

school = world.get_location('School')

school.condition_pipeline(
  HasSword(),
  IsPassTwelve(),
  IsSunny()
)

while True:
  was_moved = world.move_character(human, school)
  print(f'Was moved: {was_moved}')

  print(human.current_location)
  time.sleep(1)
