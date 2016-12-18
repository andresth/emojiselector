# Emoji Selector

## Goal
The intention is to provide an easy way to input emoji into any text entry field.

This progam is basically just a popup dialog where you can select an emoji. It then will instert the emoji by simulation keystrokes.

Currently it will only work on GTK+ based desktop environments.

## How to install
1. Make sure `python-gi` and `xdotool` is present an your system.
```
sudo apt install python3-gi xdotool
```
2. git clone this repository
```
git clone something
```
3. Add a keyboard shortcut.  
Goto `Systemsettings` > `Keyboard` > `Shortcuts` and press the `+` sign.  
Give the shortcut a name and insert this command: `sh -c 'cd /path/to/repository && /usr/bin/python3 ./emojiselector.py'` (reolace /path/to/repository with the real path on your system).  
Define a key sequence for the command ( i took `Super+F1`)
4. Enjoy 😎

## Credits
This application uses the [emojione](http://emojione.com) artwork from Rick Moby.

## Todo
* ~~Multicharacter emoji (i.e skin tone)~~
* Get rid of the `ctrl+shift+u` keysequence and input emoji directly (xdotool can do this)
* Improve UI
  * Set focus to search field
  * Display recently used emoji
  * User defined favorites
* Find a better way to interface with libxdo
