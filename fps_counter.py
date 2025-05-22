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
        self.update_interval = update_interval
        self._needs_redraw = True
        self._displayed_text: str = "" # Der String, der aktuell gerendert wird
        self._current_fps: float = 0.0
        self._window_min_fps: float = 0.0 # Min-FPS im aktuellen Fenster
        self._window_max_fps: float = 0.0 # Max-FPS im aktuellen Fenster
        self._needs_redraw: bool = True
        self._rendered_surf: pygame.Surface = None

    def update(self, current_frame_fps: float):
        """
        Aktualisiert die FPS-Historie mit dem neuesten Wert
        und berechnet die angezeigten Min/Max/Avg-Werte, wenn das Intervall erreicht ist.
        """
        if current_frame_fps > 0: # Vermeide das Hinzufügen von 0-Werten, die den Durchschnitt verfälschen
            self.samples.append(current_frame_fps)

        self._current_fps = current_frame_fps # Speichere den aktuellen FPS-Wert

        now = time.time()
        # Prüfe, ob es Zeit ist, den angezeigten Text zu aktualisieren
        if now - self.last_update >= self.update_interval:
            self.last_update = now

            if not self.samples: # Wenn keine Samples vorhanden sind (z.B. ganz am Anfang)
                new_text = "FPS: 0.0 | Max: 0.0 | Min: 0.0"
                self._window_min_fps = 0.0
                self._window_max_fps = 0.0
            else:
                # Berechne Min/Max/Avg im aktuellen Fenster
                self._window_min_fps = min(self.samples)
                self._window_max_fps = max(self.samples)
                avg_fps = sum(self.samples) / len(self.samples)

                # Formatiere den neuen Text
                new_text = f"FPS: {avg_fps:5.1f} | Max: {self._window_max_fps:5.1f} | Min: {self._window_min_fps:5.1f}"

            # Prüfe, ob sich der Text geändert hat, um unnötiges Neuzeichnen zu vermeiden
            if new_text != self._displayed_text:
                self._displayed_text = new_text
                self._needs_redraw = True # Setze Flag, dass Text-Surface neu erstellt werden muss

    def draw(self, screen: pygame.Surface):
        """
        Zeichnet den FPS-Zähler auf den Bildschirm.
        """
        if self._needs_redraw and self._displayed_text:
            self._rendered_surf = self.font.render(self._displayed_text, True, self.color)
            self._bg_rect = self._rendered_surf.get_rect(topleft=self.pos).inflate(12, 4)
            self._needs_redraw = False

        if self._rendered_surf:

            pygame.draw.rect(screen, (0, 0, 0), self._bg_rect)
            screen.blit(self._rendered_surf, self.pos)
