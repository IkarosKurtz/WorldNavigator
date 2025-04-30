from worldnavigator.locations.base_location import Location


class World:
  def __init__(self, *, name: str):
    self._name = name
    self._locations: dict[str, Location] = {}
    self._population = 0

  #################################################
  ################### Properties ##################
  #################################################

  @property
  def name(self) -> str:
    return self._name

  @property
  def locations(self) -> list[Location]:
    return list(self._locations.values())

  #################################################
  ################ Private Methods ################
  #################################################

  def _character_added(self, name: str, location: str):
    self._population += 1

    print(f'Character {name} added to {location}')

  def _character_removed(self, name: str, location: str):
    self._population -= 1

    print(f'Character {name} removed from {location}')

  #################################################
  ################ Public Methods #################
  #################################################

  def population(self) -> str:
    return f'{self._population} characters'

  def add_location(self, location: Location) -> None:
    if location.name in self._locations:
      raise ValueError(f'Location {location.name} already exists')

    location.on('character_added', self._character_added)
    location.on('character_removed', self._character_removed)
    self._locations[location.name] = location

  def remove_location(self, location: Location) -> None:
    if location.name not in self._locations:
      raise ValueError(f'Location {location.name} does not exist')

    self._locations.pop(location.name)

  def get_location(self, location_name: str) -> Location:
    if location_name not in self._locations:
      raise ValueError(f'Location {location_name} does not exist')

    return self._locations[location_name]

  def where_is(self, character: str) -> str:
    """
    Determines where a specific character is located.

    :param str character: The character to find the location of.
    :return: The location of the character.
    """

    for location in self._locations.values():
      if character in location.characters:
        return f'{character} is in {location.name}'

    return f'{character} is not found in the world.'
