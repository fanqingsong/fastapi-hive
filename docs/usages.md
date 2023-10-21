# How to integrate it in you project?

FastAPI Hive Framework is the solution to the problems in "why" chapter.
In this chapter, let see how to apply it in project.

---

## Install it.

```bash
pip3 install fastapi_hive
```


---

## Integrate it into your app

Note: You can reference example code to complete this part. 

### Make packages of cornerstones and endpoints

First, create or refactor you code into cornerstones and endpoints folders:

![module folders](img/module_folders.png)

Code Folder Structure

    app
        cornerstones
            db
                __init__.py
                implement.py
            auth
                __init__.py
                implement.py
        endpoint_packages
            heartbeat
                api.py
                models.py
                service.py
                __init__.py
            house_price
                api.py
                models.py
                service.py
                __init__.py


From code view, the setup or teardown hooks should be set in __init__.py if needed.

For cornerstone

```Python

from fastapi import FastAPI
from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks, CornerstoneAsyncHooks
from example.cornerstone.auth.implement import validate_request


class CornerstoneHooksImpl(CornerstoneHooks):

    def __init__(self):
        super(CornerstoneHooksImpl, self).__init__()

    def pre_endpoint_setup(self):
        print("call pre setup from CornerstoneHooksImpl!!!")
        print("---- get fastapi app ------")
        print(self.app)

    def post_endpoint_setup(self):
        print("call post setup from CornerstoneHooksImpl!!!")

    def pre_endpoint_teardown(self):
        print("call pre teardown from CornerstoneHooksImpl!!!")

    def post_endpoint_teardown(self):
        print("call pre teardown from CornerstoneHooksImpl!!!")

    def pre_endpoint_call(self):
        pass

    def post_endpoint_call(self):
        pass


class CornerstoneAsyncHooksImpl(CornerstoneAsyncHooks):

    def __init__(self):
        super(CornerstoneAsyncHooksImpl, self).__init__()

    async def pre_endpoint_setup(self):
        print("call pre setup from CornerstoneAsyncHooksImpl!!!")

    async def post_endpoint_setup(self):
        print("call post setup from CornerstoneAsyncHooksImpl!!!")

    async def pre_endpoint_teardown(self):
        print("call pre teardown from CornerstoneAsyncHooksImpl!!!")

    async def post_endpoint_teardown(self):
        print("call pre teardown from CornerstoneAsyncHooksImpl!!!")

    async def pre_endpoint_call(self):
        pass

    async def post_endpoint_call(self):
        pass

```


For endpoint

```Python

from fastapi import FastAPI
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks, EndpointAsyncHooks


class EndpointHooksImpl(EndpointHooks):

    def __init__(self):
        super(EndpointHooksImpl, self).__init__()

    def setup(self):
        print("call pre setup from EndpointHooksImpl!!!")
        print("---- get fastapi app ------")
        print(self.app)

    def teardown(self):
        print("call pre teardown from EndpointHooksImpl!!!")


class EndpointAsyncHooksImpl(EndpointAsyncHooks):

    def __init__(self):
        super(EndpointAsyncHooksImpl, self).__init__()

    async def setup(self):
        print("call pre setup from EndpointAsyncHooksImpl!!!")

    async def teardown(self):
        print("call pre teardown from EndpointAsyncHooksImpl!!!")


```

For the hooks running flow, please reference the belowing diagram:
Note: it only depict the startup flow, it is same as shutdown flow.

![startup_flow](img/startup_flow.png)


### Setup hive framework init codes 

Second, setup the initial code snippet of ioc_framework in main.py

```Python


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

## URL MAPPING

As you know, this framework will discover and load all cornerstones and endpoints in all packages automatically.
The API endpoint URLs will be constructed by endpoint container folder name or endpoint folder name, in order to avoid conflicts and be sensible.

If the folder structure likes below

```text
    app
        endpoint_packages
            heartbeat
                router.py
                models.py
                service.py
            prediction
                router.py
                models.py
                service.py
        main.py
```

Then, the API URLs will be like below:

```text
{API_PREFIX}/packages/heartbeat/xxx
{API_PREFIX}/packages/prediction/yyy
```

Note:

1. xxx url path is defined in endpoint_packages/heartbeat/router.py
2. yyy url path is defined in endpoint_packages/prediction/router.py

if your app don't want to display container_name name in URL, you can turn on HIDE_PACKAGE_IN_URL of configuration,
After turnning off, the endpoint URLs will be like:

```text
{API_PREFIX}/heartbeat/xxx
{API_PREFIX}/prediction/yyy
```
