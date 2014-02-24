import subprocess
import sys
import threading
import itertools
import time
import re, string; 
import Queue
from vimutil import VimUtil

class Builder:
    """Manages building a solution by invoking msbuild and monitoring its output"""
    def __init__(self, solution):
        self.solution = solution

        self.process = None
        self.monitor = None

    def Build(self):
        self.Execute("build")

    def Clean(self):
        self.Execute("clean")
    
    def Execute(self, target):
        """Executes msbuild with the provided target"""
        s = self.solution;
        args = [
            "C:\\Windows\\Microsoft.NET\\Framework\\v4.0.30319\\MSBuild.exe", 
            s.absolutePath,
            "/t:" + target, 
            "/property:Platform=" + s.platform.GetSelected(), 
            "/property:Configuration=" + s.configuration.GetSelected(),
            "/nologo",
            #"/noconsolelogger",
            ]

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
        if self.process != None:
            # Let a BuildMonitor run watch the output of msbuild from another thread
            self.monitor = _BuildMonitor()

    def Stop(self):
        """Stops the current build, if any"""
        if self.process != None:
            self.process.terminate()

    def IsRunning():
        return self.process != None

class _BuildMonitor:
    """Runs a thread that watches a queue where other two threads put the output of stdout and stderr"""
    def __init__(self, process):
        self.process = process
        self.thread = threading.Thread(target=self.StartMonitoring, args=(process,))
        self.thread.daemon = True    # So this thread dies with vim
        self.thread.start()

    def StartMonitoring(self, process):
        """This function monitors the msbuild process, printing from here will sometime produce
           garbage output back in Vim so inter thread synchronization must be used."""

        VimUtil.Print("msbuild pid=" + str(process.pid))

        # Create the two threads that watch the output of msbuild stdout/stderr
        queue = Queue.Queue()
        outIter = _FileMonitor(process.stdout, queue)
        errIter = _FileMonitor(process.stderr, queue)

        returncode = None
        while returncode == None:
            try:
                line = queue.get_nowait()
                VimUtil.Print(line)
            except Queue.Empty:
                time.sleep(1)
            returncode = process.returncode 

        # Wait for process to terminate
        VimUtil.Print("msbuild returned:" + str(returncode))

class _FileMonitor:
    """Monitors the provided file (i.e. stdout or stderr of the msbuild process) and copies it to
    the provided queue"""
    def __init__(self, file, queue):
        self.thread = threading.Thread(target=self.StartMonitoring, args=(file, queue))
        self.thread.daemon = True    # So this thread dies with vim
        VimUtil.Print("Starting thread")
        self.thread.start()

    def StartMonitoring(self, file, queue):
        VimUtil.Print("Thread started")
        for line in iter(file.readline, ''):
            queue.put(line)
