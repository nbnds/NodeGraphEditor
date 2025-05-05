import pygame
from constants import (NODE_WIDTH, NODE_HEIGHT,
                         GRAY, BLUE,
                         RED, WHITE, CONNECTION_RADIUS)

class Node:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.width = NODE_WIDTH
        self.height = NODE_HEIGHT
        self.dragging = False
        self.drag_offset = (0, 0)
        self.selected: bool = False

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

    def draw(self, screen, offset_x=0, offset_y=0, zoom=1.0):
        x = int((self.x - offset_x) * zoom)
        y = int((self.y - offset_y) * zoom)
        width = int(self.width * zoom)
        height = int(self.height * zoom)
        border_radius = int(16 * zoom)
        border_color = (0, 255, 0) if self.selected else GRAY
            # --- Create a temporary surface for transparency ---
        node_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        alpha = 225  # 0=fully transparent, 255=opaque
        # Draw node background
        pygame.draw.rect(
            node_surf,
            (64, 64, 64, alpha),
            (0, 0, width, height),
            border_radius=border_radius
        )
        screen.blit(node_surf, (x, y))
        # Draw node border
        pygame.draw.rect(
            screen,
            border_color,
            (x, y, width, height),
            max(1, int(2 * zoom)),
            border_radius=int(16 * zoom)
        )

        # Draw connection points
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

        # Draw serial number
        font = pygame.font.Font(None, max(12, int(24 * zoom)))
        text = font.render(str(self.id), True, WHITE)
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(text, text_rect)
