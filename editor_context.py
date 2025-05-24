class EditorContext:
    """
    Manages the editor state and provides access to shared resources.
    """

    def __init__(self):
        """
        Initializes the editor context with default values.
        """
        self.screen = None
        self.undo_stack = None
        self.nx_graph = None # Should be initialized as nx.DiGraph() in App
        self.component_registry = None
        self.config = {}
        self.nodes = [] # List of Node objects
        self.connections = [] # List of Connection objects
        self.next_node_id = 1
        self.next_connection_id = 1 # If connections need unique IDs

        # The screen_to_world and world_to_screen methods that were here
        # are better placed in NodeAreaComponent as they depend on its specific
        # zoom and offset state. If other components need this functionality,
        # they should either have their own view parameters or query NodeAreaComponent.

    def add_node(self, node_instance):
        """
        Adds a pre-created Node object to the editor.
        Manages node ID if not already set.
        """
        if node_instance.id is None: # Assign ID if node doesn't have one
            node_instance.id = self.next_node_id
        self.next_node_id = max(self.next_node_id, node_instance.id + 1)

        if node_instance not in self.nodes:
            self.nodes.append(node_instance)
            self.nx_graph.add_node(node_instance.id, data_dict=vars(node_instance)) # Store node data
            
            # TODO: Undo Stack Integration
            # self.undo_stack.push({'action': 'add_node', 'node_id': node_instance.id, 'data': vars(node_instance)})
        return node_instance


    def remove_node(self, node_id):
        """
        Removes a node from the graph and context lists.
        Also removes associated connections.
        """
        node_to_remove = next((n for n in self.nodes if n.id == node_id), None)
        if not node_to_remove:
            return

        # TODO: Undo Stack Integration - Save node and its connections
        # original_node_data = vars(node_to_remove).copy()
        # removed_connections_data = []

        # Remove associated connections first
        conns_to_remove = [c for c in self.connections if c.start_node_id == node_id or c.end_node_id == node_id]
        for conn in conns_to_remove:
            # removed_connections_data.append(vars(conn).copy())
            self.remove_connection(conn.start_node_id, conn.end_node_id, conn.id, record_undo=False) # Avoid double undo

        self.nodes.remove(node_to_remove)
        if self.nx_graph.has_node(node_id):
            self.nx_graph.remove_node(node_id)

        # TODO: Undo Stack
        # self.undo_stack.push({
        #     'action': 'remove_node', 
        #     'node_id': node_id, 
        #     'node_data': original_node_data,
        #     'connections_data': removed_connections_data 
        # })


    def add_connection(self, connection_instance):
        """
        Adds a pre-created Connection object to the editor.
        Manages connection ID if not already set.
        """
        if connection_instance.id is None:
            connection_instance.id = self.next_connection_id
        self.next_connection_id = max(self.next_connection_id, connection_instance.id + 1)

        # Prevent duplicate connections (optional, based on requirements)
        existing = next((c for c in self.connections if c.start_node_id == connection_instance.start_node_id and \
                         c.end_node_id == connection_instance.end_node_id and \
                         c.start_pin_id == connection_instance.start_pin_id and \
                         c.end_pin_id == connection_instance.end_pin_id), None)
        if existing:
            return existing # Or raise error, or ignore

        if connection_instance not in self.connections:
            # Ensure nodes exist before adding connection
            start_node_exists = any(n.id == connection_instance.start_node_id for n in self.nodes)
            end_node_exists = any(n.id == connection_instance.end_node_id for n in self.nodes)

            if start_node_exists and end_node_exists:
                self.connections.append(connection_instance)
                self.nx_graph.add_edge(connection_instance.start_node_id, connection_instance.end_node_id, data_dict=vars(connection_instance))
                # TODO: Undo Stack
                # self.undo_stack.push({'action': 'add_connection', 'connection_id': connection_instance.id, 'data': vars(connection_instance)})
            else:
                print(f"Error: Cannot add connection. Node(s) not found: {connection_instance.start_node_id} or {connection_instance.end_node_id}")
        return connection_instance


    def remove_connection(self, start_node_id_or_conn_id, end_node_id=None, connection_id_val=None, record_undo=True):
        """
        Removes a connection from the graph and context lists.
        Can be called with connection_id OR (start_node_id and end_node_id).
        If removing multiple connections due to node removal, set record_undo=False for those.
        """
        conn_to_remove = None
        if connection_id_val is not None:
            conn_to_remove = next((c for c in self.connections if c.id == connection_id_val), None)
        elif start_node_id_or_conn_id is not None and end_node_id is not None:
            # This might remove multiple if pins are not considered, or ambiguous.
            # For simplicity, assumes one connection between two nodes if no ID.
            # Best to use connection_id_val if available.
            conn_to_remove = next((c for c in self.connections if c.start_node_id == start_node_id_or_conn_id and c.end_node_id == end_node_id), None)
        
        if conn_to_remove:
            # TODO: Undo Stack
            # if record_undo:
            #     self.undo_stack.push({'action': 'remove_connection', 'connection_id': conn_to_remove.id, 'data': vars(conn_to_remove).copy()})
            
            self.connections.remove(conn_to_remove)
            if self.nx_graph.has_edge(conn_to_remove.start_node_id, conn_to_remove.end_node_id):
                # In NetworkX, multiple edges can exist between nodes.
                # If using a MultiDiGraph, need to specify which edge. For DiGraph, this is simpler.
                self.nx_graph.remove_edge(conn_to_remove.start_node_id, conn_to_remove.end_node_id)
        else:
            print(f"Error: Connection not found for removal.")

    def clear_all_nodes_and_connections(self):
        """
        Clears all nodes and connections from the editor.
        Resets node and connection ID counters.
        """
        self.nodes.clear()
        self.connections.clear()
        if self.nx_graph:
            self.nx_graph.clear()
        self.next_node_id = 1
        self.next_connection_id = 1
        # TODO: Consider adding a "clear_all" event to the undo stack if needed
        print("EditorContext: Cleared all nodes and connections.")
