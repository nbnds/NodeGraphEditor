from uicomponent import UIComponent

class ComponentRegistry:
    """
    Manages a list of UI components.
    """

    def __init__(self):
        """
        Initializes an empty list to store components.
        """
        self._components = []

    def register(self, component: UIComponent):
        """
        Adds a component to the list.
        """
        if component not in self._components:
            self._components.append(component)

    def unregister(self, component: UIComponent):
        """
        Removes a component from the list.
        """
        if component in self._components:
            self._components.remove(component)

    def handle_events(self, event, context):
        """
        Iterates through components and calls their handle_event method.
        """
        for component in self._components:
            component.handle_event(event, context)

    def update_components(self, dt, context):
        """
        Iterates through components and calls their update method.
        """
        for component in self._components:
            component.update(dt, context)

    def draw_components(self, screen, context):
        """
        Iterates through components and calls their draw method.
        """
        for component in self._components:
            component.draw(screen, context)
