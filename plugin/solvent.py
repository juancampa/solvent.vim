import xml.etree.ElementTree as ET
import re
import os.path
import vim

class MapScopes:
    Normal = 1
    Visual = 2
    Select = 4
    Insert = 8
    All = Insert | Select | Visual | Normal
    AllButInsert = Select | Visual | Normal

class VimUtil:
    @staticmethod
    def ConstructPlusCmd(commands):
        """Returns a correctly formatted +cmd string (see :help +cmd)"""
        result = "+" + " | ".join(commands) 
        result = result.replace(" ", "\\ ")
        return result

    @staticmethod
    def Map(keys, mapping, scope):
        keys = keys.split(",")
        for i in keys:
            if MapScopes.Normal | scope: vim.command("nnoremap <buffer> " + i + " " + mapping)
            if MapScopes.Visual | scope: vim.command("vnoremap <buffer> " + i + " " + mapping)
            if MapScopes.Select | scope: vim.command("snoremap <buffer> " + i + " " + mapping)
            if MapScopes.Insert | scope: vim.command("inoremap <buffer> " + i + " " + mapping)

    @staticmethod
    def GetCursor():
        """Returns a 2-tuple containing (row, col)"""
        # Note: There's also a function called getpos that gives more info
        row = int(vim.eval("line(\".\")"))
        col = int(vim.eval("col(\".\")"))
        return (row, col)

    @staticmethod
    def SetCursor(col, pos):
        vim.eval("setpos(\".\", [0,%s,%s,0])" % (col, pos))

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

class TreeNode:
    """Base class for all elements on the tree"""
    def __init__(self):
        self.children = []
        self.parent = None
        self.expanded = True

    def GetNodeName(self):
        pass

    def GetDisplayName(self):
        return GetNodeName()

    def GetChildByName(self, name):
        for c in self.children:
            if c.GetNodeName() == name:
                return c
        return None

    def IndentsChildren(self):
        return True

    def PerformAction(self, action):
        pass

class ProjectDef:
    """Project information as it's read from the sln file"""
    @staticmethod
    def TranslateProjectType(type):
        """Utility function to transform project type UUIDs into a human readable string"""
        if type == "{2150E333-8FDC-42A3-9474-1A3956D46DE8}":
            return "general"
        elif type == "{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}":
            return "cpp"
        else:
            print "WARNING: Unknown project type: " + type
            return "cpp"

    def __init__(self, solution, type, name, filepath, uuid):
        self.solution = solution
        self.type = ProjectDef.TranslateProjectType(type)
        self.name = name
        self.filepath = filepath
        self.absolutePath = os.path.join(solution.solutionDir, filepath)
        self.absoluteDirPath = os.path.dirname(self.absolutePath)
        self.uuid = uuid
        self.parentuuid = None

class Folder(TreeNode):
    def __init__(self, name):
        TreeNode.__init__(self)
        self.name = name

    def GetNodeName(self):
        return self.name

    def GetDisplayName(self):
        return self.ame + "/"

    def PerformAction(self, action):
        if action == Actions.Expand: self.expanded = True
        if action == Actions.Collapse: self.expanded = False
        if action == Actions.ExpandOrCollapse: self.expanded = not self.expanded

class File(TreeNode):
    def __init__(self, project, relativeFilepath):
        TreeNode.__init__(self)
        self.project = project
        self.relativeFilepath = relativeFilepath
        self.filename = os.path.basename(self.relativeFilepath)

    def GetNodeName(self):
        return self.filename

    def PerformAction(self, action):
        if action == Actions.OpenFile:
            if vim.current.window != None and vim.current.window.valid:
                vim.current.window = Solvent.lastWindow
            vim.command("edit " + os.path.join(self.project.definition.absoluteDirPath, self.relativeFilepath))

class Project(Folder):
    def __init__(self, definition):
        TreeNode.__init__(self)
        self.definition = definition

        #print "Loading " + definition.type + " project at: " + definition.absolutePath
        # Is there an actual file related to this project?
        if (definition.type == "general"):
            pass

        # TODO: Add support for other kinds of projects. Do I need to make a distinction??
        if (definition.type == "cpp"):
            try:
                # First try to open the filter file which is the tree we prefer to show
                tree = ET.parse(definition.absolutePath + ".filters")
            except Exception as e:
                try:
                    # Apparently there's no filter file, just open the regular vcxproj
                    tree = ET.parse(definition.absolutePath)
                except Exception as e:
                    print "Project " + definition.name + " could not be opened at \"" + definition.absolutePath + "\". Skipping."
                    print e
                    self.loaded = False
                    return
            root = tree.getroot()

            # Get the namespace since every tag returned by etree is prefixed by it
            # so we're gonna need it to find element using xPath
            self.xmlns = re.match("{(.*?)}", root.tag).group(1)

            itemGroups = root.findall(".//{%s}ItemGroup" % (self.xmlns));

            for g in itemGroups:
                # TODO: Apparently if it doesn't have a label then it's a group of 
                # files we want to show? There's probably a better way to determine that
                if g.get("Label") != None:
                    continue
                for i in g:
                    # Ignore filters since each file's filter specify the same information
                    if i.tag == ("{%s}Filter" % (self.xmlns)):
                        continue
                    # Ignore project references (this are project dependencies, maybe we want those?)
                    if i.tag == ("{%s}ProjectReference" % (self.xmlns)):
                        continue
                    # All items I've seen have the Include property but just to make sure
                    if i.get("Include") != None:
                        self.__ReadFile(i)

        self.loaded = True

    def __ReadFile(self, item):
        """Reads a file from xml and creates a corresponding File object in the
        right folder (according to its filter)"""
        filepath = item.get("Include")
        filter = item.find("{%s}Filter" % self.xmlns)
        if filter != None:
            filter = filter.text
            folder = self.GetOrCreateFolder(filter)
        else:
            folder = self
        folder.children.append(File(self, filepath))

    def GetOrCreateFolder(self, path):
        folders = path.split("\\")
        node = self
        for folderName in folders:
            child = node.GetChildByName(folderName)
            if child == None:
                child = Folder(folderName)
                node.children.append(child)
            node = child
        return node

    def GetNodeName(self):
        return "[%s]" % self.definition.name

    def IndentsChildren(self):
        return True

class Solution(Folder):
    """Represents a VS solution (i.e. .sln file)"""

    def __init__(self, filepath):
        TreeNode.__init__(self)
        # Read the whole solution into a string
        try:
            with open(filepath, 'r') as content_file:
                raw = content_file.read()
        except Exception as e:
            print "The solution file could not be read. Aborting."
            print e
            return
        self.solutionDir = os.path.dirname(filepath)
        self.name = os.path.basename(filepath)

        # Find out the version of the solution
        try:
            m = re.search("Format Version (.*)", raw)
            self.formatVersion = m.group(1)
            # print "Solution format version " + self.formatVersion
        except Exception as e:
            print "The solution file doesn't seem to have valid solution contents. Aborting."
            print e
            return
        
        # Read all projects' data
        try:
            projectStrings = re.findall("^Project.*?^EndProject$", raw, re.DOTALL | re.MULTILINE)
            self.projectDefs = []
            for p in projectStrings:
                m = re.match("Project\(\"(?P<type>.*?)\"\) *= *\"(?P<name>.*?)\" *, *\"(?P<filepath>.*?)\" *, *\"(?P<uuid>.*?)\"", p)
                # print m.group("type") + ": " + m.group("name") + ", " + m.group("filepath") + ", " + m.group("uuid")
                self.projectDefs.append(ProjectDef(self, m.group("type"), m.group("name"), m.group("filepath"), m.group("uuid")))
        except Exception as e:
            print ("The projects in the solution are not in the expected format, please send the solution file to juancampa "
                  "at gmail dot com so the plugin can be enhanced, thanks! Aborting. Also please include the following error:")
            print e
            return

        # Now check if there are any nested projects in the NestedProjects section
        nestings = re.search("GlobalSection\(NestedProjects\) *= *preSolution *(.*?)EndGlobalSection", raw, re.DOTALL | re.MULTILINE)
        if nestings != None:
            nestings = re.findall("(\{[A-Z0-9-]*?\}) *= *(\{[A-Z0-9-]*?\})", nestings.group(1));
            for n in nestings:
                child = self.GetProjectDefByUUID(n[0])
                child.parentuuid = n[1]

        # So if everything went well while reading the sln, let's open the projects.
        self.projects = []
        for definition in self.projectDefs:
            project = Project(definition)
            self.projects.append(project)

        # Now that the projects are loaded in a list, build the hierarchy
        for p in self.projects:
            if p.definition.parentuuid != None:
                parent = self.GetProjectByUUID(p.definition.parentuuid)
                parent.children.append(p)
                p.parent = parent
            else:
                self.children.append(p)

    def GetNodeName(self):
        return "[%s]" % self.name

    def GetProjectDefByUUID(self, uuid):
        for x in self.projectDefs:
            if x.uuid == uuid:
                return x
        return None

    def GetProjectByUUID(self, uuid):
        for x in self.projects:
            if x.definition.uuid == uuid:
                return x
        return None

    def IndentsChildren(self):
        return False

class Actions:
    """Actions that can be mapped to a key"""
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

class Solvent:
    view = None

    @staticmethod
    def StartPlugin():
        """Initializes the plugin, this method should only be called once or bad things might happen?"""

        Solvent.actionMappings = {}
        
        # sln = Solution("../../Auralux/Code/WarEngine.sln")
        # sln = Solution("../../OSWrapper/OSWrapper.sln")
        sln = Solution("F:\ChavoKart\Development\Src\UE3.sln")
        Solvent.view = SolutionView(sln)

        vim.command("augroup Solvent")
        vim.command("autocmd!")
        vim.command("autocmd BufEnter %s* stopinsert" % (Solvent.view.bufferName))
        vim.command("autocmd BufEnter %s* python Solvent.SetKeyBindings()" % (Solvent.view.bufferName))
        vim.command("autocmd WinLeave * python Solvent.OnWinLeave()")
        vim.command("augroup END")

        Solvent.view.EnsureOpen()
        Solvent.view.Render()

        # Default mappings
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

        Solvent.SetKeyBindings()

    @staticmethod
    def SetKeyBindings():
        # Default mappings
        # VimUtil.Map("i,I,a,A,o,O,r,R,c,C,d,D", "<Esc>", MapScopes.All)

        # Default + user defined mappings
        for k in Solvent.actionMappings.keys():
            VimUtil.Map(k, ":python Solvent.PerformAction(\"%s\")<Cr>" % Solvent.actionMappings[k], MapScopes.All)

    @staticmethod
    def OnWinLeave():
        # Keep the last window so when a file is opened we open it there.
        Solvent.lastWindow = vim.current.window

    @staticmethod
    def MapKey(key, actions):
        Solvent.actionMappings[key] = actions

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

            if actionNum > 0:
                Solvent.view.PerformAction(actionNum)

Solvent.StartPlugin()
