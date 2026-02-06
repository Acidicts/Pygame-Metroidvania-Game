

class FolderStorage:
    def __init__(self):
        self._data = {}

    def __getitem__(self, key):
        if key not in self._data:
            self._data[key] = {}
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __contains__(self, key):
        return key in self._data

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return f"FolderStorage({self._data})"