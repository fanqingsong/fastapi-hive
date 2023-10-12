
from fastapi import APIRouter, FastAPI
from typing import Optional
from abc import ABC, abstractmethod


class EndpointHooks(ABC):
    '''
    Base class for EndpointHooks cornerstones.

    Usage
    ===

    In your EndpointHooks cornerstones `__init__.py` create a subclass of `EndpointHooks`

    ```python
    from fastapi_hive.ioc_framework.endpoint_model import EndpointHooks


    class EndpointHooksImpl(EndpointHooks):
        def setup(self):
            pass
    ```
    '''

    def __init__(self, app: FastAPI) -> None:
        self._app = app

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def teardown(self):
        pass


class EndpointAsyncHooks(ABC):
    '''
    Base class for EndpointHooks cornerstones in async mode.

    Usage
    ===

    In your EndpointHooks cornerstones `__init__.py` create a subclass of `EndpointAsyncHooks`

    ```python
    from fastapi_hive.ioc_framework.endpoint_model import EndpointAsyncHooks


    class EndpointAsyncHooksImpl(EndpointAsyncHooks):
        async def setup(self):
            pass
    ```
    '''

    def __init__(self, app: FastAPI) -> None:
        self._app = app

    @abstractmethod
    async def setup(self):
        pass

    @abstractmethod
    async def teardown(self):
        pass


class EndpointMeta:
    def __init__(self):
        self._name: Optional[str] = None
        self._package: Optional[str] = None
        self._imported_module = None
        self._imported_module_db = None
        self._imported_module_router = None
        self._imported_module_service = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def package(self) -> str:
        return self._package

    @package.setter
    def package(self, value: str):
        self._package = value

    @property
    def imported_module(self):
        return self._imported_module

    @imported_module.setter
    def imported_module(self, value):
        self._imported_module = value

    @property
    def imported_module_db(self):
        return self._imported_module_db

    @imported_module_db.setter
    def imported_module_db(self, value):
        self._imported_module_db = value

    @property
    def imported_module_router(self):
        return self._imported_module_router

    @imported_module_router.setter
    def imported_module_router(self, value):
        self._imported_module_router = value

    @property
    def imported_module_service(self):
        return self._imported_module_service

    @imported_module_service.setter
    def imported_module_service(self, value):
        self._imported_module_service = value
