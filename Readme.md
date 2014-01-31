Solvent.vim
===========

Let's you use Visual Studio solutions from Vim. The solution structure is displayed in a tree similar to NERDTree but with the contents of the solution's file hierarchy.

## Why?

If you work in a team that uses Visual Studio but you want to use vim instead this plugin is for you

## Requirements

 * Vim 7.4 (not yet tested with other versions)
 * Python support compiled into Vim

## Status

 * **Do not clone yet. This is not ready for use yet but will be soon**
 * Shows the solution/projects structure on a side window and let's you explore it

## Roadmap

The following is a list of features to be implemented in the order they are probably going to get implemented. If you think the list need another item(s) or reordering just let me know.

 * ~~Read sln~~ (Only tested with VS 2010 .sln files for now)
 * ~~Read C++ .vcxproj and related .filter~~ (Only tested with VS 2010 format for now)
 * ~~Key mapping system~~
 * ~~Actually open files in project~~ Files are currently opened in the last used window
 * Tree coloring
 * Persist status in some kind of "solvent.suo" (?) file
 * Editing of the project/solution (adding/removing files)
 * Read the available Configurations/Platforms
 * Enable building from Vim using MSBuild
 * Check/Add support for other proj files (C#, VB, and so forth)
 * Item properties (i.e. property window)
