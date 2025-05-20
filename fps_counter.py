import pygame
from collections import deque
import time

class FPSCounter:
    def __init__(self, maxlen=60, font=None, color=(255,255,255), pos=(0,0), update_interval=0.5):
        self.samples = deque(maxlen=maxlen)
        self.font = font or pygame.font.Font(None, 36)
        self.color = color
        self.pos = pos
        self.maxlen = maxlen
        self.last_update = time.time()
        self.display_text = ""
        self.update_interval = update_interval

    def update(self, fps):
        self.samples.append(fps)
        now = time.time()
        if now - self.last_update > self.update_interval:
            avg = sum(self.samples) / len(self.samples) if self.samples else 0
            min_avg = min(self.samples) if self.samples else 0
            max_avg = max(self.samples) if self.samples else 0
            self.display_text = f"FPS: {avg:.1f} | Max: {max_avg:.1f} | Min: {min_avg:.1f}"
            self.last_update = now

    def draw(self, screen):
        if self.display_text:
            surf = self.font.render(self.display_text, True, self.color)
            screen.blit(surf, self.pos)
