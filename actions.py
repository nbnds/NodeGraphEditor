from node import Node
from connection import Connection
class Action:
    def execute(self, editor=None):
        pass  # Baseclass for actions

class NoOpAction(Action):
    def execute(self, editor):
        print("No operation action executed.")
        pass  #  No operation action

class AddNodeAction(Action):
    def execute(self, editor):
        center_x = editor.screen.get_width() // 2
        center_y = editor.screen.get_height() // 2
        world_x = (center_x + editor.canvas_offset_x * editor.zoom) / editor.zoom
        world_y = (center_y + editor.canvas_offset_y * editor.zoom) / editor.zoom
        editor.nodes.append(Node(world_x, world_y, editor.next_node_id))
        editor.nx_graph.add_node(editor.next_node_id, pos=(world_x, world_y))
        editor.next_node_id += 1

class DeleteAllAction(Action):
    def execute(self, editor):
        editor.nodes.clear()
        editor.connections.clear()
        editor.nx_graph.clear()
        editor.next_node_id = 1
        editor.selected_node = None

class DumpGraphAction(Action):
    def execute(self, editor):
        from networkx.readwrite import json_graph
        from pprint import pprint
        pprint(json_graph.node_link_data(editor.nx_graph, edges="edges"))
        print("======================")

class UndoAction(Action):
    def execute(self, editor):
        prev_graph = editor.undo_stack.pop()
        if prev_graph:
            # Restore the previous graph state
            editor.nx_graph = prev_graph
            # Synchronize nodes and connections
            editor.nodes.clear()
            editor.connections.clear()
            for node_id, data in editor.nx_graph.nodes(data=True):
                pos = data.get('pos', (0, 0))
                editor.nodes.append(Node(pos[0], pos[1], node_id))
            for start, end in editor.nx_graph.edges():
                start_node = next(n for n in editor.nodes if n.id == start)
                end_node = next(n for n in editor.nodes if n.id == end)
                editor.connections.append(Connection(start_node, end_node))
