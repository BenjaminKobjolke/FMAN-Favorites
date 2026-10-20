# Favorites

Plugin for [fman.io](https://fman.io) that gives you the ability to setup a list of favorite directories to go to.

You can install this plugin by pressing `<shift+cmd+p>` to open the command pallet. Then type `install plugin`. Look for the `favorite` plugin and select it.

After restarting **fman**, you will have the ability to set favorite directories, go to them, set path shorteners, remove path shorteners, remove favorites, and set/go to four directory locations kept in memory.

## Usage

### HotKeys Set

<Shift+f> - Set a new Favorite directory. This makes the current directory in the active pane a favorite directory.

<Ctrl+f> - Remove a Favorite Directory.

<Ctrl+0> - Go to a Favorite Directory.

<Ctrl+1> - Pop up first previous directory.

<Ctrl+2> - Pop up second previous directory.

<Ctrl+3> - Pop up third previous directory.

<Ctrl+4> - Pop up fourth previous directory.

<Ctrl+5> - Pop up fifth previous directory.

<Ctrl+6> - Pop up sixth previous directory.

<Ctrl+7> - Pop up seventh previous directory.

<Ctrl+8> - Pop up the eighth previous directory.

<Cmd+1> - Set the first directory memory to the current panel's directory.

<Cmd+2> - Set the second directory memory to the current panel's directory.

<Cmd+3> - Set the third directory memory to the current panel's directory.

<Cmd+4> - Set the fourth directory memory to the current panel's directory.

<Alt+1> - Set the current panel to go to the first directory memory location.

<Alt+2> - Set the current panel to go to the second directory memory location.

<Alt+3> - Set the current panel to go to the third directory memory location.

<Alt+4> - Set the current panel to go to the fourth directory memory location.

### Commands

`Go To Favorite` - This command will display a list of favorites by their assigned names for the user to choose from. As you type letters in the name, the list is shortened. Once one is selected, the current panel is moved to that directory.

When the `FMAN_FTPClient` plugin is installed, the command `Toggle FTP In Favorites` is available in the command palette. It switches the `show_ftp` setting in `Favorites Settings.json` on or off (off by default). When enabled, `Go To Favorite` (`Ctrl+0`) also lists FTP bookmarks as `FTP: <alias>` and active connections as `FTP open: <server>`. Selecting a bookmark opens its default path; selecting an active connection returns to its last visited path. The toggle command is hidden when the FTP plugin is not installed.

`Go To Favorite Pair` - This command will display a list of favorite directory pairs by their assigned name. When the user selects one, the left and right directories will be set as saved.

`Remove Favorite Directory` - This command will remove the selected favorite directory.

`Remove Favorite Directory Pair` - This command will remove the selected favorite directory pair.

`Set Favorite Directory` - This command sets the currently highlighted directory as a favorite. If the path contains a shortener's path, then it will be shortened to that shorener's name in double brackets.

`Set Favorite Dirctory Pair` - This command sets a left and right directory structure to save.

`Set Shorten Directory` - This command asks the user for a shortener name and creates a new shortener to that directory. Access via command palette (`Shift+Cmd+P` or `Shift+Ctrl+P`) and type "Set Shorten Directory".

`Remove Shortener Directory` - This command removes a shortener directory from the shortener list. It then expands the shortener in all the favorites that had that shortener. Access via command palette and type "Remove Shortener Directory".

`Go to hot dir` - This command set the current panel to the directory store in the memory location specified in the dirNum argument. The default is 0.

`Set hot dir` - This command set the current panel to the directory store in the memory location 1 specified in the dirNum argument. The default is 0.

`List All Hotdirs` - This command displays all currently set hot directories in an alert dialog, showing their indices and full paths. Shows "Not set" for empty slots.

`Clear Hotdirs` - This command clears all hot directories, resetting them to their default state. All hot directory slots will be cleared and the changes are saved persistently.

`pop directory` - This command pops to the previous directory.

### Files Created and Used

`~/.favoritedirs` - This file contains all of your favorite directories. Each line is the assigned name, a "|" symbol, and the path to the directory. If the path contains a directory in the `~/.shorenerdirs` file, then the path is removed and a placeholder is inserted instead.

`~/.shortenerdirs` - This file contains all the shortener directories and their names. It is in the same format as the `~/.favoritedirs` file. Once you create this file, copy it to your Dropbox location and link it back to this location. Now you can share your favorites between systems.

`~/.favoritepairs` - This file contains all the pair of directories stored.

`~/.hotdirs` - This file contains the four hot directory paths that persist across fman restarts. Each line contains one directory path corresponding to hot directory slots 0-3.

### How to Use Shortener Directories

Shortener directories are a powerful feature that allows you to create portable favorites that work across different systems. Here's how to use them:

**Step 1: Set up a shortener directory**

1. Navigate to a parent directory (e.g., `/Users/yourname/Dropbox`)
2. Open the command palette (`Shift+Cmd+P` or `Shift+Ctrl+P`)
3. Type "Set Shorten Directory" and select it
4. Enter a shortener name (e.g., "Dropbox")

**Step 2: Create favorites within the shortener**

- Any favorites you create in subdirectories of your shortener will automatically use the shortener notation
- Instead of storing `/Users/yourname/Dropbox/Projects/MyApp`, it stores `{{Dropbox}}/Projects/MyApp`

**Step 3: Share across systems**

- Copy your `~/.shortenerdirs` and `~/.favoritedirs` files to other systems
- Set up the same shortener names pointing to the equivalent directories on each system
- Your favorites will automatically work on all systems

**Managing shorteners:**

- Use "Remove Shortener Directory" from the command palette to delete a shortener
- When you remove a shortener, all favorites using it are automatically expanded to full paths

### Suggested Usage

Once you install the plugin, set up your shortener directories. I setup one for each of my Dropbox locations. Then, create your favorites in the shorteners subdirectories. Once you have the favorites setup, move your `~/.favoritedirs` to your Dropbox location you want and link to the original location and name. On the second system, setup the same shortener file using the same names and link the synced favoritedirs file to the normal location. Now you can go to the favorite directories inside these shortener directories easily! They also automatically update when you add new ones.

You can also save and restore directory locations in the hot directory memory. There are four hot directory locations that persist across fman restarts. Very useful for saving frequently accessed locations that you want to quickly return to. Use the hotkeys to set and navigate to these locations, or use the command palette to list or clear all hot directories.

### Features

- The ability to set a favorite directory.
- The ability to go to a favorite directory.
- The ability to set a favorite directory pair.
- The ability to go to a favorite directory pair.
- Remove a favorite directory.
- Remove a favorite directory pair.
- Set up directories as shorteners with a name. Then all paths under that directory will be set to the shortener's name and expanded to that path when going to it. This gives the ability to share favorites between system just using the paths in common.
- There are four persistent hot directory locations that can be easily recalled and persist across fman restarts. Store from any panel and restore to any panel.
- List all hot directories with their current paths in a formatted display.
- Clear all hot directories at once to reset them to defaults.
- The ability to backtrack previously visited directories. Not panel specific.
