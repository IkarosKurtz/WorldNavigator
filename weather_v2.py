from dataclasses import dataclass, field
import random
from typing import Iterator, List, Dict, Optional, Set, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
  from worldnavigator.locations.base_location import Location

MIN_WIND = 3
MAX_WIND = 20
MIN_INCREMENT = 5
TEMPERATURE_FACTOR = .1


@dataclass
class WeatherNode:
  connected_to: str
  wind: int = field(default=MIN_WIND)
  temperature: int = field(default=20)
  _id: int = field(default_factory=lambda: uuid4().int)

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

    # Initialize weather nodes for each location
    for location in locations.values():
      self.add_node(location.name)

  def __str__(self):
    return f"WeatherSystem with {len(self._locations)} locations"

  #################################################
  ################ Private Methods ################
  #################################################

  def _get_neighbors(self, location: 'Location') -> List[WeatherNode]:
    neighbors = []

    for connection in location.connections.values():
      weather_node = self._weather_nodes.get(connection.name, None)
      if weather_node is None:
        continue

      if weather_node in self._visited:
        continue

      neighbors.append(weather_node)

    return neighbors

  #################################################
  ################ Public Methods #################
  #################################################

  def add_node(self, location_name: str) -> None:
    self._weather_nodes[location_name] = WeatherNode(location_name)

  def change_center(self) -> None:
    if not self._weather_nodes:
      return

    self._center = random.choice(list(self._weather_nodes.values()))
    self._increment = random.randint(MIN_INCREMENT, MAX_WIND)
    self._center.add(self._increment)
    self._center.temperature += random.choice([-5, -2, 0, 2, 5])
    self._visited = set()

  def propagate(self) -> Iterator[None]:
    idx = 0

    while True:
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
        node.add(round(self._increment * .2), cap=self._center.wind)

        neighbors = self._get_neighbors(self._locations[node.connected_to])
        for neighbor in neighbors:
          delta_temp = neighbor.temperature - node.temperature
          temp_change = delta_temp * (node.wind / MAX_WIND) * TEMPERATURE_FACTOR
          node.temperature += temp_change

      for node in self._weather_nodes.values():
        if node in self._visited or node == self._center:
          continue

        node.remove(1)

        # Difusión con vecinos
        neighbors = self._get_neighbors(self._locations[node.connected_to])
        for neighbor in neighbors:
          delta_temp = neighbor.temperature - node.temperature
          node.temperature += delta_temp * 0.01

        # Tendencia a temperatura ambiente
        delta_temp = 20 - node.temperature
        node.temperature += delta_temp * 0.005

      yield idx
      idx += 1
