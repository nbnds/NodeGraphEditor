from node import Node # Keep for creating Node instances
from connection import Connection # Keep for creating Connection instances
from editor_context import EditorContext # For type hinting

class Action:
    def execute(self, context: EditorContext): # Changed signature
        pass  # Baseclass for actions

class NoOpAction(Action):
    def execute(self, context: EditorContext): # Changed signature
        print("No operation action executed.")
        pass

class AddNodeAction(Action):
    def execute(self, context: EditorContext): # Changed signature
        # Determine position for the new node.
        # This is a simplified approach. Ideally, NodeAreaComponent would provide its view center.
        # For now, add near origin or based on existing nodes to avoid overlap.
        # Let's find a position slightly offset from the last added node or origin.
        new_x, new_y = 50, 50
        if context.nodes:
            last_node = context.nodes[-1]
            new_x = last_node.x + last_node.width + 20 # Offset from last node
            new_y = last_node.y
        
        # Create a new Node instance. The Node class might need to accept all necessary data.
        # Assuming Node class constructor takes (id, title, x, y, width, height, color, etc.)
        # For simplicity, using a basic Node constructor.
        # The context.add_node method will handle ID assignment.
        new_node = Node(id=None, title=f"Node {context.next_node_id}", x=new_x, y=new_y)
        context.add_node(new_node) # context.add_node handles ID and nx_graph update
        print(f"AddNodeAction: Added node {new_node.id} at ({new_x}, {new_y})")

class DeleteAllAction(Action):
    def execute(self, context: EditorContext): # Changed signature
        # context needs a method to clear everything
        if hasattr(context, 'clear_all_nodes_and_connections'):
            context.clear_all_nodes_and_connections()
        else: # Fallback to manual clearing if method not yet on context
            context.nodes.clear()
            context.connections.clear()
            context.nx_graph.clear()
            context.next_node_id = 1
            context.next_connection_id = 1
        print("DeleteAllAction: Cleared all nodes and connections.")


class DumpGraphAction(Action):
    def execute(self, context: EditorContext): # Changed signature
        from networkx.readwrite import json_graph
        from pprint import pprint
        # Ensure nx_graph is not None
        if context.nx_graph is not None:
            # We need to ensure that the 'data_dict' is properly handled or removed if it causes issues
            # For now, let's try to extract relevant parts or use a simpler representation
            # pprint(json_graph.node_link_data(context.nx_graph, {"link": "links", "source": "source", "target": "target"}))
            
            # Simpler dump:
            print("Nodes:")
            for node_id, data in context.nx_graph.nodes(data=True):
                print(f"  Node {node_id}: {data.get('data_dict', data)}") # Print data_dict if exists
            print("Edges:")
            for u, v, data in context.nx_graph.edges(data=True):
                print(f"  Edge from {u} to {v}: {data.get('data_dict', data)}") # Print data_dict if exists
        else:
            print("DumpGraphAction: nx_graph is None.")
        print("======================")

class UndoAction(Action):
    def execute(self, context: EditorContext): # Changed signature
        if context.undo_stack:
            previous_state = context.undo_stack.pop() # Assuming pop returns the state
            if previous_state:
                # previous_state should ideally be a snapshot of (nodes_list, connections_list, next_node_id, next_conn_id)
                # Or, if it's just an nx_graph, we need to reconstruct nodes/connections from it.
                # This part depends heavily on what UndoStack stores.
                # For now, let's assume it stores a dict like:
                # {'nodes': [node_vars1, ...], 'connections': [conn_vars1, ...], 'next_node_id': id, ...}
                
                # If undo_stack stores nx_graph directly (as in old code):
                if hasattr(previous_state, 'nodes') and hasattr(previous_state, 'edges'): # Check if it's an nx_graph
                    context.nx_graph = previous_state
                    context.nodes.clear()
                    context.connections.clear()
                    
                    # Recreate Node objects from graph data
                    for node_id, data in context.nx_graph.nodes(data=True):
                        node_data = data.get('data_dict', data) # Use data_dict if available
                        # Ensure all necessary attributes are present in node_data or provide defaults
                        # Node constructor might need to be flexible or we reconstruct carefully
                        node = Node(id=node_id, 
                                    title=node_data.get('title', f"Node {node_id}"),
                                    x=node_data.get('x', 0), 
                                    y=node_data.get('y', 0),
                                    width=node_data.get('width', 100), # Default width
                                    height=node_data.get('height', 50)) # Default height
                        context.nodes.append(node)

                    # Recreate Connection objects
                    for u_id, v_id, data in context.nx_graph.edges(data=True):
                        conn_data = data.get('data_dict', data)
                        start_node = next((n for n in context.nodes if n.id == u_id), None)
                        end_node = next((n for n in context.nodes if n.id == v_id), None)
                        if start_node and end_node:
                            # Connection constructor might need to be flexible
                            connection = Connection(start_node_id=start_node.id, 
                                                    end_node_id=end_node.id,
                                                    id_val=conn_data.get('id')) 
                                                    # Add other params like pins if necessary
                            context.connections.append(connection)
                    
                    # Restore next_node_id (this is tricky if only graph is stored)
                    # A more robust undo would store the next_node_id as well.
                    if context.nodes:
                        context.next_node_id = max(n.id for n in context.nodes) + 1
                    else:
                        context.next_node_id = 1
                    if context.connections:
                         context.next_connection_id = max(c.id for c in context.connections if c.id is not None) + 1 if any(c.id for c in context.connections) else 1
                    else:
                        context.next_connection_id = 1

                    print("UndoAction: Restored state from nx_graph.")
                else:
                    print("UndoAction: Popped state is not a recognized graph format.")
            else:
                print("UndoAction: Undo stack is empty or popped None.")
        else:
            print("UndoAction: Undo stack not available in context or is empty.")
