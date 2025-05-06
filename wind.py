from collections import deque
from dataclasses import dataclass, field
import random
import time
from uuid import uuid4
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.columns import Columns

import string

console = Console()

MAX_WIND = 20
GRID_SIZE = 8
MIN_WIND = 3
GROW_FACTOR = 3
TICKS_PER_STEP = 4
PROP_DECAY = 2
ALPHABET = string.ascii_uppercase[:GRID_SIZE]


# X equals rows
# Y equals columns

@dataclass
class Node:
  x: int
  y: int
  wind: int = field(default=MIN_WIND)
  id: int = field(default_factory=lambda: uuid4().int)

  def add(self, increment: int, max_wind: int):
    self.wind = min(max_wind, max(1, self.wind + increment // GROW_FACTOR))

  def remove(self, increment: int):
    self.wind = max(MIN_WIND, max(1, self.wind - increment // GROW_FACTOR))

  def __hash__(self):
    return hash(self.id)

  def __eq__(self, other):
    return self.id == other.id


def get_neighbors(x: int, y: int, nodes: Node, size: int) -> list[Node]:
  offsets = [
    (-1, 0),  # UP
    (0, 1),  # RIGHT
    (1, 0),  # DOWN
    (0, -1)  # LEFT
  ]

  result: list[Node] = []
  for dx, dy in offsets:
    nx, ny = x + dx, y + dy

    if 0 <= nx < size and 0 <= ny < size:
      result.append(nodes[nx][ny])

  return result


def get_random_center(nodes: list[Node]) -> Node:
  x = random.randrange(GRID_SIZE)
  y = random.randrange(GRID_SIZE)
  return nodes[x][y]


def propagate(center: Node, nodes: list[list[Node]], increment: int):
  queue = deque()
  visited = set()

  # iniciamos en el foco
  queue.append((center.x, center.y, increment))
  visited.add((center.x, center.y))

  while queue:
    x, y, strength = queue.popleft()
    node = nodes[x][y]
    # aplicamos viento limitado por MAX_WIND
    node.add(strength, MAX_WIND)

    # calculamos fuerza para la siguiente capa
    next_strength = strength // GROW_FACTOR
    if next_strength <= 0:
      continue

    # encolamos vecinos no visitados
    for nb in get_neighbors(x, y, nodes, GRID_SIZE):
      coord = (nb.x, nb.y)
      if coord in visited:
        continue
      visited.add(coord)
      queue.append((nb.x, nb.y, next_strength))


winds = [[Node(x, y) for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]

tick = 0
affected_nodes: set[Node] = set()

with Live(console=console) as live:
  while True:
    table = Table(title='Weather', show_lines=True)
    table.add_column('#', style="yellow")

    for i in ALPHABET:
      table.add_column(i)

    if tick % TICKS_PER_STEP == 0:
      center = get_random_center(winds)
      increment = random.randint(0, MAX_WIND)
      center.wind = min(MAX_WIND, center.wind + increment)
      affected_nodes = set()

    for x, wind in enumerate(winds):
      row = [str(x)]
      for y, i in enumerate(wind):
        if center.x == x and center.y == y:
          row.append(f'[b red]{i.wind}[/]')
        else:
          options = {
            MIN_WIND <= i.wind < 8: f'[b yellow]{i.wind}[/]',
            8 <= i.wind <= 16: f'[b green]{i.wind}[/]',
            16 <= i.wind <= 20: f'[b blue]{i.wind}[/]',
          }
          row.append(options.get(True, str(i.wind)))

      table.add_row(*row)

    if len(affected_nodes) == 0:
      neighbors = get_neighbors(center.x, center.y, winds, GRID_SIZE)
      for node in neighbors:
        affected_nodes.add(node)
    else:
      for node in list(affected_nodes):
        neighbors = get_neighbors(node.x, node.y, winds, GRID_SIZE)
        for node in neighbors:
          if node in affected_nodes:
            continue
          affected_nodes.add(node)

    panel = Panel.fit(
      Columns([
      table,
      f'Tick: {tick}\n'
      f'Wind: {center.wind}\n'
      # f'Neighbors: {", ".join([str(i.wind) for i in neighbors])}'
      ])
    )

    for node in affected_nodes:
      node.add(increment, center.wind)

    for wind in winds:
      for node in wind:
        if node in affected_nodes or (center.x == node.x and center.y == node.y):
          continue

        node.remove(increment)

    live.update(panel)
    time.sleep(1)

    tick += 1
