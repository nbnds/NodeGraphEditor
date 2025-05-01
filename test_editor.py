import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import unittest
from editor import NodeEditor
from node import Node
from connection import Connection
import pygame

class TestNodeEditor(unittest.TestCase):
    def setUp(self):
        self.editor = NodeEditor()
        self.editor.zoom = 1.0
        self.editor.canvas_offset_x = 0
        self.editor.canvas_offset_y = 0

    def test_add_node(self):
        initial_count = len(self.editor.nodes)
        self.editor.nodes.append(Node(100, 100, 1))
        self.editor.nx_graph.add_node(1, pos=(100, 100))
        self.assertEqual(len(self.editor.nodes), initial_count + 1)
        self.assertIn(1, self.editor.nx_graph.nodes)

    def test_delete_node(self):
        node = Node(100, 100, 1)
        self.editor.nodes.append(node)
        self.editor.nx_graph.add_node(1, pos=(100, 100))
        self.editor.try_delete_node(100, 100)
        self.assertNotIn(node, self.editor.nodes)
        self.assertNotIn(1, self.editor.nx_graph.nodes)

    def test_add_connection(self):
        n1 = Node(0, 0, 1)
        n2 = Node(100, 100, 2)
        self.editor.nodes.extend([n1, n2])
        self.editor.nx_graph.add_node(1, pos=(0, 0))
        self.editor.nx_graph.add_node(2, pos=(100, 100))
        self.editor.connections.append(Connection(n1, n2))
        self.editor.nx_graph.add_edge(1, 2)
        self.assertTrue(self.editor.nx_graph.has_edge(1, 2))

    def test_identity_no_zoom_no_offset(self):
        """If zoom=1 and offset=0, screen and world coordinates are identical."""
        self.assertEqual(self.editor.screen_to_world(100, 200), (100, 200))
        self.assertEqual(self.editor.screen_to_world(0, 0), (0, 0))
    
    def test_offset_only(self):
        """If offset is set, world coordinates shift accordingly."""
        self.editor.canvas_offset_x = 50
        self.editor.canvas_offset_y = 20
        # screen (0,0) maps to world (50,20)
        self.assertEqual(self.editor.screen_to_world(0, 0), (50, 20))
        # screen (100,200) maps to world (150,220)
        self.assertEqual(self.editor.screen_to_world(100, 200), (150, 220))

    def test_zoom_functionality(self):
        """If zoom is applied, world coordinates scale accordingly."""
        self.editor.zoom = 2.0
        # screen (100,200) maps to world (50,100)
        self.assertEqual(self.editor.screen_to_world(100, 200), (50, 100))

    def test_zoom_and_offset(self):
        """If both zoom and offset are set, both effects combine."""
        self.editor.zoom = 2.0
        self.editor.canvas_offset_x = 10
        self.editor.canvas_offset_y = 20
        # screen (0,0) maps to world (10,20)
        self.assertEqual(self.editor.screen_to_world(0, 0), (10, 20))
        # screen (100,200) maps to world (60,120)
        self.assertEqual(self.editor.screen_to_world(100, 200), (60, 120))

    def test_screen_to_world_after_resize(self):
        """After resizing the window, screen_to_world should still work as expected."""
        # Simulate window resize
        new_size = (1200, 900)
        self.editor.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
        # The method should still return correct world coordinates
        self.editor.zoom = 1.0
        self.editor.canvas_offset_x = 0
        self.editor.canvas_offset_y = 0
        self.assertEqual(self.editor.screen_to_world(100, 200), (100, 200))
        # Now with offset and zoom
        self.editor.zoom = 2.0
        self.editor.canvas_offset_x = 10
        self.editor.canvas_offset_y = 20
        self.assertEqual(self.editor.screen_to_world(100, 200), (60, 120))

if __name__ == '__main__':
    unittest.main()