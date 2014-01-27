import xml.etree.ElementTree as ET
import re

class ProjectDef
    def __init__(self, type, name, filename, uuid):
        self.type = type
        self.name = name
        self.filename = filename
        self.uuid = uuid

class Project:
    def __init__(self, path):
        tree = ET.parse('D:\Eons\Eons')
        root = tree.getroot()

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
            for p in projectStrings:
                m = re.match("Project\(\"(?P<type>.*?)\"\) *= *\"(?P<name>.*?)\" *, *\"(?P<filename>.*?)\" *, *\"(?P<uuid>.*?)\"", p)
                # print m.group("type") + ": " + m.group("name") + ", " + m.group("filename") + ", " + m.group("uuid")
                self.projectDefs = []
                self.projectDefs.append(ProjectDef(group("type"), m.group("name"), m.group("filename"), m.group("uuid")))

        except Exception as e:
            print "The projects in the solution are not in the expected format, please send the solution file to juancampa 
            at gmail dot com so the plugin can be enhanced, thanks! Aborting. Also please include the following error:"
            print e
            return

        # So if everything went well while reading the sln, let's open the projects.
        for definition in self.projectDefs:
            project = Project(definition)

sln = Solution("../../Auralux/Code/WarEngine.sln")
