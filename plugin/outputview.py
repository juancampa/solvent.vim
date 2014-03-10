import vim
from vimutil import VimUtil
from vimview import View
from buildevent import *

# TODO: Call this BuilderView?
class OutputView(View):
    def __init__(self, builder):
        View.__init__(self)
        self.builder = builder
        self._lineToEventMapping = {}
        self.showerrors = True
        self.showwarnings = True
        self.showmessages = True
        self.minimportance = MessageImportance.High

        # View settings
        self.bufferName = "solvent-output"     # Just some name nobody else would ever use
        self.filetype = "solvent-output"       # This might be useful for autocmd?
        self.splitoptions = "botright"
        self.defaultViewSize = 10

    def Render(self):
        """Renders the builder's events into the current buffer"""
        if self.buffer != None and self.buffer.valid:
            self.buffer.options["modifiable"] = True

            # Save the mouse cursor because it's reset to zero when we clear the buffer
            cursor = VimUtil.GetCursor()

            # Clear everything before we render
            self.buffer[:] = None
            self._lineToEventMapping.clear()

            for e in self.builder.buildevents:
                # Filter messages
                if (e.type == EventTypes.BuildMessage and
                   ((not self.showmessages) or e.importance < self.minimportance)):
                    continue

                # Filter errors
                if e.type == EventTypes.BuildError and not self.showerrors:
                    continue

                # Filter warnings
                if e.type == EventTypes.BuildWarning and not self.showwarnings:
                    continue

                self.buffer.append(e.GetRenderedString())

            self.window.cursor = (len(self.buffer), 0)

            # Move the cursor back to where we originally were
            # VimUtil.SetCursor(cursor[0], cursor[1])
            self.buffer.options["modifiable"] = False

