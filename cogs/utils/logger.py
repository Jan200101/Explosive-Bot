from datetime import date, datetime
from sys import _getframe


class Logger:

    def __init__(self, name, *, dateform="%d/%m/%Y %H:%M"):
        self.name = name
        self.dateform = dateform

    def write(self, content, type, function):
        time = datetime.now().strftime(self.dateform)
        with open("logs/{}.log".format(str(date.today())), "a") as file:
            file.write("[{time}] {type} {name} {function}: {content}\n".format(
                time=time, type=type, name=self.name, function=function, content=content))

    def _add(self, type, content, function=None, *, display=False):
        if not function:
            function = _getframe(1).f_code.co_name
        self.write(content, type, function)
        if display:
            print("[{function}] {content}".format(
                function=function, content=content))

    def info(self, content):
        self._add("INFO", content, _getframe(1).f_code.co_name)

    def warn(self, content):
        self._add("WARNING", content, _getframe(1).f_code.co_name, display=True)
