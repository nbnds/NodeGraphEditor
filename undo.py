from collections import deque
import copy

class UndoStack:
    def __init__(self, max_depth=10):
        self.stack = deque(maxlen=max_depth)

    def push(self, nx_graph):
        # Save a deep copy of the graph to avoid modifying the original
        self.stack.append(copy.deepcopy(nx_graph))

    def pop(self):
        if self.stack:
            return self.stack.pop()
        return None

    def clear(self):
        self.stack.clear()
    
    def count_items_in_stack(self):
        return len(self.stack)
    
    def is_empty(self):
        return len(self.stack) == 0
    
    def is_not_empty(self):
        return len(self.stack) > 0
