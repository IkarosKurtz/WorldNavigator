# WorldNavigator

## Table of Contents 📋

- [What is it?? 🤔](#what-is-it)
- [Why was created?? ❗](#why-was-created)
- [Main Classes 📚](#main-classes)
  - [WorldParser 🛠️](#worldparser)
  - [WorldWeather 🌦️](#worldweather)
  - [World 🌍](#world)
- [How to create a World 🛠️](#how-to-create-a-world)

<h2 id="what-is-it">What is it?? 🤔</h2>

This project has three main classes that you will need if you want to create a World. WorldNavigator is a bunch of classes with the goal of creating a World where you can navigate and see the simulated time and weather.

In escence that is what WorldNavigator is, but now I will explain **Why I created this**.

<h2 id="why-was-created">Why was created?? ❗</h2>

This project was created because was intended to be used in other project **Worlds Apart**, if you want to know more about it you can click [here](https://github.com/ikaroskurtz/DDLC-Worlds-Apart). So some features like backgrounds for each location is made for my purposes, but I will try to make it more customizable in the future.

But for now it can be used as a base if you want to create a World for a renpy game or python game.

---

<h2 id="main-classes">Main Classes 📚</h2>

As I said before, this project has three main classes that you will need if you want to create a World.

The main classes are:

- `WorldParser`
- `WorldWeather`
- `World`

<h3 id="worldparser">WorldParser 🛠️</h3>

The WorldParser is used to create the World from a json file, beacuse is hard to read when is declared from the code, and I want to keep it easy.

When you have your JSON file ready, just create the WorldParser and call the unpack method, this will return a World class, and all locations will be appended to their corrsponding location. If you want to see all the locations name in the World use the `all_locations` property.

```python
from parser import WorldParser

world = WorldParser().unpack('my_world.json')

print(world.all_locations)
# Output: ['School', 'Left Corridor', 'Classroom', 'Right Corridor', 'Woman Bathroom', 'Man Bathroom']
```

<h3 id="worldweather">WorldWeather 🌦️</h3>

This class is used to simulate the weather in the World, is not 100% accurate like in real life, but for it's intended purpose is enough. It will be improved in the future.

Now how to use it. First you declare your WorldWeather, then you can call the `simulate_weather_with_transitions` method, this recive a period of time (for now it's in hours), this will return a list of timestamps, each timestamp is a dictionary and represents a step (hour) of the weather, the dictionary has two keys: `weather` and `data`, the `weather` key is the weather of the step, and the `data` key is a dictionary with the data of the step. For example:

My current time is 13:00 and the current weather is **Sunny** and have 3 steps, then the first step represents the weather of 13:00, the second step represents the weather of 14:00 and the third step represents the weather of 15:00.

```python
from weather import WorldWeather

world_weather = WorldWeather()
steps = world_weather.simulate_weather_with_transitions(8)

print(steps)
""" Output:
My Time: 13:00

[
  {'weather': 'Snowy', 'data': {'temperature': 33.61, 'humidity': 17.32, 'wind': 8.57, 'clouds': 3.59}}, -> 13:00
  {'weather': 'Snowy', 'data': {'temperature': 27.98, 'humidity': 25.29, 'wind': 8.36, 'clouds': 16.63}}, -> 14:00
  {'weather': 'Snowy', 'data': {'temperature': 22.36, 'humidity': 33.27, 'wind': 8.15, 'clouds': 29.66}}, -> 15:00
  {'weather': 'Snowy', 'data': {'temperature': 16.73, 'humidity': 41.25, 'wind': 7.95, 'clouds': 42.69}}, -> 16:00
  {'weather': 'Snowy', 'data': {'temperature': 11.11, 'humidity': 49.22, 'wind': 7.74, 'clouds': 55.72}}, -> 17:00
  {'weather': 'Snowy', 'data': {'temperature': 5.48, 'humidity': 57.20, 'wind': 7.53, 'clouds': 68.75}}, -> 18:00
  {'weather': 'Snowy', 'data': {'temperature': -0.14, 'humidity': 65.18, 'wind': 7.32, 'clouds': 81.78}}, -> 19:00
  {'weather': 'Snowy', 'data': {'temperature': 0.04, 'humidity': 66.27, 'wind': 10.34, 'clouds': 81.38}} -> 20:00
]

"""
```

The data in each step is useless, for now. So you don't need to worry about it.

<h3 id="world">World 🌍</h3>

The World class is where all the locations are stored, also have some useful methods like `get_location_by_name`, `get_location`, `get_characters` and `where_is`, `all_locations` is a property that returns all the locations in the World.

The `get_location_by_name` and `get_location` methods have the same purpose, but their behaviour is different, `get_location` requires a location name and iterates through `all_locations` until it finds the desired location. `get_location_by_name` requires a location name and location type (found it in [How to create a World 🛠️](#how-to-create-a-world)) then iterates through an array of locations of the same type so it doesn't iterate through all the locations, but this only matters if you have a lot of locations on your world.

```python
from enums import LocationType
from classes import World

world: World = WorldParser().unpack('my_world.json')

print(world.get_location_by_name('School')) # -> Slower
# Output: Location(School, type=B, parent=None, no_sub_locations=2)

print(world.get_location('School', 'B')) # -> Faster
# Output: Location(School, type=B, parent=None, no_sub_locations=2)

print(world.all_locations)
# Output: ['School', 'Left Corridor', 'Classroom', 'Right Corridor', 'Woman Bathroom', 'Man Bathroom']

print(world.get_characters())
""" Output:
{
  "School": ['Cochi'],
  "Right Corridor": ['Obed', 'Mike'],
}
"""

print(world.where_is('Mike'))
# Output: Mike is in Right Corridor
```

---

<h3 id="how-to-create-a-world">How to create a World 🛠️</h3>

As I said in [WorldParser 🛠️](#worldparser), you need a JSON file to create a World, but how to create it?

First, you need to know about type location, there are four types of locations:

- `Room` -> **R**
- `Corridor` -> **C**
- `Building` -> **B**
- `Street` -> **S**

Right, also you need to take into account, that your JSON file name will be the name of the World, so if you want to create a World called `Monaco` you need to create a file called `monaco.json`. The location name need a certain format, it's like this: `type-name`, for example: `B-School`, `C-Left Corridor`, `R-Classroom` and `R-Woman Bathroom`. If it have more or less than one `-`, then that location doesn't will be created, example: `C-Left-Corridor`, `C School`. If the location type doesn't belong to the list, then an error will be thrown.

Each location have one required key `day`, this key is the default background, but you can add optional keys, `afternoon` and `night` to change the backgrounds for the afternoon and night. If your location can be connected to other location, but not as child, then use the `to` (a list of strings) key, this key will create a reference to another location, basically is a non-direct child of the location, for example: if we have a location called `School` and other called `Park`, but `Park` isn't a child of `School`, beacuse is not inside of it, then use `"to": ["B-Park"]` in the `School` location, in this way you can go from `School` to `Park` but you can't go from `Park` to `School`, if you want a bidirectional path, you need to do the same thing in `Park` with `"to": ["B-School"]`.

Sadly, some locations doesn't fit within a type, for example: `Park` isn't a `B = Building`, so you can use `S = Street` instead. `Building` and `Street` aren't a indoors location, so your parameter called `is_indoor` will be **True**.

Here a example of a JSON file called `my world.json`:

```json
{
  "B-School": { // B = Building
    "to": ["B-Park"], // Reference to another location
    "day": "bg day", // Default background
    "afternoon": "bg afternoon", // Background for the afternoon
    "C-Left Corridor": { // Direct child of the location
      "day": "bg corridor_day",
      "R-Classroom": {
        "day": "bg classroom_day",
      }
    },
    "C-Right Corridor": {
      "day": "bg corridor_day",
      "R-Man Bathroom": {
        "day": "bg bathroom_day",
      },
      "R-Woman Bathroom": {
        "day": "bg bathroom_day",
      },
    },
  },
  "B-Park": { // B = Building
    "to": ["B-School"], // Reference to another location
    "day": "bg park_day", // Default background
  }
}
```
