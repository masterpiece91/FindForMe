__author__ = 'alex'


class Common:
    def __init__(self):
        self.data = []

    @staticmethod
    def enum(**enums):
        return type('Enum', (), enums)

    @staticmethod
    def get_operating_system():
        current_operating_system = None

        from sys import platform as _platform

        if _platform == "linux" or _platform == "linux2":
            # linux
            current_operating_system = "linux"
        elif _platform == "darwin":
            # OS X
            current_operating_system = "OS X"
        elif _platform == "win32":
            # Windows
            current_operating_system = "Windows"

        return current_operating_system
