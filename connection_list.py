class ConnectionList:
    def __init__(self):
        self._connections = []

    def __iter__(self):
        return iter(self._connections)

    def __len__(self):
        return len(self._connections)

    def append(self, connection):
        self._connections.append(connection)

    def remove(self, connection):
        self._connections.remove(connection)

    def clear(self):
        self._connections.clear()

    def all(self):
        return self._connections

    def filter(self, predicate):
        return [c for c in self._connections if predicate(c)]
