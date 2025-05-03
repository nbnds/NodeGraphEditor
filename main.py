from editor import NodeEditor
from toolbar import Toolbar
from button import Button
from actions import (AddNodeAction,
                     DeleteAllAction,
                     DumpGraphAction,
                     NoOpAction,
                     UndoAction)

if __name__ == "__main__":

    toolbar = Toolbar()
    toolbar.add_button(Button(action=AddNodeAction(), label="Add Node"))
    toolbar.add_button(Button(action=DeleteAllAction(), label="Clear All"))
    toolbar.add_button(Button(action=DumpGraphAction(), label="Print Graph Model"))
    toolbar.add_button(Button(action=UndoAction(), label="Undo"))
    toolbar.add_button(Button(action=NoOpAction(), label="NO_OP"))
    editor = NodeEditor(toolbar)
    editor.run()
