from constants import WHITE
import math
import pygame

class Connection:
    def __init__(self, start_node, end_node):
        self.start_node = start_node
        self.end_node = end_node

    def draw(self, screen, offset_x=0, offset_y=0, zoom=1.0):
        start_pos = (
            int((self.start_node.get_output_pos()[0] - offset_x) * zoom),
            int((self.start_node.get_output_pos()[1] - offset_y) * zoom)
        )
        end_pos = (
            int((self.end_node.get_input_pos()[0] - offset_x) * zoom),
            int((self.end_node.get_input_pos()[1] - offset_y) * zoom)
        )

        thickness = max(1, int(2 * zoom))
        pygame.draw.line(screen, WHITE, start_pos, end_pos, thickness)

    def is_clicked(self, world_x, world_y, zoom=1.0, tolerance=10):
        x1, y1 = self.start_node.get_right_center()
        x2, y2 = self.end_node.get_left_center()
        px, py = world_x, world_y
        dx, dy = x2 - x1, y2 - y1
        if dx == dy == 0:
            return False
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy
        dist = math.hypot(px - nearest_x, py - nearest_y)
        return dist < (tolerance / zoom)
