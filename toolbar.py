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

    def change_bg_color(self, color):
        self.bg_color = color

    def layout_buttons(self):
        max_width = self.min_width
        for i, btn in enumerate(self.buttons):
            text_width, text_height = btn.get_text_size()
            # Calculate the button's width and height based on the text size and padding
            btn_width = text_width + c.TOOLBAR_BUTTON_TEXT_PADDING_HORIZONTAL
            btn_height = text_height + c.TOOLBAR_BUTTON_TEXT_PADDING_VERTICAL
            # Set the button's width and height
            x = self.left_margin
            y = self.top_margin + i * (btn_height + self.padding)
            btn.rect = pygame.Rect(x, y, btn_width, btn_height)
            max_width = max(max_width, btn_width + self.left_margin * 2)
        self.width  = max_width
        self.button_width = max_width - self.left_margin * 2

    def draw(self, screen):
        # Draw the toolbar background
        pygame.draw.rect(screen, self.bg_color, (0, 0, c.TOOLBAR_WIDTH, c.WINDOW_HEIGHT))
        self.layout_buttons()
        for btn in self.buttons:
            btn.draw(screen)

    def get_clicked_button(self, x, y):
        for btn in self.buttons:
            if btn.is_clicked(x, y):
                return btn
        return None
