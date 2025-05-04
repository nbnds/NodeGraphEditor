import os
import pytest
os.environ["SDL_VIDEODRIVER"] = "dummy"
from editor import NodeEditor
from node import Node
from connection import Connection
import pygame

class TestNodeEditor:

    @pytest.fixture
    def editor(self):
        editor = NodeEditor()
        editor.zoom = 1.0
        editor.canvas_offset_x = 0
        editor.canvas_offset_y = 0
        # Return the configured object
        return editor

    def test_add_node(self, editor):
        """Test adding a node to the editor and the graph."""
        initial_count = len(editor.nodes)
        editor.nodes.append(Node(100, 100, 1))
        editor.nx_graph.add_node(1, pos=(100, 100))
        assert len(editor.nodes) == initial_count + 1
        assert 1 in editor.nx_graph.nodes

    def test_delete_node(self, editor):
        node = Node(100, 100, 1)
        editor.nodes.append(node)
        editor.nx_graph.add_node(1, pos=(100, 100))
        editor.try_delete_node(100, 100)
        assert node not in editor.nodes
        assert 1 not in editor.nx_graph.nodes

    def test_add_connection(self, editor):
        n1 = Node(0, 0, 1)
        n2 = Node(100, 100, 2)
        editor.nodes.extend([n1, n2])
        editor.nx_graph.add_node(1, pos=(0, 0))
        editor.nx_graph.add_node(2, pos=(100, 100))
        editor.connections.append(Connection(n1, n2))
        editor.nx_graph.add_edge(1, 2)
        assert editor.nx_graph.has_edge(1, 2) is True
        assert len(editor.connections) == 1

    def test_identity_no_zoom_no_offset(self, editor):
        """If zoom=1 and offset=0, screen and world coordinates are identical."""
        assert editor.screen_to_world((100, 200)) == (100, 200)
        assert editor.screen_to_world((0, 0)) == (0, 0)

    def test_offset_only(self, editor):
        """If offset is set, world coordinates shift accordingly."""
        editor.canvas_offset_x = 50
        editor.canvas_offset_y = 20
        # screen (0,0) maps to world (50,20)
        assert editor.screen_to_world((0, 0)) == (50, 20)
        # screen (100,200) maps to world (150,220)
        assert editor.screen_to_world((100, 200)) == (150, 220)

    def test_zoom_functionality(self, editor):
        """If zoom is applied, world coordinates scale accordingly."""
        editor.zoom = 2.0
        # screen (100,200) maps to world (50,100)
        assert editor.screen_to_world((100, 200)) == (50, 100)

    def test_zoom_and_offset(self, editor):
        """If both zoom and offset are set, both effects combine."""
        editor.zoom = 2.0
        editor.canvas_offset_x = 10
        editor.canvas_offset_y = 20
        # screen (0,0) maps to world (10,20)
        assert editor.screen_to_world((0, 0)) == (10, 20)
        # screen (100,200) maps to world (60,120)
        assert editor.screen_to_world((100, 200)) == (60, 120)

    def test_screen_to_world_after_resize(self, editor):
        """After resizing the window, screen_to_world should still work as expected."""
        # Simulate window resize
        new_size = (1200, 900)
        editor.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
        # The method should still return correct world coordinates
        editor.zoom = 1.0
        editor.canvas_offset_x = 0
        editor.canvas_offset_y = 0
        assert editor.screen_to_world((100, 200)) == (100, 200)
        # Now with offset and zoom
        editor.zoom = 2.0
        editor.canvas_offset_x = 10
        editor.canvas_offset_y = 20
        assert editor.screen_to_world((100, 200)) == (60, 120)
