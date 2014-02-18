import xml.etree.ElementTree as ET
import re
import os.path
from tree import Folder, File, TreeNode

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

    def __init__(self, solution, type, name, path, uuid):
        self.solution = solution
        self.type = ProjectDef.TranslateProjectType(type)
        self.name = name
        self.path = path
        self.filename = os.path.basename(path)
        self.absolutePath = os.path.join(solution.solutionDir, path)
        self.absoluteDirPath = os.path.dirname(self.absolutePath)
        self.uuid = uuid
        self.parentuuid = None
        self.configs = []

    def GetOrCreateConfig(self, solutionConfiguration, solutionPlatform):
        for i in self.configs:
            if i.solutionConfiguration == solutionConfiguration and i.solutionPlatform == solutionPlatform:
                return i
        newConf = ProjectConfiguration(solutionConfiguration, solutionPlatform)
        self.configs.append(newConf)
        return newConf

class Project(Folder):
    def __init__(self, definition):
        TreeNode.__init__(self)
        self.definition = definition
        self.solution = definition.solution
        self.files = []
        self.configurations = []

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
        path = item.get("Include")
        filter = item.find("{%s}Filter" % self.xmlns)
        if filter != None:
            filter = filter.text
            folder = self.__GetOrCreateFolder(filter)
        else:
            folder = self

        file = File(self, path)
        folder.children.append(file)
        self.files.append(file)

    def __GetOrCreateFolder(self, path):
        folders = path.split("\\")
        node = self
        for folderName in folders:
            child = node.GetChildByName(folderName)
            if child == None:
                child = Folder(folderName)
                node.children.append(child)
            node = child
        return node

    def GetProjectId(self):
        """Returns the project id of this project, we need an id because 
        different projects might use the same name"""
        for i in range(0, len(self.solution.projects)):
            if self.solution.projects[i] == self:
                return i
        return -1

    def GetNodeName(self):
        conf = self.definition.GetOrCreateConfig(self.solution.configuration.GetSelected(), self.solution.platform.GetSelected())
        if self.definition.type != "general":
            if conf.builds:
                return "[%s] (%s|%s)" % (self.definition.name, conf.configuration, conf.platform)
            else:
                return "[%s] (won't build)" % self.definition.name
        else:
            return "[%s]" % self.definition.name

    def IndentsChildren(self):
        return True

class ProjectConfiguration():
    def __init__(self, solutionConfiguration, solutionPlatform):
        self.solutionConfiguration = solutionConfiguration
        self.solutionPlatform = solutionPlatform
        self.builds = False

    def SetProjectConfig(self, configuration, platform):
        """The values for $(Platform) and $(Configuration) for this solution config"""
        self.configuration = configuration
        self.platform = platform

    def Enable(self):
        """Whether the project builds for this solution configuration"""
        self.builds = True

