import vim

class MapScopes:
    Normal = 1
    Visual = 2
    Select = 4
    Insert = 8
    All = Insert | Select | Visual | Normal
    AllButInsert = Select | Visual | Normal

class VimUtil:
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

