import os
import pytest
import pickle
import logging
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
from editor import NodeEditor
from node import Node
from connection import Connection
import networkx as nx

@pytest.fixture(scope="session", autouse=True)
def pygame_init_and_quit():
    pygame.init()
    yield
    pygame.quit()


class TestNodeEditor:

    @pytest.fixture
    def editor(self):
        editor = NodeEditor()
        editor.zoom = 1.0
        editor.panning_state.offset_x = 0
        editor.panning_state.offset_y = 0
        # Remove: editor.canvas_offset_x = 0
        # Remove: editor.canvas_offset_y = 0
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
        editor.panning_state.offset_x = 50
        editor.panning_state.offset_y = 20
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
        editor.panning_state.offset_x = 10
        editor.panning_state.offset_y = 20
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
        editor.panning_state.offset_x = 0
        editor.panning_state.offset_y = 0
        assert editor.screen_to_world((100, 200)) == (100, 200)
        # Now with offset and zoom
        editor.zoom = 2.0
        editor.panning_state.offset_x = 10
        editor.panning_state.offset_y = 20
        assert editor.screen_to_world((100, 200)) == (60, 120)

    def test_rename_node(self, editor):
        """
        When a node is selected and the user enters a new name and presses ENTER,
        the node's label and the graph's node attribute should update immediately.
        """
        # Given a node is present and selected
        node = Node(100, 100, 1)
        editor.nodes.append(node)
        editor.nx_graph.add_node(1, pos=(100, 100), name=node.node_name)
        # Simulate user selects the node (as in UI)
        editor.selection.select_node(node, editor.nodes)
        # And the text input is activated
        editor.text_input_active = True
        # And the user types a new name
        new_name = "MyNode"
        editor.visualizer.value = new_name
        # When the user presses ENTER
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        editor.handle_key_down(event)
        # Then the node's name should be updated
        assert node.node_name == new_name
        # And the graph's node attribute should be updated
        assert editor.nx_graph.nodes[1]['name'] == new_name

    def test_load_graph_id_collision(self, editor):
        """
        When loading a graph, node ids should not collide with existing nodes.
        After loading, new nodes should get the next free id.
        """

        # Use variables for initial node ids and derive coordinates from id
        initial_ids = [1, 2, 3]
        for nid in initial_ids:
            node = Node(nid * 10, nid * 10, nid)
            editor.nodes.append(node)
            editor.nx_graph.add_node(nid, pos=(nid * 10, nid * 10), name=chr(64 + nid))  # names: 'A', 'B', 'C'
        editor.next_node_id = max(initial_ids) + 1

        logging.info(f"[TEST] Initial node set: ids={initial_ids}, node_names={[chr(64 + i) for i in initial_ids]}")

        # Prepare a graph file with nodes having ids that may collide
        loaded_ids = [2, 3, 4]
        G = nx.DiGraph()
        for nid in loaded_ids:
            G.add_node(nid, pos=(nid * 100, nid * 100), name=chr(86 + nid))  # names: 'X', 'Y', 'Z'
        graph_file = os.path.join(os.path.dirname(__file__), "test_graph.pickle")
        with open(graph_file, "wb") as f:
            pickle.dump(G, f)

        logging.info(f"[TEST] Graph file node ids: {loaded_ids}, node_names={[chr(86 + i) for i in loaded_ids]}")

        # Load the graph (this replaces all nodes and connections)
        editor.load_graph(graph_file)

        # Remove the test file after loading
        os.remove(graph_file)

        # Collect all node ids after loading
        ids = [n.id for n in editor.nodes]
        logging.info(f"[TEST] Editor node ids after load: {ids}")
        loaded_names = set(n.node_name for n in editor.nodes)
        logging.info(f"[TEST] Editor node names after load: {loaded_names}")

        # There should be no duplicate ids
        logging.info(f"[ASSERT] Checking uniqueness: ids={ids}, set(ids)={set(ids)}")
        assert len(ids) == len(set(ids)), f"Loaded node IDs were not unique: {ids}"
        # All expected node names should be present
        expected_names = {chr(86 + i) for i in loaded_ids}
        logging.info(f"[ASSERT] Checking names: expected={expected_names}, loaded={loaded_names}")
        assert expected_names.issubset(loaded_names), (
            f"Expected node names {expected_names}, got {loaded_names}"
        )
        # next_node_id should be one higher than the highest id
        logging.info(f"[ASSERT] Checking next_node_id: next_node_id={editor.next_node_id}, max(ids)+1={max(ids) + 1}")
        assert editor.next_node_id == max(ids) + 1, (
            f"next_node_id should be {max(ids) + 1}, got {editor.next_node_id}"
        )

        # Add a new node and check that its id does not collide
        new_node = Node(999, 999, editor.next_node_id)
        editor.nodes.append(new_node)
        editor.nx_graph.add_node(editor.next_node_id, pos=(999, 999), name="NEW")
        ids_after = [n.id for n in editor.nodes]
        logging.info(f"[ASSERT] After add: ids_after={ids_after}, new_node.id={new_node.id}, previous_ids={ids}")
        assert len(ids_after) == len(set(ids_after)), (
            f"After adding, node IDs were not unique: {ids_after}"
        )
        assert new_node.id not in ids[:-1], (
            f"New node id {new_node.id} collides with loaded ids {ids}"
        )

    def test_load_graph_with_id_collision_and_edge_remap(self, editor, caplog):
        """
        Test that when loading a graph with node id collisions, both nodes and edges are remapped correctly.
        This test creates a graph file with overlapping node ids and edges, loads it, and verifies that:
        - Node ids are unique after loading.
        - Edges are remapped to the new node ids.
        - Node names and edge labels are preserved.
        - All steps are logged for clarity.
        """
        caplog.set_level(logging.INFO)

        # Initial state: add nodes with ids 1, 2, 3 to the editor
        initial_ids = [1, 2, 3]
        for nid in initial_ids:
            node = Node(nid * 10, nid * 10, nid)
            editor.nodes.append(node)
            editor.nx_graph.add_node(nid, pos=(nid * 10, nid * 10), name=f"Editor{nid}")
        editor.next_node_id = max(initial_ids) + 1
        logging.info(f"[TEST] Initial editor node ids: {initial_ids}")

        # Prepare a graph file with colliding node ids and edges
        loaded_ids = [2, 3, 4]
        G = nx.DiGraph()
        for nid in loaded_ids:
            G.add_node(nid, pos=(nid * 100, nid * 100), name=f"Node-{nid}")
        # Add edges between these nodes (2->3, 3->4, 4->2)
        G.add_edge(2, 3, label="A")
        G.add_edge(3, 4, label="B")
        G.add_edge(4, 2, label="C")
        graph_file = os.path.join(os.path.dirname(__file__), "test_graph_collision.pickle")
        with open(graph_file, "wb") as f:
            pickle.dump(G, f)
        logging.info(f"[TEST] Graph file node ids: {loaded_ids}")
        logging.info(f"[TEST] Graph file edges: {list(G.edges(data=True))}")

        # Load the graph (should remap ids and edges)
        editor.load_graph(graph_file)
        os.remove(graph_file)

        # Gather loaded node ids and names
        ids = [n.id for n in editor.nodes]
        names = [n.node_name for n in editor.nodes]
        logging.info(f"[TEST] Editor node ids after load: {ids}")
        logging.info(f"[TEST] Editor node names after load: {names}")

        # Assert node ids are unique
        assert len(ids) == len(set(ids)), f"Node IDs are not unique after remapping: {ids}"

        # Build mapping from node names to ids for easier edge verification
        name_to_id = {n.node_name: n.id for n in editor.nodes}
        logging.info(f"[TEST] Name to id mapping: {name_to_id}")

        # Gather all edges from the editor's nx_graph
        edges = list(editor.nx_graph.edges(data=True))
        logging.info(f"[TEST] Editor edges after load: {edges}")

        # Check that all expected node names are present
        expected_names = {f"Node-{nid}" for nid in loaded_ids}
        assert expected_names.issubset(set(names)), f"Expected node names {expected_names}, got {set(names)}"

        # Check that all expected edges exist and labels are preserved
        expected_edges = [
            ("Node-2", "Node-3", "A"),
            ("Node-3", "Node-4", "B"),
            ("Node-4", "Node-2", "C"),
        ]
        for src_name, dst_name, label in expected_edges:
            src_id = name_to_id[src_name]
            dst_id = name_to_id[dst_name]
            assert editor.nx_graph.has_edge(src_id, dst_id), (
                f"Missing edge {src_name}->{dst_name}"
            )
            edge_label = editor.nx_graph[src_id][dst_id].get("label", None)
            assert edge_label == label, (
                f"Edge label mismatch for {src_name}->{dst_name}: "
                f"expected '{label}', got '{edge_label}'"
            )
            logging.info(
                "[ASSERT] Edge %s(%s)->%s(%s) with label '%s' exists and is correct.",
                src_name, src_id, dst_name, dst_id, label
            )

        # Check that next_node_id is correct
        expected_next_id = max(ids) + 1
        assert editor.next_node_id == expected_next_id, (
            f"next_node_id should be {expected_next_id}, got {editor.next_node_id}"
        )
        logging.info(
            "[ASSERT] next_node_id is correct: %s", editor.next_node_id
        )
