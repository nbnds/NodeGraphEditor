import pytest
import pygame # Required for conftest.py pygame_init fixture
import networkx as nx
from editor_context import EditorContext
from node import Node
from connection import Connection
from undo import UndoStack

# Ensure conftest.py is in the same directory or a parent directory for pygame_init
# and other fixtures like mock events if needed.

@pytest.fixture
def context(pygame_init): # Use pygame_init fixture
    """Fixture to create an EditorContext with an initialized UndoStack and nx_graph."""
    ctx = EditorContext()
    ctx.undo_stack = UndoStack() # Ensure undo_stack is initialized
    ctx.nx_graph = nx.DiGraph()  # Ensure nx_graph is initialized
    return ctx

def test_add_node_to_context(context):
    """Test adding a Node instance to EditorContext."""
    initial_node_count = len(context.nodes)
    initial_graph_nodes = len(context.nx_graph.nodes)
    
    node1 = Node(id=None, title="Node 1", x=100, y=100) # id will be assigned by context
    context.add_node(node1)
    
    assert len(context.nodes) == initial_node_count + 1
    assert context.nodes[0] == node1
    assert node1.id is not None, "Node ID should be assigned by context"
    assert context.next_node_id == node1.id + 1
    
    assert len(context.nx_graph.nodes) == initial_graph_nodes + 1
    assert node1.id in context.nx_graph.nodes
    assert context.nx_graph.nodes[node1.id]['data_dict']['title'] == "Node 1"

def test_remove_node_from_context(context):
    """Test removing a Node instance from EditorContext."""
    node1 = Node(id=None, title="Node 1", x=100, y=100)
    context.add_node(node1)
    node1_id = node1.id # Get assigned ID

    node2 = Node(id=None, title="Node 2", x=200, y=200)
    context.add_node(node2)
    
    initial_node_count = len(context.nodes)
    initial_graph_nodes = len(context.nx_graph.nodes)

    context.remove_node(node1_id)
    
    assert len(context.nodes) == initial_node_count - 1
    assert node1 not in context.nodes
    assert node1_id not in context.nx_graph.nodes
    assert len(context.nx_graph.nodes) == initial_graph_nodes - 1

def test_add_connection_to_context(context):
    """Test adding a Connection instance to EditorContext."""
    node1 = Node(id=None, title="N1", x=0, y=0)
    node2 = Node(id=None, title="N2", x=100, y=100)
    context.add_node(node1)
    context.add_node(node2)

    initial_conn_count = len(context.connections)
    initial_graph_edges = len(context.nx_graph.edges)

    # Connection constructor might take start_node_id, end_node_id, id_val (optional)
    # Connection(start_node_id, end_node_id, start_pin_id=None, end_pin_id=None, id_val=None)
    connection1 = Connection(start_node_id=node1.id, end_node_id=node2.id) # id will be assigned
    context.add_connection(connection1)

    assert len(context.connections) == initial_conn_count + 1
    assert context.connections[0] == connection1
    assert connection1.id is not None, "Connection ID should be assigned by context"
    assert context.next_connection_id == connection1.id + 1
    
    assert len(context.nx_graph.edges) == initial_graph_edges + 1
    assert context.nx_graph.has_edge(node1.id, node2.id)

def test_remove_connection_from_context(context):
    """Test removing a Connection instance from EditorContext."""
    node1 = Node(id=None, title="N1", x=0, y=0)
    node2 = Node(id=None, title="N2", x=100, y=100)
    node3 = Node(id=None, title="N3", x=200, y=0)
    context.add_node(node1)
    context.add_node(node2)
    context.add_node(node3)

    conn1 = Connection(start_node_id=node1.id, end_node_id=node2.id)
    context.add_connection(conn1)
    conn1_id = conn1.id

    conn2 = Connection(start_node_id=node2.id, end_node_id=node3.id)
    context.add_connection(conn2)

    initial_conn_count = len(context.connections)
    initial_graph_edges = len(context.nx_graph.edges)

    context.remove_connection(connection_id_val=conn1_id)
    
    assert len(context.connections) == initial_conn_count - 1
    assert conn1 not in context.connections
    assert not context.nx_graph.has_edge(node1.id, node2.id)
    assert len(context.nx_graph.edges) == initial_graph_edges - 1
    assert context.nx_graph.has_edge(node2.id, node3.id) # Ensure other connection still exists


def test_remove_node_also_removes_connections(context):
    """Test that removing a node also removes its connections."""
    node1 = Node(id=None, x=0, y=0)
    node2 = Node(id=None, x=100, y=100)
    node3 = Node(id=None, x=200, y=0)
    context.add_node(node1)
    context.add_node(node2)
    context.add_node(node3)
    node2_id = node2.id

    conn1 = Connection(start_node_id=node1.id, end_node_id=node2.id)
    context.add_connection(conn1)
    conn2 = Connection(start_node_id=node2.id, end_node_id=node3.id)
    context.add_connection(conn2)
    conn3 = Connection(start_node_id=node1.id, end_node_id=node3.id) # Connection not involving node2
    context.add_connection(conn3)

    assert len(context.connections) == 3
    assert context.nx_graph.number_of_edges() == 3

    context.remove_node(node2_id)

    assert node2 not in context.nodes
    assert conn1 not in context.connections
    assert conn2 not in context.connections
    assert conn3 in context.connections # This connection should remain
    assert len(context.connections) == 1
    assert context.nx_graph.number_of_edges() == 1
    assert context.nx_graph.has_edge(node1.id, node3.id)
    assert not context.nx_graph.has_node(node2_id)

def test_clear_all_nodes_and_connections(context):
    """Test the clear_all_nodes_and_connections method."""
    node1 = Node(id=None, x=0, y=0)
    node2 = Node(id=None, x=100, y=100)
    context.add_node(node1)
    context.add_node(node2)
    conn1 = Connection(start_node_id=node1.id, end_node_id=node2.id)
    context.add_connection(conn1)

    assert len(context.nodes) == 2
    assert len(context.connections) == 1
    assert context.nx_graph.number_of_nodes() == 2
    assert context.nx_graph.number_of_edges() == 1
    assert context.next_node_id > 1
    assert context.next_connection_id > 1

    context.clear_all_nodes_and_connections()

    assert len(context.nodes) == 0
    assert len(context.connections) == 0
    assert context.nx_graph.number_of_nodes() == 0
    assert context.nx_graph.number_of_edges() == 0
    assert context.next_node_id == 1
    assert context.next_connection_id == 1

# Basic Undo/Redo Test (more comprehensive tests would be in test_undo.py or here)
# This test is simplified and assumes UndoStack stores snapshots of (nodes, connections, next_ids)
# The current UndoAction in actions.py reconstructs from nx_graph, which is a bit different.
# For a true context undo, EditorContext would need to manage snapshots.
# Let's adapt this to test a conceptual "push_to_undo" if context had it.

# For now, testing UndoStack interaction via Actions is complex here without an App instance.
# A simple test for UndoStack itself might be more appropriate in a separate test_undo.py.
# The subtask mentions "UndoStack interactions within EditorContext are tested (e.g., an action that uses undo should correctly restore data in the context)."
# This implies testing the *effect* of an undo action on the context.
# This will be better tested in test_actions.py or test_button_component_actions.py where actions are executed.

# Placeholder for more advanced undo/redo tests if EditorContext directly manages snapshots.
# For now, the UndoAction in actions.py uses context.undo_stack.pop() and reconstructs.
# We can test if an action (like AddNodeAction) followed by an UndoAction (conceptually)
# correctly reverts the context. This is better suited for test_actions.py.
```
