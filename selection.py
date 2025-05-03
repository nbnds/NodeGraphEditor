class NodeSelection:
    def __init__(self):
        self.rect_start = None
        self.rect_end = None
        self.nodes = []

    def begin(self, start_pos):
        self.rect_start = start_pos
        self.rect_end = start_pos
        self.nodes = []

    def update(self, end_pos):
        self.rect_end = end_pos

    def finish(self, all_nodes, canvas_offset_x, canvas_offset_y, zoom):
        if self.rect_start and self.rect_end:
            x0, y0 = self.rect_start
            x1, y1 = self.rect_end
            rx0, ry0 = min(x0, x1), min(y0, y1)
            rx1, ry1 = max(x0, x1), max(y0, y1)
            self.nodes = []
            for node in all_nodes:
                nx = (node.x - canvas_offset_x) * zoom
                ny = (node.y - canvas_offset_y) * zoom
                nw = node.width * zoom
                nh = node.height * zoom
                if rx0 <= nx and nx + nw <= rx1 and ry0 <= ny and ny + nh <= ry1:
                    self.nodes.append(node)
        self.rect_start = None
        self.rect_end = None

    def clear(self):
        self.rect_start = None
        self.rect_end = None
        self.nodes = []

    def is_active(self):
        return self.rect_start is not None and self.rect_end is not None
