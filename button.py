import pygame
from typing import Optional
from actions import Action, NoOpAction

class Button:
    def __init__(self,
                 rect: pygame.Rect | None = None,
                 label: Optional[str] = None,
                 color: Optional[tuple] = None,
                 action: Action | None = None):
        self.rect = rect if isinstance(rect, pygame.Rect)  else pygame.Rect(0, 0, 0, 0)
        self.label = label if label is not None else "<UNNAMED>"
        self.font = pygame.font.Font(None, 24)
        self.color = color if color is not None else (200, 200, 200)
        self.action: Action = action if action is not None else NoOpAction()
        self.hovered = False

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 236, 150) if self.hovered else self.color, self.rect, width=1, border_radius=5)
        text_surface = self.font.render(self.label, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = self.rect.center
        text_rect.centery += 2
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def get_text_size(self):
        """Gibt die Größe des Labels mit der gegebenen Font zurück (Hilfsmethode für Layout)."""
        return self.font.size(self.label)

    def __repr__(self):
        return f"Button(label='{self.label}', rect={self.rect})"
