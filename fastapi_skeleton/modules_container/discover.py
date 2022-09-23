import importlib
import os


class Discover():
    def __init__(self):
        self._modules = {}

        self._module_path = "./fastapi_skeleton/modules"

        self._load_modules()

    @property
    def modules(self):
        return self._modules

    def _get_module_names(self):
        folder_names = os.listdir(self._module_path)

        module_names = [one_name for one_name in folder_names if one_name != "__init__.py" and one_name != "__pycache__"]

        return module_names

    def _get_module_paths(self):
        module_names = self._get_module_names()

        module_paths = {}

        for one_name in module_names:
            one_module_paths = {}

            module_path = os.path.join("fastapi_skeleton/modules", one_name)

            service_path = os.path.join(module_path, "service")
            router_path = os.path.join(module_path, "router")

            service_path = service_path.replace(os.path.sep, ".")
            router_path = router_path.replace(os.path.sep, ".")

            one_module_paths["service"] = service_path
            one_module_paths["router"] = router_path

            module_paths[one_name] = one_module_paths

        return module_paths

    def _load_modules(self):
        module_paths = self._get_module_paths()

        for one_module in module_paths:
            one_module_entity = {}

            one_module_paths = module_paths[one_module]

            service_path = one_module_paths["service"]
            router_path = one_module_paths["router"]

            one_module_entity["service"] = importlib.import_module(service_path)
            one_module_entity["router"] = importlib.import_module(router_path)

            self._modules[one_module] = one_module_entity

    def get_module(self, module_name: str):
        module_name = module_name.upper()

        for one_name, one_entity in self._modules.items():
            one_name = one_name.upper()
            if module_name == one_name:
                return one_entity


discover = Discover()


