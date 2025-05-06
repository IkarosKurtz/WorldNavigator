import os
import signal
import sys
from typing import Annotated

from worldnavigator.core import WorldObject, WorldParser
from worldnavigator.decorators import evaluate_events
from worldnavigator.locations import Location
from worldnavigator.types import Params
from worldnavigator.weather import WorldWeather

game_time = [12, 0]
weather = WorldWeather()
weather_steps = None
current_weather = None


def update_time(val):
  global game_time
  global weather_steps
  global current_weather

  if (game_time[1] + val) >= 60:
    game_time[1] = 0
    game_time[0] += 1

    if len(weather_steps) == 0:
      update_weather()

    current_weather = weather_steps.pop(0)

  if game_time[0] >= 24:
    game_time[0] = 0

  game_time[1] += val


def update_weather():
  global game_time
  global weather_steps

  weather_steps = weather.simulate_weather_with_transitions(24 - game_time[0])


def signal_handler(sig, frame):
  sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


@evaluate_events
class WCEvents:
  flush: Annotated[str, Params()]
  watch_it: Annotated[str, Params()]


def interact(location: Location):
  interacting = True
  while interacting:
    objects = list(location.objects.values())
    for idx, obj in enumerate(objects):
      print(f'{idx + 1}. {obj.name}')

    print('0. Go back')
    selected_object = input('>')
    if selected_object == '0':
      interacting = False
      continue

    try:
      obj = location.get_object(objects[int(selected_object) - 1].name)
      print(f'Selected object: {obj.name}')

      for idx, event_name in enumerate(obj.events):
        print(f'{idx + 1}. {event_name.replace("_", " ")}')

      what_do_i_do = input('>')

      obj.interact(obj.events[int(what_do_i_do) - 1])
      interacting = False
      input('')
      continue
    except Exception as e:
      print(e)
      continue


def main():
  global game_time
  global current_weather

  town = WorldParser.scene_graph_parser('./examples/worlds/nexis.world.json')

  update_weather()
  current_weather = weather_steps.pop(0)

  current_location = town.get_location('Club Room')
  town.get_location('Closet').add_character('Monika')
  w_bathroom = town.get_location('Woman Bathroom')

  w_bathroom.add_character('Yuri')

  current_location.add_character('Sayori')
  current_location.add_character('Natsuki')

  wc = WorldObject[WCEvents, None]('WC')

  w_bathroom.add_object(wc)

  def flush_wc():
    print('You used WC')

  def watch():
    print('Why do you watch a WC??? .... That\'s weaird')

  wc.register_interaction('flush', flush_wc)
  wc.register_interaction('watch_it', watch)

  while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    someone = f'Characters here: {current_location.who_is_here()}' if len(
        current_location.characters) > 0 else 'No Characters Here'

    time = f'{game_time[0]:02}:{game_time[1]:02}'

    print(
      f'\nTime: {time}\nWeather: {current_weather["weather"]}\nCurrent location: {current_location.name}\nBackground: {current_location.backgrounds.retrieve_scene_background(game_time)}\n{someone}')
    print('Locations in this location: ')

    locations = current_location.get_locations()
    for i, sub_location in enumerate(locations):
      print(f'{i + 1}. {sub_location.name}')

    if len(current_location.objects) > 0:
      print('type "i" to interact with an object')

    to = input('>')

    if to.strip() == 'i':
      interact(current_location)
      continue

    try:
      to = int(to) - 1

      update_time(2)
      next_location = current_location.get_location(locations[to].name)
      current_location = next_location
    except Exception as e:
      print(f'Error: {e}')
      continue


if __name__ == '__main__':
  main()
