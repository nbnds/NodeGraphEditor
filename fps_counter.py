import pygame
from constants import WHITE # Import WHITE from constants.py

class FPSCounter:
    def __init__(self, font_size=30, position=(10, 10)):
        pygame.font.init() # Ensure font module is initialized
        self.font = pygame.font.Font(None, font_size) # Use a default system font
        self.position = position
        self.color = WHITE

    def draw(self, screen, clock):
        fps_value = round(clock.get_fps())
        fps_text = f"FPS: {fps_value}"
        fps_surface = self.font.render(fps_text, True, self.color)
        screen.blit(fps_surface, self.position)
