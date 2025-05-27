from typing import TypedDict
from worldnavigator.core import GameCharacter, WorldParser
from worldnavigator.types import BaseCondition
from worldnavigator.types.types import ConditionPipelineContext


# This class is optional, but it's recommended to use it to avoid typos, probably doesn't work in Ren'Py
class MyData(TypedDict):
  inventory: list[str]
  health: int
  damage: int


my_data: MyData = {
  'damage': 10,
  'health': 100,
  'inventory': ['shield']
}

human = GameCharacter[MyData]("Human", data=my_data)

world = WorldParser.scene_graph_parser(f'./examples/worlds/nexis.world.json')


class HasSword(BaseCondition):
  def handle(self, context: ConditionPipelineContext):
    if 'sword' in human.data['inventory']:
      self.handle_next(context)
      return

    context.denied = True


world.character_entrypoint('Main Entrance')
world.add_character(human)
print(human.current_location)

school = world.get_location('School')

school.condition_pipeline(
  HasSword()
)

was_moved = world.move_character(human, school)
print(f'Was moved: {was_moved}')

print(human.current_location)
