import importlib
import os
from loguru import logger
from fastapi_hive.ioc_framework.cornerstone_model import CornerstoneMeta


class CornerstoneContainer:
    def __init__(self):
        self._cornerstones = {}
        self._cornerstone_package_paths = set([])

    @property
    def cornerstones(self):
        return self._cornerstones

    def register_cornerstone_package_paths(self, cornerstone_package_paths):
        cornerstone_package_paths = set(cornerstone_package_paths)
        current_package_paths = self._cornerstone_package_paths

        self._cornerstone_package_paths = current_package_paths | cornerstone_package_paths

        logger.info(
            f"after registering, cornerstone package paths = {self._cornerstone_package_paths}")

    def unregister_cornerstone_package_paths(self, cornerstone_package_paths):
        cornerstone_package_paths = set(cornerstone_package_paths)
        current_package_paths = self._cornerstone_package_paths

        self._cornerstone_package_paths = current_package_paths - cornerstone_package_paths

        logger.info(
            f"after unregistering, cornerstone package paths = {self._cornerstone_package_paths}")

    def load_cornerstones(self):
        module_package_paths = self._cornerstone_package_paths
        logger.info(f"cornerstone package paths = {module_package_paths}")

        for one_package_path in module_package_paths:
            cornerstone_paths = self._get_cornerstone_paths(one_package_path)
            package_name = os.path.basename(one_package_path)

            for one_module_name in cornerstone_paths:
                one_module_path = cornerstone_paths[one_module_name]

                one_module_entity = importlib.import_module(one_module_path)

                cornerstone_instance = CornerstoneMeta()
                cornerstone_instance.name = one_module_name
                cornerstone_instance.package = package_name
                cornerstone_instance.imported_module = one_module_entity

                self._cornerstones[one_module_name] = cornerstone_instance

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
        folder_names = os.listdir(package_path)

        cornerstone_names = []

        for file in folder_names:
            if file == '__pycache__':
                continue

            file_path = os.path.join(package_path, file)

            if os.path.isdir(file_path):
                cornerstone_names.append(file)

        return cornerstone_names
