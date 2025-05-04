import pygame

def lmb_down(position):
    """Creates a pygame.MOUSEBUTTONDOWN event for the left button at the given position."""
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=position, button=pygame.BUTTON_LEFT)

def lmb_up(position):
    """Creates a pygame.MOUSEBUTTONUP event for the left button at the given position."""
    return pygame.event.Event(pygame.MOUSEBUTTONUP, pos=position, button=pygame.BUTTON_LEFT)

def rmb_down(position):
    """Creates a pygame.MOUSEBUTTONDOWN event for the right button at the given position."""
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=position, button=pygame.BUTTON_RIGHT)

def rmb_up(position):
    """Creates a pygame.MOUSEBUTTONUP event for the right button at the given position."""
    return pygame.event.Event(pygame.MOUSEBUTTONUP, pos=position, button=pygame.BUTTON_RIGHT)

def mouse_move(start_pos, end_pos, buttons=(0, 0, 0)):
    """
    Creates a pygame.MOUSEMOTION event to simulate mouse movement.

    Args:
        start_pos: The starting (x, y) position of the mouse movement.
        end_pos: The ending (x, y) position of the mouse movement.
        buttons:  A tuple of three values (left, middle, right) indicating which mouse
                  buttons are pressed during the movement.  Each value should be 0 (not pressed)
                  or 1 (pressed).  Default is (0, 0, 0) (no buttons pressed).

    Returns:
        A pygame.event.Event object representing the mouse movement.
    """
    start_x = start_pos[0]
    start_y = start_pos[1]
    end_x = end_pos[0]
    end_y = end_pos[1]
    return pygame.event.Event(pygame.MOUSEMOTION, {
        'pos': end_pos,
        'rel': (end_x - start_x, end_y - start_y),
        'buttons': buttons,
    })
