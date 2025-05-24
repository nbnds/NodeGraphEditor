import pygame
from uicomponent import UIComponent
from button_component import ButtonComponent
from editor_context import EditorContext
import constants as c # Assuming constants.py exists and has TOOLBAR_WIDTH etc.

class ToolbarComponent(UIComponent):
    """
    A UI component representing a toolbar that holds buttons.
    """

    def __init__(self, context: EditorContext):
        """
        Initializes the ToolbarComponent.
        Args:
            context: The editor context.
        """
        self.context = context
        self.buttons: list[ButtonComponent] = []
        
        # Default attributes, can be customized or loaded from config
        self.bg_color = (50, 50, 50) # Dark grey
        self.padding = 5  # Padding around buttons and edges of toolbar
        self.button_spacing = 5 # Spacing between buttons
        self.left_margin = self.padding
        self.top_margin = self.padding
        
        # Toolbar width will be determined by the screen width from context or a fixed value
        # For now, let's assume it spans the width of the screen or a portion of it.
        # The height will be determined by the tallest button + padding.
        self.min_width = c.TOOLBAR_WIDTH if hasattr(c, 'TOOLBAR_WIDTH') else 200 # Default or from constants
        self.width = self.min_width
        self.height = 0 # Will be calculated in _layout_buttons
        
        # The toolbar's own rect will be defined by its position and calculated width/height
        # Position can be fixed (e.g., top of the screen)
        self.rect = pygame.Rect(0, 0, self.width, 50) # Initial placeholder height

    def add_button(self, button_component: ButtonComponent):
        """
        Adds a button to the toolbar and recalculates layout.
        """
        self.buttons.append(button_component)
        self._layout_buttons()

    def _layout_buttons(self):
        """
        Arranges buttons horizontally within the toolbar.
        Calculates the necessary height of the toolbar.
        """
        current_x = self.left_margin
        max_button_height = 0

        for button in self.buttons:
            # Set button position
            button.rect.topleft = (current_x, self.top_margin + self.rect.top) # Position relative to toolbar's top
            
            # Update current_x for the next button
            current_x += button.rect.width + self.button_spacing
            
            # Track maximum button height to determine toolbar height
            if button.rect.height > max_button_height:
                max_button_height = button.rect.height
        
        # Update toolbar dimensions
        # Width could be fixed or expand to fit buttons up to screen width
        # For now, assume a fixed width or width of the screen from context
        screen_width = self.context.config.get('screen_width', 800) # Default if not in context
        self.width = screen_width # Span full width
        self.rect.width = self.width
        
        self.height = max_button_height + (2 * self.padding)
        self.rect.height = self.height

        # Ensure buttons are within the new height if toolbar height changed
        for button in self.buttons:
             button.rect.centery = self.rect.centery


    def handle_event(self, event, context: EditorContext):
        """
        Passes events to each button in the toolbar.
        """
        # Check if the event is within the toolbar's bounds first (optional optimization)
        # if not self.rect.collidepoint(pygame.mouse.get_pos()):
        # if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
        # if not self.rect.collidepoint(event.pos if hasattr(event, 'pos') else (-1,-1)):
        # return # Only process if mouse is over the toolbar (for mouse events)


        for button in self.buttons:
            button.handle_event(event, context)

    def update(self, dt, context: EditorContext):
        """
        Updates all buttons in the toolbar. (Currently buttons don't have time-based updates)
        """
        for button in self.buttons:
            button.update(dt, context)
        # Recalculate layout if screen size changed
        if self.width != self.context.config.get('screen_width', self.width) :
             self._layout_buttons()


    def draw(self, screen, context: EditorContext):
        """
        Draws the toolbar background and all its buttons.
        """
        # Draw toolbar background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, (30,30,30), self.rect, 1) # Border for the toolbar itself


        # Draw buttons
        for button in self.buttons:
            button.draw(screen, context)

    # UIComponent methods (if needed for direct manipulation, though layout handles it)
    def set_position(self, x: int, y: int):
        """Sets the top-left position of the toolbar."""
        self.rect.topleft = (x, y)
        self._layout_buttons() # Re-layout buttons relative to new toolbar position

    def set_size(self, width: int, height: int):
        """Sets the size of the toolbar (primarily width, height is often auto-calculated)."""
        self.rect.width = width
        # self.rect.height = height # Usually height is dynamic
        self._layout_buttons() # Re-layout buttons within new size
```
