import vim
from vimutil import VimUtil

class View:
    """Base class for views (vim windows)"""
    def __init__(self):
        self.window = None
        self.buffer = None
        self.bufferName = "solvent-view"     # Just some name nobody else would ever use
        self.filetype = "solvent-view-ft"     # Just some name nobody else would ever use
        self.splitoptions = "vertical topleft"
        self.wrap = False

    def IsOpen(self):
        """Whether the view is open"""
        buffer, window = self.FindBufferAndWindow()

        # if there's a window it's because we found the buffer in it so
        # we don't have to check the buffer.
        return window and window.valid

    def Show(self):
        """Ensures that there's a window open and it's associated 
           with our buffer so the user can see it"""
        
        # Make sure there's no previous buffer open
        for w in vim.windows:
            if self.bufferName in w.buffer.name:
                saved = vim.current.window
                vim.current.window = w
                vim.command("hide")
                if saved.valid:                    # We might have closed the saved
                    vim.current.window = saved

        self.buffer, self.window = self.FindBufferAndWindow()
        if not self.window or not self.window.valid:
            wrap = "wrap" if self.wrap else "nowrap"
            vim.command(
                self.splitoptions + " " +
                str(self.defaultViewSize) +"new" +# Window size
                VimUtil.ConstructPlusCmd([
                "set nobuflisted",                  # Don't list this buffer
                "set buftype=nofile",               # Not a file buffer (so vim won't try to save)
                "set bufhidden=unload",             # Unload when the window closes (we can always create a new one)
                "setlocal " + wrap,                 # No line wrapping
                "setlocal noswapfile",              # No swap file for this buffer
                "set filetype=" + self.filetype,    # Our own filetype
                "setlocal nomodifiable",            # Only the plugin can change the contents
                "set cursorline",                   # Make vim highlight the whole line
                "file %s" % self.bufferName]))      # Set the name so we know how to find it

            self.buffer, self.window = self.FindBufferAndWindow()

        # Finally render the contents of the view.
        self.Render()

    def FindBufferAndWindow(self):
        buffer = None
        window = None
        # Find our window and buffer
        for b in vim.buffers:
            if self.bufferName in b.name:
                buffer = b
                break
        if buffer:
            for w in vim.windows:
                if w.buffer == buffer:
                    window = w
                    break

        return (buffer, window)

    def Render(self):
        print "This method should never be called."
        pass

