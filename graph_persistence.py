import os
import pickle
from connection import Connection
from node import Node

class GraphPersistence:
    def __init__(self, editor):
        self.editor = editor

    def save_graph(self, filename="graph.gpickle"):
        with open(filename, "wb") as f:
            pickle.dump(self.editor.nx_graph, f)

    def load_graph(self, filename="graph.gpickle"):
        if not os.path.exists(filename):
            print(f"File {filename} does not exist.")
            return
        with open(filename, "rb") as f:
            self.editor.nx_graph = pickle.load(f)
        # Rebuild self.nodes and self.connections from nx_graph
        self.editor.nodes.clear()
        self.editor.connections.clear()
        id_to_node = {}
        used_ids = set()
        # Recreate nodes, resolve id collisions
        for orig_id, data in self.editor.nx_graph.nodes(data=True):
            x, y = data.get('pos', (0, 0))
            node_id = orig_id
            while node_id in used_ids:
                node_id += 1
            used_ids.add(node_id)
            node = Node(x, y, node_id)
            node.node_name = data.get('name', node.node_name)
            id_to_node[orig_id] = node  # map original id to new node
            self.editor.nodes.append(node)
            # Ensure nx_graph node id matches node.id
            if node_id != orig_id:
                self.editor.nx_graph.remove_node(orig_id)
                self.editor.nx_graph.add_node(node_id, **data)
        # After remapping nodes:
        old_to_new_id = {orig_id: node.id for orig_id, node in id_to_node.items()}

        # Collect all edges and their data
        edges = list(self.editor.nx_graph.edges(data=True))
        self.editor.nx_graph.clear_edges()  # Remove all edges

        # Re-add edges with remapped node IDs
        for u, v, data in edges:
            new_u = old_to_new_id.get(u, u)
            new_v = old_to_new_id.get(v, v)
            self.editor.nx_graph.add_edge(new_u, new_v, **data)
        # Recreate connections
        for u, v, data in list(self.editor.nx_graph.edges(data=True)):
            if u in id_to_node and v in id_to_node:
                label = data.get('label', "")
                conn = Connection(id_to_node[u], id_to_node[v], label=label)
                self.editor.connections.append(conn)
        # Set next_node_id to one higher than the highest used id
        self.editor.next_node_id = max([n.id for n in self.editor.nodes], default=0) + 1
        # Reset selection and drag state
        self.editor.selection.clear_selection(self.editor.nodes)
        self.editor.marked_connection = None
        self.editor._node_drag_in_progress = False
