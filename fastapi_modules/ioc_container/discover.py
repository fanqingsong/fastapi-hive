import importlib
import os


class Discover():
    def __init__(self):
        self._modules = {}

        self._module_path = "./fastapi_modules/modules"

        self._load_modules()

    @property
    def modules(self):
        return self._modules

    def _get_module_names(self):
        folder_names = os.listdir(self._module_path)

        module_names = [one_name for one_name in folder_names if one_name !=
                        "__init__.py" and one_name != "__pycache__"]

        return module_names

    def _get_module_paths(self):
        module_names = self._get_module_names()

        module_paths = {}

        for one_name in module_names:
            module_path = os.path.join("fastapi_modules/modules", one_name)

            module_path = module_path.replace(os.path.sep, ".")

            module_paths[one_name] = module_path

        return module_paths

    def _load_modules(self):
        module_paths = self._get_module_paths()

        for one_module in module_paths:
            one_module_path = module_paths[one_module]

            one_module_entity = importlib.import_module(one_module_path)

            self._modules[one_module] = one_module_entity

    def get_module(self, module_name: str):
        module_name = module_name.upper()

        for one_name, one_entity in self._modules.items():
            one_name = one_name.upper()
            if module_name == one_name:
                return one_entity


discover = Discover()
