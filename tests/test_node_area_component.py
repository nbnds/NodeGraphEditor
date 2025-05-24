import pytest
import pygame
import networkx as nx
from editor_context import EditorContext
from node_area_component import NodeAreaComponent
from node import Node
from connection import Connection
from undo import UndoStack
from component_registry import ComponentRegistry # For context setup

# Pygame needs to be initialized for font rendering, event processing, etc.
# conftest.py should handle pygame.init() and quit() via a fixture.

@pytest.fixture
def context_for_nac(pygame_init): # Using the pygame_init fixture from conftest.py
    """Fixture to create an EditorContext with necessary initializations for NodeAreaComponent tests."""
    ctx = EditorContext()
    ctx.undo_stack = UndoStack()
    ctx.nx_graph = nx.DiGraph()
    ctx.nodes = [] # Ensure these are initialized lists
    ctx.connections = []
    ctx.component_registry = ComponentRegistry() # NodeAreaComponent might use this (e.g. for screen_to_world if it was in context)
    
    # Mock screen and config for NodeAreaComponent if it uses them directly from context
    # For screen_to_world and world_to_screen, NodeAreaComponent uses its own state,
    # but it might need screen dimensions from context.config for other things (e.g. drawing grid).
    mock_screen = pygame.Surface((1280, 720))
    ctx.screen = mock_screen
    ctx.config = {
        'screen_width': 1280,
        'screen_height': 720,
    }
    return ctx

@pytest.fixture
def nac(context_for_nac):
    """Fixture to create a NodeAreaComponent."""
    return NodeAreaComponent(context_for_nac)

# Migrated Coordinate Transformation Tests
def test_identity_no_zoom_no_offset_nac(nac):
    """If zoom=1 and offset=0, screen and world coordinates are identical."""
    nac.zoom = 1.0
    nac.canvas_offset_x = 0.0
    nac.canvas_offset_y = 0.0
    assert nac.screen_to_world((100, 200)) == (100.0, 200.0)
    assert nac.world_to_screen((100.0, 200.0)) == (100, 200)
    assert nac.screen_to_world((0, 0)) == (0.0, 0.0)
    assert nac.world_to_screen((0.0,0.0)) == (0,0)


def test_offset_only_nac(nac):
    """If offset is set, world coordinates shift accordingly."""
    nac.zoom = 1.0
    nac.canvas_offset_x = 50.0
    nac.canvas_offset_y = 20.0
    assert nac.screen_to_world((0, 0)) == (-50.0, -20.0) # Corrected: screen_to_world subtracts offset
    assert nac.world_to_screen((-50.0, -20.0)) == (0,0)
    assert nac.screen_to_world((100, 200)) == (50.0, 180.0) # 100-50, 200-20
    assert nac.world_to_screen((50.0, 180.0)) == (100,200)


def test_zoom_functionality_nac(nac):
    """If zoom is applied, world coordinates scale accordingly."""
    nac.zoom = 2.0
    nac.canvas_offset_x = 0.0
    nac.canvas_offset_y = 0.0
    assert nac.screen_to_world((100, 200)) == (50.0, 100.0) # 100/2, 200/2
    assert nac.world_to_screen((50.0,100.0)) == (100,200)

def test_zoom_and_offset_nac(nac):
    """If both zoom and offset are set, both effects combine."""
    nac.zoom = 2.0
    nac.canvas_offset_x = 10.0 # World units
    nac.canvas_offset_y = 20.0 # World units
    # screen_to_world: (screen_x / zoom) - offset_x
    # world_to_screen: (world_x + offset_x) * zoom

    # Screen (0,0) -> World: (0/2 - 10, 0/2 - 20) = (-10, -20)
    assert nac.screen_to_world((0, 0)) == (-10.0, -20.0)
    assert nac.world_to_screen((-10.0,-20.0)) == (0,0)

    # Screen (100,200) -> World: (100/2 - 10, 200/2 - 20) = (50 - 10, 100 - 20) = (40, 80)
    assert nac.screen_to_world((100, 200)) == (40.0, 80.0)
    assert nac.world_to_screen((40.0,80.0)) == (100,200)


# New Tests for NodeAreaComponent Event Handling

def test_nac_node_selection_left_click(nac, context_for_nac, create_mouse_event):
    """Test selecting a node by left-clicking."""
    node1 = Node(id=None, title="N1", x=50, y=50, width=100, height=50) # World coords
    context_for_nac.add_node(node1)
    
    # Simulate left mouse button down on the node
    # NodeAreaComponent.get_node_at_pos uses world coordinates.
    # NodeAreaComponent.handle_event converts mouse_pos to world_mouse_pos.
    # So, we need to provide screen coordinates that map to the node's world coordinates.
    screen_pos_node = nac.world_to_screen((node1.x + 10, node1.y + 10)) # Click inside node
    
    event_down = create_mouse_event(pygame.MOUSEBUTTONDOWN, 1, screen_pos_node) # Button 1 (left)
    nac.handle_event([event_down], context_for_nac)
    
    assert nac.selection.is_node_selected(node1), "Node should be selected after click"
    assert nac.dragging_node == node1, "Node should be marked as dragging_node"

def test_nac_node_drag(nac, context_for_nac, create_mouse_event):
    """Test dragging a node."""
    node1 = Node(id=None, title="N1", x=50, y=50, width=100, height=50)
    context_for_nac.add_node(node1)
    original_x, original_y = node1.x, node1.y

    # 1. Select node (press button)
    screen_pos_start_drag = nac.world_to_screen((node1.x + 10, node1.y + 10))
    event_down = create_mouse_event(pygame.MOUSEBUTTONDOWN, 1, screen_pos_start_drag)
    nac.handle_event([event_down], context_for_nac)
    assert nac.dragging_node == node1

    # 2. Drag node (mouse motion)
    # Target screen position: e.g., move by (200, 150) screen pixels
    # Target world position will be calculated by handle_event
    screen_pos_during_drag = (screen_pos_start_drag[0] + 100, screen_pos_start_drag[1] + 50)
    world_pos_during_drag = nac.screen_to_world(screen_pos_during_drag)
    
    event_motion = create_mouse_event(pygame.MOUSEMOTION, pos=screen_pos_during_drag, buttons=(1,0,0)) # Left button held
    nac.handle_event([event_motion], context_for_nac)
    
    # Node's x, y should be updated based on world_mouse_pos - drag_offset
    # drag_offset was (world_mouse_pos_initial[0] - node_clicked.x, world_mouse_pos_initial[1] - node_clicked.y)
    # So, node_clicked.x = world_mouse_pos[0] - drag_offset[0]
    expected_node_x = world_pos_during_drag[0] - nac.drag_offset[0]
    expected_node_y = world_pos_during_drag[1] - nac.drag_offset[1]

    assert node1.x == pytest.approx(expected_node_x)
    assert node1.y == pytest.approx(expected_node_y)
    assert (node1.x != original_x or node1.y != original_y)

    # 3. Release node (button up)
    event_up = create_mouse_event(pygame.MOUSEBUTTONUP, 1, screen_pos_during_drag)
    nac.handle_event([event_up], context_for_nac)
    assert nac.dragging_node is None, "Node should not be dragging after mouse up"


def test_nac_connection_creation(nac, context_for_nac, create_mouse_event):
    """Test creating a connection between two nodes."""
    node1 = Node(id=None, title="N1", x=50, y=50, width=100, height=50)
    node2 = Node(id=None, title="N2", x=250, y=150, width=100, height=50)
    context_for_nac.add_node(node1)
    context_for_nac.add_node(node2)

    # 1. Start connection (right mouse button down on node1)
    screen_pos_node1 = nac.world_to_screen((node1.x + 10, node1.y + 10))
    event_down_n1 = create_mouse_event(pygame.MOUSEBUTTONDOWN, 3, screen_pos_node1) # Button 3 (right)
    nac.handle_event([event_down_n1], context_for_nac)
    
    assert nac.dragging_connection is True
    assert nac.connection_start_node == node1

    # 2. Drag connection line (mouse motion)
    screen_pos_drag_conn = nac.world_to_screen((150, 100)) # Some arbitrary point
    event_motion_conn = create_mouse_event(pygame.MOUSEMOTION, pos=screen_pos_drag_conn, buttons=(0,0,1)) # Right button held
    nac.handle_event([event_motion_conn], context_for_nac)
    assert nac.connection_end_pos == nac.screen_to_world(screen_pos_drag_conn)

    # 3. End connection (right mouse button up on node2)
    screen_pos_node2 = nac.world_to_screen((node2.x + 10, node2.y + 10))
    event_up_n2 = create_mouse_event(pygame.MOUSEBUTTONUP, 3, screen_pos_node2)
    nac.handle_event([event_up_n2], context_for_nac)

    assert nac.dragging_connection is False
    assert nac.connection_start_node is None
    assert len(context_for_nac.connections) == 1
    new_connection = context_for_nac.connections[0]
    assert new_connection.start_node_id == node1.id
    assert new_connection.end_node_id == node2.id
    assert context_for_nac.nx_graph.has_edge(node1.id, node2.id)


def test_nac_panning_middle_mouse(nac, context_for_nac, create_mouse_event):
    """Test panning the canvas using the middle mouse button."""
    initial_offset_x, initial_offset_y = nac.canvas_offset_x, nac.canvas_offset_y
    
    # 1. Start panning (middle mouse button down)
    pan_start_screen_pos = (100, 100)
    event_down_pan = create_mouse_event(pygame.MOUSEBUTTONDOWN, 2, pan_start_screen_pos) # Button 2 (middle)
    nac.handle_event([event_down_pan], context_for_nac)
    
    assert nac.panning is True
    assert nac.pan_start == pan_start_screen_pos
    assert nac.pan_offset_start == (initial_offset_x, initial_offset_y)

    # 2. Drag mouse (mouse motion)
    pan_current_screen_pos = (200, 150) # Moved by (100, 50) screen pixels
    event_motion_pan = create_mouse_event(pygame.MOUSEMOTION, pos=pan_current_screen_pos, buttons=(0,1,0)) # Middle button held
    nac.handle_event([event_motion_pan], context_for_nac)
    
    # Expected change in offset: dx_screen / zoom, dy_screen / zoom
    # nac.canvas_offset_x = self.pan_offset_start[0] + dx_screen / self.zoom
    dx_screen = pan_current_screen_pos[0] - pan_start_screen_pos[0] # 100
    dy_screen = pan_current_screen_pos[1] - pan_start_screen_pos[1] # 50
    
    expected_offset_x = initial_offset_x + (dx_screen / nac.zoom)
    expected_offset_y = initial_offset_y + (dy_screen / nac.zoom)
    
    assert nac.canvas_offset_x == pytest.approx(expected_offset_x)
    assert nac.canvas_offset_y == pytest.approx(expected_offset_y)

    # 3. Stop panning (middle mouse button up)
    event_up_pan = create_mouse_event(pygame.MOUSEBUTTONUP, 2, pan_current_screen_pos)
    nac.handle_event([event_up_pan], context_for_nac)
    assert nac.panning is False

def test_nac_zooming_mouse_wheel(nac, context_for_nac, create_mouse_event):
    """Test zooming the canvas using the mouse wheel."""
    initial_zoom = nac.zoom
    initial_offset_x, initial_offset_y = nac.canvas_offset_x, nac.canvas_offset_y
    mouse_pos_screen = (context_for_nac.config['screen_width'] // 2, context_for_nac.config['screen_height'] // 2) # Zoom towards center

    # Simulate mouse wheel scroll up (zoom in)
    event_wheel_zoom_in = create_mouse_event(pygame.MOUSEWHEEL, y=1, pos=mouse_pos_screen) # y=1 for scroll up
    world_pos_before_zoom_in = nac.screen_to_world(mouse_pos_screen)
    nac.handle_event([event_wheel_zoom_in], context_for_nac)
    
    assert nac.zoom > initial_zoom
    # Check that the point under the mouse remains the same in world coordinates (or close to it)
    world_pos_after_zoom_in = nac.screen_to_world(mouse_pos_screen)
    assert world_pos_before_zoom_in[0] == pytest.approx(world_pos_after_zoom_in[0])
    assert world_pos_before_zoom_in[1] == pytest.approx(world_pos_after_zoom_in[1])

    # Simulate mouse wheel scroll down (zoom out)
    current_zoom = nac.zoom
    event_wheel_zoom_out = create_mouse_event(pygame.MOUSEWHEEL, y=-1, pos=mouse_pos_screen) # y=-1 for scroll down
    world_pos_before_zoom_out = nac.screen_to_world(mouse_pos_screen)
    nac.handle_event([event_wheel_zoom_out], context_for_nac)

    assert nac.zoom < current_zoom
    world_pos_after_zoom_out = nac.screen_to_world(mouse_pos_screen)
    assert world_pos_before_zoom_out[0] == pytest.approx(world_pos_after_zoom_out[0])
    assert world_pos_before_zoom_out[1] == pytest.approx(world_pos_after_zoom_out[1])


def test_nac_delete_node_with_del_key(nac, context_for_nac, create_key_event):
    """Test deleting a selected node using the DELETE key."""
    node1 = Node(id=None, title="N1", x=50, y=50)
    context_for_nac.add_node(node1)
    node1_id = node1.id
    
    # Select the node first (simulating a click or selection rect)
    nac.selection.select_node(node1, False) # select_node(node, is_shift_held)
    assert nac.selection.is_node_selected(node1)

    event_del_key = create_key_event(pygame.KEYDOWN, pygame.K_DELETE)
    nac.handle_event([event_del_key], context_for_nac)

    assert node1 not in context_for_nac.nodes
    assert node1_id not in context_for_nac.nx_graph
    assert not nac.selection.get_selected_nodes() # Selection should be cleared
```
