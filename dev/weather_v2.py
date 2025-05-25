from dataclasses import dataclass, field
from typing import Iterator, List, Dict, Optional, Set, TYPE_CHECKING
from uuid import uuid4
import math
import random
from json_logger import get_logger

log = get_logger('weather')

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
WIND_DRY_FACTOR = 0.01
NIGHT_DRY_FACTOR = 0.2


@dataclass
class WeatherNode:
  connected_to: str
  wind: int = field(default=MIN_WIND)
  wind_vec: list[float] = field(default=list((0, 0)))
  temperature: int = field(default=20)
  humidity: float = field(default_factory=lambda: random.uniform(30, 50))
  # humidity: float = field(default_factory=lambda: random.randint(20, 35))
  _id: int = field(default_factory=lambda: uuid4().int)

  def adjust_temperature(self, delta: int) -> None:
    self.temperature = max(MIN_TEMP, min(MAX_TEMP, delta))

  def adjust_wind(self, increment: int, *, cap: int = MAX_WIND) -> None:
    # TODO: Better way of adding wind, not always need some increment

    self.wind = min(cap, self.wind + increment)

  def adjust_humidity(self, value: float) -> None:
    self.humidity = max(0, min(100, value))

  def remove(self, increment: int) -> None:
    self.wind = max(MIN_WIND, self.wind - increment)

  def __str__(self):
    return f'WeatherNode(connected_to={self.connected_to}, wind={self.wind}, temperature={self.temperature}, humidity={self.humidity})'

  def __repr__(self):
    return self.__str__()

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

  def _update_wind(self):
    for node in self._weather_nodes.values():
      if node == self._center:
        continue

      # Add a certain amount of wind if location is indoor
      if node in self._visited:
        location = self._locations[node.connected_to]
        wind_decay = .2 if not location.is_indoor else .05
        before_wind = node.wind
        node.adjust_wind(
          self._increment * wind_decay,
          cap=self._center.wind
        )
        log.info(
          'Adjusting wind',
          extra={
            'location': node.connected_to,
            'wind_decay': wind_decay,
            'before_wind': before_wind,
            'after_wind': node.wind,
            'increment_rounded': f'{self._increment} * {wind_decay}={round(self._increment * wind_decay)}',
            'cap': self._center.wind,
          }
        )
        continue

      # If location is not visited, remove wind
      node.remove(1)
      log.info(
        'Removing one point of wind',
        extra={
          'location': node.connected_to,
          'before_wind': node.wind + 1,
          'after_wind': node.wind,
        }
      )

  def _update_temperature(self):
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

      next_temperature = temperature + delta_diff + delta_adv + self._get_temperature_by_time()
      next_temperature = max(MIN_TEMP, min(MAX_TEMP, next_temperature))

      new_temp[node.connected_to] = next_temperature if not location.is_indoor else next_temperature * .85

      log.info(
        'Adjusting temperature',
        extra={
          'location': node.connected_to,
          'delta_diff': f'{ALPHA} * ({diff} / {total_neighbors})={delta_diff}',
          'delta_adv': f'{BETA} * ({self._center.temperature} - {temperature})={delta_adv}' if delta_adv != 0 else '0',
          'next_temperature': next_temperature,
          'before_temperature': node.temperature,
          'adjusted_temperature': new_temp[node.connected_to],
        }
      )

    for node_name, next_temperature in new_temp.items():
      node = self._weather_nodes[node_name]
      node.adjust_temperature(next_temperature)

  def _update_humidity(self):
    for node in self._weather_nodes.values():
      T = node.temperature
      es = 6.1094 * math.exp(17.625 * T / (T + 243.04))
      e = (node.humidity / 100) * es

      neighbors = self._get_neighbors(self._locations[node.connected_to], filter=False)
      hum_diff = sum(n.humidity - node.humidity for n in neighbors)
      delta_diff = HUMIDITY_DIFFUSION * (hum_diff / (len(neighbors) or 1))
      delta_source = EVAPORATION_FACTOR * (es - e)
      wind_dry = WIND_DRY_FACTOR * node.wind

      before_humidity = node.humidity
      next_humidity = before_humidity + (delta_diff + delta_source - wind_dry)
      next_humidity_back = before_humidity + delta_diff + delta_source - wind_dry

      is_night = self._clock[0] > 20 or self._clock[0] < 8
      if is_night:
        next_humidity -= NIGHT_DRY_FACTOR

      node.adjust_humidity(next_humidity)

      log.info(
        'Adjusting humidity',
        extra={
          'location': node.connected_to,
          'e_s': f'6.1094 * e^(17.625 * {T} / ({T} + 243.04))={es}',
          'e': f'({node.humidity} / 100) * {es}={e}',
          'humidity_diff': f'{HUMIDITY_DIFFUSION} * ({hum_diff} / {len(neighbors) or 1})={delta_diff}',
          'evaporation': f'{EVAPORATION_FACTOR} * ({es} - {e})={delta_source}',
          'dry_by_wind': f'{WIND_DRY_FACTOR} * {node.wind}={wind_dry}',
          'next_humidity': f'{before_humidity} + {delta_diff} + {delta_source} - {wind_dry}={next_humidity_back}',
          'is_night': f'{is_night}',
          'night_dry': f'{next_humidity_back} - {NIGHT_DRY_FACTOR}={next_humidity}',
          'before_humidity': before_humidity,
          'adjusted_humidity': node.humidity,
        }
      )

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
    self._center.adjust_wind(self._increment)
    self._center.temperature += random.choice([-5, -2, 0, 2, 5])

    log.info(
      'Changing center',
      extra={
        'center': str(self._center),
        'increment': self._increment,
      }
    )

    self._visited = set()

  def propagate(self) -> Iterator[None]:
    idx = 0

    while True:
      self._update_clock(10)

      log.info(
        f'Clock: {self.show_clock()}'
      )

      # If center is None, we don't do anything
      if self._center is None:
        yield idx
        idx += 1
        continue
      # if idx > 3:
      #   break
      # Each step we add to the visited set the neighbors of each node in the visited set
      if len(self._visited) == 0:
        neighbors = self._get_neighbors(self._locations[self._center.connected_to])

        for node in neighbors:
          self._visited.add(node)

        log.info(
          'Adding first neighbors from center',
          extra={
            'center': self._center.connected_to,
            'neighbors': ', '.join([node.connected_to for node in neighbors]),
          }
        )
      else:
        neighbors = []
        for node in list(self._visited):
          neighbors = self._get_neighbors(self._locations[node.connected_to])
          for node in neighbors:
            if node in self._visited:
              continue

            self._visited.add(node)

          log.info(
            'Adding neighbors from sub center',
            extra={
              'center': node.connected_to,
              'sub_center': self._center.connected_to,
              'neighbors': ', '.join([n.connected_to for n in neighbors]),
            }
          )

      # Increment wind in each location, depending if is indoor or not
      # If some node isn't in the visited set, remove wind from it
      self._update_wind()

      # Calculate the new temperature for each node
      self._update_temperature()

      # Calculate the new humidity for each node
      self._update_humidity()

      yield idx
      idx += 1
