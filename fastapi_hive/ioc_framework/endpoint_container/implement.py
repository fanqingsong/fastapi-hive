import importlib
import os
from loguru import logger
from fastapi_hive.ioc_framework.endpoint_model import EndpointMeta


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
            f"after registering, endpoint package paths = {self._endpoint_package_paths}")

    def unregister_endpoint_package_paths(self, endpoint_package_paths):
        endpoint_package_paths = set(endpoint_package_paths)
        current_package_paths = self._endpoint_package_paths

        self._endpoint_package_paths = current_package_paths - endpoint_package_paths

        logger.info(
            f"after unregistering, endpoint package paths = {self._endpoint_package_paths}")

    def load_endpoints(self):
        endpoint_package_paths = self._endpoint_package_paths
        logger.info(f"endpoint package paths = {endpoint_package_paths}")

        for one_package_path in endpoint_package_paths:
            endpoint_paths = self._get_endpoint_paths(one_package_path)
            package_name = os.path.basename(one_package_path)

            for one_endpoint_name in endpoint_paths:
                one_endpoint_path = endpoint_paths[one_endpoint_name]

                one_endpoint_entity = importlib.import_module(one_endpoint_path)

                endpoint_instance = EndpointMeta()
                endpoint_instance.name = one_endpoint_name
                endpoint_instance.package = package_name
                endpoint_instance.imported_module = one_endpoint_entity

                # cache regular submodule - db
                if os.path.exists(f'{one_package_path}/{one_endpoint_name}/db'):
                    endpoint_instance.imported_module_db = importlib.import_module(f'{one_endpoint_path}.db')

                # cache regular submodule - router
                if os.path.exists(f'{one_package_path}/{one_endpoint_name}/router'):
                    endpoint_instance.imported_module_router = importlib.import_module(f'{one_endpoint_path}.router')

                # cache regular submodule - service, such as ML model loading cost time
                if os.path.exists(f'{one_package_path}/{one_endpoint_name}/service'):
                    endpoint_instance.imported_module_service = importlib.import_module(f'{one_endpoint_path}.service')

                endpoint_instance.service = one_endpoint_entity.service

                self._endpoints[one_endpoint_name] = endpoint_instance

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

