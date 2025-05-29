import time
from typing import TypedDict
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from worldnavigator.core import GameCharacter, WorldParser

console = Console()


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
world.time.adjust_time(30)


def weather(current_step, steps):
  text = Markdown(
    "### **Current Weather:**\n{current}\n### **Next Weather:**\n{next}".format(
      current=current_step["weather"], next=steps[0]["weather"])
  )
  console.print(Panel(text, title='Weather'))


def thunder():
  console.print(Panel(Markdown('⚡ ⚡ ⚡ ⚡ ⚡'), title='Thunder'))


def updated_time(time):
  text = Markdown(
    "### **Current Time:**\n{time}\n### **Current Date:**\n{date}".format(
      time=world.time.show_clock('12:00'),
      date=world.time.show_date('DD-MM-YYYY', full_month=True)
    )
  )
  console.print(Panel(text, title='Time'))


def updated_date(date):
  console.print(Panel(Markdown(f'### **Current Date:**\n{date}'), title='Date'))


world.time.weather.listen_for_weather_change(weather)
world.time.weather.listen_for_thunder(thunder)
world.time.listen_for_time(updated_time)
world.time.listen_for_date(updated_date)

world.time.weather.override_weather('Stormy', 'Stormy', 15)
world.time.override_time(20, 0)

world.time.start_time()


idx = 0
while True:
  time.sleep(1)
  if idx == 15:
    world.time.weather.throw_thunder()
  idx += 1
