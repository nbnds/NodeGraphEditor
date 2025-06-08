import pygame
import sys
import math
import copy
import networkx as nx
from constants import (BLUEPRINT_COLOR, BLUEPRINT_LINE_COLOR, WHITE,
                        WINDOW_WIDTH, WINDOW_HEIGHT, TOOLBAR_WIDTH,
                        BLUEPRINT_GRID_SIZE)

from connection import Connection
from undo import UndoStack
from toolbar import Toolbar
from selection import NodeSelection
from settings import PANNING_FOLLOWS_MOUSE
from textinput import TextInputRenderer, TextInputEngine
from typing import List
from node import Node
from fps_counter import FPSCounter

class NodeEditor:
    def __init__(self, toolbar=None, undo_depth=10):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Node Graph Editor")
        self.clock = pygame.time.Clock()
        self.fps_counter = FPSCounter(pos=(0, self.screen.get_height()-40))
        self.nx_graph = nx.DiGraph()
        self.nodes: List[Node] = []
        self.connections = []
        self.undo_stack = UndoStack(max_depth=undo_depth)
        self.selection = NodeSelection() # multiple selection of nodes
        self.dragging_connection: bool = False
        self.connection_start_node: tuple[int, int] | None = None
        self.connection_end_pos: tuple[int,int] | None = None
        self.next_node_id = 1
        self.canvas_offset_x: float = 0
        self.canvas_offset_y: float = 0
        self.panning = False
        self.pan_start = (0, 0)
        self.pan_offset_start = (0, 0)
        self.zoom: float = 1.0  # 1.0 = 100%, min 0.1 (1:10), max e.g. 2.0
        self.toolbar = toolbar if toolbar else Toolbar()
        self.text_input_active = False
        self.visualizer = TextInputRenderer(font_color=WHITE,cursor_color=WHITE, engine=TextInputEngine())
        self.fps_counter = FPSCounter(pos=(0, WINDOW_HEIGHT - 40))
        self._node_drag_in_progress = False  # Track if a node drag is in progress

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
                    node.selected = True
                    clicked_node = node
                    # --- Selected node should be always on top ---
                    self.nodes.remove(node)
                    self.nodes.append(node)
                    # --- Push undo only once per drag start ---
                    if not self._node_drag_in_progress:
                        self.undo_stack.push(copy.deepcopy(self.nx_graph))
                        self._node_drag_in_progress = True
                else:
                    node.selected = False

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
                self.panning = True
                self.pan_start = event.pos
                self.pan_offset_start = (self.canvas_offset_x, self.canvas_offset_y)

    def handle_mouse_up(self, event):
        if event.button == pygame.BUTTON_LEFT:
            for node in self.nodes:
                node.dragging = False
            self._node_drag_in_progress = False  # Reset drag flag
        elif event.button == pygame.BUTTON_RIGHT:
            self.panning = False

    def handle_mouse_motion(self, event):
        x, y = event.pos
        #Update hover state for toolbar buttons
        for btn in self.toolbar.buttons:
            btn.hovered = btn.rect.collidepoint(x, y)
        world_x = (x + self.canvas_offset_x * self.zoom) / self.zoom
        world_y = (y + self.canvas_offset_y * self.zoom) / self.zoom
        for node in self.nodes:
            if node.dragging:
                node.x = world_x - node.drag_offset[0]
                node.y = world_y - node.drag_offset[1]
                self.nx_graph.nodes[node.id]['pos'] = (node.x, node.y)
        if self.panning:
            dx = (x - self.pan_start[0]) / self.zoom
            dy = (y - self.pan_start[1]) / self.zoom
            if PANNING_FOLLOWS_MOUSE:
                self.canvas_offset_x = self.pan_offset_start[0] - dx
                self.canvas_offset_y = self.pan_offset_start[1] - dy
            else:
                self.canvas_offset_x = self.pan_offset_start[0] + dx
                self.canvas_offset_y = self.pan_offset_start[1] + dy

    def handle_mouse_wheel(self, event):
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Convert to world coordinates before zoom
        world_x_before = (mouse_x + self.canvas_offset_x * self.zoom) / self.zoom
        world_y_before = (mouse_y + self.canvas_offset_y * self.zoom) / self.zoom

        if event.y > 0:
            self.zoom = min(self.zoom * 1.1, 2.0)
        elif event.y < 0:
            self.zoom = max(self.zoom / 1.1, 0.1)

        # After zoom, adjust offset so the world point under the mouse stays the same
        self.canvas_offset_x = (world_x_before * self.zoom - mouse_x) / self.zoom
        self.canvas_offset_y = (world_y_before * self.zoom - mouse_y) / self.zoom

    def draw(self, events):
        self.draw_grid()
        self.draw_connections()
        self.draw_nodes()
        self.draw_toolbar()
        self.draw_offscreen_indicators()
        self.draw_text(events)
        self.fps_counter.draw(self.screen)
        pygame.display.flip()

    def draw_text(self, events):
        if self.text_input_active:
            self.visualizer.overlay_enabled = True
            self.visualizer.render_with_overlay(self.screen, events)
            if self.visualizer.should_block_mouse():
                pass
        else:
            self.visualizer.overlay_enabled = False
            # Optional: falls du das Textfeld auch ohne Overlay anzeigen willst
            # self.visualizer.update(events)
            # self.screen.blit(self.visualizer.surface, (200, 200))

    def draw_grid(self):
        # Background
        self.screen.fill(BLUEPRINT_COLOR)

        # Grid with zoom
        grid_size = BLUEPRINT_GRID_SIZE * self.zoom
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()
        x_start = TOOLBAR_WIDTH - (self.canvas_offset_x % BLUEPRINT_GRID_SIZE) * self.zoom
        y_start = - (self.canvas_offset_y % BLUEPRINT_GRID_SIZE) * self.zoom

        x = x_start
        while x < screen_w:
            pygame.draw.line(self.screen, BLUEPRINT_LINE_COLOR, (x, 0), (x, screen_h))
            x += grid_size
        y = y_start
        while y < screen_h:
            pygame.draw.line(self.screen, BLUEPRINT_LINE_COLOR, (TOOLBAR_WIDTH, y), (screen_w, y))
            y += grid_size

    def draw_connections(self):
        # Connections
        for connection in self.connections:
            connection.draw(self.screen, self.canvas_offset_x, self.canvas_offset_y, zoom=self.zoom)

    def draw_nodes(self):
        # Nodes
        for node in self.nodes:
            node.draw(self.screen, self.canvas_offset_x, self.canvas_offset_y, zoom=self.zoom)

    def draw_toolbar(self):
        self.toolbar.draw(self.screen)

    def draw_offscreen_indicators(self):
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()
        color = (160, 160, 160)
        margin = 0
        r_size = 16 # size of the indicator rect

        def is_node_visible(screen_x, screen_y):
            return (
                TOOLBAR_WIDTH + margin < screen_x < screen_w - margin and
                margin < screen_y < screen_h - margin
            )

        def get_screen_coords(node):
            return (
                (node.x * self.zoom) - self.canvas_offset_x * self.zoom,
                (node.y * self.zoom) - self.canvas_offset_y * self.zoom,
            )

        center_x = TOOLBAR_WIDTH + (screen_w - TOOLBAR_WIDTH) // 2
        center_y = screen_h // 2

        for node in self.nodes:
            # COnvert world coordinates to screen coordinates
            screen_x, screen_y = get_screen_coords(node)

            if is_node_visible(screen_x, screen_y):
                continue

            dx = screen_x - center_x
            dy = screen_y - center_y

            # Normalize direction to the edge of the window
            if dx == 0 and dy == 0:
                continue  # should not happen, but just in case

            angle = math.atan2(dy, dx)

            # Determine intersection with window edge
            if abs(dx) > abs(dy * (screen_w / screen_h)):
                # Left/Right edge
                edge_x = screen_w - margin if dx > 0 else TOOLBAR_WIDTH + margin
                edge_y = center_y + (edge_x - center_x) * math.tan(angle)
            # Top/Bottom
            else:
                # Top/Bottom edge
                edge_y = screen_h - margin if dy > 0 else margin
                edge_x = center_x + (edge_y - center_y) / math.tan(angle)

            # Draw indicator rect at edge
            rect_x = int(edge_x - r_size // 2)
            rect_y = int(edge_y - r_size // 2)
            rect = pygame.Rect(rect_x, rect_y, r_size, r_size)
            pygame.draw.rect(
                self.screen,
                color,
                rect,
                width=1,
                border_radius=3
                )

    def try_delete_connection(self, world_x, world_y):
        for conn in self.connections:
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
                self.connections = [
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
        """Wandelt Bildschirmkoordinaten in Weltkoordinaten um (berücksichtigt Zoom und Offset)."""
        x, y = pos
        world_x = (x + self.canvas_offset_x * self.zoom) / self.zoom
        world_y = (y + self.canvas_offset_y * self.zoom) / self.zoom
        return world_x, world_y
