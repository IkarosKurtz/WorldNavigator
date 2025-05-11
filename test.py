import time

from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.columns import Columns


from weather_v2 import WeatherSystem
from worldnavigator.core import WorldParser

world = WorldParser().scene_graph_parser('./examples/worlds/nexis.world.json')

weather_system = WeatherSystem(world._locations)

print(weather_system)


with Live(console=Console()) as live:
  for i in weather_system.propagate():
    if i % 4 == 0:
      weather_system.change_center()

    table = Table(title='Weather', show_lines=True)
    table.add_column('Location')
    table.add_column('Wind')
    table.add_column('Temperature')
    table.add_column('Humidity')
    table.add_column('Connections')

    for location, weather_node in zip(world.locations, weather_system._weather_nodes.values()):
      connections = ', '.join([connection.name for connection in location.connections.values()])
      options = {
        weather_node.wind < 8: f'[b yellow]{weather_node.wind}[/]',
        8 <= weather_node.wind <= 16: f'[b green]{weather_node.wind}[/]',
        16 <= weather_node.wind <= 20: f'[b blue]{weather_node.wind}[/]',
      }
      table.add_row(location.name, options[True], str(weather_node.temperature),
                    str(round(weather_node.humidity)) + '%', connections)

    table.add_row(str(i))
    panel = Panel(Columns([
      table,
      Panel(Columns([
          Text(f'Center: {weather_system._center.connected_to}\nIncrement: {weather_system._increment}\nTemperature: {weather_system._get_temperature_by_time()}', style='bold blue'),
          f'Clock: {weather_system.show_clock()}',
      ]))
    ]))

    live.update(panel)

    time.sleep(1)
