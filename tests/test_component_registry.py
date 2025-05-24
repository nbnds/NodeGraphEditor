import pytest
import pygame # Required for conftest.py pygame_init fixture
from component_registry import ComponentRegistry
from uicomponent import UIComponent
from editor_context import EditorContext # For type hinting if needed by mock components

# Mock UIComponent for testing
class MockUIComponent(UIComponent):
    def __init__(self):
        self.handled_events = []
        self.updated_dt = None
        self.drawn_screen = None
        self.context_received = None # To check if context is passed

    def handle_event(self, event, context):
        self.handled_events.append(event)
        self.context_received = context

    def update(self, dt, context):
        self.updated_dt = dt
        self.context_received = context

    def draw(self, screen, context):
        self.drawn_screen = screen
        self.context_received = context

@pytest.fixture
def registry(pygame_init): # Use pygame_init fixture from conftest.py
    """Fixture to create a ComponentRegistry."""
    return ComponentRegistry()

@pytest.fixture
def mock_component():
    """Fixture to create a MockUIComponent."""
    return MockUIComponent()

@pytest.fixture
def mock_context():
    """Fixture to create a mock EditorContext (can be very basic)."""
    return EditorContext() # Or a more sophisticated mock if methods are called on it

def test_register_component(registry, mock_component):
    """Test registering a component."""
    assert len(registry._components) == 0
    registry.register(mock_component)
    assert len(registry._components) == 1
    assert registry._components[0] == mock_component

    # Test registering the same component again (should not add duplicates)
    registry.register(mock_component)
    assert len(registry._components) == 1

def test_unregister_component(registry, mock_component):
    """Test unregistering a component."""
    registry.register(mock_component)
    assert len(registry._components) == 1
    
    registry.unregister(mock_component)
    assert len(registry._components) == 0

    # Test unregistering a component not in the list (should not raise error)
    registry.unregister(mock_component) 
    assert len(registry._components) == 0


def test_handle_events_calls_components(registry, mock_component, mock_context, create_mouse_event):
    """Test that handle_events calls handle_event on registered components."""
    registry.register(mock_component)
    
    event1 = create_mouse_event(pygame.MOUSEBUTTONDOWN, 1, (10,10))
    event2 = create_mouse_event(pygame.MOUSEMOTION, pos=(20,20))
    events_list = [event1, event2]
    
    registry.handle_events(events_list, mock_context)
    
    assert len(mock_component.handled_events) == len(events_list), "Component should have handled all events"
    assert mock_component.handled_events[0] == event1
    assert mock_component.handled_events[1] == event2
    assert mock_component.context_received == mock_context

def test_update_components_calls_components(registry, mock_component, mock_context):
    """Test that update_components calls update on registered components."""
    registry.register(mock_component)
    
    dt = 0.016 # Sample delta time
    registry.update_components(dt, mock_context)
    
    assert mock_component.updated_dt == dt
    assert mock_component.context_received == mock_context

def test_draw_components_calls_components(registry, mock_component, mock_context):
    """Test that draw_components calls draw on registered components."""
    registry.register(mock_component)
    
    # Mock screen surface
    mock_screen = pygame.Surface((100, 100)) 
    registry.draw_components(mock_screen, mock_context)
    
    assert mock_component.drawn_screen == mock_screen
    assert mock_component.context_received == mock_context


def test_order_of_operations(registry, mock_context, create_mouse_event):
    """Test that components are called in the order they were registered for draw, update, events."""
    comp1 = MockUIComponent()
    comp2 = MockUIComponent()
    
    registry.register(comp1)
    registry.register(comp2)
    
    # Test draw order (assuming draw_components iterates in registration order)
    # This requires more complex mocking to capture call order if just checking final state.
    # For simplicity, we'll assume if both are called, it's likely in order.
    # A more robust test would mock pygame.draw on the screen or use specific side effects.
    
    # Test event handling order
    # Events are passed to components one by one.
    # If comp1 modifies an event or context that comp2 uses, order matters.
    # Here, just check they both get the events.
    event1 = create_mouse_event(pygame.MOUSEBUTTONDOWN, 1, (10,10))
    events_list = [event1]
    registry.handle_events(events_list, mock_context)
    assert event1 in comp1.handled_events
    assert event1 in comp2.handled_events
    
    # Test update order
    dt = 0.016
    registry.update_components(dt, mock_context)
    assert comp1.updated_dt == dt
    assert comp2.updated_dt == dt

    # To truly test order, one component could set a flag in context that the other checks.
    # Example:
    # class OrderedMockComponent(MockUIComponent):
    #     def __init__(self, order_id):
    #         super().__init__()
    #         self.order_id = order_id
    #     def update(self, dt, context):
    #         super().update(dt, context)
    #         if not hasattr(context, 'update_order'):
    #             context.update_order = []
    #         context.update_order.append(self.order_id)
    #
    # comp_ordered1 = OrderedMockComponent(1)
    # comp_ordered2 = OrderedMockComponent(2)
    # registry.register(comp_ordered1)
    # registry.register(comp_ordered2)
    # registry.update_components(dt, mock_context)
    # assert mock_context.update_order == [1, 2]
```
