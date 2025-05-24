import pygame
from uicomponent import UIComponent
from actions import Action # Assuming Action is in actions.py
from editor_context import EditorContext # For type hinting context in execute

class ButtonComponent(UIComponent):
    """
    A UI component representing a clickable button.
    """

    def __init__(self, context: EditorContext, action: Action, label: str,
                 rect: pygame.Rect = None, color: tuple = None,
                 font_color: tuple = (0,0,0), hover_color: tuple = (170,170,170)):
        """
        Initializes the ButtonComponent.
        Args:
            context: The editor context.
            action: The Action object to execute when clicked.
            label: The text label for the button.
            rect: The pygame.Rect defining the button's position and size.
                  Defaults to (0,0,100,30).
            color: The base color of the button. Defaults to (200,200,200).
            font_color: The color of the button's label text. Defaults to (0,0,0).
            hover_color: The color of the button when hovered. Defaults to (170,170,170).
        """
        self.context = context
        self.action = action
        self.label = label
        self.rect = rect if rect else pygame.Rect(0, 0, 100, 30)
        self.font = pygame.font.Font(None, 24) # Default font and size
        self.base_color = color if color else (200, 200, 200)
        self.font_color = font_color
        self.hover_color = hover_color
        self.hovered = False

    def handle_event(self, event, context: EditorContext):
        """
        Handles mouse events for the button.
        Executes the button's action if clicked.
        Updates hover state on mouse motion.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                if self.action:
                    self.action.execute(context) # Pass context to action
        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

    def update(self, dt, context: EditorContext):
        """
        Updates the button state (currently none).
        """
        pass # No time-based updates needed for a simple button

    def draw(self, screen, context: EditorContext):
        """
        Draws the button on the given screen.
        Appearance changes if the button is hovered.
        """
        current_color = self.hover_color if self.hovered else self.base_color
        pygame.draw.rect(screen, current_color, self.rect)
        pygame.draw.rect(screen, (0,0,0), self.rect, 1) # Border

        if self.label:
            text_surface = self.font.render(self.label, True, self.font_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def get_text_size(self) -> tuple[int, int]:
        """
        Calculates the size of the button's label text.
        Returns:
            A tuple (width, height) of the text.
        """
        if not self.label:
            return (0,0)
        return self.font.size(self.label)

    # Required by UIComponent, but not strictly needed if position is managed by ToolbarComponent
    def set_position(self, x: int, y: int):
        """Sets the top-left position of the button."""
        self.rect.topleft = (x, y)

    def set_size(self, width: int, height: int):
        """Sets the size of the button."""
        self.rect.size = (width, height)
