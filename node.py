import pygame
from constants import (NODE_WIDTH, NODE_HEIGHT,
                         GRAY, BLUE, YELLOW,
                         RED, WHITE, CONNECTION_RADIUS)

class Node:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.node_name: str = self._id_to_name(self.id)
        self.width = NODE_WIDTH
        self.height = NODE_HEIGHT
        self.dragging = False
        self.drag_offset = (0, 0)
        self.selected: bool = False
        self._cache_surface = None
        self._cache_params = None  # (width, height, selected, zoom, id)

    def get_right_center(self):
        return (self.x + self.width, self.y + self.height / 2)

    def get_left_center(self):
        return (self.x, self.y + self.height / 2)

    def get_center(self):
        return (self.x + self.width / 2, self.y + self.height / 2)

    def get_input_pos(self):
        return (self.x, self.y + self.height // 2)

    def get_output_pos(self):
        return (self.x + self.width, self.y + self.height // 2)

    def contains_point(self, x, y):
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def _id_to_name(self, id_num: int) -> str:
    # Convert 1-based id to spreadsheet-style name similar to Excel column names.
        name = ""
        id_num -= 1  # Perform subtraction once before the loop
        while id_num >= 0:
            n, letter_index = divmod(id_num, 26)
            name = chr(65 + letter_index) + name
            id_num = n - 1
        return name

    def _render_surface(self, width, height, border_radius, selected, zoom):
        node_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        alpha = 225
        # Draw node background
        pygame.draw.rect(
            node_surf,
            (64, 64, 64, alpha),
            (0, 0, width, height),
            border_radius=border_radius
        )
        # Draw node border
        border_color = (0, 255, 0) if selected else GRAY
        pygame.draw.rect(
            node_surf,
            border_color,
            (0, 0, width, height),
            max(1, int(2 * zoom)),
            border_radius=border_radius
        )
        # Draw serial number
        font = pygame.font.Font(None, max(12, int(24 * zoom)))
        text = font.render(str(self.id), True, WHITE)
        text_rect = text.get_rect(center=(width // 2, height*0.6 // 2))
        node_surf.blit(text, text_rect)
        # Draw node name
        if self.node_name is None:
            self.node_name = "--"
        gap = int(self.height * 0.20 * zoom)
        name_font = pygame.font.Font(None, max(16, int(22 * zoom)))
        name_text = name_font.render(self.node_name, True, YELLOW)
        name_rect = name_text.get_rect(center=(width // 2, text_rect.centery + gap + name_text.get_height() // 2))
        node_surf.blit(name_text, name_rect)
        return node_surf

    def draw(self, screen, offset_x=0.0, offset_y=0.0, zoom=1.0):
        x = int((self.x - offset_x) * zoom)
        y = int((self.y - offset_y) * zoom)
        width = int(self.width * zoom)
        height = int(self.height * zoom)
        border_radius = int(16 * zoom)
        cache_params = (width, height, self.selected, zoom, self.id)
        if self._cache_surface is None or self._cache_params != cache_params:
            self._cache_surface = self._render_surface(width, height, border_radius, self.selected, zoom)
            self._cache_params = cache_params
        screen.blit(self._cache_surface, (x, y))

        # Draw connection points (die ändern sich je nach Zoom/Position, daher nicht cachen)
        input_pos = self.get_input_pos()
        output_pos = self.get_output_pos()
        input_screen = (
            int((input_pos[0] - offset_x) * zoom),
            int((input_pos[1] - offset_y) * zoom),
        )
        output_screen = (
            int((output_pos[0] - offset_x) * zoom),
            int((output_pos[1] - offset_y) * zoom),
        )
        conn_radius = max(2, int(CONNECTION_RADIUS * zoom))
        pygame.draw.circle(screen, BLUE, input_screen, conn_radius)
        pygame.draw.circle(screen, RED, output_screen, conn_radius)
