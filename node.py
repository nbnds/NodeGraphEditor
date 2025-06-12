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
        # Draw node id at fixed distance from bottom
        id_font = pygame.font.Font(None, max(12, int(14 * zoom)))
        id_text = id_font.render(str(self.id), True, WHITE)
        id_margin_bottom = int(8 * zoom)
        id_y = height - id_margin_bottom - id_text.get_height() // 2
        id_rect = id_text.get_rect(center=(width // 2, id_y))
        node_surf.blit(id_text, id_rect)

        # Calculate area for node name (from top to just above the id)
        name_area_top = 0
        name_area_bottom = id_rect.top - int(4 * zoom)
        name_area_height = name_area_bottom - name_area_top

        # Prepare node name lines (up to 3)
        if self.node_name is None:
            self.node_name = "--"
        name_font = pygame.font.Font(None, max(16, int(22 * zoom)))
        max_text_width = int(width * 0.9)
        name_lines = self._wrap_text(self.node_name, name_font, max_text_width, max_lines=3)
        total_name_height = len(name_lines) * name_font.get_height()
        # Center name lines vertically in the name area
        start_y = name_area_top + (name_area_height - total_name_height) // 2
        for i, line in enumerate(name_lines):
            name_text = name_font.render(line, True, YELLOW)
            name_rect = name_text.get_rect(center=(width // 2,
                                                   start_y + name_text.get_height() // 2 + i * name_text.get_height()))
            node_surf.blit(name_text, name_rect)
        return node_surf

    def _wrap_text(self, text, font, max_width, max_lines=2):
        # Try to break text into up to max_lines lines, breaking on spaces if possible
        words = text.split(' ')
        lines = []
        while words and len(lines) < max_lines:
            for i in range(len(words), 0, -1):
                candidate = ' '.join(words[:i])
                if font.size(candidate)[0] <= max_width:
                    lines.append(candidate)
                    words = words[i:]
                    break
            else:
                # If no fit, hard break
                for i in range(len(words[0]), 0, -1):
                    if font.size(words[0][:i])[0] <= max_width:
                        lines.append(words[0][:i])
                        words[0] = words[0][i:]
                        break
                else:
                    lines.append(words.pop(0))
        if words and len(lines) == max_lines:
            # Add ellipsis to last line if text remains
            if lines:
                lines[-1] = lines[-1].rstrip() + '…'
        return lines

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

    def invalidate_cache(self):
        self._cache_surface = None
        self._cache_params = None
