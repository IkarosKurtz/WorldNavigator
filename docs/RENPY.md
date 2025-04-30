# WorldNavigator Ren'Py Implementation 👥

## Table of Contents 📋

- [How to use it 🛠️](#how-to-use-it)
- [Content of rpy files 📚](#content-of-rpy-files)
- [Bind backgrounds 🎨](#bind-backgrounds)
- [How to add a character 👥](#how-to-add-a-character)
- [Main Components 📚](#main-components)
- [On Action 🎮](#on-action)
- [Customizable variables 🎨](#customizable-variables)
  - [Sounds volume 🔊](#sounds-volume)
  - [Styles 🎨](#styles)
- [Demo 🎮](#demo)

---

<h2 id="how-to-use-it">How to use it 🛠️</h2>

Go to the latest release of `WorldNavigator`, where you can download a demo game to see how it works and how it looks, or download the necessary files to integrate into your own game.

When you download the .rar containing the .rpy files, simply copy all the contents to your `game` folder, and you're ready to go.

<h2 id="content-of-rpy-files">Content of rpy files 📚</h2>

The .rar contains the following:

- `world_navigator` folder
  - `world_definitions.rpy`: Contains all the definitions such as variables, sounds, functions, screens, styles, and labels.
  - `weather_effects.rpy`: Contains image definitions for rain, snow, and thunder effects.
  - The files `classes.rpy`, `enums.rpy`, `parser.rpy`, and `weather.rpy` contain all the classes and some logic for the World Navigator. If you know how to use them, you can modify them to suit your needs; otherwise, stick with the previously mentioned files.
  
- `mod_assets` folder
  - `effects`: Contains all the images for the rain and snow effects.
  - `sfx`: Contains all the sounds for rain, snow, and thunder effects.

<h2 id="bind-backgrounds">Bind backgrounds 🎨</h2>

As explained in [How to create a World 🛠️](./README.md#how-to-create-a-world), you need a JSON file to create a World. If you've already read that section, you might be wondering, *how do I bind my backgrounds to the locations?* It's easy! You just need to reference the background names in the corresponding key for backgrounds. For example:

If I define these backgrounds in Ren'Py:

```python
image bg bedroom_day = "mod_assets/bg/bedroom/bedroom_day.jpg"
image bg bedroom_afternoon = "mod_assets/bg/bedroom/bedroom_afternoon.jpg"
image bg bedroom_night = "mod_assets/bg/bedroom/bedroom_night.jpg"
```

Then, just add the same names to the corresponding keys in the JSON file:

```json
{
  "B-Bedroom": {
    "day": "bg bedroom_day",
    "afternoon": "bg bedroom_afternoon",
    "night": "bg bedroom_night"
  }
}
```

And that's it! You're ready to go.

<h2 id="how-to-add-a-character">How to add a character 👥</h2>

To add a character to a location, first get the desired location using `world.get_location_by_name` or `world.get_location` (which is faster). For details on how to use these functions, check [World 🌍](./README.md#world).

Once you have the location, use the `add_character` method and provide the name of the character you want to add. For example:

```python
school = world.get_location_by_name('School')
# or
# school = world.get_location('School', 'B')

school.add_character('Mike')

print(school.who_is_here())
# Output: Mike
```

This will add Mike to the School location, and you will then see Mike in the character selector.

<h2 id="main-components">Main Components 📚</h2>

To display the **world info**, you need to add a screen called `world_info`. Remember to use the `show screen` statement. To show the locations and characters, use the `location_selector` screen with the `call screen` statement. This will pause the game's flow until a location or character is selected.

When combined, it looks like this:

```python
show screen world_info
call screen location_selector()
```

The `location_selector` screen requires trhee parameters: `characters`, `locations`, and `parent location`. To pass these parameters, you need the `current_place` object (Building, Room, etc.). In the demo game, it looks like this:

```python
  python:
    # To avoid of getting the same location twice
    if current_place is None or current_place.name != persistent.location:
      current_place = world.get_location_by_name(persistent.location)

show screen world_info
call screen location_selector(current_place.characters, current_place.sub_locations_here(), current_place.parent_location)
```

The `current_place` variable is already defined in `world_navigator_definitions.rpy`, so you don't need to redefine it.

Another important function is `set_bg_manually`, which sets the background when you reach a location. Here's how you would add it to the previous example:

```python
  python:
    # To avoid of getting the same location twice
    if current_place is None or current_place.name != persistent.location:
      current_place = world.get_location_by_name(persistent.location)

scene expression set_bg_manually() with fadeIn
show screen world_info
call screen location_selector(current_place.characters, current_place.sub_locations_here(), current_place.parent_location)
```

If this seems complex, you can use the `navigation_label` screen. This screen functions similarly to the previous example. Here's what it looks like:

```python
######################################################
# This label is where navigation happens,
# but if you want a specific use case, you can change this
######################################################
label navigation_label(my_label):
  python:
    # To avoid of getting the same location twice
    if current_place is None or current_place.name != persistent.location:
      current_place = world.get_location_by_name(persistent.location)

    
  scene expression set_bg_manually() with fadeIn
  show screen world_info
  call screen location_selector(current_place.characters, current_place.sub_locations_here(), current_place.parent_location)

  $ renpy.call(my_label)

  jump navigation_label # This maintains the loop of navigation
```

`my_label` is a label used in the demo game, and you're welcome to use it as well. However, I recommend developing your own logic based on your needs. Essentially, this label allows for specific dialogue to trigger based on the character selected in the character selector.

<h2 id="on-action">On Action 🎮</h2>

Now it's time to see how it looks in action. First, take a look at the dynamic weather in the demo game.

<video src="./static/dynamic_weather.mp4" controls></video>

As you can see, the weather effects are dynamic, and the backgrounds also change according to the time. Unfortunately, they cannot change based on the weather (yet).

<video src="./static/dynamic_background.mp4" controls></video>

When the weather is `Stormy`, there is a thunder effect with a `12.5%` chance of being triggered (this can be changed). In theory, it's set to mimic real-life thunderstorms, but it still needs some improvements.

<video src="./static/thunders.mp4" controls></video>

As you already know, the rain and snow effects are triggered by the weather. However, if you are in a location marked as `is_indoor` (such as a Room or Corridor), all weather effects will be disabled until you leave the location. The sound effects follow the same logic.


<video src="./static/indoors.mp4" controls ></video>

<h3 id="customizable-variables">Customizable variables 🎨</h3>

In the `world_definitions.rpy` file, you will find a list of variables that can be customized.

```python
define world = parser.unpack('demo.json') # Change this file for your JSON file

# This values affects the world
define interval_seconds = 1.5 # This means that every 1.5 seconds in real time is 2 in game time
define game_time = 2 # 2 minutes in game time
define day_duration = 24 # 24 hours is a day
define weather_period_transition = (2, 4) # Hours between weather transitions
define thunder_chance = 0.125 # Chance of thunder it goes from 0.0 to 1.0
```

The most important variable is `world`, this is the `World` that you will be using. Just change the file name to the one you want to use (see the [How to create a World 🛠️](./README.md#how-to-create-a-world) section).

You can change these values to your liking. For example, if you want to change the weather period transition to `3` hours, you can do so by changing the `weather_period_transition` variable, like this:

```python
# Every weather last at least 3 hours and canno't be longer than 4 hours
define weather_period_transition = (3, 4)
```

This means if is `Rainy` that weather will last at least 3 hours (game time) and cannot be longer than 4 hours (game time).

Another example is `game_time` which is the amount of minutes for every `interval_seconds` in real time. By default, it's set to 2 minutes, but if is too slow, you can change it, for example:

```python
# Every 2 minutes in real time is 1 minute in game time
define interval_seconds = 1.5
define game_time = 10
```

With this changes, every `1.5 seconds` in real time is `10` minutes in game time. On the other hand, if you want every `.5 seconds` in real time to be `2 minutes` in game time, you can do so by changing the `interval_seconds` variable, like this:

```python
# Every .5 seconds in real time is 2 minutes in game time
define interval_seconds = .5
define game_time = 2
```

This means every `.5 seconds` in real time is `2 minutes` in game time.

Here is a table where you can see the duration of some times with the defualt values:

| Real life time | Game time          |
|----------------|--------------------|
| 1.5 seconds    | 2 minutes          |
| 45 seconds     | 1 hour             |
| 18 minutes     | 24 hours           |
| 1 hour         | 1 day and 20 hours |
| 24 hours       | 32 days            |

<h3 id="sounds-volume">Sounds volume 🔊</h3>

In the `world_definitions.rpy` file, I defined two channels for the sounds, `weather_music` and `thunder_sounds` so be carfull with re-defining them. The `weather_music` channel is used for the weather sounds, and the `thunder_sounds` channel is used for the thunder sounds.


```python
# Register sound channels
renpy.music.register_channel("weather_music", mixer="weather", tight=True)
renpy.music.register_channel("thunder_sounds", mixer="weather", tight=True)
```

To change the volume of the sounds, you can use the `weather_volume_control` screen. This screen is just a slider that you can use to change the volume of the weather sounds. To use it on your preferences screen (or any other screen), just add this code: 

```python
use weather_volume_control
```

And that's it!

<h3 id="styles">Styles 🎨</h3>

The styles for `world_info` and `location_selector` are customizable, just go to the `world_definitions.rpy` file and change the styles.

This are the styles:
```python
style world_info_frame:
  yalign 0.025
  xsize 300
  padding (10, 10)

style world_info_vbox:
  xfill True
  spacing 5

style world_info_hbox:
  xfill True
  spacing 5

style  world_info_text:
  size 25
  xalign 0.0

style location_selector_window:
  background None
  yalign 0
  xalign 0
  ypos 200
  xsize 300
  ysize config.screen_height - 300

style location_selector_vbox:
  xalign .5
  spacing 15

style location_selector_grid:
  spacing 10
  align (0.5, 0)

style location_selector_frame:
  xfill True
  padding (10, 10)
  top_padding 20
  bottom_padding 20

style location_selector_button:  
  xminimum 100
    
style location_selector_button_text:
  size 35
  align (0.5, 0.5)

style location_selector_text:
  size 25
```

Maybe is too complicated, but is the most customizable option, so you can change the styles to your liking.

<h2 id="demo">Demo 🎮</h2>

If you want to see the demo, you can download it from the [releases](https://github.com/ikaroskurtz/WorldNavigator/releases) page. Is a .rar called `WorldNavigator Demo.rar` just download and extract it, and run the `WorldNavigatorDemo.exe` file.
