class ConnectionDragState:
    def __init__(self):
        self.active = False
        self.start_node = None  # Typically a Node or node id
        self.end_pos = None     # (x, y) tuple

    def start(self, start_node, end_pos=None):
        self.active = True
        self.start_node = start_node
        self.end_pos = end_pos

    def update_end(self, end_pos):
        self.end_pos = end_pos

    def stop(self):
        self.active = False
        self.start_node = None
        self.end_pos = None

    def is_active(self):
        return self.active
