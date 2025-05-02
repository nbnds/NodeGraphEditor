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
    toolbar.add_button(Button(action=DeleteAllAction(), label="Alle löschen"))
    toolbar.add_button(Button(action=DumpGraphAction(), label="Daten ausgeben"))
    toolbar.add_button(Button(action=NoOpAction(), label="NOOP"))
    toolbar.add_button(Button(action=UndoAction(), label="Undo"))
    editor = NodeEditor(toolbar)
    editor.run()