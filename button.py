import pygame

class Button:
    def __init__(self, rect, label, color, action=None):
        self.rect = rect
        self.label = label
        self.color = color
        self.action = action
        self.hovered = False

    def draw(self, screen, font):
        pygame.draw.rect(screen, (180, 180, 180) if self.hovered else self.color, self.rect, border_radius=5)
        text = font.render(self.label, True, (255, 255, 255))
        screen.blit(text, (self.rect.x + 10, self.rect.y + 10))

    def is_clicked(self, x, y):
        return self.rect.collidepoint(x, y)