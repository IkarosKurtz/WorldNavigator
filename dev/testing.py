from typing import TypedDict
from worldnavigator.core.character import GameCharacter
from worldnavigator.core import WorldParser


# This class is optional, but it's recommended to use it to avoid typos, probably doesn't work in Ren'Py
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
world.add_character(human)
print(human.current_location)
world.move_character(human, 'School')
world.add_character(human)

print(human.current_location)
