class CanvasPanning:
    def __init__(self):
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.panning = False
        self.pan_start = (0, 0)
        self.pan_offset_start = (0, 0)

    def start_panning(self, mouse_pos):
        self.panning = True
        self.pan_start = mouse_pos
        self.pan_offset_start = (self.offset_x, self.offset_y)

    def stop_panning(self):
        self.panning = False

    def update_panning(self, mouse_pos, zoom, follows_mouse):
        dx = (mouse_pos[0] - self.pan_start[0]) / zoom
        dy = (mouse_pos[1] - self.pan_start[1]) / zoom
        if follows_mouse:
            self.offset_x = self.pan_offset_start[0] - dx
            self.offset_y = self.pan_offset_start[1] - dy
        else:
            self.offset_x = self.pan_offset_start[0] + dx
            self.offset_y = self.pan_offset_start[1] + dy
