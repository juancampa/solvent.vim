import subprocess
import sys
import threading
import itertools
import time
import re, string; 
import Queue
from vimutil import VimUtil
from outputview import OutputView
from buildevent import *

class Builder:
    """Manages building a solution by invoking msbuild and monitoring its output"""
    def __init__(self, solution):
        self.solution = solution

        self.process = None
        self.monitor = None
        self.outputview = OutputView(self)
        self.buildevents = []

        # Where the monitor thread will put the processed output of msbuild
        self.outputqueue = Queue.Queue()
        VimUtil.RegisterAsyncComponent(self)

    def Build(self):
        self.Execute("build")

    def Clean(self):
        self.Execute("clean")
    
    def Execute(self, target):
        """Executes msbuild with the provided target"""
        s = self.solution;
        loggerPath = "D:\\Git\\vim_msbuild\\plugin\\SolventLogger.dll"
        args = [
            "C:\\Windows\\Microsoft.NET\\Framework\\v4.0.30319\\MSBuild.exe", # TODO: fix this path!
            s.absolutePath,
            "/t:" + target, 
            "/property:Platform=" + s.platform.GetSelected(), 
            "/property:Configuration=" + s.configuration.GetSelected(),
            "/nologo",
            "/noconsolelogger",
            "/logger:" + loggerPath,
            ]

        # print args
        self.outputview.Show()

        startupinfo = subprocess.STARTUPINFO()
        if subprocess.mswindows:
            startupinfo.dwFlags = 0x00000010 | 0x00000001 # subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0x00000000 # subprocess.SW_HIDE

        try:
            self.process = subprocess.Popen(args=args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        except Exception as e:
            self.process = None
            VimUtil.Print("Couldn't spawn msbuild process")
            VimUtil.Print(e)

        # Did we succeeded creating the msbuild subprocess?
        # Let a BuildMonitor run watch the output of msbuild from another thread
        if self.process != None:
            self.monitor = _BuildMonitor(self.process, self.outputqueue)

    def Stop(self):
        """Stops the current build, if any"""
        if self.process != None:
            self.process.terminate()

    def IsRunning(self):
        return self.process != None

    def UpdateAsync(self):
        while True:
            needUpdate = False
            try:
                while True:
                    e = self.outputqueue.get_nowait()
                    self.buildevents.append(e)
                    needUpdate = True
            except Queue.Empty:
                # Re-render if there are any new events events coming from the buildmonitor.
                if needUpdate:
                    self.outputview.Render()
                break
            except:
                break

class _BuildMonitor:
    """Runs a thread that watches a queue where other two threads put the output
    of stdout and stderr FIXME: I think we could live without this thread, using
    the queue used by the _FileMonitor thread directly
    """

    def __init__(self, process, queue):
        self.process = process
        self.thread = threading.Thread(target=self.StartMonitoring, args=(process,))
        self.thread.daemon = True    # So this thread dies with vim
        self.thread.start()
        self.outputqueue = queue

    def StartMonitoring(self, process):
        """This function monitors the msbuild process, printing from here will
        sometime produce garbage output back in Vim so inter thread
        synchronization must be used.
        """

        # Create the two threads that watch the output of msbuild stdout/stderr
        queue = Queue.Queue()
        outIter = _FileMonitor(process.stdout, queue)
        errIter = _FileMonitor(process.stderr, queue)

        returncode = None
        while returncode == None:
            needUpdate = False
            try:
                while True:
                    event = queue.get_nowait()
                    self.outputqueue.put(event)
                    needUpdate = True
            except Queue.Empty:
                if needUpdate:
                    VimUtil.TriggerUpdate()
                # If the queue was empty and the process ended there is
                # definitely nothing else to monitor so end this thread.
                returncode = process.returncode 
            time.sleep(0.300)

        # Wait for process to terminate
        VimUtil.Print("msbuild returned:" + str(returncode))

class _FileMonitor:
    """Monitors the provided file (i.e. stdout or stderr of the msbuild process)
    and for each json object put in it it will create the corresponding instance
    in the provided queue
    """
    def __init__(self, file, queue):
        self.thread = threading.Thread(target=self.StartMonitoring, args=(file, queue))
        self.thread.daemon = True    # So this thread dies with vim
        self.thread.start()

    def StartMonitoring(self, file, queue):
        buffer = ""
        for line in iter(file.readline, ''):
            buffer += line
            # Whenever we find a closing bracket by itself it's because we've
            # found the end of an event. TODO: shouldn't this detection be more robust?
            if ( # TODO: this is the handling of messages output by msbuild that don't come from our solventlogger.dll
                 # we need to make this more robust because there might also be messages mixed in the jsons.
               line.strip() == "}" or
               line.startswith("Verbosity:") or
               line.startswith("Building the projects in this solution one at a time")
               ):
                e = BuildEvent.FromJSON(buffer)
                queue.put(e)
                buffer = ""

