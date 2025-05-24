from abc import ABC, abstractmethod

class UIComponent(ABC):
    """
    Abstract base class for UI components.
    """

    @abstractmethod
    def handle_event(self, event, context):
        """
        Handle an event.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, dt, context):
        """
        Update the component.
        """
        raise NotImplementedError

    @abstractmethod
    def draw(self, screen, context):
        """
        Draw the component.
        """
        raise NotImplementedError
