Solvent.vim
===========

Let's you use Visual Studio solutions from Vim. The solution structure is displayed in a tree similar to NERDTree but with the contents of the solution's file hierarchy.

## Why?

If you work in a team that uses Visual Studio but you want to use vim instead this plugin is for you

## Requirements

 * Vim 7.4 (not yet tested with other versions but it might work at least with 7.3.596)
 * Python support compiled into Vim

## Status

 * **This project is unmaintained but it's there if you want the code**
 * Shows the solution/projects structure on a side window and let's you explore it

## Usage

 * Open a .sln file in Vim and run `:Dissolve` this will open a window showing all projects and files. The default mappings for this window are:

```python
Solvent.MapKey("<CR>",      "ExpandOrCollapse,OpenFile,ToggleOption")
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
Solvent.MapKey("<space>",   "ExpandOrCollapse,ToggleOption")
```

 * If you have [CtrlP](https://github.com/kien/ctrlp.vim) installed, you can use `:CtrlPCmdSolvent` to search through solution files.
 * Unite.vim integration will be eventually added.

## Roadmap

The following is a list of features to be implemented in the order they are probably going to get implemented. If you think the list need another item(s) or reordering just let me know.

 - [x] Read sln (Only tested with VS 2010 .sln files for now)
 - [x] Read C++ .vcxproj and related .filter (Only tested with VS 2010 format for now)
 - [x] Key mapping system
 - [x] Actually open files in project Files are currently opened in the last used window
 - [x] CtrlP extension for fuzzy search within the solution Use command :CtrlPCmdSolvent (see above)
 - [ ] Enable building from Vim using MSBuild (Work in progress)
 - [ ] Tree coloring
 - [ ] Persist status in some kind of "<solutionname>.solvent.suo" file
 - [ ] Unite.vim integration
 - [ ] Editing of the project/solution (adding/removing files)
 - [x] Read the available Configurations/Platforms for projects and solution
 - [ ] Check/Add support for other proj files (C#, VB, and so forth). This seem to already work for most projects types.
 - [ ] Item properties (i.e. property window)
 - [ ] Add support for other project formats (e.g. xcodeproj and so forth)
 - [ ] Support the workflow where the solution tree is shown temporarily in the current buffer instead of another window
 - [ ] Write vim docs
