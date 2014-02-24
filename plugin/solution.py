import vim
import re
import os.path
from tree import Folder, TreeOption, TreeNode
from project import ProjectDef, Project, ProjectConfiguration
from builder import Builder

class Solution(Folder):
    """Represents a VS solution (i.e. .sln file)"""

    def __init__(self, path):
        TreeNode.__init__(self)
        # Read the whole solution into a string
        try:
            with open(path, 'r') as content_file:
                raw = content_file.read()
        except Exception as e:
            print "The solution file could not be read. Aborting."
            print e
            return
        self.absolutePath = os.path.abspath(path)
        self.solutionDir = os.path.dirname(path)
        self.name = os.path.basename(path)

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
                m = re.match("Project\(\"(?P<type>.*?)\"\)\s*=\s*\"(?P<name>.*?)\"\s*,\s*\"(?P<path>.*?)\"\s*,\s*\"(?P<uuid>.*?)\"", p)
                # print m.group("type") + ": " + m.group("name") + ", " + m.group("path") + ", " + m.group("uuid")
                self.projectDefs.append(ProjectDef(self, m.group("type"), m.group("name"), m.group("path"), m.group("uuid")))
        except Exception as e:
            print ("The projects in the solution are not in the expected format, please send the solution file to juancampa "
                  "at gmail dot com so the plugin can be enhanced, thanks! Aborting. Also please include the following error:")
            print e
            return

        # Create the builder, if anything goes wrong while reading the
        # configuration/platform data this field will be set to None to
        # indicate that we don't know how to build this solution.
        self.builder = Builder(self)

        # Read all solution configuration/platform data.
        try: 
            self.configurations = []
            self.platforms = []
            block = re.search("GlobalSection\(SolutionConfigurationPlatforms\)\s*=\s*preSolution\s*(.*?)EndGlobalSection", raw, re.DOTALL | re.MULTILINE)
            if block != None:
                blockItems = re.findall("^\s*(.*?)\|(.*?)\s*=\s*.*", block.group(1), re.MULTILINE);
                for i in blockItems:
                    config = i[0]
                    plat = i[1]

                    if not config in self.configurations:
                        self.configurations.append(config)
                    if not plat in self.platforms:
                        self.platforms.append(plat)

            # Add the solution options to the hierarchy
            self.configuration = TreeOption("Config  ", self.configurations, 0)
            self.platform = TreeOption("Platform", self.platforms, 0)
            self.children.append(self.configuration)
            self.children.append(self.platform)

        except Exception as e:
            self.builder = None         # Disable building
            print ("Configuration data could not be read from the .sln file, the solution won't be buildable from Vim:")
            print e
            return

        # Read all project configuration/platform data. This is the most bizarre
        # part of an sln file the value after the Build.0 doesn't really mean
        # anything. But if a "Build.0" exists is because the project is selected to
        # be built under the solution configuration
        try: 
            block = re.search("GlobalSection\(ProjectConfigurationPlatforms\)\s*=\s*postSolution\s*(.*?)EndGlobalSection", raw, re.DOTALL | re.MULTILINE)
            if block != None:
                blockItems = re.findall("^\s*(\{[A-Z0-9-]*?\})\.(.*?)\|(.*?)\.(.*?)\s*=\s*(.*?)\|(.*?)\s*$", block.group(1), re.MULTILINE);
                for i in blockItems:
                    projectUUID = i[0]
                    solutionConfig = i[1]
                    solutionPlatform = i[2]
                    prop = i[3]
                    projectConfig = i[4]
                    projectPlatform = i[5]

                    projectDef = self.GetProjectDefByUUID(projectUUID)
                    if projectDef != None:
                        config = projectDef.GetOrCreateConfig(solutionConfig, solutionPlatform)
                        # print i[0] + "-" + i[1] + "-" + i[2] + "-" + i[3] + "-" + i[4] + "-" + i[5] + "-"
                        if "ActiveCfg" in prop:
                            config.SetProjectConfig(projectConfig, projectPlatform)
                        elif "Build.0" in prop:
                            config.Enable()

        except Exception as e:
            self.builder = None         # Disable building
            print ("Project configuration data could not be read from the .sln file, the solution won't be buildable from Vim:")
            print e
            return

        # Now check if there are any nested projects in the NestedProjects section
        nestings = re.search("GlobalSection\(NestedProjects\)\s*=\s*preSolution\s*(.*?)EndGlobalSection", raw, re.DOTALL | re.MULTILINE)
        if nestings != None:
            nestings = re.findall("(\{[A-Z0-9-]*?\})\s*=\s*(\{[A-Z0-9-]*?\})", nestings.group(1), re.MULTILINE);
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

