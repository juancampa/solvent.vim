import vim
from vimutil import VimUtil
from tree import Actions

class SolutionView:
    """Represents the window in vim where the solution is shown"""

    def __init__(self, solution):
        self.window = None
        self.buffer = None
        self.solution = solution
        self.bufferName = "sln-vim-buffer-name"     # Just some name nobody else would ever use
        self.defaultBufferWidth = 32
        self.lineToNodeMapping = {}

    def IsOpen(self):
        """Whether the view is open"""
        for w in vim.windows:
            if self.bufferName in w.buffer.name:
                return w.valid and w.buffer.valid
        return False

    def EnsureOpen(self):
        """Ensures that there's a window open and it's associated 
           with our buffer so we can render to it"""
        
        # Make sure there's no previous buffer open
        for w in vim.windows:
            if self.bufferName in w.buffer.name:
                saved = vim.current.window
                vim.current.window = w
                vim.command("hide")
                if saved.valid:                    # We might have closed the saved
                    vim.current.window = saved

        if (not self.IsOpen()):
            vim.command(str(self.defaultBufferWidth) + 
                "vnew " + VimUtil.ConstructPlusCmd([
                    "set nobuflisted",                  # Don't list this buffer
                    "set buftype=nofile",               # Not a file buffer (so vim won't try to save)
                    "set bufhidden=unload",             # Unload when the window closes (we can always create a new one)
                    "setlocal nowrap",                  # No line wrapping
                    "setlocal noswapfile",              # No swap file for this buffer
                    "set filetype=sln-vim",             # Our own filetype
                    "setlocal nomodifiable",            # Only the plugin can change the contents
                    "set cursorline",                   # Make vim highlight the whole line
                    "file %s" % self.bufferName]))      # Set the name so we know how to find it

            # Find our window and buffer
            for b in vim.buffers:
                if self.bufferName in b.name:
                    self.buffer = b
                    break
            for w in vim.windows:
                if w.buffer == b:
                    self.window = w
                    break

    def Render(self):
        """Renders the tree in the current buffer"""
        if self.buffer != None and self.buffer.valid:
            self.buffer.options["modifiable"] = True

            # Save the mouse cursor because it's reset to zero when we clear the buffer
            cursor = VimUtil.GetCursor()

            # Clear everything before we render
            self.buffer[:] = None
            self.lineToNodeMapping.clear()

            # Recursively render the tree
            self.__RenderTree(self.solution, 0)

            # Move the cursor back to where we originally were
            VimUtil.SetCursor(cursor[0], cursor[1])
            self.buffer.options["modifiable"] = False

    def __RenderTree(self, node, depth):
        """Helper method that does the actual rendering recursively"""

        # Render the expand symbold (TODO: move this to be part of the node?)
        if len(node.children) > 0:
            if node.expanded:
                statusSym = "-"
            else:
                statusSym = "+"
        else:
            statusSym = " "

        # setup the mapping for this node so we know in which line it is
        self.lineToNodeMapping[len(self.buffer) + 1] = node

        # Render the node
        indent = " " * depth
        self.buffer.append(indent + statusSym + node.GetNodeName())

        # Recursively render this node's children
        if node.expanded:
            for child in node.children:
                if node.IndentsChildren():
                    self.__RenderTree(child, depth + 1)
                else:
                    self.__RenderTree(child, depth + 0)

    def GetSelected(self):
        cursor = VimUtil.GetCursor()
        if cursor[0] in self.lineToNodeMapping:
            return self.lineToNodeMapping[cursor[0]]
        else:
            return None

    def PerformAction(self, action):
        """Forwards the action to the currently selected node"""
        assert vim.current.window == self.window
        assert vim.current.buffer == self.buffer

        # Forward the action to the currently selected node
        selected = self.GetSelected()
        if selected != None:
            selected.PerformAction(action)

            # Actions that apply to all descendants of the selected node
            if action == Actions.ExpandDescendants: 
                self.__PerformInDescendants(selected, Actions.Expand)
            if action == Actions.CollapseDescendants: 
                self.__PerformInDescendants(selected, Actions.Collapse)

        # Actions that apply to all nodes
        if action == Actions.ExpandAll: 
            for n in self.lineToNodeMapping.values(): 
                n.PerformAction(Actions.Expand) 
        if action == Actions.CollapseAll: 
            for n in self.lineToNodeMapping.values(): 
                n.PerformAction(Actions.Collapse) 
        if action == Actions.ExpandOrCollapseAll: 
            for n in self.lineToNodeMapping.values(): 
                n.PerformAction(Actions.ExpandOrCollapse) 

        # Render again because something probably changed
        if vim.current.window == self.window:
            self.Render()

    def __PerformInDescendants(self, node, action):
        node.PerformAction(action)
        for c in node.children:
            self.__PerformInDescendants(c, action)
