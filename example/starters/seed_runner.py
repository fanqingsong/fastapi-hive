"""Loaded by hive.runners.imports, not owned by a foundation module."""

from fastapi import FastAPI

from fastapi_hive.ioc_framework.application_runner import ApplicationRunner
from fastapi_hive.ioc_framework.decorators import runner
from fastapi_hive.ioc_framework.registry import Inject


@runner(name="seed-data", order=10, profiles=["demo"])
class SeedDataRunner(ApplicationRunner):

    def run(self, app: FastAPI, imported=Inject("showcase.imported")):
        app.state.hive_lifecycle.append("runner:" + imported)


@runner(name="never-seed", profiles=["never"])
class NeverSeedRunner(ApplicationRunner):

    def run(self):
        raise RuntimeError("disabled application runner must not run")
