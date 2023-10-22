# Reference


## ioc_framework configs

---

| name | description | default |
| ----- | ---- | ---- |
| CORNERSTONE_PACKAGE_PATH | cornerstone path | "./cornerstone" |
| API_PREFIX | all api prefix, usual for version, such as "v1" | "" |
| ROUTER_MOUNT_AUTOMATED | if router mounted automatically | True |
| HIDE_ENDPOINT_CONTAINER_IN_API | if endpoint container folder name showed in API | False |
| HIDE_ENDPOINT_IN_API | if endpoint name showed in API | Flase |
| HIDE_ENDPOINT_IN_TAG | if endpoint name showed in tag |
| PRE_ENDPOINT_SETUP | external pre endpoint setup | None |
| POST_ENDPOINT_SETUP | external post endpoint setup | None |
| PRE_ENDPOINT_TEARDOWN | external pre endpoint teardown | None |
| POST_ENDPOINT_TEARDOWN | external post endpoint POST_ENDPOINT_TEARDOWN | None |
| ASYNC_PRE_ENDPOINT_SETUP | external async pre endpoint setup | None |
| ASYNC_POST_ENDPOINT_SETUP | external async post endpoint setup | None |
| ASYNC_PRE_ENDPOINT_TEARDOWN | external async pre endpoint teardown | None |
| ASYNC_POST_ENDPOINT_TEARDOWN | external async post endpoint POST_ENDPOINT_TEARDOWN | None |


These configs are set before ioc framework initialization.

```python

from fastapi import FastAPI
from loguru import logger
from example.cornerstone.config import (APP_NAME, APP_VERSION, API_PREFIX,
                                        IS_DEBUG)

from fastapi_hive.ioc_framework import IoCFramework


def get_app() -> FastAPI:
    logger.info("app is starting.")

    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    def hive_pre_setup():
        logger.info("------ call pre setup -------")

    def hive_post_setup():
        logger.info("------ call post setup -------")

    async def hive_async_pre_setup():
        logger.info("------ call async pre setup -------")

    async def hive_async_post_setup():
        logger.info("------ call async post setup -------")

    ioc_framework = IoCFramework(fast_app)
    ioc_framework.config.CORNERSTONE_PACKAGE_PATH = "./example/cornerstone/"

    ioc_framework.config.API_PREFIX = API_PREFIX
    ioc_framework.config.ENDPOINT_PACKAGE_PATHS = ["./example/endpoints_package1", "./example/endpoints_package2"]
    ioc_framework.config.ROUTER_MOUNT_AUTOMATED = True
    ioc_framework.config.HIDE_ENDPOINT_CONTAINER_IN_API = True
    ioc_framework.config.HIDE_ENDPOINT_IN_API = False
    ioc_framework.config.HIDE_ENDPOINT_IN_TAG = True
    ioc_framework.config.PRE_ENDPOINT_SETUP = hive_pre_setup
    ioc_framework.config.POST_ENDPOINT_SETUP = hive_post_setup
    ioc_framework.config.ASYNC_PRE_ENDPOINT_SETUP = hive_async_pre_setup
    ioc_framework.config.ASYNC_POST_ENDPOINT_SETUP = hive_async_post_setup

    ioc_framework.init_modules()

    @fast_app.get("/")
    def get_root():
        return "Go to docs URL to look up API: http://localhost:8000/docs"

    return fast_app


app = get_app()

```

## cornerstone hooks

----

The framework provides abstract parent classes (CornerstoneHooks & CornerstoneAsyncHooks), every cornerstone instance must setup hook instace inherited from the parent classes, and can use dependency objects of parent classes.

the following is the visibility of dependency objects regarding to each hook.

| hook name | app | cornerstone | request | app_state  | request_state |
| --- | --- | --- | --- | --- | --- |
| pre_endpoint_setup | Yes | Yes | No | Yes | No |
| post_endpoint_setup | Yes | Yes | No | Yes | No |
| pre_endpoint_teardown | Yes | Yes | No | Yes | No |
| post_endpoint_teardown | Yes | Yes | No | Yes |  No |
| pre_endpoint_call | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| post_endpoint_call | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

If the visibility of one dependency object is Yes to one hook, i.e. this dependency can be used in the hook.

dependency objects are injected by framework, each object has its meaning like below:

| name | meaning |
| --- | --- |
| app | the instance of FastAPI |
| cornerstone | the meta data of the cornerstone that hook belong to |
| request | the incoming http request object |
| app_state | this cornerstone's state in app.state, hook can set key with value in this dict, and it can be accessed by request.app.state.cornerstones['cornerstone.xxx']['key'] in router implementation. |
| request_state | this cornerstone's state in request.state，hook can set key with value in this dict, and it can be accessed by request.state.cornerstones['cornerstone.xxx']['key'] in router implementation. |



please check in the code for usages.

either of sync or async mode can be used.

hooks can be set in cornerstone init file.

example/cornerstone/db/__init__.py

```python
import logging
import time
from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks, CornerstoneAsyncHooks
from example.cornerstone.db.implement import Base, create_all_tables, add_db_middleware
from fastapi import FastAPI
from starlette.requests import Request
from fastapi_sqlalchemy import db


__all__ = ['Base']


class CornerstoneHooksImpl(CornerstoneHooks):

    def __init__(self):
        super(CornerstoneHooksImpl, self).__init__()

    def pre_endpoint_setup(self):
        print("call pre setup from cornerstone db!!!")

        add_db_middleware(self.app, self.cornerstone)

        self.app_state['db'] = db

    def post_endpoint_setup(self):
        print("call post setup from cornerstone!!!")

        create_all_tables(self.app)

    def pre_endpoint_teardown(self):
        print("call pre teardown from cornerstone!!!")

    def post_endpoint_teardown(self):
        print("call pre teardown from cornerstone!!!")

    def pre_endpoint_call(self):
        print("call pre endpoint call from cornerstone!!!")

        self.request_state['db'] = db

    def post_endpoint_call(self):
        print("call post endpoint call from cornerstone!!!")


class CornerstoneAsyncHooksImpl(CornerstoneAsyncHooks):

    def __init__(self):
        super(CornerstoneAsyncHooksImpl, self).__init__()

    async def pre_endpoint_setup(self):
        print("call pre setup from cornerstone async!!!")

    async def post_endpoint_setup(self):
        print("call post setup from cornerstone async!!!")

    async def pre_endpoint_teardown(self):
        print("call pre teardown from cornerstone async!!!")

    async def post_endpoint_teardown(self):
        print("call pre teardown from cornerstone async!!!")

    async def pre_endpoint_call(self):
        print("call pre endpoint call from cornerstone async!!!")

    async def post_endpoint_call(self):
        print("call post endpoint call from cornerstone async!!!")
```


## endpoint hooks

----

The framework provides abstract parent classes (EndpointHooks & EndpointAsyncHooks), every endpoint instance can setup hook instace inherited from the parent classes, and can use dependency objects of parent classes.

the following is the visibility of dependency objects regarding to each hook.

| hook name | app | endpoint | app_state |
| --- | --- | --- | --- |
| setup | Yes | Yes | Yes |
| teardown | Yes | Yes | Yes |

If the visibility of one dependency object is Yes to one hook, i.e. this dependency can be used in the hook.

dependency objects are injected by framework, each object has its meaning like below:

| name | meaning |
| --- | --- |
| app | the instance of FastAPI |
| endpoint | the meta data of the endpoint that hook belong to |
| app_state | this endpoint's state in app.state, hook can set key with value in this dict, and it can be accessed by request.app.state.endpoints['xxx_endpoints.xxx']['key'] in router implementation. |


please check in the code for usages.

either of sync or async mode can be used.

hooks can be set in endpoint init file and three sub-modules(db/service/router) init file.

example/endpoints_package1/house_price/service/__init__.py

```python

from example.endpoints_package1.house_price.service.implement import HousePriceModel
from example.endpoints_package1.house_price.config import DEFAULT_MODEL_PATH
from fastapi import FastAPI
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks, EndpointAsyncHooks


class EndpointHooksImpl(EndpointHooks):

    def __init__(self):
        super(EndpointHooksImpl, self).__init__()

    def setup(self):
        print("call pre setup from EndpointHooksImpl (service)!!!")

        app_state = self.app_state
        app_state['house_price_model'] = HousePriceModel(DEFAULT_MODEL_PATH)

    def teardown(self):
        print("call pre teardown from EndpointHooksImpl (service)!!!")


class EndpointAsyncHooksImpl(EndpointAsyncHooks):

    def __init__(self):
        super(EndpointAsyncHooksImpl, self).__init__()

    async def setup(self):
        print("call pre setup from EndpointAsyncHooksImpl (service)!!!")

    async def teardown(self):
        print("call pre teardown from EndpointAsyncHooksImpl (service)!!!")

```

