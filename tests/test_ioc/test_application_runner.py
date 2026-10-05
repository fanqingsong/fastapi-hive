import asyncio
import types

import pytest
from fastapi import FastAPI

from fastapi_hive.ioc_framework.application_runner import (
    ApplicationRunner,
    ApplicationRunnerCaller,
    collect_runner_classes,
)
from fastapi_hive.ioc_framework.decorators import collect_hooks, foundation, provides, runner
from fastapi_hive.ioc_framework.foundation_hooks import FoundationHooks
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from fastapi_hive.ioc_framework.registry import HiveRegistry, Inject


def test_runner_is_not_a_foundation_hook():
    module = types.ModuleType("mixed")

    @foundation(name="db")
    class DbHooks(FoundationHooks):
        pass

    @runner(name="seed")
    class Seed(ApplicationRunner):
        pass

    module.DbHooks = DbHooks
    module.Seed = Seed

    assert collect_hooks(module, role="foundation") == [DbHooks]
    assert collect_hooks(module, role="runner") == [Seed]


def test_collect_runner_classes_imports_and_rejects_duplicates():
    module = types.ModuleType("scanned")

    @runner(name="from-scan", order=2)
    class FromScan(ApplicationRunner):
        pass

    module.FromScan = FromScan
    config = IoCConfig(RUNNER_IMPORTS=["example.starters.seed_runner:SeedDataRunner"])
    classes = collect_runner_classes([module], config)
    names = {cls.__hive__.name for cls in classes}
    assert names == {"from-scan", "seed-data"}

    @runner(name="seed-data")
    class OtherSeed(ApplicationRunner):
        pass

    conflict = types.ModuleType("conflict")
    conflict.OtherSeed = OtherSeed
    with pytest.raises(ValueError, match="duplicate runner name"):
        collect_runner_classes([conflict], config)


def test_collect_runner_classes_rejects_non_runner_import():
    config = IoCConfig(RUNNER_IMPORTS=["example.starters.imported_auto:ImportedAuto"])
    with pytest.raises(TypeError, match="not an @runner"):
        collect_runner_classes([], config)


def test_provides_on_run_raises():
    with pytest.raises(TypeError, match="lifecycle method"):
        @runner(name="bad")
        class BadRunner(ApplicationRunner):
            @provides("model")
            def run(self):
                return "nope"


def test_runner_caller_filters_orders_and_injects():
    app = FastAPI()
    registry = HiveRegistry()
    registry.register("banner", "ok")
    app.state.hive = registry
    log = []

    @runner(name="late", order=20)
    class Late(ApplicationRunner):
        def run(self):
            log.append("late")

    @runner(name="early", order=1)
    class Early(ApplicationRunner):
        def run(self, banner=Inject("banner")):
            log.append("early:" + banner)

    @runner(name="off", profiles=["never"])
    class Off(ApplicationRunner):
        def run(self):
            log.append("off")

    caller = ApplicationRunnerCaller(app, [Late, Off, Early], IoCConfig(ACTIVE_PROFILES=["demo"]))
    asyncio.run(caller.run_all())
    assert log == ["early:ok", "late"]
