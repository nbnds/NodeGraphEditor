"""
Adapted from https://github.com/Nearoo/pygame-text-input
Copyright (c) 2021 Silas Gyger
MIT License
"""

import pygame
from typing import List, Callable
import pygame.locals as pl

class TextInputEngine:
    '''
    Keeps track of text inputted, cursor position, etc.
    Pass a validator function returning if a string is valid,
    and the string will only be updated if the validator function
    returns true.

    For example, limit input to 5 characters:
    ```
    limit_5 = lambda x: len(x) <= 5
    manager = TextInputEngine(validator=limit_5)
    ```

    :param initial: The initial string
    :param validator: A function string -> bool defining valid input
    '''

    def __init__(self,
                initial = "",
                validator: Callable[[str], bool] = lambda x: True):

        self.left = initial # string to the left of the cursor
        self.right = "" # string to the right of the cursor
        self.validator = validator


    @property
    def value(self):
        """ Get / set the value currently inputted. Doesn't change cursor position if possible."""
        return self.left + self.right

    @value.setter
    def value(self, value):
        cursor_pos = self.cursor_pos
        self.left = value[:cursor_pos]
        self.right = value[cursor_pos:]

    @property
    def cursor_pos(self):
        """ Get / set the position of the cursor. Will clamp to [0, length of input]. """
        return len(self.left)

    @cursor_pos.setter
    def cursor_pos(self, value):
        complete = self.value
        self.left = complete[:value]
        self.right = complete[value:]

    def update(self, events: List[pygame.event.Event]):
        """
        Update the interal state with fresh pygame events.
        Call this every frame with all events returned by `pygame.event.get()`.
        """
        for event in events:
            if event.type == pl.KEYDOWN:
                v_before = self.value
                c_before = self.cursor_pos
                self._process_keydown(event)
                if not self.validator(self.value):
                    self.value = v_before
                    self.cursor_pos = c_before

    def _process_keydown(self, ev):
        attrname = f"_process_{pygame.key.name(ev.key)}"
        if hasattr(self, attrname):
            getattr(self, attrname)()
        else:
            self._process_other(ev)

    def _process_delete(self):
        self.right = self.right[1:]

    def _process_backspace(self):
        self.left = self.left[:-1]

    def _process_right(self):
        self.cursor_pos += 1

    def _process_left(self):
        self.cursor_pos -= 1

    def _process_end(self):
        self.cursor_pos = len(self.value)

    def _process_home(self):
        self.cursor_pos = 0

    def _process_return(self):
        pass

    def _process_other(self, event):
        # Nur druckbare Zeichen akzeptieren (keine Steuerzeichen wie TAB, ESC, etc.)
        if event.unicode and event.unicode.isprintable() and event.unicode not in ('\t', '\r', '\n'):
            self.left += event.unicode


class TextInputRenderer:
    """
    Utility class to quickly visualize textual input, like a message or username.
    Pass events every frame to the `.update` method, then get the surface
    of the rendered font using the `.surface` attribute.

    All arguments of constructor can also be set via attributes, so e.g.
    to change `font_color` do
    ```
    inputVisualizer.font_color = (255, 100, 0)
    ```
    The surface itself is lazily re-rendered only when the `.surface` field is
    accessed, and if any parameters changed since the last `.surface` access, so
    values can freely be changed between renders without performance overhead.

    :param manager: The TextInputManager used to manage the user input
    :param font_object: a pygame.font.Font object used for rendering
    :param antialias: whether to render the font antialiased or not
    :param font_color: color of font rendered
    :param cursor_blink_interal: the interval of the cursor blinking, in ms
    :param cursor_width: The width of the cursor, in pixels
    :param cursor_color: The color of the cursor
    """
    def __init__(self,
            engine = None,
            font_object = None,
            antialias = True,
            font_color = (0, 0, 0),
            cursor_blink_interval = 300,
            cursor_width = 1,
            cursor_color = (0, 0, 0),
            overlay_enabled = False,
            overlay_color = (0, 0, 0, 128)
            ):

        self._manager = TextInputEngine() if engine is None else engine
        self._font_object = pygame.font.Font(pygame.font.get_default_font(), 25) if font_object is None else font_object
        self._antialias = antialias
        self._font_color = font_color

        self._clock = pygame.time.Clock()
        self._cursor_blink_interval = cursor_blink_interval
        self._cursor_visible = False
        self._last_blink_toggle = 0

        self._cursor_width = cursor_width
        self._cursor_color = cursor_color

        self._surface = pygame.Surface((self._cursor_width, self._font_object.get_height()))
        self._rerender_required = True
        self._overlay_enabled = overlay_enabled
        self._overlay_color = overlay_color

    @property
    def overlay_enabled(self):
        """ Get / set whether the overlay is enabled or not """
        return self._overlay_enabled

    @overlay_enabled.setter
    def overlay_enabled(self, v):
        """ Get / set whether the overlay is enabled or not """
        self._overlay_enabled = v
        self._require_rerender()

    @property
    def overlay_color(self):
        """ Get / set the color of the overlay """
        return self._overlay_color

    @overlay_color.setter
    def overlay_color(self, v):
        """ Get / set the color of the overlay """
        self._overlay_color = v
        self._require_rerender()

    def render_with_overlay(self, screen, events: List[pygame.event.Event]):
        """
        Render the overlay on top of the text input surface.
        :param surface: The surface to render the overlay on
        """
        if self._overlay_enabled:
            overlay_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay_surface.fill(self._overlay_color)
            screen.blit(overlay_surface, (0, 0))
        self.update(events)
        surface = self.surface
        rect = surface.get_rect(center=screen.get_rect().center)
        # Draw a white border around the input field
        border_rect = rect.inflate(16, 16)
        pygame.draw.rect(screen, (255, 255, 255), border_rect, width=2, border_radius=8)
        screen.blit(surface, rect)
        # Draw a ground line just beneath the text
        line_y = rect.bottom - 4
        ground_color = (255, 255, 0)  # yellow
        ground_width = 1  # thinner line
        if self.manager.value.strip():
            # Draw line under the text
            pygame.draw.line(screen, ground_color, (rect.left + 4, line_y), (rect.right - 4, line_y), ground_width)
        else:
            # Draw a single line with width of one character, centered, and with a gap from the cursor
            char_width = self.font_object.size("A")[0]
            gap_from_cursor = 6  # pixels gap between ground line and cursor
            center_x = rect.centerx
            # Draw the ground line 2px below the cursor line for a visible gap
            ground_line_y = line_y + 2
            half_line = (char_width - gap_from_cursor) // 2
            pygame.draw.line(
                screen,
                ground_color,
                (center_x - half_line, ground_line_y),
                (center_x + half_line, ground_line_y),
                ground_width
            )

    def should_block_mouse(self):
        """
        Returns whether the overlay should block mouse events or not.
        This is useful for overlaying the text input on top of other elements
        """
        return self._overlay_enabled

    @property
    def value(self):
        """ Get / set the value of text alreay inputted. Doesn't change cursor position if possible."""
        return self.manager.value

    def clear_text(self):
        """ Clear the text inputted. """
        self.manager.value = ""

    @value.setter
    def value(self, v):
        self.manager.value = v

    @property
    def manager(self):
        """ Get / set the underlying `TextInputManager` for this instance"""
        return self._manager

    @manager.setter
    def manager(self, v):
        self._manager = v

    @property
    def surface(self):
        """ Get the surface with the rendered user input """
        if self._rerender_required:
            self._rerender()
            self._rerender_required = False
        return self._surface

    @property
    def antialias(self):
        """ Get / set antialias of the render """
        return self._antialias

    @antialias.setter
    def antialias(self, v):
        self._antialias = v
        self._require_rerender()

    @property
    def font_color(self):
        """ Get / set color of rendered font """
        return self._font_color

    @font_color.setter
    def font_color(self, v):
        self._font_color = v
        self._require_rerender()

    @property
    def font_object(self):
        """ Get / set the font object used to render the text """
        return self._font_object

    @font_object.setter
    def font_object(self, v):
        self._font_object = v
        self._require_rerender()

    @property
    def cursor_visible(self):
        """ Get / set cursor visibility (flips again after `.cursor_interval` if continuously update)"""
        return self._cursor_visible

    @cursor_visible.setter
    def cursor_visible(self, v):
        self._cursor_visible = v
        self._last_blink_toggle = 0
        self._require_rerender()

    @property
    def cursor_width(self):
        """ Get / set width in pixels of the cursor """
        return self._cursor_width

    @cursor_width.setter
    def cursor_width(self, v):
        self._cursor_width = v
        self._require_rerender()

    @property
    def cursor_color(self):
        """ Get / set the color of the cursor """
        return self._cursor_color

    @cursor_color.setter
    def cursor_color(self, v):
        self._cursor_color = v
        self._require_rerender()

    @property
    def cursor_blink_interval(self):
        """ Get / set the interval of time with which the cursor blinks (toggles), in ms"""
        return self._cursor_blink_interval

    @cursor_blink_interval.setter
    def cursor_blink_interval(self, v):
        self._cursor_blink_interval = v

    def update(self, events: List[pygame.event.Event]):
        """
        Update internal state.
        Call this once every frame with all events returned by `pygame.event.get()`
        """

        # Update self.manager internal state, rerender if value changes
        value_before = self.manager.value
        self.manager.update(events)
        if self.manager.value != value_before:
            self._require_rerender()

        # Update cursor visibility after self._blink_interval milliseconds
        self._clock.tick()
        self._last_blink_toggle += self._clock.get_time()
        if self._last_blink_toggle > self._cursor_blink_interval:
            self._last_blink_toggle %= self._cursor_blink_interval
            self._cursor_visible = not self._cursor_visible

            self._require_rerender()

        # Make cursor visible when something is pressed
        if [event for event in events if event.type == pl.KEYDOWN]:
            self._last_blink_toggle = 0
            self._cursor_visible = True
            self._require_rerender()


    def _require_rerender(self):
        """
        Trigger a re-render of the surface the next time the surface is accessed.
        """
        self._rerender_required = True

    def _rerender(self):
        """ Rerender self._surface."""
        # Final surface is slightly larger than font_render itself, to accomodate for cursor
        rendered_surface = self.font_object.render(self.manager.value + " ",
                                                self.antialias,
                                                self.font_color)
        w, h = rendered_surface.get_size()
        self._surface = pygame.Surface((w + self._cursor_width, h)).convert_alpha()
        self._surface.fill((0, 0, 0, 0))
        self._surface.blit(rendered_surface, (0, 0))

        if self._cursor_visible:
            str_left_of_cursor = self.manager.value[:self.manager.cursor_pos]
            cursor_y = self.font_object.size(str_left_of_cursor)[0]
            cursor_rect = pygame.Rect(cursor_y, 0, self._cursor_width, self.font_object.get_height())
            self._surface.fill(self._cursor_color, cursor_rect)
