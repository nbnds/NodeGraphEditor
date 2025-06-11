from constants import WHITE, GREEN
import math
import pygame

class Connection:
    def __init__(self, start_node, end_node, label=""):
        self.start_node = start_node
        self.end_node = end_node
        self.marked = False  # New attribute
        self.label = label   # New attribute

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
        color = GREEN if self.marked else WHITE

        # Draw label in a rectangle if present
        label_rect = None
        label_box_halfwidth = 0
        label_box_halfheight = 0
        label_center = None
        if self.label:
            # Font size decreases with zoom, but not too fast (clamped)
            min_font_size = 10
            max_font_size = 28
            font_size = int(18 * max(0.7, min(1.0, zoom)))
            font_size = max(min_font_size, min(max_font_size, font_size))
            font = pygame.font.Font(None, font_size)
            label_surf = font.render(self.label, True, color)
            # Padding is reduced for less box size at low zoom
            min_pad = 4
            max_pad = 12
            pad_scale = max(0.5, min(1.0, zoom))
            label_padding_x = int(max_pad * pad_scale)
            label_padding_y = int(3 * pad_scale)
            rect_width = label_surf.get_width() + 2 * label_padding_x
            rect_height = label_surf.get_height() + 2 * label_padding_y

            # Midpoint of the line
            mid_x = (start_pos[0] + end_pos[0]) // 2
            mid_y = (start_pos[1] + end_pos[1]) // 2

            rect_center = (mid_x, mid_y)
            label_center = rect_center
            label_rect = pygame.Rect(0, 0, rect_width, rect_height)
            label_rect.center = rect_center
            label_box_halfwidth = rect_width // 2
            label_box_halfheight = rect_height // 2

            # Draw filled rectangle (background) directly on the screen to cover the line
            bg_color = (32, 32, 32)
            pygame.draw.rect(screen, bg_color, label_rect, border_radius=6)
            # Draw border (always thin, regardless of zoom)
            border_width = 1
            pygame.draw.rect(screen, color, label_rect, width=border_width, border_radius=6)
            # Blit label text centered
            label_text_rect = label_surf.get_rect(center=label_rect.center)
            screen.blit(label_surf, label_text_rect)

        # Draw the line so that it touches the label box, not crosses it
        if label_rect and label_center is not None:
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            length = math.hypot(dx, dy)
            if length == 0:
                return
            ux = dx / length
            uy = dy / length

            def edge_offset(half_w, half_h, ux, uy):
                if ux == 0:
                    tx = float('inf')
                else:
                    tx = half_w / abs(ux)
                if uy == 0:
                    ty = float('inf')
                else:
                    ty = half_h / abs(uy)
                return min(tx, ty)

            offset = edge_offset(label_box_halfwidth, label_box_halfheight, ux, uy)
            line1_end = (
                int(label_center[0] - ux * offset),
                int(label_center[1] - uy * offset)
            )
            line2_start = (
                int(label_center[0] + ux * offset),
                int(label_center[1] + uy * offset)
            )
            pygame.draw.line(screen, color, start_pos, line1_end, thickness)
            pygame.draw.line(screen, color, line2_start, end_pos, thickness)
        else:
            pygame.draw.line(screen, color, start_pos, end_pos, thickness)

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
