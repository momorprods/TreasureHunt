# Treasure Hunt for Pythonista

This application allows you to run and create your own Scavenger-like experiences straight on your iOS device.

## Features

The app offers the following features:
* Seek & find hint locations using the GPS
* Photo & Speech-based hints (suitable for kids)
* Works offline - no internet connection required, no user account to create
* Editor allows you to create your own adventures
* Share your creations with your friends (using iOS built-in share function)

## Installation
There is not specific dependency or setup to do into Pythonista. Just create a dedicated folder and copy all the project files in it.

Run **TreasureHunt.py** to launch the app.

Be sure to have enabled Location and Photo library & Camera access to the Pythonista app.

## How to create an Adventure
The app comes by default with no predefined adventure, so you will have to create one first.


You can also use relative paths like

![Menu Screen](_doc/screen_menu.png?raw=true "Menu screen")

From there, click on the **"+"** button. Enter a name for your adventure and touch the **Create** button.

![Create Screen](_doc/screen_create.png?raw=true "Create screen")

You can now select your adventure and edit it.

An adventure can be considered as a list of hints. For each hint, you have to define:
* The GPS location of the hint
* A photo
* A question that the user has to answer when he reaches the hint

![Editor Screen](_doc/screen_editor.png?raw=true "Editor screen")

Additionally, you can also setup for the adventure:
* An introduction message
* A message displayed at the end of the hunt
* The language used by the speech synthesis

![Settings Screen](_doc/screen_settings.png?raw=true "Settings screen")

## How to play an Adventure

The player must seek & find all the hints, in their sequential order.

![Game Screen](_doc/screen_game.png?raw=true "Game screen")

When he reaches a hint position, the photo is displayed and he is asked to answer the question. Then the game loops to the next hint.

A final score is displayed at the end of the hunt, based on the number of correct answers.

