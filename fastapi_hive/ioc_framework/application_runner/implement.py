from typing import List, Optional, Sequence

from fastapi import FastAPI
from loguru import logger

from fastapi_hive.ioc_framework.autoconfigure import load_dotted
from fastapi_hive.ioc_framework.decorators import (
    bind_runner,
    collect_hooks,
    create_hook,
    invoke,
    select_hooks,
)
from fastapi_hive.ioc_framework.ioc_config import IoCConfig


class ApplicationRunner:
    """Application-level callback after foundation and endpoint startup."""

    def __init__(self) -> None:
        self._app: Optional[FastAPI] = None

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, value: FastAPI):
        self._app = value

    def run(self):
        pass


def collect_runner_classes(modules: Sequence, config: IoCConfig) -> List[type]:
    by_name = {}

    def add(cls: type) -> None:
        hive = getattr(cls, "__hive__", None)
        if hive is None or hive.role != "runner":
            raise TypeError(f"{cls!r} is not an @runner class")
        existing = by_name.get(hive.name)
        if existing is not None and existing is not cls:
            raise ValueError(f"duplicate runner name {hive.name!r}")
        by_name[hive.name] = cls

    for module in modules:
        for cls in collect_hooks(module, role="runner"):
            add(cls)
    for path in getattr(config, "RUNNER_IMPORTS", None) or []:
        if not path or path in ("[]", ".",):
            continue
        add(load_dotted(path))
    return list(by_name.values())


class ApplicationRunnerCaller:
    def __init__(self, app: FastAPI, classes: Sequence[type], ioc_config: IoCConfig):
        logger.info("application runner caller is initializing.")
        self._app = app
        self._classes = list(classes)
        self._ioc_config = ioc_config

    async def run_all(self):
        logger.info("running application runners...")
        context = getattr(self._app.state, "hive", None)
        extras = {FastAPI: self._app}
        pairs = [(cls, None) for cls in self._classes]
        for cls, _ in select_hooks(pairs, self._ioc_config):
            instance = create_hook(cls, context, extras)
            bind_runner(instance, self._app)
            await invoke(instance, "run", context, extras=extras)
