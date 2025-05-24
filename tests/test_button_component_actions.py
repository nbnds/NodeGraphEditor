# import os # No longer needed for dummy SDL driver
import pytest
import pygame
import networkx as nx
from editor_context import EditorContext
from button_component import ButtonComponent
from actions import AddNodeAction, DeleteAllAction, UndoAction, DumpGraphAction
from node import Node # For checking node properties if necessary
from connection import Connection # For checking connection properties
from undo import UndoStack

# Pygame_init fixture is expected to be in conftest.py
# Event fixtures (lmb_down, etc.) from conftest.py can be used with create_mouse_event

@pytest.fixture
def context(pygame_init): # Use pygame_init fixture
    """Fixture to create an EditorContext with necessary initializations."""
    ctx = EditorContext()
    ctx.undo_stack = UndoStack()
    ctx.nx_graph = nx.DiGraph()
    # Mock screen if actions need it (though they shouldn't directly)
    ctx.screen = pygame.Surface((1280, 720)) 
    ctx.config = {'screen_width': 1280, 'screen_height': 720}
    return ctx

def test_add_node_action_via_button_component(context, create_mouse_event):
    """Test AddNodeAction executed via ButtonComponent click."""
    action = AddNodeAction()
    # ButtonComponent requires a rect for collision detection.
    # Position and size don't matter much if we directly call handle_event with a position inside.
    button_rect = pygame.Rect(0, 0, 100, 30)
    add_node_button = ButtonComponent(context, action, "Add Node", rect=button_rect)
    
    initial_node_count = len(context.nodes)
    
    # Simulate click on the button
    click_pos = button_rect.center
    event = create_mouse_event(pygame.MOUSEBUTTONDOWN, 1, click_pos) # Left click
    add_node_button.handle_event(event, context)
    
    assert len(context.nodes) == initial_node_count + 1
    new_node = context.nodes[-1]
    assert isinstance(new_node, Node)
    assert new_node.id is not None
    assert context.nx_graph.has_node(new_node.id)
    # Check AddNodeAction's specific placement logic (e.g., offset from origin or last node)
    # The current AddNodeAction places nodes at (50,50) or offset from last node.
    if initial_node_count == 0:
        assert new_node.x == 50 and new_node.y == 50
    else:
        # This part depends on the exact placement logic if there were prior nodes.
        # For a clean test, ensure no prior nodes or mock the last node's position.
        pass


def test_delete_all_action_via_button_component(context, create_mouse_event):
    """Test DeleteAllAction executed via ButtonComponent click."""
    # Add some nodes and connections first
    node1 = Node(id=None, title="N1", x=10, y=10)
    node2 = Node(id=None, title="N2", x=110, y=110)
    context.add_node(node1)
    context.add_node(node2)
    conn1 = Connection(start_node_id=node1.id, end_node_id=node2.id)
    context.add_connection(conn1)
    
    assert len(context.nodes) == 2
    assert len(context.connections) == 1
    assert context.nx_graph.number_of_nodes() == 2
    assert context.nx_graph.number_of_edges() == 1

    action = DeleteAllAction()
    button_rect = pygame.Rect(0, 0, 100, 30)
    delete_all_button = ButtonComponent(context, action, "Clear All", rect=button_rect)
    
    # Simulate click
    click_pos = button_rect.center
    event = create_mouse_event(pygame.MOUSEBUTTONDOWN, 1, click_pos)
    delete_all_button.handle_event(event, context)
    
    assert len(context.nodes) == 0
    assert len(context.connections) == 0
    assert context.nx_graph.number_of_nodes() == 0
    assert context.nx_graph.number_of_edges() == 0
    assert context.next_node_id == 1
    assert context.next_connection_id == 1


def test_undo_action_after_add_node_via_button(context, create_mouse_event):
    """Test UndoAction after an AddNodeAction, both via ButtonComponents."""
    # Setup buttons
    add_action = AddNodeAction()
    undo_action = UndoAction()
    add_button_rect = pygame.Rect(0, 0, 100, 30)
    undo_button_rect = pygame.Rect(110, 0, 100, 30)
    add_node_button = ButtonComponent(context, add_action, "Add", rect=add_button_rect)
    undo_button = ButtonComponent(context, undo_action, "Undo", rect=undo_button_rect)

    # 1. Add a node (Action should push to undo stack if implemented in EditorContext or Action)
    # For this test, we manually push to undo stack as Actions currently don't.
    # A more integrated test would be in test_app.py or by enhancing Actions/EditorContext.
    
    # Simulate AddNodeAction
    click_pos_add = add_button_rect.center
    event_add = create_mouse_event(pygame.MOUSEBUTTONDOWN, 1, click_pos_add)
    
    # Manually push state to undo stack BEFORE action (or action does it)
    # The current UndoStack in undo.py expects an nx_graph.
    # The UndoAction reconstructs from this graph.
    context.undo_stack.push(context.nx_graph.copy()) # Push current (empty) graph state
    
    add_node_button.handle_event(event_add, context)
    assert len(context.nodes) == 1
    node_added_id = context.nodes[0].id

    # 2. Execute UndoAction
    click_pos_undo = undo_button_rect.center
    event_undo = create_mouse_event(pygame.MOUSEBUTTONDOWN, 1, click_pos_undo)
    undo_button.handle_event(event_undo, context)
    
    assert len(context.nodes) == 0, "Node should be removed after undo"
    assert not context.nx_graph.has_node(node_added_id), "Node should be removed from nx_graph after undo"
    # Check if next_node_id was restored (depends on UndoAction's implementation)
    # Current UndoAction re-calculates next_node_id based on max existing node ID.
    assert context.next_node_id == 1, "next_node_id should be reset if no nodes remain"


def test_dump_graph_action_via_button(context, create_mouse_event, capsys):
    """Test DumpGraphAction via ButtonComponent, check stdout."""
    node1 = Node(id=None, title="N1", x=10, y=10)
    context.add_node(node1) # node1.id will be 1

    action = DumpGraphAction()
    button_rect = pygame.Rect(0, 0, 100, 30)
    dump_button = ButtonComponent(context, action, "Dump", rect=button_rect)

    click_pos = button_rect.center
    event_click = create_mouse_event(pygame.MOUSEBUTTONDOWN, 1, click_pos)
    dump_button.handle_event(event_click, context)

    captured = capsys.readouterr()
    assert "Nodes:" in captured.out
    assert f"Node {node1.id}" in captured.out # Check if node1's ID is in output
    assert "Edges:" in captured.out
    assert "======================" in captured.out

# The test_clicking_add_node_button_does_not_remove_node_selection is more complex
# as it involves NodeAreaComponent for selection state.
# That kind of interaction test is better suited for test_app.py or a dedicated
# integration test file once NodeAreaComponent's selection logic is fully integrated
# with EditorContext and actions. For now, this file focuses on actions modifying context.
