import pygame
import sys
import copy
import networkx as nx
from constants import (WHITE,
                        WINDOW_WIDTH, WINDOW_HEIGHT)

from connection import Connection
from connection_list import ConnectionList
from undo import UndoStack
from toolbar import Toolbar
from selection import NodeSelection
from settings import PANNING_FOLLOWS_MOUSE
from textinput import TextInputRenderer, TextInputEngine
from typing import List
from node import Node
from fps_counter import FPSCounter
from renderer import NodeEditorRenderer  # <-- new import
from canvas_panning import CanvasPanning

class NodeEditor:
    def __init__(self, toolbar=None, undo_depth=10):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Node Graph Editor")
        self.clock = pygame.time.Clock()
        self.fps_counter = FPSCounter(pos=(0, self.screen.get_height()-40))
        self.nx_graph = nx.DiGraph()
        self.nodes: List[Node] = []
        self.connections = ConnectionList()
        self.undo_stack = UndoStack(max_depth=undo_depth)
        self.selection = NodeSelection() # multiple selection of nodes
        self.dragging_connection: bool = False
        self.connection_start_node: tuple[int, int] | None = None
        self.connection_end_pos: tuple[int,int] | None = None
        self.next_node_id = 1
        self.zoom: float = 1.0  # 1.0 = 100%, min 0.1 (1:10), max e.g. 2.0
        self.toolbar = toolbar if toolbar else Toolbar()
        self.text_input_active = False
        self.visualizer = TextInputRenderer(font_color=WHITE,cursor_color=WHITE, engine=TextInputEngine())
        self.fps_counter = FPSCounter(pos=(0, WINDOW_HEIGHT - 40))
        self._node_drag_in_progress = False  # Track if a node drag is in progress
        self.renderer = NodeEditorRenderer(self)  # Pass self or required state
        self.panning_state = CanvasPanning()

    def run(self):
        while True:
            events = pygame.event.get()
            filtered_events = []
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if self.text_input_active:
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key in (pygame.K_TAB, pygame.K_ESCAPE):
                        self.handle_key_down(event)
                        continue
                    if event.type == pygame.KEYUP and event.key in (pygame.K_TAB, pygame.K_ESCAPE):
                        continue
                    filtered_events.append(event)
            else:
                for event in events:
                    self.dispatch_event(event)
                filtered_events = events

            self.draw(filtered_events)
            self.fps_counter.update(self.clock.get_fps())
            self.fps_counter.draw(self.screen)
            pygame.display.flip()
            self.clock.tick()

    def dispatch_event(self, event):
            if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event)
            elif event.type == pygame.MOUSEWHEEL:
                self.handle_mouse_wheel(event)
            elif event.type == pygame.KEYDOWN:
                self.handle_key_down(event)
            elif event.type == pygame.DROPFILE:
                file_path = event.file # type: ignore
                pygame.display.set_caption(f"Node Graph Editor - {file_path}")

    def handle_key_down(self, event):
        if event.key == pygame.K_TAB and not self.text_input_active:
            self.text_input_active = True
        elif event.key == pygame.K_ESCAPE:
            self.text_input_active = False
            self.visualizer.clear_text()

    def handle_mouse_down(self, event):
        btn = self.toolbar.get_clicked_button(event.pos)
        if btn:
            # Execute the action associated with the button
            btn.action.execute(self)
            return

        world_x, world_y = self.screen_to_world(event.pos)
        if event.button == pygame.BUTTON_LEFT:
            clicked_node = None
            for node in reversed(self.nodes):
                if node.contains_point(world_x, world_y) and clicked_node is None:
                    node.dragging = True
                    node.drag_offset = (world_x - node.x, world_y - node.y)
                    # Delegate selection logic:
                    self.selection.select_node(node, self.nodes)
                    clicked_node = node
                    # --- Selected node should be always on top ---
                    self.nodes.remove(node)
                    self.nodes.append(node)
                    # --- Push undo only once per drag start ---
                    if not self._node_drag_in_progress:
                        self.undo_stack.push(copy.deepcopy(self.nx_graph))
                        self._node_drag_in_progress = True
            # Deselect all if no node was clicked
            if clicked_node is None:
                self.selection.clear_selection(self.nodes)

        elif event.button == pygame.BUTTON_MIDDLE:
            # Check if a node was clicked
            if self.try_delete_node(world_x, world_y):
                return
            # Check if a connection was clicked
            self.try_delete_connection(world_x, world_y)


        elif event.button == pygame.BUTTON_RIGHT:
            # Check if a node is under the cursor
            clicked_node = None
            for node in reversed(self.nodes):
                if node.contains_point(world_x, world_y):
                    clicked_node = node
                    break
            selected_nodes = [n for n in self.nodes if n.selected]
            # If a node is selected and another node is right-clicked, connect them
            if selected_nodes and clicked_node is not None and selected_nodes[0] != clicked_node:
                selected_node = selected_nodes[0]
                already_connected = any(
                    (c.start_node == selected_node and c.end_node == clicked_node) or
                    (c.start_node == clicked_node and c.end_node == selected_node)
                    for c in self.connections
                )
                if not already_connected:
                    self.undo_stack.push(copy.deepcopy(self.nx_graph))  # Push before adding edge
                    self.connections.append(Connection(selected_node, clicked_node))
                    self.nx_graph.add_edge(selected_node.id, clicked_node.id)
                # After connecting, deselect the node
                selected_node.selected = False
            # Canvas panning only if no node was hit
            elif clicked_node is None:
                self.panning_state.start_panning(event.pos)

    def handle_mouse_up(self, event):
        if event.button == pygame.BUTTON_LEFT:
            for node in self.nodes:
                node.dragging = False
            self._node_drag_in_progress = False  # Reset drag flag
        elif event.button == pygame.BUTTON_RIGHT:
            self.panning_state.stop_panning()

    def handle_mouse_motion(self, event):
        x, y = event.pos
        #Update hover state for toolbar buttons
        for btn in self.toolbar.buttons:
            btn.hovered = btn.rect.collidepoint(x, y)
        world_x = (x + self.panning_state.offset_x * self.zoom) / self.zoom
        world_y = (y + self.panning_state.offset_y * self.zoom) / self.zoom
        for node in self.nodes:
            if node.dragging:
                node.x = world_x - node.drag_offset[0]
                node.y = world_y - node.drag_offset[1]
                self.nx_graph.nodes[node.id]['pos'] = (node.x, node.y)
        if self.panning_state.panning:
            self.panning_state.update_panning(
                (x, y), self.zoom, PANNING_FOLLOWS_MOUSE
            )

    def handle_mouse_wheel(self, event):
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Convert to world coordinates before zoom
        world_x_before = (mouse_x + self.panning_state.offset_x * self.zoom) / self.zoom
        world_y_before = (mouse_y + self.panning_state.offset_y * self.zoom) / self.zoom

        if event.y > 0:
            self.zoom = min(self.zoom * 1.1, 2.0)
        elif event.y < 0:
            self.zoom = max(self.zoom / 1.1, 0.1)

        # After zoom, adjust offset so the world point under the mouse stays the same
        self.panning_state.offset_x = (world_x_before * self.zoom - mouse_x) / self.zoom
        self.panning_state.offset_y = (world_y_before * self.zoom - mouse_y) / self.zoom

    def draw(self, events):
        self.renderer.draw(events)  # Delegate to renderer

    def try_delete_connection(self, world_x, world_y):
        for conn in list(self.connections):  # Use list() to allow removal during iteration
            if conn.is_clicked(world_x, world_y, zoom=self.zoom):
                self.undo_stack.push(copy.deepcopy(self.nx_graph))
                self.connections.remove(conn)
                if self.nx_graph.has_edge(conn.start_node.id, conn.end_node.id):
                    self.nx_graph.remove_edge(conn.start_node.id, conn.end_node.id)
                return True
        return False

    def try_delete_node(self, world_x, world_y):
        for node in reversed(self.nodes):
            if node.contains_point(world_x, world_y):
                # Remove all connections to/from this node
                self.connections._connections = [
                    c for c in self.connections
                    if c.start_node != node and c.end_node != node
                ]
                self.undo_stack.push(copy.deepcopy(self.nx_graph))
                self.nodes.remove(node)
                self.nx_graph.remove_node(node.id)
                node.selected = False  # Deselect the node if it was selected
                return True
        return False

    def screen_to_world(self, pos):
        x, y = pos
        world_x = (x + self.panning_state.offset_x * self.zoom) / self.zoom
        world_y = (y + self.panning_state.offset_y * self.zoom) / self.zoom
        return world_x, world_y
