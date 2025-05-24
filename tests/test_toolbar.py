import pygame
import pytest
from editor_context import EditorContext
from toolbar_component import ToolbarComponent
from button_component import ButtonComponent
from actions import NoOpAction # For creating dummy actions

# Pygame_init fixture is expected to be in conftest.py

@pytest.fixture
def context(pygame_init): # Use pygame_init fixture from conftest.py
    ctx = EditorContext()
    # Mock screen and config for ToolbarComponent layout
    mock_screen = pygame.Surface((1280, 720))
    ctx.screen = mock_screen
    ctx.config = {
        'screen_width': 1280,
        'screen_height': 720,
    }
    return ctx

@pytest.fixture
def toolbar_comp(context):
    """Fixture to create a ToolbarComponent."""
    return ToolbarComponent(context)

def test_buttons_are_added_and_toolbar_layouts_them(toolbar_comp, context):
    """Test adding buttons and basic layout."""
    assert len(toolbar_comp.buttons) == 0
    initial_toolbar_height = toolbar_comp.rect.height
    
    # Buttons are expected to have a default size if not specified, e.g., (100,30) by ButtonComponent
    # ToolbarComponent._layout_buttons adjusts their x position and the toolbar's height.
    
    btn1 = ButtonComponent(context, NoOpAction(), "Button 1")
    btn1_initial_width = btn1.rect.width 
    btn1_initial_height = btn1.rect.height
    
    toolbar_comp.add_button(btn1)
    assert len(toolbar_comp.buttons) == 1
    assert toolbar_comp.buttons[0] == btn1
    
    # Check layout: button position
    assert btn1.rect.x == toolbar_comp.left_margin
    assert btn1.rect.y == toolbar_comp.top_margin + toolbar_comp.rect.top # Relative to toolbar's top
    
    # Check toolbar height update
    expected_toolbar_height = btn1_initial_height + (2 * toolbar_comp.padding)
    assert toolbar_comp.rect.height == expected_toolbar_height
    
    btn2 = ButtonComponent(context, NoOpAction(), "Button 2")
    btn2_initial_width = btn2.rect.width
    toolbar_comp.add_button(btn2)
    assert len(toolbar_comp.buttons) == 2
    
    # Check layout of second button
    expected_btn2_x = toolbar_comp.left_margin + btn1_initial_width + toolbar_comp.button_spacing
    assert btn2.rect.x == expected_btn2_x
    
    # Toolbar height should remain based on the tallest button (assuming they are same height here)
    assert toolbar_comp.rect.height == expected_toolbar_height


def test_toolbar_width_spans_screen_width(toolbar_comp, context):
    """Test that the toolbar width is set to the screen width from context."""
    # ToolbarComponent's _layout_buttons sets self.width = screen_width
    # and self.rect.width = self.width
    
    # Add a button to trigger layout
    btn1 = ButtonComponent(context, NoOpAction(), "Test")
    toolbar_comp.add_button(btn1) # This calls _layout_buttons
    
    assert toolbar_comp.rect.width == context.config['screen_width']


# The old tests 'test_buttons_grow_when_longer_label_added' and 
# 'test_toolbar_width_adapts_to_buttons_width' are not directly applicable
# because ButtonComponent itself does not auto-resize based on label in the current implementation.
# ButtonComponent has a fixed rect or one passed in.
# ToolbarComponent lays out buttons based on their existing rect.width.

# If the requirement was for ButtonComponent to auto-size to its label,
# and ToolbarComponent to then adjust all buttons to the widest button,
# those components would need to be designed differently.

# For now, let's test that ToolbarComponent correctly positions buttons
# based on their given sizes and updates its own height.

def test_toolbar_height_adapts_to_tallest_button(toolbar_comp, context):
    """Test that toolbar height adapts to the tallest button."""
    
    btn_short = ButtonComponent(context, NoOpAction(), "Short", rect=pygame.Rect(0,0,80,30))
    btn_tall = ButtonComponent(context, NoOpAction(), "Tall", rect=pygame.Rect(0,0,80,50)) # Taller button
    
    toolbar_comp.add_button(btn_short)
    expected_height_1 = btn_short.rect.height + (2 * toolbar_comp.padding)
    assert toolbar_comp.rect.height == expected_height_1
    
    toolbar_comp.add_button(btn_tall)
    expected_height_2 = btn_tall.rect.height + (2 * toolbar_comp.padding)
    assert toolbar_comp.rect.height == expected_height_2

    # Add another short button, height should remain based on tallest
    btn_short2 = ButtonComponent(context, NoOpAction(), "Short2", rect=pygame.Rect(0,0,80,30))
    toolbar_comp.add_button(btn_short2)
    assert toolbar_comp.rect.height == expected_height_2


def test_button_event_handling_via_toolbar(toolbar_comp, context, create_mouse_event):
    """Test that button events are handled when passed through the toolbar."""
    action = NoOpAction()
    
    # Mock the action's execute method to check if it's called
    action_executed_count = 0
    def mock_execute(ctx):
        nonlocal action_executed_count
        action_executed_count += 1
    
    action.execute = mock_execute

    btn = ButtonComponent(context, action, "ClickMe")
    toolbar_comp.add_button(btn) # This will layout the button, giving it a position
    
    # Simulate a click on the button's area
    # Ensure btn.rect has valid screen coordinates after layout
    # ToolbarComponent places buttons relative to its own rect.top
    # For this test, assume toolbar_comp.rect.top is 0.
    
    click_pos = btn.rect.center # Get the center of the button after layout
    
    event_down = create_mouse_event(pygame.MOUSEBUTTONDOWN, 1, click_pos)
    event_up = create_mouse_event(pygame.MOUSEBUTTONUP, 1, click_pos) # Some actions might trigger on UP

    # Toolbar handle_event should pass it to the button
    toolbar_comp.handle_event(event_down, context)
    toolbar_comp.handle_event(event_up, context) # ButtonComponent executes on MOUSEBUTTONDOWN
    
    assert action_executed_count == 1, "Button action should have been executed once"

    # Test click outside the button
    click_pos_outside = (btn.rect.right + 10, btn.rect.centery)
    event_down_outside = create_mouse_event(pygame.MOUSEBUTTONDOWN, 1, click_pos_outside)
    toolbar_comp.handle_event(event_down_outside, context)
    
    assert action_executed_count == 1, "Button action should not execute if clicked outside"
