import logging
import pygame
# from editor import NodeEditor # Old import
# from toolbar import Toolbar # Old import
# from button import Button # Old import
# from actions import (AddNodeAction, # Old import
#                      DeleteAllAction, # Old import
#                      DumpGraphAction, # Old import
#                      UndoAction) # Old import
from app import App # New import

if __name__ == "__main__":
    # Pygame initialization is now handled in App.__init__
    # logging.basicConfig(level=logging.INFO) # Can be kept if needed, or moved to App
    
    # Old setup:
    # toolbar = Toolbar()
    # toolbar.add_button(Button(action=AddNodeAction(), label="Add Node"))
    # toolbar.add_button(Button(action=DeleteAllAction(), label="Clear All"))
    # toolbar.add_button(Button(action=UndoAction(), label="Undo"))
    # toolbar.add_button(Button(action=DumpGraphAction(), label="Print Graph Model"))
    # editor = NodeEditor(toolbar)
    # editor.run()

    # New setup:
    logging.basicConfig(level=logging.INFO) # Keep logging setup here for now
    app_instance = App()
    app_instance.run()
