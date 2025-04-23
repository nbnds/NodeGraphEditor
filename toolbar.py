import pygame
from constants import GRAY, DARK_GRAY, WHITE, TOOLBAR_WIDTH, WINDOW_HEIGHT
from button import Button

NODE_TYPES = [
    {"name": "Node", "color": (64, 64, 64)},
    {"name": "Add", "color": (0, 200, 0)},
    {"name": "Subtract", "color": (200, 0, 0)},
]

class ToolbarButton(Button):
    def __init__(self, rect, label, color, action=None, node_type=None):
        super().__init__(rect, label, color, action)
        self.node_type = node_type  # Nur für Knotentyp-Buttons

class Toolbar:
    def __init__(self, node_types=NODE_TYPES):
        self.buttons = []
        self._layout_buttons(node_types)

    def _layout_buttons(self, node_types):
        top_padding = 10
        for node_type in node_types:
            rect = pygame.Rect(10, top_padding, 80, 40)
            btn = ToolbarButton(rect, node_type["name"], node_type["color"], action="add_node", node_type=node_type)
            self.buttons.append(btn)
            top_padding += 50
        # "Alle löschen"-Button
        delete_rect = pygame.Rect(10, WINDOW_HEIGHT - 50, 80, 40)
        delete_btn = ToolbarButton(delete_rect, "Alle löschen", (180, 50, 50), action="delete_all")
        self.buttons.append(delete_btn)

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, (0, 0, TOOLBAR_WIDTH, WINDOW_HEIGHT))
        font = pygame.font.Font(None, 24)
        for btn in self.buttons:
            btn.draw(screen, font)

    def get_clicked_button(self, x, y):
        for btn in self.buttons:
            if btn.is_clicked(x, y):
                return btn
        return None

