import importlib
import os
from loguru import logger
# import sys
# from .module_path import ModulePath


class ModuleContainer:
    def __init__(self):
        self._modules = {}
        self._module_package_paths = set([])

    @property
    def modules(self):
        return self._modules

    def register_module_package_paths(self, module_package_paths):
        module_package_paths = set(module_package_paths)
        current_package_paths = self._module_package_paths

        self._module_package_paths = current_package_paths | module_package_paths

        logger.info(
            f"after registering, module package paths = {self._module_package_paths}")

    def unregister_module_package_paths(self, module_package_paths):
        module_package_paths = set(module_package_paths)
        current_package_paths = self._module_package_paths

        self._module_package_paths = current_package_paths - module_package_paths

        logger.info(
            f"after unregistering, module package paths = {self._module_package_paths}")

    def load_modules(self):
        module_package_paths = self._module_package_paths
        logger.info(f"module package paths = {module_package_paths}")

        for one_package_path in module_package_paths:
            module_paths = self._get_module_paths(one_package_path)

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

    def _get_module_paths(self, relative_path):
        module_names = self._get_module_names(relative_path)

        module_paths = {}

        for one_name in module_names:
            module_path = os.path.join(relative_path, one_name)

            module_path = module_path.replace("./", "")
            module_path = module_path.replace(os.path.sep, ".")

            logger.info(f"module path = {module_path}")

            module_paths[one_name] = module_path

        return module_paths

    def _get_module_names(self, relative_path):
        folder_names = os.listdir(relative_path)

        module_names = [one_name for one_name in folder_names if one_name !=
                        "__init__.py" and one_name != "__pycache__"]

        return module_names
