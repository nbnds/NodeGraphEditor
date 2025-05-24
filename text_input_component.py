import pygame
from uicomponent import UIComponent
from editor_context import EditorContext # For type hinting
from textinput import TextInputRenderer, TextInputEngine # From existing textinput.py

class TextInputComponent(UIComponent):
    """
    A UI component for text input, using TextInputRenderer and TextInputEngine.
    """

    def __init__(self, context: EditorContext, initial_text: str = "", 
                 pos: tuple[int, int] = (100, 100), 
                 font_color: tuple[int, int, int] = (255, 255, 255), 
                 cursor_color: tuple[int, int, int] = (255, 255, 255),
                 overlay_color: tuple[int,int,int,int] = (0,0,0,128) ): # Added overlay color
        """
        Initializes the TextInputComponent.
        Args:
            context: The editor context.
            initial_text: The initial text for the input field.
            pos: The (x, y) position for the text input field if drawn independently.
                 Note: render_with_overlay centers it, so pos might be for reference.
            font_color: Color of the text.
            cursor_color: Color of the cursor.
            overlay_color: Color of the screen overlay when active.
        """
        self.context = context
        self.active = False  # Controls if the component is actively processing input
        
        self.engine = TextInputEngine(initial=initial_text)
        self.text_input_visualizer = TextInputRenderer(
            engine=self.engine,
            font_color=font_color,
            cursor_color=cursor_color,
            overlay_enabled=False, # Overlay managed by this component's active state
            overlay_color=overlay_color
        )
        
        self.pos = pos # Position if not using full-screen overlay
        self.on_submit_callback = None # Callback for when text is submitted

    def activate(self, initial_text: str = None, on_submit: callable = None):
        """Activates the text input field."""
        self.active = True
        self.text_input_visualizer.overlay_enabled = True
        if initial_text is not None:
            self.engine.value = initial_text
        self.engine.cursor_pos = len(self.engine.value) # Move cursor to end
        self.on_submit_callback = on_submit
        print("TextInputComponent activated.")

    def deactivate(self, submit: bool = False):
        """Deactivates the text input field."""
        if self.active and submit and self.on_submit_callback:
            self.on_submit_callback(self.engine.value)
        
        self.active = False
        self.text_input_visualizer.overlay_enabled = False
        self.on_submit_callback = None # Clear callback
        print(f"TextInputComponent deactivated. Submitted: {submit}")


    def handle_event(self, event, context: EditorContext):
        """
        Handles events if the component is active.
        """
        if not self.active:
            return

        # Let TextInputEngine process the event first if it's a KEYDOWN
        # The TextInputEngine.update() method expects a list of events.
        # We are calling this for each event, so we wrap it.
        if event.type == pygame.KEYDOWN:
            self.engine.update([event]) # engine.update modifies text based on key presses
            
            if event.key == pygame.K_RETURN:
                self.deactivate(submit=True)
            elif event.key == pygame.K_ESCAPE:
                self.clear_text() # Clear text on escape
                self.deactivate(submit=False)
        # Other event types like TEXTINPUT are handled by engine.update if needed by its design.
        # Based on textinput.py, TextInputEngine._process_other uses event.unicode,
        # which is typically part of KEYDOWN events for printable chars, not TEXTINPUT.
        # So, only passing KEYDOWN to engine.update seems correct for that implementation.

    def update(self, dt: float, context: EditorContext):
        """
        Updates the text input visualizer (e.g., for cursor blinking).
        """
        if self.active:
            # The visualizer's update method takes a list of events,
            # but for blinking, it only needs to be called.
            # It uses its internal clock for blink timing.
            self.text_input_visualizer.update([]) 

    def draw(self, screen: pygame.Surface, context: EditorContext):
        """
        Draws the text input field using the visualizer's overlay method if active.
        """
        if self.active:
            # render_with_overlay takes events, but for drawing only, an empty list is fine.
            # It draws its own overlay and then the text input centered.
            self.text_input_visualizer.render_with_overlay(screen, []) 

    def get_text(self) -> str:
        """Returns the current text in the input field."""
        return self.engine.value

    def set_text(self, text: str):
        """Sets the current text in the input field."""
        self.engine.value = text
        self.engine.cursor_pos = len(text)


    def clear_text(self):
        """Clears the text in the input field."""
        self.engine.value = ""
        self.engine.cursor_pos = 0
        
    def set_position(self, x: int, y: int): # Required by UIComponent
        """Sets the position of the component (for non-overlay drawing)."""
        self.pos = (x, y) # Used if drawing method changes from full overlay
        # For render_with_overlay, position is typically centered by the renderer itself.
```
