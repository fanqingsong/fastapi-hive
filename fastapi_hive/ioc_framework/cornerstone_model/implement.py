
from fastapi import FastAPI
from abc import ABC,abstractmethod


class CornerstoneHooks(ABC):
    '''
    Base class for cornerstone hooks.

    Usage
    ===

    In your cornerstone cornerstones `__init__.py` create a subclass of `CornerstoneHooks`

    ```python
    from fastapi_hive.ioc_framework.cornerstone_model import CornerstoneHooks


    class CornerstoneImpl(CornerstoneHooks):
        def pre_endpoint_setup(self):
            pass
    ```
    '''

    def __init__(self, app: FastAPI) -> None:
        self._app = app

    @abstractmethod
    def pre_endpoint_setup(self):
        pass

    @abstractmethod
    def post_endpoint_setup(self):
        pass

    @abstractmethod
    def pre_endpoint_teardown(self):
        pass

    @abstractmethod
    def post_endpoint_teardown(self):
        pass


class CornerstoneAsyncHooks:
    '''
    Base class for cornerstone cornerstones in async mode.

    Usage
    ===

    In your cornerstone cornerstones `__init__.py` create a subclass of `CornerstoneAsyncHooks`

    ```python
    from fastapi_hive.ioc_framework.cornerstone_model import CornerstoneAsyncHooks


    class CornerstoneAsyncImpl(CornerstoneAsyncHooks):
        async def pre_endpoint_setup(self):
            pass
    ```
    '''

    def __init__(self, app: FastAPI) -> None:
        self._app = app

    @abstractmethod
    async def pre_endpoint_setup(self):
        pass

    @abstractmethod
    async def post_endpoint_setup(self):
        pass

    @abstractmethod
    async def pre_endpoint_teardown(self):
        pass

    @abstractmethod
    async def post_endpoint_teardown(self):
        pass


class CornerstoneMeta:
    def __init__(self):
        self._name: Optional[str] = None
        self._package: Optional[str] = None
        self._imported_module = None

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

