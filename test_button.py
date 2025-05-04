import os
import pytest
from conftest import lmb_down, lmb_up, mouse_move, rmb_down, rmb_up
os.environ["SDL_VIDEODRIVER"] = "dummy"
from editor import NodeEditor
from button import Button
from toolbar import Toolbar
from actions import AddNodeAction, DeleteAllAction
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


    def test_toolbar_initialization(self, editor):
        add_node_button = Button(rect=pygame.Rect(50, 50, 40, 40), label=None, action=AddNodeAction())
        button_pos = editor.toolbar.add_button(add_node_button)

        assert len(editor.toolbar.buttons) == 1
        assert editor.toolbar.buttons[-1].label == "<UNNAMED>"
        editor.dispatch_event(lmb_down(button_pos))
        clicked_button = editor.toolbar.get_clicked_button(button_pos)  # Updated to use button_pos

        assert clicked_button is not None
        assert clicked_button.label == "<UNNAMED>"
        assert len(editor.nodes) == 1


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

    def test_clear_all_action_button(self,editor):
        """Test the Clear All action button."""
        add_node_btn = Button(action=AddNodeAction())
        add_node_btn_pos = editor.toolbar.add_button(add_node_btn)
        clear_all_btn = Button(action=DeleteAllAction(), label="Clear All")
        clear_all_btn_pos = editor.toolbar.add_button(clear_all_btn)
        # add a node to the editor
        editor.dispatch_event(lmb_down(add_node_btn_pos))
        editor.dispatch_event(lmb_up(add_node_btn_pos))
        # add second node to the editor
        editor.dispatch_event(lmb_down(add_node_btn_pos))
        editor.dispatch_event(lmb_up(add_node_btn_pos))
        assert len(editor.nodes) == 2, "Expected two nodes to be created"

        editor.dispatch_event(lmb_down(clear_all_btn_pos))
        editor.dispatch_event(lmb_up(clear_all_btn_pos))

        assert len(editor.nodes) == 0, "Expected all nodes to be cleared"
        assert len(editor.connections) == 0, "Expected all connections to be cleared"
        assert editor.next_node_id == 1, "Expected next_node_id to be reset to 1"

    def test_clear_all_removes_connections(self,editor):
        """Test the Clear All action button removes connections."""
        add_node_btn = Button(action=AddNodeAction())
        add_node_btn_pos = editor.toolbar.add_button(add_node_btn)
        clear_all_btn = Button(action=DeleteAllAction(), label="Clear All")
        clear_all_btn_pos = editor.toolbar.add_button(clear_all_btn)
        # no connections should be present at the start
        assert len(editor.connections) == 0, "no connections should be present at the start"

        # add a node to the editor
        editor.dispatch_event(lmb_down(add_node_btn_pos))
        editor.dispatch_event(lmb_up(add_node_btn_pos))
        first_node = editor.nodes[-1]

        # move first node to select it
        node_center = first_node.get_center()
        editor.dispatch_event(lmb_down(node_center))
        target_pos = node_center[0] + first_node.width + 50, node_center[1] # Move right by 50 pixels
        editor.dispatch_event(mouse_move(node_center, (target_pos[0], target_pos[1]), buttons=(1, 0, 0)))
        editor.dispatch_event(lmb_up(target_pos))
        assert first_node.selected is True

        # add second node to the editor
        editor.dispatch_event(lmb_down(add_node_btn_pos))
        editor.dispatch_event(lmb_up(add_node_btn_pos))
        second_node = editor.nodes[-1]

        assert second_node.selected is False, "Expected the newly created node to be unselected"
        assert first_node.selected is True, "Expected the previously created node to stay selected"

        # Check the second node is not at the same position as the first
        # (most recent nodes are on top, hence the -1)
        assert second_node.get_center() != editor.nodes[-2].get_center()

        # create a connection between the two nodes
        editor.dispatch_event(rmb_down(second_node.get_center()))
        editor.dispatch_event(rmb_up(second_node.get_center()))

        assert len(editor.connections) == 1, "Expected one connection to be created"

        # click the Clear All button
        editor.dispatch_event(lmb_down(clear_all_btn_pos))
        editor.dispatch_event(lmb_up(clear_all_btn_pos))

        assert len(editor.nodes) == 0, "Expected all nodes to be cleared"
        assert len(editor.connections) == 0, "Expected all connections to be cleared"
