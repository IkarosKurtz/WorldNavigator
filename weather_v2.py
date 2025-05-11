from dataclasses import dataclass, field
from typing import Iterator, List, Dict, Optional, Set, TYPE_CHECKING
from uuid import uuid4
import math
import random

if TYPE_CHECKING:
  from worldnavigator.locations.base_location import Location

MIN_WIND = 3
MAX_WIND = 20
MIN_INCREMENT = 5
TEMPERATURE_FACTOR = .1
ALPHA = .4
BETA = .02
MAX_TEMP = 34
MIN_TEMP = 10

HUMIDITY_DIFFUSION = 0.2
EVAPORATION_FACTOR = 0.02


@dataclass
class WeatherNode:
  connected_to: str
  wind: int = field(default=MIN_WIND)
  temperature: int = field(default=20)
  humidity: float = field(default=0.0)
  _id: int = field(default_factory=lambda: uuid4().int)

  def adjust_temperature(self, delta: int) -> None:
    pass

  def add(self, increment: int, *, cap: int = MAX_WIND) -> None:
    # TODO: Better way of adding wind, not always need some increment

    self.wind = min(cap, self.wind + increment)

  def remove(self, increment: int) -> None:
    self.wind = max(MIN_WIND, self.wind - increment)

  def __hash__(self):
    return hash(self._id)

  def __eq__(self, other: 'WeatherNode'):
    return self._id == other._id


class WeatherSystem:
  def __init__(self, locations: dict[str, 'Location']):
    self._weather_nodes: Dict[str, WeatherNode] = {}
    self._increment = 0
    self._locations = locations
    self._visited: Set[WeatherNode] = set()
    self._center: Optional[WeatherNode] = None

    self._clock = [12, 0]

    # Initialize weather nodes for each location
    for location in locations.values():
      self.add_node(location.name)

  def __str__(self):
    return f"WeatherSystem with {len(self._locations)} locations"

  #################################################
  ################ Private Methods ################
  #################################################

  def _get_neighbors(self, location: 'Location', *, filter: bool = True) -> List[WeatherNode]:
    neighbors = []

    for connection in location.connections.values():
      weather_node = self._weather_nodes.get(connection.name, None)
      if weather_node is None:
        continue

      if filter and weather_node in self._visited:
        continue

      neighbors.append(weather_node)

    return neighbors

  def _get_temperature_by_time(self) -> float:
    options = {
      self._clock[0] < 12: -.7,
      12 <= self._clock[0] < 18: 1,
      18 <= self._clock[0] <= 24: -.5,
    }

    return options[True]

  def _update_clock(self, amount: int = 1) -> None:
    if self._clock[0] >= 24:
      self._clock[0] = 0

    if self._clock[1] >= 60:
      self._clock[1] = 0
      self._clock[0] += 1

    self._clock[1] += amount

  #################################################
  ################ Public Methods #################
  #################################################

  def show_clock(self):
    hours = self._clock[0] if self._clock[0] >= 10 else f'0{self._clock[0]}'
    minutes = self._clock[1] if self._clock[1] >= 10 else f'0{self._clock[1]}'
    return f'{hours}:{minutes}'

  def add_node(self, location_name: str) -> None:
    self._weather_nodes[location_name] = WeatherNode(location_name)

  def change_center(self) -> None:
    if not self._weather_nodes:
      return

    location = None
    while not location or location.is_indoor:
      self._center = random.choice(list(self._weather_nodes.values()))
      location = self._locations[self._center.connected_to]

    self._increment = random.randint(MIN_INCREMENT, MAX_WIND)
    self._center.add(self._increment)
    self._center.temperature += random.choice([-5, -2, 0, 2, 5])

    self._visited = set()

  def propagate(self) -> Iterator[None]:
    idx = 0

    while True:
      self._update_clock(10)
      if self._center is None:
        yield idx
        idx += 1
        continue

      if len(self._visited) == 0:
        neighbors = self._get_neighbors(self._locations[self._center.connected_to])

        for node in neighbors:
          self._visited.add(node)
      else:
        for node in list(self._visited):
          neighbors = self._get_neighbors(self._locations[node.connected_to])
          for node in neighbors:
            if node in self._visited:
              continue

            self._visited.add(node)

      for node in self._visited:
        location = self._locations[node.connected_to]
        if location.is_indoor:
          node.add(round(self._increment * 0.05), cap=self._center.wind)
          continue

        node.add(round(self._increment * .2), cap=self._center.wind)

      for node in self._weather_nodes.values():
        if node in self._visited or node == self._center:
          continue

        node.remove(1)

      new_temp: dict[str, int] = {}

      for node in self._weather_nodes.values():
        temperature = node.temperature
        location = self._locations[node.connected_to]

        neighbors = self._get_neighbors(self._locations[node.connected_to], filter=False)
        diff = sum(neighbor.temperature - temperature for neighbor in neighbors)
        total_neighbors = len(neighbors) or 1
        delta_diff = ALPHA * (diff / total_neighbors)  # Normalize the diff by the number of neighbors

        if node in self._visited or node == self._center:
          delta_adv = BETA * (self._center.temperature - temperature)
        else:
          delta_adv = 0

        next_temperature = round(temperature + delta_diff + delta_adv + self._get_temperature_by_time())
        next_temperature = max(MIN_TEMP, min(MAX_TEMP, next_temperature))

        new_temp[node.connected_to] = next_temperature if not location.is_indoor else round(next_temperature * .85)

      for node_name, next_temperature in new_temp.items():
        node = self._weather_nodes[node_name]
        node.temperature = next_temperature

        T = next_temperature
        es = 6.1094 * math.exp(17.625 * T / (T + 243.04))
        e = (node.humidity / 100) * es

        neighbors = self._get_neighbors(self._locations[node.connected_to], filter=False)
        hum_diff = sum(n.humidity - node.humidity for n in neighbors)
        delta_diff = HUMIDITY_DIFFUSION * (hum_diff / (len(neighbors) or 1))
        delta_source = EVAPORATION_FACTOR * (es - e)
        next_humidity = round(node.humidity + delta_diff + delta_source) - (0.01 * node.wind)
        next_humidity = max(0, min(100, next_humidity))
        node.humidity = next_humidity

      yield idx
      idx += 1
