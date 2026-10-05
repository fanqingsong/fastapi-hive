import importlib
import os
import re
from collections import defaultdict
from typing import Optional

from loguru import logger
from fastapi_hive.ioc_framework.decorators import collect_hooks


class FoundationMeta:
    def __init__(self):
        self._name: Optional[str] = None
        self._container_name: Optional[str] = None
        self._package_path: Optional[str] = None
        self._imported_module = None
        self.hooks = []

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def container_name(self) -> str:
        return self._container_name

    @container_name.setter
    def container_name(self, value: str):
        self._container_name = value

    @property
    def package_path(self) -> str:
        return self._package_path

    @package_path.setter
    def package_path(self, value: str):
        self._package_path = value

    @property
    def imported_module(self):
        return self._imported_module

    @imported_module.setter
    def imported_module(self, value):
        self._imported_module = value


class FoundationContainer:
    def __init__(self):
        self._foundations = {}
        self._foundation_package_path = None

    @property
    def foundations(self):
        return self._foundations

    def register_foundation_package_path(self, foundation_package_path):
        self._foundation_package_path = foundation_package_path

        logger.info(
            f"after registering, foundation container_name path = {self._foundation_package_path}")

    def load_foundations(self):
        foundation_package_path: str = self._foundation_package_path
        logger.info(f"foundation container_name path = {foundation_package_path}")

        foundation_paths = self._get_foundation_paths(foundation_package_path)
        foundation_package_path = re.sub(r'/$', "", foundation_package_path)
        container_name = os.path.basename(foundation_package_path)

        for one_foundation_name in foundation_paths:
            one_foundation_pkg_path = foundation_paths[one_foundation_name]

            one_module_entity = importlib.import_module(one_foundation_pkg_path)

            foundation_instance = FoundationMeta()
            foundation_instance.name = one_foundation_name
            foundation_instance.container_name = container_name
            foundation_instance.package_path = one_foundation_pkg_path
            foundation_instance.imported_module = one_module_entity
            foundation_instance.hooks = collect_hooks(
                one_module_entity,
                role="foundation",
            )

            # logger.debug(f'{container_name}.{one_foundation_name}')
            self._foundations[f'{container_name}.{one_foundation_name}'] = foundation_instance

    def get_foundation(self, module_name: str):
        module_name = module_name.upper()

        for one_name, one_foundation in self._foundations.items():
            one_name = one_name.upper()
            if module_name == one_name:
                return one_foundation

    def _get_foundation_paths(self, package_path):
        foundation_names = self._get_foundation_names(package_path)

        foundation_paths = {}

        for one_foundation_name in foundation_names:
            foundation_path = os.path.join(package_path, one_foundation_name)

            foundation_path = foundation_path.replace("./", "")
            foundation_path = foundation_path.replace(os.path.sep, ".")

            logger.info(f"foundation path = {foundation_path}")

            foundation_paths[one_foundation_name] = foundation_path

        return foundation_paths

    def _get_foundation_names(self, package_path):
        logger.debug(package_path)
        folder_names = os.listdir(package_path)

        foundation_names = []

        for file in folder_names:
            if file == '__pycache__':
                continue

            file_path = os.path.join(package_path, file)

            if os.path.isdir(file_path):
                foundation_names.append(file)

        return foundation_names
