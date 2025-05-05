import pygame
import constants as c


class Toolbar:
    def __init__(self):
        self.bg_color = c.TOOLBAR_BG_COLOR
        self.buttons = []
        self.padding = 10
        self.left_margin = c.TOOLBAR_BUTTON_LEFT_MARGIN
        self.top_margin = c.TOOLBAR_BUTTON_TOP_MARGIN
        self.min_width = c.TOOLBAR_WIDTH
        self.width = self.min_width

    def add_button(self, button):
        self.buttons.append(button)
        self._layout_buttons()
        return self.buttons[-1].rect.centerx, self.buttons[-1].rect.centery

    def change_toolbar_bg_color(self, color):
        self.bg_color = color

    def _layout_buttons(self):
        # First, find the maximum text width
        max_text_width = 0
        btn_height = 0
        for btn in self.buttons:
            text_width, text_height = btn.get_text_size()
            max_text_width = max(max_text_width, text_width)
            btn_height = max(btn_height, text_height + c.TOOLBAR_BUTTON_TEXT_PADDING_VERTICAL)
        # Calculate the button width based on the widest text and padding
        btn_width = max_text_width + c.TOOLBAR_BUTTON_TEXT_PADDING_HORIZONTAL
        max_width = max(self.min_width, btn_width + self.left_margin * 2)
        # Set all button rects to the same width
        for i, btn in enumerate(self.buttons):
            x = self.left_margin
            y = self.top_margin + i * (btn_height + self.padding)
            btn.rect = pygame.Rect(x, y, btn_width, btn_height)
        self.width = max_width
        self.button_width = btn_width

    def draw(self, screen):
        # Draw the toolbar background
        height = screen.get_height()
        pygame.draw.rect(
            screen,
            self.bg_color,
            (0, 0, self.width, height))

        for btn in self.buttons:
            btn.draw(screen)

    def get_clicked_button(self, pos):
        for btn in self.buttons:
            if btn.is_clicked(pos):
                return btn
        return None
