import pytest
import pygame # Required for conftest.py pygame_init fixture
from app import App
from editor_context import EditorContext
from component_registry import ComponentRegistry
from node_area_component import NodeAreaComponent
from toolbar_component import ToolbarComponent
from fps_counter_component import FPSCounterComponent
from text_input_component import TextInputComponent

# conftest.py should provide pygame_init fixture

@pytest.fixture
def test_app(pygame_init): # Use pygame_init fixture
    """Fixture to create an App instance for testing."""
    return App()

def test_app_initialization_registers_default_components(test_app):
    """Test that App initializes and registers default components."""
    
    assert isinstance(test_app.context, EditorContext), "App should have an EditorContext."
    assert isinstance(test_app.registry, ComponentRegistry), "App should have a ComponentRegistry."
    
    # Check that the context has references set up by App
    assert test_app.context.screen is not None, "Context should have a screen reference."
    assert test_app.context.component_registry == test_app.registry, "Context should reference the app's registry."
    assert test_app.context.undo_stack is not None, "Context should have an UndoStack."
    assert test_app.context.nx_graph is not None, "Context should have an nx_graph."
    assert test_app.context.clock == test_app.clock, "Context should reference the app's clock."
    assert 'screen_width' in test_app.context.config
    assert 'screen_height' in test_app.context.config
    
    # Check for registered components by type
    registered_component_types = [type(comp) for comp in test_app.registry._components]
    
    assert NodeAreaComponent in registered_component_types, "NodeAreaComponent should be registered."
    assert ToolbarComponent in registered_component_types, "ToolbarComponent should be registered."
    assert FPSCounterComponent in registered_component_types, "FPSCounterComponent should be registered."
    assert TextInputComponent in registered_component_types, "TextInputComponent should be registered."
    
    # Verify specific instances if needed (though type checking is often sufficient for registration)
    # Example: check that the toolbar instance in App is the one in the registry
    toolbar_instance_in_app = test_app.toolbar_component # Assuming App stores it like this
    assert toolbar_instance_in_app in test_app.registry._components
    
    node_area_instance_in_app = test_app.node_area_component # Assuming App stores it
    assert node_area_instance_in_app in test_app.registry._components

    fps_counter_instance_in_app = test_app.fps_counter_component
    assert fps_counter_instance_in_app in test_app.registry._components

    text_input_instance_in_app = test_app.text_input_component
    assert text_input_instance_in_app in test_app.registry._components

    # Check that the toolbar has buttons (indirectly tests App's button setup)
    toolbar_comp = next(c for c in test_app.registry._components if isinstance(c, ToolbarComponent))
    assert len(toolbar_comp.buttons) > 0, "ToolbarComponent should have buttons added by App."

# More tests could be added for App.run() loop, but that would require
# more complex event simulation and mocking of Pygame's loop,
# which is beyond typical unit testing for initialization.
# Integration tests would be better for run() loop behavior.
```
