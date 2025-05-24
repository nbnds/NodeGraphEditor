import pygame
import sys
# import math # No longer used here
# import networkx as nx # No longer used here
from constants import (WHITE, WINDOW_WIDTH, WINDOW_HEIGHT, TOOLBAR_WIDTH) # Removed unused constants

# from connection import Connection # No longer directly managed here
# from undo import UndoStack # No longer directly managed here
from toolbar import Toolbar
# from selection import NodeSelection # No longer directly managed here
# from settings import PANNING_FOLLOWS_MOUSE # No longer used here
from textinput import TextInputRenderer, TextInputEngine
# from typing import List # No longer used here
# from node import Node # No longer directly managed here
# from fps_counter import FPSCounter # Replaced by FPSCounterComponent

class NodeEditor:
    """
    Manages the overall editor application, including toolbar,
    text input, and coordinating with other components.
    This class is being refactored. Node/canvas specific logic is moved
    to NodeAreaComponent and EditorContext.
    It is becoming a very thin class.
    """
    def __init__(self, toolbar=None): # undo_depth removed, toolbar likely to be a component too
        # Screen, clock, FPSCounter are managed by App.
        
        # Most attributes previously here are now in EditorContext or NodeAreaComponent.
        # self.fps_counter = FPSCounter(pos=(0, self.screen.get_height()-40)) # Removed

        # nx_graph, nodes, connections, undo_stack, selection, next_node_id,
        # canvas_offset_x, canvas_offset_y, panning, pan_start, pan_offset_start, zoom
        # are now managed by EditorContext and/or NodeAreaComponent.
        
        # self.toolbar = toolbar if toolbar else Toolbar() # Toolbar is now a component managed by App
        # self.text_input_active = False # Managed by TextInputComponent
        # self.visualizer = TextInputRenderer(...) # Managed by TextInputComponent

        # The App class now holds references to EditorContext and ComponentRegistry
        # self.context = EditorContext() # This would be passed in or created by App
        # self.registry = ComponentRegistry() # This would be passed in or created by App
        # self.node_area = NodeAreaComponent(self.context) # This would be created by App
        # self.registry.register(self.node_area)
        # self.registry.register(self.toolbar) # Toolbar is now a component

    # The run method is now entirely in App.
    # def run(self):
    #     pass

    # Event handling for node area, panning, zooming, etc., is in NodeAreaComponent.
    # Event handling for text input is in TextInputComponent (activated by App).
    # Event handling for toolbar is in ToolbarComponent.
    # Global event handling (QUIT, VIDEORESIZE, K_TAB for text input activation) is in App.

    # def dispatch_event(self, event): # Removed
    #     pass

    # def handle_key_down(self, event): # Removed, text input activation in App, specific keys in TextInputComponent
    #     pass
    
    # All specific mouse handlers (handle_mouse_down, _up, _motion, _wheel) removed.
    # These are now in NodeAreaComponent or handled by individual components like ButtonComponent.

    # The main draw call is managed by App through ComponentRegistry.
    # Specific draw methods like draw_grid, draw_nodes, draw_connections, draw_offscreen_indicators
    # are in NodeAreaComponent.
    # draw_toolbar is in ToolbarComponent.
    # draw_text is in TextInputComponent.
    
    # def draw(self, events): # Removed
    #     pass

    # def draw_text(self, events): # Removed
    #     pass

    # def draw_toolbar(self, screen): # Removed
    #     pass

    # Utility methods like try_delete_connection, try_delete_node, screen_to_world are
    # in NodeAreaComponent or EditorContext.

    # Placeholder methods for old Actions are kept for now, but will be phased out
    # as Actions are updated to use EditorContext directly.
    # If NodeEditor class is kept, it should not be passed to Actions.
    # Actions should operate on EditorContext.

    def add_node_editor_method(self, node_type, position=None):
        """ Placeholder: Actions should use EditorContext.add_node. """
        print(f"NodeEditor (deprecated call): add_node_editor_method({node_type}, {position})")
        # Example: self.context.add_node(Node(id=None, title=node_type, x=position[0], y=position[1]))

    def delete_all_nodes_editor_method(self):
        """ Placeholder: Actions should use EditorContext.clear_all_nodes_and_connections. """
        print("NodeEditor (deprecated call): delete_all_nodes_editor_method")
        # Example: self.context.clear_all_nodes_and_connections()

    def undo_editor_method(self):
        """ Placeholder: Actions should use EditorContext.undo_stack.undo(). """
        print("NodeEditor (deprecated call): undo_editor_method")
        # Example: self.context.undo_stack.undo()
        
    def dump_graph_editor_method(self):
        """ Placeholder: Actions should use EditorContext.nx_graph. """
        print("NodeEditor (deprecated call): dump_graph_editor_method")
        # Example: print(self.context.nx_graph.nodes(data=True))
