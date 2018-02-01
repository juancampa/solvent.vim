import json
from vimutil import VimUtil

class MessageImportance:
    Low     = 0
    Medium  = 1
    High    = 2

class EventTypes:
    """Event types generated by msbuild"""
    Unknown               = 0
    RawMessage            = 1
    BuildStarted          = 2
    BuildFinished         = 3
    ProjectStarted        = 4
    ProjectFinished       = 5
    TargetStarted         = 6
    TargetFinished        = 7
    TaskStarted           = 8
    TaskFinished          = 9
    BuildMessage          = 10
    BuildWarning          = 11
    BuildError            = 12

    @staticmethod
    def GetString(t):
        if t == EventTypes.Unknown: return "Unknown"
        if t == EventTypes.RawMessage: return "Message"
        if t == EventTypes.BuildStarted: return "Build Started"
        if t == EventTypes.BuildFinished: return "Build Finished"
        if t == EventTypes.ProjectStarted: return "Project Started"
        if t == EventTypes.ProjectFinished: return "Project Finished"
        if t == EventTypes.TargetStarted: return "Target Started"
        if t == EventTypes.TargetFinished: return "Target Finished"
        if t == EventTypes.TaskStarted: return "Task Started"
        if t == EventTypes.TaskFinished: return "Task Finished"
        if t == EventTypes.BuildMessage: return "Message"
        if t == EventTypes.BuildWarning: return "Warning"
        if t == EventTypes.BuildError: return "ERROR"

class BuildEvent:
    def __init__(self):
        self.type = EventTypes.Unknown
        self.importance = MessageImportance.High
        self.values = None
        self.expanded = False
        pass

    def __getitem__(self, i):
        if self.values:
            return self.values[i]
        else:
            return None

    def __setitem__(self, i, values):
        if self.values == None:
            self.values = {}
        self.values[i] = values

    def GetRenderedString(self):
        result = EventTypes.GetString(self.type).ljust(16) + "| " + self["shortmessage"]
        # TODO: handle expanded!
        return result

    @staticmethod
    def FromJSON(jsonstr):
        """Reads the input string and returns a BuildEvent object containing
        all the data from the json string accessible as a dictionary. Some
        values (i.e. type and importance) are copied to their respective
        BuildEvent fields for faster usage during filtering.  If jsonstr is not
        an actual json object the BuildEvent returned is a RawMessage with the
        "message" value containg whatever was passed in jsonstr
        """ 
        result = BuildEvent()
        try:
            result.values = json.loads(jsonstr)
        except ValueError:
            result["type"] = "RawMessage"
            result["timestamp"] = "n/a"
            result["message"] = jsonstr

        # Get the short version of the message (the first line) which is rendered
        # when the event is collapsed in the builder view.
        try:
            result["shortmessage"] = result["message"][0:result["message"].index("\n")]
        except ValueError:
            result["shortmessage"] = result["message"]

        assert result["type"]

        type = result["type"].strip().lower()
        if type == "rawmessage": result.type = EventTypes.RawMessage
        if type == "buildstarted": result.type = EventTypes.BuildStarted
        if type == "buildfinished": result.type = EventTypes.BuildFinished
        if type == "projectstarted": result.type = EventTypes.ProjectStarted
        if type == "projectfinished": result.type = EventTypes.ProjectFinished
        if type == "targetstarted": result.type = EventTypes.TargetStarted
        if type == "targetfinished": result.type = EventTypes.TargetFinished
        if type == "taskstarted": result.type = EventTypes.TaskStarted
        if type == "taskfinished": result.type = EventTypes.TaskFinished
        if type == "buildmessage": result.type = EventTypes.BuildMessage
        if type == "buildwarning": result.type = EventTypes.BuildWarning
        if type == "builderror": result.type = EventTypes.BuildError

        # if this is a message, transalte the "importance" value into ints.
        if result.type == EventTypes.BuildMessage:
            if result["importance"] == "Low": result["importance"] = MessageImportance.Low
            if result["importance"] == "Medium": result["importance"] = MessageImportance.Medium
            if result["importance"] == "High": result["importance"] = MessageImportance.High
            result.importance = result["importance"]

        return result