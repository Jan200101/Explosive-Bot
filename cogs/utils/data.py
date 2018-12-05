from json import load, dump


class Data(dict):

    def __init__(self, path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(path) as file:
            self.update(load(file))

    def __setitem__(self, key, value):
        super().__setitem__(str(key), value)
        self.__save__()

    def __delitem__(self, key):
        super().__delitem__(str(key))
        self.__save__()

    def __getitem__(self, key):
        return super().__getitem__(str(key))

    def __save__(self):
        with open(self.path, "w") as file:
            dump(self, file)
