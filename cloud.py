
from logging import DEBUG, FileHandler, getLogger
import os
import random
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.columns import Columns
from rich.panel import Panel

console = Console()


class Cloud:
  def __init__(self):
    self._water = 0
    self._fill = False
    self._status = 'Sunny'

  @property
  def water(self):
    return self._water

  @property
  def name(self):
    options = {
      'Sunny': '[b yellow]Sunny[/]',
      'Cloudy': '[b gris]Cloudy[/]',
      'Rainy': '[b blue]Rainy[/]',
    }

    return options[self._status]

  def predict(self):
    if self._water <= 30:
      self._fill = True
      self._status = 'Sunny'

    if self._fill and self._water <= 100:
      self.add_water()
    elif self._fill and self._water > 100:
      self._fill = False

    if 50 < self._water < 80 and self._status != 'Rainy':
      self._status = 'Cloudy'

    if not self._fill and self._water > 30:
      self._status = 'Rainy'
      self._water -= 1

  def add_water(self):
    prob = random.random()

    if prob < .7:
      self._water += random.randint(1, 5)

  def __rich_repr__(self):
    yield 'water', self._water
    yield 'status', self._status


logger = getLogger()

if not os.path.exists('./tmp'):
  os.makedirs('./tmp', exist_ok=True)

logger.addHandler(FileHandler('./tmp/w.log'))
logger.setLevel(DEBUG)
clouds: list[list[Cloud]] = []

for _ in range(5):
  row_clouds = []
  for _ in range(5):
    row_clouds.append(Cloud())
  clouds.append(row_clouds)

rows = ['A', 'B', 'C', 'D', 'E']
tick = 0
with Live(console=console) as live:
  while True:

    table = Table(title='World', show_lines=True)

    table.add_column('#')
    table.add_column('1')
    table.add_column('2')
    table.add_column('3')
    table.add_column('4')
    table.add_column('5')

    for row_clouds in clouds:
      for idx, cloud in enumerate(row_clouds):
        cloud.predict()
        logger.info(
          f'predict: cloud {idx}; water = {cloud.water}; status = {cloud.name}; fill = {cloud._fill}; {id(cloud)}')

    for idx, row in enumerate(rows):
      row_clouds = clouds[idx]

      table.add_row(row, row_clouds[0].name, row_clouds[1].name,
                    row_clouds[2].name, row_clouds[3].name, row_clouds[4].name)

    table.add_row(str(tick))

    texts = ['', '']
    text_idx = 0
    cloud_idx = 0
    for row_clouds in clouds:
      for cloud in row_clouds:
        if cloud_idx == 12:
          text_idx += 1
        texts[text_idx] += f'Cloud {cloud_idx + 1}: water = {cloud.water}; status = {cloud.name}; fill = {cloud._fill}\n'
        cloud_idx += 1

    panel = Panel.fit(Columns([table, *texts]), title='adsd')

    live.update(panel)
    time.sleep(1)
    tick += 1
