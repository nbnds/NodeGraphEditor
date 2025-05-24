import pygame
import networkx as nx
import networkx as nx
from component_registry import ComponentRegistry
from editor_context import EditorContext
# from editor import NodeEditor # Old, to be removed or fully refactored
# from toolbar import Toolbar # Old, replaced by ToolbarComponent
# from button import Button # Old, replaced by ButtonComponent
from actions import AddNodeAction, DeleteAllAction, DumpGraphAction, UndoAction # Import specific actions
from undo import UndoStack
from node_area_component import NodeAreaComponent
from toolbar_component import ToolbarComponent
from button_component import ButtonComponent
from fps_counter_component import FPSCounterComponent # New import
from text_input_component import TextInputComponent # New import

class App:
    """
    Main application class for the node editor.
    Manages the Pygame loop, event handling, and component updates.
    """

    def __init__(self):
        """
        Initializes the application, Pygame, and core components.
        """
        pygame.init()

        # Screen setup (similar to NodeEditor)
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Node Editor")

        self.clock = pygame.time.Clock()
        self.context = EditorContext()
        self.registry = ComponentRegistry()

        # Populate context with references
        self.context.screen = self.screen # Pygame screen surface
        self.context.component_registry = self.registry
        self.context.undo_stack = UndoStack() 
        self.context.nx_graph = nx.DiGraph() 
        self.context.clock = self.clock # Add clock to context for FPSCounterComponent
        self.context.config = {
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
        }

        # Create and register core components
        self.node_area_component = NodeAreaComponent(self.context)
        self.registry.register(self.node_area_component)

        self.toolbar_component = ToolbarComponent(self.context)
        self.registry.register(self.toolbar_component)

        # Add buttons to toolbar
        self.toolbar_component.add_button(ButtonComponent(self.context, AddNodeAction(), "Add Node"))
        self.toolbar_component.add_button(ButtonComponent(self.context, DeleteAllAction(), "Clear All"))
        self.toolbar_component.add_button(ButtonComponent(self.context, UndoAction(), "Undo"))
        self.toolbar_component.add_button(ButtonComponent(self.context, DumpGraphAction(), "Dump Graph"))

        # Create and register FPSCounterComponent
        self.fps_counter_component = FPSCounterComponent(self.context, pos=(10, self.screen_height - 30))
        self.registry.register(self.fps_counter_component)
        
        # Create and register TextInputComponent
        self.text_input_component = TextInputComponent(self.context)
        self.registry.register(self.text_input_component)
        # Example: self.context.text_input = self.text_input_component # If other components need to activate it

    def run(self):
        """
        Starts and runs the main application loop.
        """
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds

            all_events = pygame.event.get()
            
            # Global event handling (e.g., for quitting or activating text input)
            for event in all_events:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.VIDEORESIZE:
                    self.screen_width = event.w
                    self.screen_height = event.h
                    self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
                    self.context.screen = self.screen
                    self.context.config['screen_width'] = self.screen_width
                    self.context.config['screen_height'] = self.screen_height
                    # Update FPS counter position on resize
                    self.fps_counter_component.set_position(10, self.screen_height - 30) 
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        if self.text_input_component.active:
                            # If active and TAB is pressed again, could cycle fields or deactivate
                            # For now, let's make TAB only activate if not active.
                            # Deactivation is by Enter/Escape in TextInputComponent.
                            pass 
                        else:
                            # Example: Activate with some default text or for a specific purpose
                            self.text_input_component.activate(initial_text="Enter text...", 
                                                               on_submit=lambda text: print(f"Submitted: {text}"))
                    # If text input is active, it will handle Enter/Escape internally.
                    # If not active, other components might use these keys.

            # Pass all events to the component registry
            # TextInputComponent will only process events if self.text_input_component.active is True
            self.registry.handle_events(all_events, self.context)
            self.registry.update_components(dt, self.context)

            self.screen.fill((30, 30, 30))  # Clear screen
            self.registry.draw_components(self.screen, self.context)

            pygame.display.flip()

        pygame.quit()

if __name__ == '__main__':
    # This part is usually in main.py, but for testing app.py directly.
    # Ensure this test setup doesn't conflict with main.py's setup if main.py also runs App.
    app_instance = App()
    app_instance.run()
