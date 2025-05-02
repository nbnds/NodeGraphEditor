from collections import deque
import copy

class UndoStack:
    def __init__(self, max_depth=10):
        self.stack = deque(maxlen=max_depth)

    def push(self, nx_graph):
        # Speichere eine tiefe Kopie des Graphen
        self.stack.append(copy.deepcopy(nx_graph))

    def pop(self):
        if self.stack:
            return self.stack.pop()
        return None

    def clear(self):
        self.stack.clear()