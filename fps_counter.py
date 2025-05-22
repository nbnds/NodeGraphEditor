import pygame
import collections # Added
from constants import WHITE # Import WHITE from constants.py

class FPSCounter:
    def __init__(self, font_size=30, position='bottom-left', window_size=60): # Modified
        pygame.font.init() # Ensure font module is initialized
        self.font = pygame.font.Font(None, font_size)
        self.font_size = font_size # Added
        self.position_config = position # Renamed to avoid conflict
        self.color = WHITE
        self.fps_values = collections.deque(maxlen=window_size) # Added
        self.min_fps = float('inf') # Added
        self.max_fps = float('-inf') # Added

    def draw(self, screen, clock, screen_height): # Modified
        current_fps = clock.get_fps()
        if current_fps == 0: # Avoid division by zero or skewed stats if FPS is 0
            current_fps = 0.00001 # A very small number to prevent issues, will be rounded

        self.fps_values.append(current_fps)

        if self.fps_values: # Ensure deque is not empty
            self.min_fps = min(self.fps_values)
            self.max_fps = max(self.fps_values)
        else:
            # This case should ideally not be hit if window_size > 0 and we append before this
            self.min_fps = current_fps
            self.max_fps = current_fps
            
        # Prevent displaying inf if fps_values was empty on first few frames or current_fps is 0.
        display_min_fps = round(self.min_fps) if self.min_fps != float('inf') else round(current_fps)
        display_max_fps = round(self.max_fps) if self.max_fps != float('-inf') else round(current_fps)

        # If current_fps was set to a tiny number, round it to 0 for display
        display_current_fps = round(current_fps) if current_fps > 0.0001 else 0


        fps_text = f"FPS: {display_current_fps} (Min: {display_min_fps}, Max: {display_max_fps})"
        fps_surface = self.font.render(fps_text, True, self.color)

        actual_position = (0,0)
        if self.position_config == 'bottom-left':
            actual_x = 10
            # Adjust y by font_size and a small padding to prevent going off-screen
            actual_y = screen_height - self.font_size - 5 
            actual_position = (actual_x, actual_y)
        elif isinstance(self.position_config, tuple):
            actual_position = self.position_config
        else: # Default to top-left if unknown config
            actual_position = (10,10) # Default to top-left

        screen.blit(fps_surface, actual_position)
