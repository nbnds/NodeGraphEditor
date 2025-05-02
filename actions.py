from node import Node

class Action:
    def execute(self, editor=None):
        pass  # Basisklasse für Aktionen, die von Buttons ausgeführt werden

class NoOpAction(Action):
    def execute(self, editor):
        print("No operation action executed.")
        pass  # Keine Aktion, wenn kein Button gedrückt wird

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
        pprint(json_graph.node_link_data(editor.nx_graph))
        print("======================")