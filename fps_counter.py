import pygame
import collections
from constants import WHITE # Import WHITE from constants.py

class FPSCounter:
    def __init__(self, font_size=30, position='bottom-left', window_size=60, update_interval=0.5):
        pygame.font.init() # Ensure font module is initialized
        self.font = pygame.font.Font(None, font_size)
        self.font_size = font_size
        self.position_config = position
        self.color = WHITE
        
        self.fps_values = collections.deque(maxlen=window_size)
        self.min_fps = float('inf')
        self.max_fps = float('-inf')
        
        self.update_interval = update_interval  # seconds
        self.last_update_time = 0 # milliseconds
        self.fps_surface = None # Cache for the text surface

    def draw(self, screen, dt_ms, screen_height): # dt_ms is delta time in milliseconds
        if dt_ms > 0:
            current_potential_fps = 1000.0 / dt_ms
        else:
            # Avoid division by zero or if dt_ms is 0 (e.g. first frame or paused)
            # We can show 0 or a very high number if it's truly paused.
            # For now, let's assume if dt_ms is 0, potential fps is also 0 for this sample.
            current_potential_fps = 0 

        self.fps_values.append(current_potential_fps)

        # Update min/max based on the current window of values
        if self.fps_values:
            self.min_fps = min(self.fps_values)
            self.max_fps = max(self.fps_values)
        else: 
            # This case would only be hit if window_size is 0
            self.min_fps = current_potential_fps
            self.max_fps = current_potential_fps
            
        current_time = pygame.time.get_ticks() # current time in milliseconds
        
        # Update the FPS text surface only at the specified interval or if it's not yet created
        if (current_time - self.last_update_time) >= (self.update_interval * 1000) or self.fps_surface is None:
            # Handle cases where min_fps/max_fps might still be inf/-inf if fps_values was empty
            display_min = round(self.min_fps) if self.min_fps != float('inf') else round(current_potential_fps)
            display_max = round(self.max_fps) if self.max_fps != float('-inf') else round(current_potential_fps)
            
            # For "current" FPS, using the latest potential FPS value.
            # Could also average self.fps_values for a smoother "current" display if desired.
            display_current = round(current_potential_fps) 

            fps_text = f"FPS: {display_current} (Min: {display_min}, Max: {display_max})"
            self.fps_surface = self.font.render(fps_text, True, self.color)
            self.last_update_time = current_time

        if self.fps_surface:
            actual_position = (0,0) # Default
            if self.position_config == 'bottom-left':
                actual_x = 10
                actual_y = screen_height - self.font_size - 5 # 5px padding from bottom
                actual_position = (actual_x, actual_y)
            elif isinstance(self.position_config, tuple):
                actual_position = self.position_config
            else: # Default to top-left if unknown config or other string
                actual_position = (10,10)
            screen.blit(self.fps_surface, actual_position)
