import pygame

def lmb_down(position):
    """Creates a pygame.MOUSEBUTTONDOWN event for the left button at the given position."""
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=position, button=pygame.BUTTON_LEFT)

def lmb_up(position):
    """Creates a pygame.MOUSEBUTTONUP event for the left button at the given position."""
    return pygame.event.Event(pygame.MOUSEBUTTONUP, pos=position, button=pygame.BUTTON_LEFT)
