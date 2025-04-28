import pygame
import sys
import math
from constants import (BLUEPRINT_COLOR, BLUEPRINT_LINE_COLOR, 
                        WINDOW_WIDTH, WINDOW_HEIGHT, TOOLBAR_WIDTH,  
                        BLUEPRINT_GRID_SIZE)

from node import Node
from connection import Connection
from toolbar import Toolbar, ToolbarButton
from selection import NodeSelection
from settings import PANNING_FOLLOWS_MOUSE

pygame.init()

class NodeEditor:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Node Graph Editor")
        self.clock = pygame.time.Clock()
        self.nodes = []
        self.connections = []
        self.selected_node = None
        self.selection = NodeSelection()    
        self.potential_select_node = None
        self.dragging_connection = False
        self.connection_start_node = None
        self.connection_end_pos = None
        self.next_node_id = 1
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        self.panning = False
        self.pan_start = (0, 0)
        self.pan_offset_start = (0, 0)
        self.button_x = 10
        self.button_y = WINDOW_HEIGHT - 50
        self.button_w = 80
        self.button_h = 40
        self.zoom = 1.0  # 1.0 = 100%, min 0.1 (1:10), max e.g. 2.0
        self.toolbar = Toolbar()
        self.toolbar.addButton(ToolbarButton(action="add_node", label="Add Node"))
        self.toolbar.addButton(ToolbarButton(action="delete_all", label="Alle löschen"))
        self.toolbar.addButton(ToolbarButton( action="save_graph", label="Speichern"))
        self.toolbar.layout_buttons()

    def run(self):
        while True:
            for event in pygame.event.get():
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
                    file_path = event.file
                    pygame.display.set_caption(f"Node Graph Editor - {file_path}")
            self.draw()
            self.clock.tick(60)

    def handle_mouse_down(self, event):
        x, y = event.pos
        btn = self.toolbar.get_clicked_button(x, y)
        if btn:
            if btn.action == "add_node":
                # Place new node at the center of the visible canvas
                center_x = self.screen.get_width() // 2
                center_y = self.screen.get_height() // 2
                world_x = (center_x + self.canvas_offset_x * self.zoom) / self.zoom
                world_y = (center_y + self.canvas_offset_y * self.zoom) / self.zoom
                self.nodes.append(Node(world_x, world_y, self.next_node_id))
                self.next_node_id += 1
            elif btn.action == "delete_all":
                self.nodes.clear()
                self.connections.clear()
                self.next_node_id = 1
                self.selected_node = None
            return
        
        world_x, world_y = self.screen_to_world(x, y)
        if event.button == pygame.BUTTON_LEFT:
            # Linksklick: Prüfe, ob ein Node unter dem Cursor ist.
            # Falls ja, aktiviere Dragging für diesen Node.
            # Falls nein, hebe die aktuelle Node-Auswahl auf.
            # x, y = event.pos
            
            for node in reversed(self.nodes):
                if node.contains_point(world_x, world_y):
                    node.dragging = True
                    node.drag_offset = (world_x - node.x, world_y - node.y)
                    self.potential_select_node = node
                    break
            else:
                self.selected_node = None
                self.potential_select_node = None

        elif event.button == pygame.BUTTON_MIDDLE:
            # Knoten unter dem Cursor löschen
            for node in reversed(self.nodes):
                if node.contains_point(world_x, world_y):
                    # Entferne alle Verbindungen zu diesem Knoten
                    self.connections = [
                        c for c in self.connections
                        if c.start_node != node and c.end_node != node
                    ]
                    self.nodes.remove(node)
                    if self.selected_node == node:
                        self.selected_node = None
                    break

        elif event.button == pygame.BUTTON_RIGHT:
            # Prüfe, ob ein Node unter dem Cursor ist
            clicked_node = None
            for node in reversed(self.nodes):
                if node.contains_point(world_x, world_y):
                    clicked_node = node
                    break

            # Wenn ein Node markiert ist und ein anderer Node mit rechts geklickt wird, verbinde sie
            if self.selected_node is not None and clicked_node is not None and self.selected_node != clicked_node:
                already_connected = any(
                    (c.start_node == self.selected_node and c.end_node == clicked_node) or
                    (c.start_node == clicked_node and c.end_node == self.selected_node)
                    for c in self.connections
                )
                if not already_connected:
                    self.connections.append(Connection(self.selected_node, clicked_node))
                self.selected_node = None  # Markierung aufheben nach Verbindung
            # Canvas-Panning nur, wenn kein Node getroffen wurde
            elif clicked_node is None:
                self.panning = True
                self.pan_start = (x, y)
                self.pan_offset_start = (self.canvas_offset_x, self.canvas_offset_y)

    def handle_mouse_up(self, event):
        if event.button == 1:
            for node in self.nodes:
                if node.dragging:
                    node.dragging = False
                    # Nur Markierung setzen, keine Verbindung!
                    if self.potential_select_node == node:
                        self.selected_node = node
                    self.potential_select_node = None
        elif event.button == 3:
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

        old_zoom = self.zoom
        if event.y > 0:
            self.zoom = min(self.zoom * 1.1, 2.0)
        elif event.y < 0:
            self.zoom = max(self.zoom / 1.1, 0.1)

        # After zoom, adjust offset so the world point under the mouse stays the same
        self.canvas_offset_x = (world_x_before * self.zoom - mouse_x) / self.zoom
        self.canvas_offset_y = (world_y_before * self.zoom - mouse_y) / self.zoom

    def handle_key_down(self, event):
        pass
    
    def screen_to_world(self, x, y):
        """Wandelt Bildschirmkoordinaten in Weltkoordinaten um (berücksichtigt Zoom und Offset)."""
        world_x = (x + self.canvas_offset_x * self.zoom) / self.zoom
        world_y = (y + self.canvas_offset_y * self.zoom) / self.zoom
        return world_x, world_y

    def draw(self):
        self.draw_grid()
        self.draw_connections()
        self.draw_nodes()
        self.draw_toolbar()
        self.draw_offscreen_indicators()
        pygame.display.flip()

    def draw_grid(self):
        # Hintergrund
        self.screen.fill(BLUEPRINT_COLOR)

        # Grid (mit Zoom!)
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
        # Verbindungen
        for connection in self.connections:
            connection.draw(self.screen, self.canvas_offset_x, self.canvas_offset_y, zoom=self.zoom)

    def draw_nodes(self):
        # Nodes
        for node in self.nodes:
            node.draw(self.screen, self.canvas_offset_x, self.canvas_offset_y, selected=(node == self.selected_node), zoom=self.zoom)

    def draw_toolbar(self):
        self.toolbar.draw(self.screen)
    
    def draw_offscreen_indicators(self):
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()
        margin = 0
        rect_size = 16

        for node in self.nodes:
            # Welt- zu Bildschirmkoordinaten
            screen_x = (node.x * self.zoom) - self.canvas_offset_x * self.zoom
            screen_y = (node.y * self.zoom) - self.canvas_offset_y * self.zoom

            # Prüfen, ob Node außerhalb des sichtbaren Bereichs liegt
            if (TOOLBAR_WIDTH + margin < screen_x < screen_w - margin and
                margin < screen_y < screen_h - margin):
                continue  # Node ist sichtbar, kein Indikator nötig

            # Richtung zum Node berechnen (vom Mittelpunkt des sichtbaren Bereichs)
            center_x = TOOLBAR_WIDTH + (screen_w - TOOLBAR_WIDTH) // 2
            center_y = screen_h // 2
            dx = screen_x - center_x
            dy = screen_y - center_y

            # Normiere Richtung auf den Rand des Fensters
            if dx == 0 and dy == 0:
                continue  # Sollte nicht passieren

            angle = math.atan2(dy, dx)
            # Bestimme Schnittpunkt mit Fenster-Rand
            # Links/Rechts
            if abs(dx) > abs(dy * (screen_w / screen_h)):
                if dx > 0:
                    edge_x = screen_w - margin
                else:
                    edge_x = TOOLBAR_WIDTH + margin
                edge_y = center_y + (edge_x - center_x) * math.tan(angle)
            # Oben/Unten
            else:
                if dy > 0:
                    edge_y = screen_h - margin
                else:
                    edge_y = margin
                edge_x = center_x + (edge_y - center_y) / math.tan(angle)

            # Draw yellow inidicator rect at edge
            rect_x = int(edge_x - rect_size // 2)
            rect_y = int(edge_y - rect_size // 2)
            pygame.draw.rect(self.screen, (160, 160, 160), (rect_x, rect_y, rect_size, rect_size), width=1, border_radius=3)