import importlib
import os
import pkgutil
from typing import List, Optional

from loguru import logger
from fastapi_hive.ioc_framework.decorators import (
    collect_hooks,
    collect_routers,
    endpoint_hook_order,
    resolve_mount,
)


def import_package_tree(package_name: str) -> List:
    root = importlib.import_module(package_name)
    modules = [root]
    paths = getattr(root, "__path__", None)
    if paths is None:
        return modules
    for module_info in pkgutil.walk_packages(paths, root.__name__ + "."):
        leaf = module_info.name.rsplit(".", 1)[-1]
        if leaf == "__pycache__":
            continue
        modules.append(importlib.import_module(module_info.name))
    return modules


class EndpointMeta:
    def __init__(self):
        self._name: Optional[str] = None
        self._container_name: Optional[str] = None
        self._package_path: Optional[str] = None
        self._imported_module = None
        self.imported_modules = []
        self.hooks = []
        self.mount_spec = resolve_mount([])
        self.routers = []

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


class EndpointContainer:
    def __init__(self):
        self._endpoints = {}
        self._endpoint_package_paths = set([])

    @property
    def endpoints(self):
        return self._endpoints

    def register_endpoint_package_paths(self, endpoint_package_paths):
        endpoint_package_paths = set(endpoint_package_paths)
        current_package_paths = self._endpoint_package_paths

        self._endpoint_package_paths = current_package_paths | endpoint_package_paths

        logger.info(
            f"after registering, endpoint container_name paths = {self._endpoint_package_paths}")

    def load_endpoints(self):
        endpoint_package_paths = self._endpoint_package_paths
        logger.info(f"endpoint container_name paths = {endpoint_package_paths}")

        for one_package_path in endpoint_package_paths:
            endpoint_paths = self._get_endpoint_paths(one_package_path)
            container_name = os.path.basename(one_package_path)

            for one_endpoint_name in endpoint_paths:
                one_endpoint_path = endpoint_paths[one_endpoint_name]

                imported_modules = import_package_tree(one_endpoint_path)
                one_endpoint_entity = imported_modules[0]

                endpoint_instance = EndpointMeta()
                endpoint_instance.name = one_endpoint_name
                endpoint_instance.container_name = container_name
                endpoint_instance.package_path = one_package_path
                endpoint_instance.imported_module = one_endpoint_entity
                endpoint_instance.imported_modules = imported_modules

                hooks = []
                seen_hooks = set()
                for module in imported_modules:
                    for cls in collect_hooks(module, role="endpoint"):
                        if cls in seen_hooks:
                            continue
                        seen_hooks.add(cls)
                        hooks.append(cls)

                endpoint_instance.hooks = hooks
                endpoint_instance.mount_spec = resolve_mount(hooks)
                endpoint_instance.routers = collect_routers(
                    imported_modules,
                    mount_spec=endpoint_instance.mount_spec,
                    order=endpoint_hook_order(hooks),
                    name=one_endpoint_name,
                )

                self._endpoints[f'{container_name}.{one_endpoint_name}'] = endpoint_instance

    def get_endpoint(self, endpoint_name: str):
        endpoint_name = endpoint_name.upper()

        for one_name, one_endpoint in self._endpoints.items():
            one_name = one_name.upper()
            if endpoint_name == one_name:
                return one_endpoint

    def _get_endpoint_paths(self, package_path):
        endpoint_names = self._get_endpoint_names(package_path)

        endpoint_paths = {}

        for one_name in endpoint_names:
            endpoint_path = os.path.join(package_path, one_name)

            endpoint_path = endpoint_path.replace("./", "")
            endpoint_path = endpoint_path.replace(os.path.sep, ".")

            logger.info(f"endpoint path = {endpoint_path}")

            endpoint_paths[one_name] = endpoint_path

        return endpoint_paths

    def _get_endpoint_names(self, package_path):
        folder_names = os.listdir(package_path)

        endpoint_names = []

        for file in folder_names:
            if file == '__pycache__':
                continue

            file_path = os.path.join(package_path, file)

            if os.path.isdir(file_path):
                endpoint_names.append(file)

        return endpoint_names
