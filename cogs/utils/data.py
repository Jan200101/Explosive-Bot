from json import load, dump


class Data(dict):
    """Data management class"""

    def __init__(self, path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        try:
            with open(path) as file:
                self.update(load(file))
        except FileNotFoundError:
            pass

    def __setitem__(self, key, value):
        super().__setitem__(str(key), value)
        self.save()

    def __delitem__(self, key):
        super().__delitem__(str(key))
        self.save()

    def __getitem__(self, key):
        return super().__getitem__(str(key))

    def save(self):
        with open(self.path, "w") as file:
            dump(self, file)
