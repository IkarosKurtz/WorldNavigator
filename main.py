from threading import Thread
import threading
import time
import signal
import sys

from parser import WorldParser

game_time = [12, 0]


def update_time(val):
  global game_time
  t = threading.current_thread()

  while getattr(t, "do_run", True):
    time.sleep(1.5)
    if (game_time[1] + val) >= 60:
      game_time[1] = 0
      game_time[0] += 1

    if game_time[0] >= 24:
      game_time[0] = 0

    game_time[1] += val


thread = Thread(target=update_time, args=(42,), )


def signal_handler(sig, frame):
  print('Adios')

  thread.do_run = False
  thread.join()
  sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def main():
  global game_time
  town = WorldParser().unpack("nexis.json")
  # thread.start()

  current_location = town.get_location('Club Room', 'R')
  town.get_location("Closet", 'R').add_character("Monika")
  town.get_location("Woman Bathroom", 'R').add_character("Yuri")
  current_location.add_character("Sayori")
  current_location.add_character("Natsuki")

  print(town.get_characters())

  while True:
    someone = f'Aquí se encuentra {current_location.who_is_here()}' if len(
        current_location.characters) > 0 else 'Aquí no hay nadie'

    time = f'{game_time[0]:02}:{game_time[1]:02}'

    print(f'\nHora: {time}\nEstas en {current_location.name}\nFondo: {current_location.retrieve_scene_background(game_time)}\n{someone}')
    print('Puedes ir a: ')
    for i, sub_location in enumerate(current_location.all_sub_locations()):
      print(f'{i + 1}. {sub_location.name}')

    if current_location.parent_location is not None:
      print(f'0. {current_location.parent_location.name}')

    to = input('>')

    try:
      to = int(to) - 1

      if to == -1:
        current_location = current_location.parent_location
        continue

      current_location = current_location.all_sub_locations()[to]
    except:
      continue


if __name__ == "__main__":
  main()
