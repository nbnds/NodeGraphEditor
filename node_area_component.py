import pygame
from typing import List
import pygame
from uicomponent import UIComponent
from node import Node # Assuming Node class is defined in node.py
from connection import Connection # Assuming Connection class is defined in connection.py
from editor_context import EditorContext
from selection import NodeSelection # Import NodeSelection

class NodeAreaComponent(UIComponent):
    """
    Manages the node editing area, including nodes, connections, panning, and zooming.
    """

    def __init__(self, context: EditorContext):
        """
        Initializes the NodeAreaComponent.
        """
        self.context = context
        # self.nodes and self.connections are now primarily managed by self.context
        self.canvas_offset_x = 0.0
        self.canvas_offset_y = 0.0
        self.zoom = 1.0
        self.panning = False
        self.pan_start = (0, 0)
        self.pan_offset_start = (0.0, 0.0) # Stores the canvas_offset when panning starts
        # self.next_node_id is now managed by EditorContext

        # Selection and interaction state
        self.selection = NodeSelection()
        self.dragging_node = None # Stores the node being dragged
        self.drag_offset = (0, 0) # Offset from mouse to node's top-left during drag
        self.dragging_connection = False
        self.connection_start_node = None # Node where connection starts
        self.connection_start_pin = None # Pin where connection starts (if applicable)
        self.connection_end_pos = (0, 0) # Mouse position for drawing pending connection

        # UI attributes from NodeEditor relevant to this component
        self.grid_size = 20
        self.background_color = (30, 30, 30)
        self.grid_color = (50, 50, 50)
        # ... any other relevant attributes from NodeEditor ...

    # screen_to_world and world_to_screen are now in EditorContext,
    # but NodeAreaComponent needs them frequently for its own logic.
    # It's more direct to keep local versions that use its own state (zoom, offset).
    def screen_to_world(self, screen_pos: tuple[int, int]) -> tuple[float, float]:
        """Converts screen coordinates to world coordinates specific to this component's view."""
        return (screen_pos[0] / self.zoom - self.canvas_offset_x,
                screen_pos[1] / self.zoom - self.canvas_offset_y)

    def world_to_screen(self, world_pos: tuple[float, float]) -> tuple[int, int]:
        """Converts world coordinates to screen coordinates specific to this component's view."""
        return (int((world_pos[0] + self.canvas_offset_x) * self.zoom),
                int((world_pos[1] + self.canvas_offset_y) * self.zoom))

    def handle_event(self, events, context: EditorContext):
        """
        Handles events for the node area (panning, zooming, node interaction).
        Migrates logic from NodeEditor.dispatch_event and related handlers.
        """
        for event in events: # events is now a list of all Pygame events
            mouse_pos = pygame.mouse.get_pos()
            world_mouse_pos = self.screen_to_world(mouse_pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Panning Start (Middle Mouse)
                if event.button == 2:
                    self.panning = True
                    self.pan_start = mouse_pos
                    self.pan_offset_start = (self.canvas_offset_x, self.canvas_offset_y)
                
                # Node interaction (Left Mouse)
                elif event.button == 1:
                    node_clicked = self.get_node_at_pos(world_mouse_pos) # Helper method needed
                    if node_clicked:
                        self.dragging_node = node_clicked
                        self.drag_offset = (world_mouse_pos[0] - node_clicked.x, 
                                            world_mouse_pos[1] - node_clicked.y)
                        if not self.selection.is_node_selected(node_clicked): # Helper method needed in NodeSelection
                            self.selection.select_node(node_clicked, pygame.key.get_mods() & pygame.KMOD_SHIFT) # Helper method needed
                    else:
                        # Start selection rect if no node is clicked
                        self.selection.begin(world_mouse_pos) # NodeSelection.begin should take world coords
                
                # Connection Start (Right Mouse - assuming original logic) / Delete Node (Middle Mouse on Node)
                elif event.button == 3: # Right mouse button
                    node_clicked = self.get_node_at_pos(world_mouse_pos)
                    if node_clicked:
                        # Check if clicked on an output pin (requires pin logic in Node class)
                        # For now, assume connection starts from node center
                        self.dragging_connection = True
                        self.connection_start_node = node_clicked
                        self.connection_end_pos = world_mouse_pos
                    # else:
                        # Context menu logic could go here

            elif event.type == pygame.MOUSEBUTTONUP:
                # Panning End
                if event.button == 2 and self.panning:
                    self.panning = False
                
                # Node Dragging End / Selection Rect End
                elif event.button == 1:
                    if self.dragging_node:
                        # TODO: Record undo action for node move
                        # context.undo_stack.push({'action': 'move_node', 'node_id': self.dragging_node.id, 'old_pos': old_pos, 'new_pos': (self.dragging_node.x, self.dragging_node.y)})
                        self.dragging_node = None
                    elif self.selection.is_active():
                        self.selection.finish(context.nodes, self.canvas_offset_x, self.canvas_offset_y, self.zoom)
                        # The selection.finish() in selection.py needs to be adapted to use world coords
                        # or this component needs to convert its rect to screen for that method.
                        # For now, assume selection.finish() can take world_coords for rect_start/end
                        # and iterate through context.nodes.

                # Connection End / Delete Logic
                elif event.button == 3: # Right mouse button
                    if self.dragging_connection:
                        end_node = self.get_node_at_pos(world_mouse_pos)
                        if end_node and end_node != self.connection_start_node:
                            # Check for pin clicked (if applicable)
                            # Ensure not connecting to self if disallowed, or input to input etc.
                            context.add_connection(self.connection_start_node.id, end_node.id)
                        self.dragging_connection = False
                        self.connection_start_node = None
                        self.connection_end_pos = None


            elif event.type == pygame.MOUSEMOTION:
                if self.panning:
                    current_mouse_pos = mouse_pos
                    dx = (current_mouse_pos[0] - self.pan_start[0]) # Screen space delta
                    dy = (current_mouse_pos[1] - self.pan_start[1]) # Screen space delta
                    self.canvas_offset_x = self.pan_offset_start[0] + dx / self.zoom
                    self.canvas_offset_y = self.pan_offset_start[1] + dy / self.zoom
                elif self.dragging_node:
                    self.dragging_node.x = world_mouse_pos[0] - self.drag_offset[0]
                    self.dragging_node.y = world_mouse_pos[1] - self.drag_offset[1]
                    # TODO: Update positions of connected connections if node is dragged
                elif self.dragging_connection:
                    self.connection_end_pos = world_mouse_pos
                elif self.selection.is_active():
                    self.selection.update(world_mouse_pos) # NodeSelection.update should take world_coords

            elif event.type == pygame.MOUSEWHEEL:
                # Zooming logic (already good, uses self.screen_to_world)
                world_pos_before_zoom = self.screen_to_world(mouse_pos)
                if event.y > 0: self.zoom *= 1.1
                else: self.zoom /= 1.1
                self.zoom = max(0.1, min(self.zoom, 3.0))
                world_pos_after_zoom = self.screen_to_world(mouse_pos)
                self.canvas_offset_x += (world_pos_before_zoom[0] - world_pos_after_zoom[0])
                self.canvas_offset_y += (world_pos_before_zoom[1] - world_pos_after_zoom[1])

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    # Delete selected nodes
                    # Create a copy for iteration as items will be removed
                    selected_nodes_copy = list(self.selection.get_selected_nodes()) # Helper in NodeSelection needed
                    for node in selected_nodes_copy:
                        self.try_delete_node(node.id, context) # try_delete_node to be implemented
                    self.selection.clear()
                # Add other KEYDOWN events (e.g., Ctrl+A to select all)

    def update(self, dt, context: EditorContext):
        """
        Updates the state of the node area.
        (Placeholder for now, might include animations or other time-based updates)
        """
        # For now, node and connection updates are mostly event-driven or handled by context
        pass

    def get_node_at_pos(self, world_pos: tuple[float, float]) -> Node | None:
        """Returns the node at the given world position, if any."""
        for node in reversed(self.context.nodes): # Draw top nodes first, so check them first
            if node.get_rect().collidepoint(world_pos): # Node.get_rect() needs to return world coords rect
                # Further check if over a pin for connection logic might be needed here or in Node
                return node
        return None

    def try_delete_node(self, node_id: int, context: EditorContext):
        """Attempts to delete a node and its connections, pushing to undo stack."""
        # TODO: Push to undo stack: context.undo_stack.push(...)
        # This should include the node itself and any connected connections.
        # Store enough info to recreate them.
        
        # Connections to remove (from context.connections and nx_graph)
        connections_to_remove = [
            conn for conn in context.connections 
            if conn.start_node_id == node_id or conn.end_node_id == node_id
        ]
        for conn in connections_to_remove:
            context.remove_connection(conn.start_node_id, conn.end_node_id, conn.id) # Assuming Connection has an id

        # Remove node (from context.nodes and nx_graph)
        context.remove_node(node_id)


    def try_delete_connection(self, connection_id: int, context: EditorContext): # Or pass start/end node_ids
        """Attempts to delete a specific connection."""
        # TODO: Push to undo stack
        # Find connection by ID or by start/end nodes
        # context.remove_connection(start_node_id, end_node_id)
        pass # Placeholder


    def draw_grid(self, screen, context: EditorContext):
        """Draws the background grid."""
        screen_width = context.config.get('screen_width', screen.get_width())
        screen_height = context.config.get('screen_height', screen.get_height())

        # Adjust grid start based on canvas offset and zoom
        # These are screen coordinates for drawing
        world_top_left_x = -self.canvas_offset_x
        world_top_left_y = -self.canvas_offset_y
        
        screen_top_left_x, screen_top_left_y = self.world_to_screen((world_top_left_x, world_top_left_y))

        # Calculate the effective grid size on screen
        effective_grid_size = self.grid_size * self.zoom

        # Ensure we don't try to draw if grid lines are too far apart or too close
        if effective_grid_size < 5: return # Too dense
        if effective_grid_size > min(screen_width, screen_height) * 5: return # Too sparse

        # Offset for drawing lines to align with the origin (0,0) of the world space
        # This is the screen x-coordinate of the first grid line that should be drawn
        # It's the remainder of the screen position of (0,0) world, divided by effective_grid_size
        offset_x = screen_top_left_x % effective_grid_size
        offset_y = screen_top_left_y % effective_grid_size


        for x in range(int(offset_x - effective_grid_size), screen_width + int(effective_grid_size), int(effective_grid_size)):
             if x >= 0 and x <= screen_width : # Draw only visible lines
                pygame.draw.line(screen, self.grid_color, (x, 0), (x, screen_height))
        for y in range(int(offset_y - effective_grid_size), screen_height + int(effective_grid_size), int(effective_grid_size)):
            if y >=0 and y <= screen_height: # Draw only visible lines
                pygame.draw.line(screen, self.grid_color, (0, y), (screen_width, y))


    def draw_nodes(self, screen, context: EditorContext):
        """Draws the nodes onto the screen."""
        for node in context.nodes: # Iterate through nodes from context
            # Node.draw() method should handle its own drawing at its position,
            # taking zoom and selection state into account.
            # It will need to convert its world position to screen position.
            # node.draw(screen, self.zoom, self.world_to_screen, self.selection.is_node_selected(node))
            
            # Placeholder drawing until Node.draw() is fleshed out:
            node_rect_world = node.get_rect() # Assuming Node.get_rect() returns world coords rect
            
            # Convert world rect to screen rect for drawing
            screen_x, screen_y = self.world_to_screen((node_rect_world.x, node_rect_world.y))
            screen_width = int(node_rect_world.width * self.zoom)
            screen_height = int(node_rect_world.height * self.zoom)
            
            node_screen_rect = pygame.Rect(screen_x, screen_y, screen_width, screen_height)

            # Basic node representation
            border_color = (255, 0, 0) if self.selection.is_node_selected(node) else node.border_color
            pygame.draw.rect(screen, node.color, node_screen_rect)
            pygame.draw.rect(screen, border_color, node_screen_rect, node.border_width)
            
            # Draw node title (simplified)
            font = pygame.font.SysFont(None, int(20 * self.zoom)) # Adjust font size with zoom
            text_surface = font.render(node.title, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=node_screen_rect.center)
            screen.blit(text_surface, text_rect)
            # Pins would also be drawn here, relative to the node's screen position.


    def draw_connections(self, screen, context: EditorContext):
        """Draws the connections between nodes."""
        for connection in context.connections: # Iterate through connections from context
            # Connection.draw() method would be ideal.
            # It would get start/end node positions from context.nodes or node IDs.
            # connection.draw(screen, self.zoom, self.world_to_screen, context)
            
            # Placeholder drawing:
            start_node = next((n for n in context.nodes if n.id == connection.start_node_id), None)
            end_node = next((n for n in context.nodes if n.id == connection.end_node_id), None)

            if start_node and end_node:
                # For simplicity, connect centers. Ideally, connect pins.
                start_pos_world = start_node.get_rect().center
                end_pos_world = end_node.get_rect().center
                
                start_pos_screen = self.world_to_screen(start_pos_world)
                end_pos_screen = self.world_to_screen(end_pos_world)
                
                pygame.draw.line(screen, connection.color, start_pos_screen, end_pos_screen, connection.thickness)

        # Draw pending connection
        if self.dragging_connection and self.connection_start_node:
            start_node_rect = self.connection_start_node.get_rect() # World coords
            # Assume connection starts from node center for now
            start_pos_screen = self.world_to_screen(start_node_rect.center)
            # self.connection_end_pos is already in world coordinates from MOUSEMOTION
            end_pos_screen = self.world_to_screen(self.connection_end_pos)
            pygame.draw.line(screen, (200, 200, 200), start_pos_screen, end_pos_screen, 2)


    def draw_selection_rect(self, screen):
        """Draws the selection rectangle if active."""
        if self.selection.is_active() and self.selection.rect_start and self.selection.rect_end:
            # rect_start and rect_end are in world coordinates
            rect_start_screen = self.world_to_screen(self.selection.rect_start)
            rect_end_screen = self.world_to_screen(self.selection.rect_end)
            
            rect = pygame.Rect(min(rect_start_screen[0], rect_end_screen[0]),
                               min(rect_start_screen[1], rect_end_screen[1]),
                               abs(rect_start_screen[0] - rect_end_screen[0]),
                               abs(rect_start_screen[1] - rect_end_screen[1]))
            # Use a semi-transparent color for the selection rectangle
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            s.fill((100, 100, 255, 100))  # RGBA for transparency
            screen.blit(s, rect.topleft)
            pygame.draw.rect(screen, (150, 150, 255), rect, 1) # Border for the rect


    def draw_offscreen_indicators(self, screen, context: EditorContext):
        """Draws indicators for off-screen nodes."""
        screen_width = context.config.get('screen_width', screen.get_width())
        screen_height = context.config.get('screen_height', screen.get_height())
        indicator_size = 10
        padding = 5

        for node in context.nodes:
            node_rect_world = node.get_rect()
            node_center_screen = self.world_to_screen(node_rect_world.center)

            indicator_pos = list(node_center_screen)
            is_offscreen = False

            if node_center_screen[0] < 0:
                indicator_pos[0] = padding
                is_offscreen = True
            elif node_center_screen[0] > screen_width:
                indicator_pos[0] = screen_width - indicator_size - padding
                is_offscreen = True
            
            if node_center_screen[1] < 0:
                indicator_pos[1] = padding
                is_offscreen = True
            elif node_center_screen[1] > screen_height:
                indicator_pos[1] = screen_height - indicator_size - padding
                is_offscreen = True

            if is_offscreen:
                # Clamp indicator position to be fully visible
                indicator_pos[0] = max(padding, min(indicator_pos[0], screen_width - indicator_size - padding))
                indicator_pos[1] = max(padding, min(indicator_pos[1], screen_height - indicator_size - padding))
                
                pygame.draw.circle(screen, node.color, (int(indicator_pos[0] + indicator_size / 2), int(indicator_pos[1] + indicator_size / 2)), int(indicator_size / 2))


    def draw(self, screen, context: EditorContext):
        """
        Draws the node area (grid, nodes, connections, selection rectangle).
        """
        # screen.fill(self.background_color) # App.py fills the whole screen
        self.draw_grid(screen, context)
        self.draw_connections(screen, context) 
        self.draw_nodes(screen, context)
        self.draw_offscreen_indicators(screen, context)
        self.draw_selection_rect(screen) # Draw selection rectangle last
        
    # TODO: Add helper methods:
    # - get_node_at_pos (already added a basic version)
    # - Methods for handling pin interactions if applicable
    # - Methods for creating nodes (e.g., context.add_node(...)) that might be called by actions
    #   Example: def create_new_node(self, type, position_world):
    #                node_data = {'type': type, 'pos': position_world, ...}
    #                self.context.add_node(node_data)
