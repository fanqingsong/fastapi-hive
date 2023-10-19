import importlib
import os
import re
from collections import defaultdict
from typing import Callable

from loguru import logger


class CornerstoneMeta:
    def __init__(self):
        self._name: Optional[str] = None
        self._container_name: Optional[str] = None
        self._package_path: Optional[str] = None
        self._imported_module = None

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


class CornerstoneContainer:
    def __init__(self):
        self._cornerstones = {}
        self._cornerstone_package_path = None

    @property
    def cornerstones(self):
        return self._cornerstones

    def iterate_cornerstones(self, callback: Callable):
        cornerstones = self._cornerstones
        for _, one_cornerstone in cornerstones.items():
            one_cornerstone: CornerstoneMeta = one_cornerstone

            callback(one_cornerstone)

    async def async_iterate_cornerstones(self, callback: Callable):
        cornerstones = self._cornerstones
        for _, one_cornerstone in cornerstones.items():
            one_cornerstone: CornerstoneMeta = one_cornerstone

            await callback(one_cornerstone)

    def register_cornerstone_package_path(self, cornerstone_package_path):
        self._cornerstone_package_path = cornerstone_package_path

        logger.info(
            f"after registering, cornerstone container_name path = {self._cornerstone_package_path}")

    def load_cornerstones(self):
        cornerstone_package_path: str = self._cornerstone_package_path
        logger.info(f"cornerstone container_name path = {cornerstone_package_path}")

        cornerstone_paths = self._get_cornerstone_paths(cornerstone_package_path)
        cornerstone_package_path = re.sub(r'/$', "", cornerstone_package_path)
        container_name = os.path.basename(cornerstone_package_path)

        for one_cornerstone_name in cornerstone_paths:
            one_cornerstone_pkg_path = cornerstone_paths[one_cornerstone_name]

            one_module_entity = importlib.import_module(one_cornerstone_pkg_path)

            cornerstone_instance = CornerstoneMeta()
            cornerstone_instance.name = one_cornerstone_name
            cornerstone_instance.container_name = container_name
            cornerstone_instance.package_path = one_cornerstone_pkg_path
            cornerstone_instance.imported_module = one_module_entity

            # logger.debug(f'{container_name}.{one_cornerstone_name}')
            self._cornerstones[f'{container_name}.{one_cornerstone_name}'] = cornerstone_instance

    def get_cornerstone(self, module_name: str):
        module_name = module_name.upper()

        for one_name, one_cornerstone in self._cornerstones.items():
            one_name = one_name.upper()
            if module_name == one_name:
                return one_cornerstone

    def _get_cornerstone_paths(self, package_path):
        cornerstone_names = self._get_cornerstone_names(package_path)

        cornerstone_paths = {}

        for one_cornerstone_name in cornerstone_names:
            cornerstone_path = os.path.join(package_path, one_cornerstone_name)

            cornerstone_path = cornerstone_path.replace("./", "")
            cornerstone_path = cornerstone_path.replace(os.path.sep, ".")

            logger.info(f"cornerstone path = {cornerstone_path}")

            cornerstone_paths[one_cornerstone_name] = cornerstone_path

        return cornerstone_paths

    def _get_cornerstone_names(self, package_path):
        logger.debug(package_path)
        folder_names = os.listdir(package_path)

        cornerstone_names = []

        for file in folder_names:
            if file == '__pycache__':
                continue

            file_path = os.path.join(package_path, file)

            if os.path.isdir(file_path):
                cornerstone_names.append(file)

        return cornerstone_names
