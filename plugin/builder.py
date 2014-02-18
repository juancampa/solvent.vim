import subprocess
import sys
import threading

class Builder:
    def __init__(self, solution):
        self.solution = solution

        self.process = None
        self.thread = None
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
            self.process = subprocess.Popen(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        except Exception as e:
            self.process = None
            print "The solution file doesn't seem to have valid solution contents. Aborting."
            print e

        # Did we succeeded creating the msbuild subprocess?
        if self.process != None:
            # Let a BuildMonitor run on another thread watching the output of msbuild
            self.monitor = _BuildMonitor()
            self.thread = threading.Thread(target=self.monitor.StartMonitoring, args=(self.process,))
            self.thread.start()

    def Stop(self):
        """Stops the current build, if any"""
        if self.process != None:
            self.process.terminate()

    def IsRunning():
        return self.process != None

class _BuildMonitor:
    def __init__(self):
        pass

    def StartMonitoring(self, process):
        """This function monitors the msbuild process, printing from here will sometime produce
           garbage output back in Vim so inter thread synchronization must be used."""
        print "msbuild pid=" + str(process.pid)
        print "msbuild returned:" + str(process.returncode)
        output, error_output = process.communicate()
        print "msbuild returned:" + str(process.returncode)
        print 'OUTPUT:'
        print output
        print 'ERROR:'
        print error_output
