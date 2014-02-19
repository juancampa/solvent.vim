import vim
import os.path
import threading
import subprocess
import sys

# __file__ is not defined by vim for some reason, so do it ourselves.
__file__ = vim.vars["python_filename"]
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from solution import Solution
from solutionview import SolutionView
from tree import Actions
from vimutil import VimUtil, MapScopes

class Solvent:
    view = None

    @staticmethod
    def StartPlugin(solutionPath):
        """Initializes the plugin, this method should only be called once or bad things might happen?"""
        Solvent._actionMappings = {}
        
        # Create the solution and the tree view.
        Solvent.solution = Solution(solutionPath)
        Solvent.view = SolutionView(Solvent.solution)

        vim.command("augroup Solvent")
        vim.command("autocmd!")
        vim.command("autocmd BufEnter %s* stopinsert" % (Solvent.view.bufferName))
        vim.command("autocmd BufEnter %s* python Solvent.SetKeyBindings()" % (Solvent.view.bufferName))
        vim.command("autocmd WinLeave * python Solvent.OnWinLeave()")
        vim.command("augroup END")

        Solvent.view.EnsureOpen()
        Solvent.view.Render()

        # Default mappings
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

        Solvent.SetKeyBindings()

    @staticmethod
    def SetKeyBindings():
        # Disable editing.
        # VimUtil.Map("i,I,a,A,o,O,r,R,c,C,d,D", "<Esc>", MapScopes.All)

        # Default + user defined mappings
        for k in Solvent._actionMappings.keys():
            VimUtil.Map(k, ":python Solvent.PerformAction(\"%s\")<Cr>" % Solvent._actionMappings[k], MapScopes.All)

    @staticmethod
    def Build():
        if Solvent.solution.builder != None:
            Solvent.solution.builder.Build()

    @staticmethod
    def Clean():
        if Solvent.solution.builder != None:
            Solvent.solution.builder.Clean()

    @staticmethod
    def OnWinLeave():
        # Keep the last window so when a file is opened we open it there.
        if Solvent.view != None and Solvent.view.window != vim.current.window:
            Solvent.lastWindow = vim.current.window

    @staticmethod
    def MapKey(key, actions):
        Solvent._actionMappings[key] = actions

    @staticmethod
    def PerformAction(actions):
        actions = actions.split(",")

        for action in actions:
            actionNum = 0
            action = action.strip().lower()
            if action == "expand": actionNum = Actions.Expand
            if action == "collapse": actionNum = Actions.Collapse
            if action == "expandorcollapse": actionNum = Actions.ExpandOrCollapse
            if action == "expandall": actionNum = Actions.ExpandAll
            if action == "collapseall": actionNum = Actions.CollapseAll
            if action == "expandorcollapseall": actionNum = Actions.ExpandOrCollapseAll
            if action == "expanddescendants": actionNum = Actions.ExpandDescendants
            if action == "collapsedescendants": actionNum = Actions.CollapseDescendants
            if action == "openfile": actionNum = Actions.OpenFile
            if action == "openfileinvertsplit": actionNum = Actions.OpenFileInVertSplit
            if action == "openfileinhorisplit": actionNum = Actions.OpenFileInHoriSplit
            if action == "toggleoption": actionNum = Actions.ToggleOption
            if actionNum > 0:
                Solvent.view.PerformAction(actionNum)

    @staticmethod
    def GetCtrlPFileList():
        """Return the complete list of files to vimscript to be used inside ctrlp"""
        result = []
        if Solvent.view != None and Solvent.solution != None:
            for p in Solvent.solution.projects:
                pid = p.GetProjectId()
                projectName = p.definition.name
                for i in range(0, len(p.files)):
                    f = p.files[i]
                    result.append(f.relativePath + " \t(in " + projectName + ") (id:" + str(pid) + "-" + str(i) + ")")
        return vim.List(result)

    @staticmethod
    def AcceptCtrlPStr():
        """Processes the result of a ctrlp search by opening the selected file"""
        # Parameters for this function are passed through a global var to avoid having
        # problems with special characters
        mode = vim.vars["solvent_strParam1"]
        line = vim.vars["solvent_strParam2"]

        # Extract the id from the string which uniquely identifies each file
        m = re.search("\(id:([0-9]*)-([0-9]*)\)$", line)
        projectIndex = int(m.group(1))
        fileIndex = int(m.group(2))

        # Open the file
        Solvent.solution.projects[projectIndex].files[fileIndex].PerformAction(Actions.OpenFile)

VimUtil.Init()
Solvent.StartPlugin(vim.current.buffer.name)

