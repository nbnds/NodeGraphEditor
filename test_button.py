import os
import pytest
os.environ["SDL_VIDEODRIVER"] = "dummy"
from editor import NodeEditor
from button import Button
from toolbar import Toolbar
import pygame

class TestButton:

    @pytest.fixture
    def toolbar(self):
        """Fixture to create a toolbar for testing."""
        toolbar = Toolbar()
        toolbar.bg_color = (0, 0, 0)
        toolbar.buttons = []
        toolbar.padding = 10
        toolbar.left_margin = 5
        toolbar.top_margin = 5
        toolbar.min_width = 100
        toolbar.width = 100
        # Das konfigurierte Objekt zurückgeben
        return toolbar

    @pytest.fixture
    def editor(self, toolbar):
        editor = NodeEditor(toolbar)
        editor.zoom = 1.0
        editor.canvas_offset_x = 0
        editor.canvas_offset_y = 0
        # Das konfigurierte Objekt zurückgeben
        return editor

    @pytest.fixture
    def AddNodeButton(self):
        """Fixture to create a button for testing."""
        button = Button(rect=pygame.Rect(50, 50, 30, 30), label=None, action=None)
        return button

    def test_button_initialization(self, editor, AddNodeButton):
        """Test the initialization of a button."""
        editor.toolbar.add_button(AddNodeButton)
        assert len(editor.toolbar.buttons) == 1
        assert editor.toolbar.buttons[-1].label == "<UNNAMED>"
        leftclick = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(60, 60), button=pygame.BUTTON_LEFT)
        pygame.event.post(leftclick)
        clicked_button = editor.toolbar.get_clicked_button(60, 60)
        assert clicked_button is not None
        assert clicked_button.label == "<UNNAMED>"
        assert clicked_button.rect == pygame.Rect(50, 50, 30, 30)
