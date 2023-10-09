
import sys
import os


class ModulePath:
    def __init__(self, relative_path):
        # main.py path
        self._main_path = os.path.abspath(sys.argv[0])

        # current path
        self._cur_path = os.path.curdir
        self._relative_path = relative_path

        self._module_path = f"{relative_path}"

        self._init()

    @property
    def relative_path(self):
        return self._relative_path

    def _init(self):
        print(self._module_path)
        # self._module_path = f"{self._main_path}{os.path.sep}"


if __name__ == "__main__":
    module_path = ModulePath("./fastapi_hive/xxx_endpoint")
