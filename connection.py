from constants import WHITE
import pygame

class Connection:
    def __init__(self, start_node, end_node):
        self.start_node = start_node
        self.end_node = end_node

    def draw(self, screen, offset_x=0, offset_y=0, zoom=1.0):
        start_pos = (int((self.start_node.get_output_pos()[0] - offset_x) * zoom), int((self.start_node.get_output_pos()[1] - offset_y) * zoom))
        end_pos = (int((self.end_node.get_input_pos()[0] - offset_x) * zoom), int((self.end_node.get_input_pos()[1] - offset_y) * zoom))
        thickness = max(1, int(2 * zoom))
        pygame.draw.line(screen, WHITE, start_pos, end_pos, thickness)