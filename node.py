import pygame
from constants import (NODE_WIDTH, NODE_HEIGHT,
                         DARK_GRAY, GRAY, BLUE, 
                         RED, WHITE, CONNECTION_RADIUS)

class Node:
    def __init__(self, x, y, serial):
        self.x = x
        self.y = y
        self.serial = serial
        self.width = NODE_WIDTH
        self.height = NODE_HEIGHT
        self.dragging = False
        self.drag_offset = (0, 0)

    def get_input_pos(self):
        return (self.x, self.y + self.height // 2)

    def get_output_pos(self):
        return (self.x + self.width, self.y + self.height // 2)

    def contains_point(self, x, y):
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def draw(self, screen, offset_x=0, offset_y=0, selected=False, zoom=1.0):
        x = int((self.x - offset_x) * zoom)
        y = int((self.y - offset_y) * zoom)
        width = int(self.width * zoom)
        height = int(self.height * zoom)
        pygame.draw.rect(
            screen,
            DARK_GRAY,
            (x, y, width, height),
            border_radius=int(16 * zoom)
        )
        border_color = (0, 255, 0) if selected else GRAY
        pygame.draw.rect(
            screen,
            border_color,
            (x, y, width, height),
            max(1, int(2 * zoom)),
            border_radius=int(16 * zoom)
        )
        # Connection points
        pygame.draw.circle(screen, BLUE, (int((self.get_input_pos()[0] - offset_x) * zoom), int((self.get_input_pos()[1] - offset_y) * zoom)), max(2, int(CONNECTION_RADIUS * zoom)))
        pygame.draw.circle(screen, RED, (int((self.get_output_pos()[0] - offset_x) * zoom), int((self.get_output_pos()[1] - offset_y) * zoom)), max(2, int(CONNECTION_RADIUS * zoom)))
        # Serial number
        font = pygame.font.Font(None, max(12, int(24 * zoom)))
        text = font.render(str(self.serial), True, WHITE)
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(text, text_rect)