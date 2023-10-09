
from fastapi import APIRouter
from typing import Optional


class Endpoint:
    def __init__(self):
        self._name: Optional[str] = None
        self._package: Optional[str] = None
        self._imported_module = None
        self._service = None
        self._router: Optional[APIRouter] = None

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
    def service(self):
        return self._service

    @service.setter
    def service(self, value):
        self._service = value

    @property
    def router(self) -> APIRouter:
        return self._router

    @router.setter
    def router(self, value: APIRouter):
        self._router = value
