import vim
import threading
import subprocess
import tempfile

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
        VimUtil._printbuffer = []
        VimUtil._lock = threading.RLock()

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

    @staticmethod
    def Print(text):
        with VimUtil._lock:
            VimUtil._printbuffer.append(text)
        VimUtil.TriggerUpdate()

    @staticmethod
    def AsyncUpdate():
        with VimUtil._lock:
            for i in VimUtil._printbuffer:
                print i
            del VimUtil._printbuffer[:]

        return 0

    @staticmethod
    def TriggerUpdate():
        servername = vim.eval("v:servername")
        startupinfo = subprocess.STARTUPINFO()
        if subprocess.mswindows:
            startupinfo.dwFlags = 0x00000010 | 0x00000001 # CREATE_NEW_CONSOLE | STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0x00000000 # SW_HIDE
        outfile = tempfile.TemporaryFile(mode="w")
        errfile = tempfile.TemporaryFile(mode="w")
        infile = tempfile.TemporaryFile(mode="r")
        subprocess.Popen(["vim", "--servername", "" + servername + "", "--remote-expr", "pyeval(\"VimUtil.AsyncUpdate()\")"], shell=False, stdout=outfile, stderr=errfile, stdin=infile, startupinfo=startupinfo) 

        # TODO: should we delete the tempfiles?
