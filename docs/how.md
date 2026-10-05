# How

FastAPI Hive Framework is the solution to the problems in "why" chapter.
In this chapter, let see how to apply it in project.

---

## Install it.

The package published on PyPI can lag behind this repository. Install from the local source instead.

```bash
git clone git@github.com:fanqingsong/fastapi-hive.git
cd fastapi-hive
pip3 install .
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


From code view, the startup or shutdown hooks should be set in __init__.py if needed.

Decorate the hook class. `order` decides who runs first in the same phase. `profiles` must overlap `ACTIVE_PROFILES` when it is set. `enabled_when` reads a dotted key from `FEATURES`. `@provides` / `@component` register beans on `HiveContext`. Lifecycle methods cannot use `@provides`. Hook parameters and `Inject` resolve the same keys. `@autoconfigure` + `@conditional` load optional starters.

Only decorated hook classes are loaded. Methods may be `def` or `async def`. `configure()` on a cornerstone must stay synchronous so middleware can be registered before the app starts. Blocking I/O in a hook should use `anyio.to_thread.run_sync`.

Beans stay on an `@autoconfigure` class. Cornerstone hooks, such as `example/cornerstone/db`, stay on `@cornerstone`.

For a cornerstone bean

```Python

from fastapi_hive.ioc_framework.decorators import autoconfigure, provides
from example.cornerstone.auth.implement import validate_http_request


@autoconfigure(name="hive.auth", order=100)
class AuthAuto:

    @provides("auth.ok")
    def checker(self):
        return validate_http_request

```


Endpoint lifecycle stays on `@endpoint`. The model factory is separate:

For an endpoint bean

```Python

from fastapi_hive.ioc_framework.decorators import autoconfigure, provides
from example.endpoints_package1.house_price.service.implement import HousePriceModel
from example.endpoints_package1.house_price.config import DEFAULT_MODEL_PATH


@autoconfigure(name="house_price.model")
class HousePriceModelAuto:

    @provides(HousePriceModel)
    def model(self):
        return HousePriceModel(DEFAULT_MODEL_PATH)

```

Routes read registered objects with `Inject`:

```Python

from fastapi_hive.ioc_framework.registry import Inject

def post_predict(model: HousePriceModel = Inject(HousePriceModel)):
    return model.predict(block_data)

```

For the hooks running flow, please reference the belowing diagram:
Note: it only depict the startup flow, it is same as shutdown flow.

![startup_flow](img/startup_flow.png)


### Setup hive framework init codes 

Second, bootstrap the container. Convention looks for `cornerstone(s)/` and
`endpoints/` beside the caller or the working directory. Put the rest in
`hive.yaml` (beside that caller, or in the working directory) or in `HIVE_*`
environment variables. The sample file is `example/hive.yaml`.

```Python
from fastapi import FastAPI
from loguru import logger
from example.cornerstone.config import APP_NAME, APP_VERSION, IS_DEBUG

from fastapi_hive.ioc_framework import IoCFramework


def get_app() -> FastAPI:
    logger.info("app is starting.")
    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)
    IoCFramework.bootstrap(fast_app)
    return fast_app


app = get_app()
```

```yaml
# example/hive.yaml — paths are relative to this file
hive:
  api_prefix: /api
  cornerstone_package_path: ./cornerstone
  endpoint_package_paths:
    - ./endpoints_package1
    - ./endpoints_package2
  hide_endpoint_container_in_api: true
  hide_endpoint_in_tag: true
```

Programmatic assignment (`hive.config.API_PREFIX = ...`) still works and wins
over env and file.

## URL MAPPING

The framework discovers cornerstones and endpoints in the same load pass.
While an endpoint package is imported, the loader walks every submodule and
collects each module-level `APIRouter` named `router` onto `EndpointMeta.routers`
(the same object exported from several modules is mounted once). After endpoint
startup hooks run, a built-in caller mounts those collected routers.

The default URL is built from the API prefix, the endpoint container folder
name, and the endpoint folder name, so paths stay unique and predictable.

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
{API_PREFIX}/endpoint_packages/heartbeat/xxx
{API_PREFIX}/endpoint_packages/prediction/yyy
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

`@endpoint(prefix=..., tags=...)` replaces the generated prefix and OpenAPI tag.
The example `heart_beat2` module mounts at `/api/hb2` instead of
`/api/heart_beat2`. `GET /hive/routers` on the example app lists every collected
binding.

If you want to disable automatic mounting, set `ROUTER_MOUNT_AUTOMATED = False`
(or `router_mount_automated: false` in `hive.yaml`) and register the router in
a startup hook:

example/endpoints_package1/house_price/router/__init__.py


```python

from example.endpoints_package1.house_price.router.implement import router

from fastapi import FastAPI
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks
from fastapi_hive.ioc_framework.decorators import endpoint


@endpoint(name="house_price", mount=False)
class EndpointHooksImpl(EndpointHooks):

    def startup(self):
        print("call pre startup from EndpointHooksImpl (service)!!!")

        app: FastAPI = self.app

        app.include_router(router, tags=["house price"], prefix="/v1/house_price1")

```
