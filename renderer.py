import pygame
import math
from constants import (BLUEPRINT_COLOR, BLUEPRINT_LINE_COLOR, TOOLBAR_WIDTH,
                        BLUEPRINT_GRID_SIZE)

class GridRenderer:
    def draw(self, screen, canvas_offset_x, canvas_offset_y, zoom):
        # Background
        screen.fill(BLUEPRINT_COLOR)

        # Grid with zoom
        grid_size = BLUEPRINT_GRID_SIZE * zoom
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        x_start = TOOLBAR_WIDTH - (canvas_offset_x % BLUEPRINT_GRID_SIZE) * zoom
        y_start = - (canvas_offset_y % BLUEPRINT_GRID_SIZE) * zoom

        x = x_start
        while x < screen_w:
            pygame.draw.line(screen, BLUEPRINT_LINE_COLOR, (x, 0), (x, screen_h))
            x += grid_size
        y = y_start
        while y < screen_h:
            pygame.draw.line(screen, BLUEPRINT_LINE_COLOR, (TOOLBAR_WIDTH, y), (screen_w, y))
            y += grid_size

class NodeEditorRenderer:
    def __init__(self, editor):
        self.editor = editor
        self.grid_renderer = GridRenderer()

    def draw(self, events):
        self.grid_renderer.draw(
            self.editor.screen,
            self.editor.canvas_offset_x,
            self.editor.canvas_offset_y,
            self.editor.zoom
        )
        self.draw_connections()
        self.draw_nodes()
        self.draw_toolbar()
        self.draw_offscreen_indicators()
        self.draw_text(events)
        self.editor.fps_counter.draw(self.editor.screen)
        pygame.display.flip()

    def draw_connections(self):
        # Connections
        for connection in self.editor.connections:
            connection.draw(self.editor.screen,
                            self.editor.canvas_offset_x,
                            self.editor.canvas_offset_y,
                            zoom=self.editor.zoom)

    def draw_nodes(self):
        # Nodes
        for node in self.editor.nodes:
            node.draw(self.editor.screen,
                      self.editor.canvas_offset_x,
                      self.editor.canvas_offset_y,
                      zoom=self.editor.zoom)

    def draw_toolbar(self):
        self.editor.toolbar.draw(self.editor.screen)

    def draw_offscreen_indicators(self):
        screen_w = self.editor.screen.get_width()
        screen_h = self.editor.screen.get_height()
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
                (node.x * self.editor.zoom) - self.editor.canvas_offset_x * self.editor.zoom,
                (node.y * self.editor.zoom) - self.editor.canvas_offset_y * self.editor.zoom,
            )

        center_x = TOOLBAR_WIDTH + (screen_w - TOOLBAR_WIDTH) // 2
        center_y = screen_h // 2

        for node in self.editor.nodes:
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
                self.editor.screen,
                color,
                rect,
                width=1,
                border_radius=3
                )

    def draw_text(self, events):
        if self.editor.text_input_active:
            self.editor.visualizer.overlay_enabled = True
            self.editor.visualizer.render_with_overlay(self.editor.screen, events)
            if self.editor.visualizer.should_block_mouse():
                pass
        else:
            self.editor.visualizer.overlay_enabled = False
            # Optional: falls du das Textfeld auch ohne Overlay anzeigen willst
            # self.visualizer.update(events)
            # self.screen.blit(self.visualizer.surface, (200, 200))
