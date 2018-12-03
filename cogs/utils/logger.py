from inspect import currentframe, getouterframes
from datetime import date, datetime


class Logger:

    def __init__(self, name, *, dateform="%Y-%m-%d %H:%M"):
        self.name = name
        self.dateform = dateform

    def write(self, content, entrytype, function):
        time = datetime.now().strftime(self.dateform)
        with open("logs/{}.log".format(str(date.today())), "a") as file:
            file.write(f"[{time}] {entrytype} {self.name} {function}: {content}\n")

    def _add(self, entrytype, content, *, display=False):
        function = getouterframes(currentframe(), 3)[2][3]
        self.write(content, entrytype, function)
        if display:
            print(f"[{function}] {content}")

    def add(self, entrytype, content, *, display=False):
        self._add(entrytype, content, display=display)

    def info(self, content, *, display=False):
        self._add("INFO", content, display=display)

    def warn(self, content, *, display=True):
        self._add("WARNING", content, display=display)
