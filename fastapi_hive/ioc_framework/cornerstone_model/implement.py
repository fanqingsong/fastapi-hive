

class Cornerstone:
    '''
    Base class for cornerstone modules.

    Usage
    ===

    In your cornerstone modules `__init__.py` create a subclass of `Cornerstone`

    ```python
    from fastapi_hive.ioc_framework import Cornerstone


    class CornerstoneImpl(Cornerstone):
        def pre_setup(self):
            pass
    ```
    '''

    def __init__(self) -> None:
        pass

    def pre_setup(self):
        pass

    def post_setup(self):
        pass

    def pre_teardown(self):
        pass

    def post_teardown(self):
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

