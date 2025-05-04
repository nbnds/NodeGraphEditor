import os
import pytest
from conftest import lmb_down, lmb_up
os.environ["SDL_VIDEODRIVER"] = "dummy"
from editor import NodeEditor
from button import Button
from toolbar import Toolbar
from actions import AddNodeAction
import pygame

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()

class TestButton:



    @pytest.fixture
    def toolbar(self):
        """Fixture to create a toolbar for testing."""
        toolbar = Toolbar()
        toolbar.bg_color = (0, 0, 0)
        toolbar.buttons = []
        toolbar.padding = 10
        toolbar.left_margin = 5
        toolbar.top_margin = 5
        toolbar.min_width = 100
        toolbar.width = 100
        # Return the configured object
        return toolbar

    @pytest.fixture
    def editor(self, toolbar):
        editor = NodeEditor(toolbar)
        editor.zoom = 1.0
        editor.canvas_offset_x = 0
        editor.canvas_offset_y = 0
        return editor

    @pytest.fixture
    def AddNodeButton(self):
        """Fixture to create a button for testing."""
        button = Button(rect=pygame.Rect(50, 50, 30, 30), label=None, action=AddNodeAction())
        return button

    def test_button_initialization(self, editor, AddNodeButton):
        """Test the initialization of a button."""
        editor.toolbar.add_button(AddNodeButton)

        assert len(editor.toolbar.buttons) == 1
        assert editor.toolbar.buttons[-1].label == "<UNNAMED>"
        editor.dispatch_event(lmb_down((60, 60)))
        editor.dispatch_event(lmb_down((60, 60)))
        editor.dispatch_event(lmb_down((60, 60)))
        clicked_button = editor.toolbar.get_clicked_button(60, 60)
        print(editor.nodes[0].x, editor.nodes[0].y)
        assert clicked_button is not None
        assert clicked_button.label == "<UNNAMED>"
        assert clicked_button.rect == pygame.Rect(50, 50, 30, 30)
        assert len(editor.nodes) == 3

    def test_add_node_action_button(self, editor):
            add_node_btn = Button(action=AddNodeAction())
            add_node_btn_pos = editor.toolbar.add_button(add_node_btn)
            editor.dispatch_event(lmb_down(add_node_btn_pos))
            editor.dispatch_event(lmb_up(add_node_btn_pos))

            assert len(editor.nodes) == 1
            assert editor.nodes[-1].selected is False
            node_center = editor.nodes[-1].get_center()
            editor.dispatch_event(lmb_down(node_center))
            editor.dispatch_event(lmb_up(node_center))
            assert editor.nodes[-1].selected is True


    def test_clicking_add_node_button_does_not_remove_node_selection(self, editor):
        add_node_btn = Button(action=AddNodeAction())
        add_node_btn_pos = editor.toolbar.add_button(add_node_btn)
        editor.dispatch_event(lmb_down(add_node_btn_pos))
        editor.dispatch_event(lmb_up(add_node_btn_pos))
        assert len(editor.nodes) == 1, "Expected only one node to be created"
        assert editor.nodes[-1].selected is False, "Expected the first ever created node to be unselected"

        # clicking the node to select it
        node_center = editor.nodes[-1].get_center()
        editor.dispatch_event(lmb_down(node_center))
        editor.dispatch_event(lmb_up(node_center))
        assert editor.nodes[-1].selected is True

        # clicking the add node button again to add another node removes node selection
        editor.dispatch_event(lmb_down(add_node_btn_pos))
        editor.dispatch_event(lmb_up(add_node_btn_pos))
        assert len(editor.nodes) == 2, "Expected two nodes to be present after adding another node"
        assert sum(1 for node in editor.nodes if node.selected) == 1, "Expected exactly one node to be selected"
        assert editor.nodes[-1].selected is False, "Expected the newly created node to be unselected"
        assert editor.nodes[-2].selected is True, "Expected the previously created node to stay selected"


