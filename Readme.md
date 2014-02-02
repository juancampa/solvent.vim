Solvent.vim
===========

Let's you use Visual Studio solutions from Vim. The solution structure is displayed in a tree similar to NERDTree but with the contents of the solution's file hierarchy.

## Why?

If you work in a team that uses Visual Studio but you want to use vim instead this plugin is for you

## Requirements

 * Vim 7.4 (not yet tested with other versions but it might work at least with 7.3.596)
 * Python support compiled into Vim

## Status

 * **Do not clone yet. This is not ready for use yet but will be soon**
 * Shows the solution/projects structure on a side window and let's you explore it

## Usage

 * Open a .sln file in Vim and run `:Dissolve` this will open a window showing all projects and files. The default mappings for this buffer are:

    Solvent.MapKey("<CR>",      "ExpandOrCollapse,OpenFile")
    Solvent.MapKey("o",         "Expand,OpenFile")
    Solvent.MapKey("O",         "ExpandDescendants,OpenFile")
    Solvent.MapKey("c",         "Collapse")
    Solvent.MapKey("C",         "CollapseDescendants")
    Solvent.MapKey("<C-CR>",    "ExpandOrCollapse,OpenFileInVertSplit")
    Solvent.MapKey("zo",        "Expand")
    Solvent.MapKey("zc",        "Collapse")
    Solvent.MapKey("za",        "ExpandOrCollapse")
    Solvent.MapKey("zO",        "ExpandAll")
    Solvent.MapKey("zC",        "CollapseAll")
    Solvent.MapKey("zA",        "ExpandOrCollapseAll")
    Solvent.MapKey("<space>",   "ExpandOrCollapse")

 * If you have [CtrlP](https://github.com/kien/ctrlp.vim) installed, you can use `:CtrlPCmdSolvent` to search through solution files

## Roadmap

The following is a list of features to be implemented in the order they are probably going to get implemented. If you think the list need another item(s) or reordering just let me know.

 * ~~Read sln~~ (Only tested with VS 2010 .sln files for now)
 * ~~Read C++ .vcxproj and related .filter~~ (Only tested with VS 2010 format for now)
 * ~~Key mapping system~~
 * ~~Actually open files in project~~ Files are currently opened in the last used window
 * ~~CtrlP extension for fuzzy search within the solution~~ Use command :CtrlPCmdSolvent (see above)
 * Tree coloring
 * Persist status in some kind of "solvent.suo" (?) file
 * Support the workflow where the solution tree is shown temporarily in the current buffer instead of another window
 * Editing of the project/solution (adding/removing files)
 * Read the available Configurations/Platforms
 * Enable building from Vim using MSBuild
 * Check/Add support for other proj files (C#, VB, and so forth)
 * Item properties (i.e. property window)
 * Add support for other project formats (e.g. xcodeproj and so forth)
 * Write vim docs
