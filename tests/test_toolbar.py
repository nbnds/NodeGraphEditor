import pygame
import pytest
from toolbar import Toolbar
from button import Button

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()

def test_buttons_grow_when_longer_label_added():
    toolbar = Toolbar()
    labels = ["Short", "Medium Label", "This is the longest label"]
    prev_widths = []
    for i, label in enumerate(labels):
        toolbar.add_button(Button(label=label))
        widths = [btn.rect.width for btn in toolbar.buttons]
        max_width = max(widths)
        # All buttons should have the same width
        assert all(w == max_width for w in widths), f"Step {i}: Button widths: {widths}"
        # If this is not the first button, check that previous buttons grew (if needed)
        if prev_widths:
            for prev, curr in zip(prev_widths, widths[:-1]):
                assert curr >= prev, f"Button did not grow: before={prev}, after={curr}"
        prev_widths = widths.copy()

def test_toolbar_width_adapts_to_buttons_width():
    toolbar = Toolbar()
    initial_width = toolbar.width  # Save initial width before adding buttons
    labels = ["Short", "Medium Label", "This is the longest label"]
    for label in labels:
        toolbar.add_button(Button(label=label))
    btn_widths = [btn.rect.width for btn in toolbar.buttons]
    max_btn_width = max(btn_widths)
    expected_min_width = max_btn_width + toolbar.left_margin * 2
    # Assert toolbar grew
    assert toolbar.width > initial_width, (
        f"Toolbar width did not grow: before={initial_width}, after={toolbar.width}")
    # Assert toolbar is wide enough for buttons and margins
    assert toolbar.width >= expected_min_width, (
        f"Toolbar width {toolbar.width} is less than expected minimum {expected_min_width}")
