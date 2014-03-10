import vim
import threading
import subprocess
import tempfile
import sets

class MapScopes:
    Normal = 1
    Visual = 2
    Select = 4
    Insert = 8
    All = Insert | Select | Visual | Normal
    AllButInsert = Select | Visual | Normal

class VimUtil:
    @staticmethod
    def Init():
        """Must be called by the plugin during init"""
        VimUtil._printbuffer = []
        VimUtil._appendbuffer = []
        VimUtil._lock = threading.RLock()
        VimUtil._asynccomponents = []

        # Set of buffer names that belong to the plugin
        VimUtil._pluginbuffers = sets.Set()

    @staticmethod
    def DeclarePluginBuffer(name):
        VimUtil._pluginbuffers.add(name)

    @staticmethod
    def ConstructPlusCmd(commands):
        """Returns a correctly formatted +cmd string (see :help +cmd)"""
        result = "+" + " | ".join(commands) 
        result = result.replace(" ", "\\ ")
        return result

    @staticmethod
    def Map(keys, mapping, scope):
        """Conveniently define vim mappings"""
        keys = keys.split(",")
        for i in keys:
            if MapScopes.Insert | scope: vim.command("inoremap <silent> <buffer> " + i + " " + mapping)
            if MapScopes.Visual | scope: vim.command("vnoremap <silent> <buffer> " + i + " " + mapping)
            if MapScopes.Select | scope: vim.command("snoremap <silent> <buffer> " + i + " " + mapping)
            if MapScopes.Normal | scope: vim.command("nnoremap <silent> <buffer> " + i + " " + mapping)

    @staticmethod
    def GetCursor():
        """Returns a 2-tuple containing (row, col)"""
        # Note: There's also a function called getpos that gives more info
        row = int(vim.eval("line(\".\")"))
        col = int(vim.eval("col(\".\")"))
        return (row, col)

    @staticmethod
    def SetCursor(col, pos):
        """Set the cursor position of the current window"""
        vim.eval("setpos(\".\", [0,%s,%s,0])" % (col, pos))

    @staticmethod
    def RegisterAsyncComponent(component):
        assert component != None
        with VimUtil._lock:
            VimUtil._asynccomponents.append(component)

    @staticmethod
    def Print(text):
        """Thread safe print method, can be used to print from other threads"""
        with VimUtil._lock:
            VimUtil._printbuffer.append(text)
        VimUtil.TriggerUpdate()

    @staticmethod
    def UpdateAsync():
        with VimUtil._lock:
            # Print any pending prints
            for i in VimUtil._printbuffer:
                print i
            del VimUtil._printbuffer[:]

            # Update any async components
            for c in VimUtil._asynccomponents:
                c.UpdateAsync()

        return 0

    @staticmethod
    def TriggerUpdate():
        """This method should be called whenever a thread wants the main thread to call UpdateAsync"""
        servername = vim.eval("v:servername")
        startupinfo = subprocess.STARTUPINFO()
        if subprocess.mswindows:
            startupinfo.dwFlags = 0x00000010 | 0x00000001 # CREATE_NEW_CONSOLE | STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0x00000000 # SW_HIDE

        outfile = tempfile.TemporaryFile(mode="w")
        errfile = tempfile.TemporaryFile(mode="w")
        infile = tempfile.TemporaryFile(mode="r")
        subprocess.Popen(["vim", "--servername", "" + servername + "", "--remote-expr", "pyeval(\"VimUtil.UpdateAsync()\")"], shell=False, stdout=outfile, stderr=errfile, stdin=infile, startupinfo=startupinfo) 

        # TODO: should we delete the tempfiles? 
        # TODO: should we reuse them?

    @staticmethod
    def OnWinLeave():
        # Keep the last window so when a file is opened we open it there but 
        # don't use our own windows to open files of course.
        if vim.current.window.buffer.name not in VimUtil._pluginbuffers:
            VimUtil.lastWindow = vim.current.window

