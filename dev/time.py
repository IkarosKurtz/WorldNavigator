from threading import Thread
import time
from worldnavigator.core.world_time import WorldTime

world_time = WorldTime()


def show_clock():
  while True:
    time.sleep(.5)
    print(world_time.show_clock())


clock = Thread(target=show_clock, daemon=True)


def main():
  clock.start()
  world_time.change_time(5)

  idx = 0
  time.sleep(1)
  print('Start')
  world_time.start_time()
  while True:
    time.sleep(world_time.amount_of_time)

    if world_time.is_time_frozen():
      world_time.unfreeze_time()

    idx += 1


if __name__ == '__main__':
  main()
