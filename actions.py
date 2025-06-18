from node import Node
import copy

class Action:
    def execute(self, editor):
        pass  # Baseclass for actions

class NoOpAction(Action):
    def execute(self, editor):
        print("No operation action executed.")
        pass  #  No operation action

class AddNodeAction(Action):
    def execute(self, editor):
        editor._sync_node_names_to_graph()
        editor.undo_stack.push(copy.deepcopy(editor.nx_graph))
        center_x = editor.screen.get_width() // 2
        center_y = editor.screen.get_height() // 2
        world_x = (center_x + editor.panning_state.offset_x * editor.zoom) / editor.zoom
        world_y = (center_y + editor.panning_state.offset_y * editor.zoom) / editor.zoom
        node = Node(world_x, world_y, editor.next_node_id)
        editor.nodes.append(node)
        editor.nx_graph.add_node(editor.next_node_id,name=node.node_name, pos=(world_x, world_y))
        editor.next_node_id += 1

class DeleteAllAction(Action):
    def execute(self, editor):
        # Clear the undo stack so clear all cannot be undone
        editor.undo_stack.clear()
        editor.nodes.clear()
        editor.connections.clear()
        editor.nx_graph.clear()
        editor.next_node_id = 1
        editor.selected_node = None

class DumpGraphAction(Action):
    def execute(self, editor):
        print("=== Current Graph Model ===")
        print(editor.nx_graph)
        print("=== Undo Stack (most recent last) ===")
        for i, g in enumerate(editor.undo_stack.stack):
            print(f"UndoStack[{i}]: {g}")
        print("======================")

class UndoAction(Action):
    def execute(self, editor):
        editor.undo()

class SaveGraphAction(Action):
    def execute(self, editor):
        editor.save_graph()

class LoadGraphAction(Action):
    def execute(self, editor):
        editor.load_graph()
