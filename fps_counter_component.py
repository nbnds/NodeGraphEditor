import pygame
from uicomponent import UIComponent
from editor_context import EditorContext # For type hinting

class FPSCounterComponent(UIComponent):
    """
    A UI component that displays the current FPS.
    """

    def __init__(self, context: EditorContext, pos: tuple[int, int] = (10, 10), 
                 font_size: int = 24, color: tuple[int, int, int] = (255, 255, 255)):
        """
        Initializes the FPSCounterComponent.
        Args:
            context: The editor context.
            pos: The (x, y) position for the FPS display.
            font_size: The font size for the FPS text.
            color: The color of the FPS text.
        """
        self.context = context
        self.pos = pos
        self.font = pygame.font.Font(None, font_size) # Use default system font
        self.color = color
        self.fps_text = ""

    def handle_event(self, event, context: EditorContext):
        """
        This component does not handle any direct events.
        """
        pass

    def update(self, dt: float, context: EditorContext):
        """
        Updates the FPS text based on the clock from the context.
        Args:
            dt: Delta time.
            context: The editor context, expected to have a 'clock' attribute.
        """
        if hasattr(context, 'clock') and context.clock is not None:
            fps = context.clock.get_fps()
            self.fps_text = f"FPS: {fps:.2f}"
        else:
            self.fps_text = "FPS: N/A (clock not in context)"

    def draw(self, screen: pygame.Surface, context: EditorContext):
        """
        Draws the FPS text onto the given screen.
        Args:
            screen: The Pygame surface to draw on.
            context: The editor context.
        """
        if self.fps_text:
            text_surface = self.font.render(self.fps_text, True, self.color)
            screen.blit(text_surface, self.pos)

    # Optional: If position needs to be changed after initialization
    def set_position(self, x: int, y: int):
        """Sets the position of the FPS display."""
        self.pos = (x, y)
