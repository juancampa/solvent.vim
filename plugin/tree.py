import os.path
import vim
from vimutil import VimUtil

# TODO: rename this to TreeAction?
class Actions:
    """Actions that can be performed on the solution view and can be mapped to a key"""
    Expand                  = 1
    Collapse                = 2
    ExpandOrCollapse        = 3
    ExpandAll               = 4
    CollapseAll             = 5
    ExpandOrCollapseAll     = 6
    ExpandDescendants       = 7
    CollapseDescendants     = 8
    OpenFile                = 9
    OpenFileInVertSplit     = 10
    OpenFileInHoriSplit     = 11
    ToggleOption            = 12

class TreeNode:
    """Base class for all elements on the tree"""
    def __init__(self):
        self.children = []
        self.parent = None
        self.expanded = True

    def GetNodeName(self):
        pass

    def GetChildByName(self, name):
        for c in self.children:
            if c.GetNodeName() == name:
                return c
        return None

    def IndentsChildren(self):
        return True

    def PerformAction(self, action):
        pass

class Folder(TreeNode):
    """Base class for folders in the tree"""
    def __init__(self, name):
        TreeNode.__init__(self)
        self.name = name

    def GetNodeName(self):
        return self.name

    def PerformAction(self, action):
        if action == Actions.Expand: self.expanded = True
        if action == Actions.Collapse: self.expanded = False
        if action == Actions.ExpandOrCollapse: self.expanded = not self.expanded

class File(TreeNode):
    """Represents a single file in the tree"""
    def __init__(self, project, relativePath):
        TreeNode.__init__(self)
        self.project = project
        self.relativePath = relativePath
        self.filename = os.path.basename(self.relativePath)

    def GetNodeName(self):
        return self.filename

    def PerformAction(self, action):
        if action == Actions.OpenFile:
            if vim.current.window != None and vim.current.window.valid:
                vim.current.window = VimUtil.lastWindow
            vim.command("edit " + os.path.join(self.project.definition.absoluteDirPath, self.relativePath))


class TreeOption(TreeNode):
    """Elements on the tree that represent an option (e.g. Platform, Config, etc)"""
    def __init__(self, name, optionList, selectedIndex=0):
        TreeNode.__init__(self)
        self.selectedIndex = selectedIndex 
        self.options = optionList
        self.name = name

    def PerformAction(self, action):
        if action == Actions.ToggleOption:
            self.selectedIndex = (self.selectedIndex + 1) % len(self.options)

    def GetSelected(self):
        return self.options[self.selectedIndex];

    def GetNodeName(self):
        return self.name + ":" + self.GetSelected();

