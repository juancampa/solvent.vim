import xml.etree.ElementTree as ET
import re
import os.path

def TranslateProjectType(type):
    if type == "{2150E333-8FDC-42A3-9474-1A3956D46DE8}":
        return "general"
    elif type == "{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}":
        return "cpp"

class ProjectDef:
    def __init__(self, solution, type, name, filepath, uuid):
        self.solution = solution
        self.type = TranslateProjectType(type)
        self.name = name
        self.filepath = filepath
        self.absolutePath = os.path.join(solution.solutionDir, filepath)
        self.uuid = uuid

class Project:
    def __init__(self, definition):
        self.definition = definition

        print "Loading " + definition.type + " project at: " + definition.absolutePath
        # Is there an actual file related to this project?
        if (definition.type == "general"):
            pass

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

            # Get all cpp files
            self.codeFiles = root.findall(".//{%s}ItemGroup//{%s}ClCompile" % (self.xmlns, self.xmlns));

            # Get all include files
            self.includeFiles = root.findall(".//{%s}ItemGroup//{%s}ClInclude" % (self.xmlns, self.xmlns));

            print str(len(self.codeFiles)) + " code files. " + str(len(self.includeFiles)) + " include files."
            # for f in cppFiles:
            #     print f.get("Include")
            # for f in root:
            #     print str(f.tag)

        self.loaded = True

class Solution:
    """Represents a VS solution (i.e. .sln file)"""

    def __init__(self, filepath):
        # Read the whole solution into a string
        try:
            with open(filepath, 'r') as content_file:
                raw = content_file.read()
        except Exception as e:
            print "The solution file could not be read. Aborting."
            print e
            return
        self.solutionDir = os.path.dirname(filepath)

        # Find out the version of the solution
        try:
            m = re.search("Format Version (.*)", raw)
            self.formatVersion = m.group(1)
            print "Solution format version " + self.formatVersion
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

        # So if everything went well while reading the sln, let's open the projects.
        for definition in self.projectDefs:
            project = Project(definition)

sln = Solution("../../Auralux/Code/WarEngine.sln")
