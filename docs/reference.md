# Reference


## ioc_framework configs

---

All configuarable parameters are listed below.


| name | description | default |
| ----- | ---- | ---- |
| CORNERSTONE_PACKAGE_PATH | cornerstone path | "./cornerstone" |
| ENDPOINT_PACKAGE_PATHS | endpoint package paths | ["./endpoints"] |
| API_PREFIX | all api prefix, usual for version, such as "v1" | "" |
| ACTIVE_PROFILES | profiles that enable a decorated module | [] |
| FEATURES | feature flags read by enabled_when | {} |
| AUTOCONFIGURE_ENABLED | load `hive.autoconfigure` entry points and imports | True |
| AUTOCONFIGURE_IMPORTS | extra `module:Class` autoconfigure paths | [] |
| AUTOCONFIGURE_EXCLUDE | skip autoconfigure by name or `module:Class` | [] |
| ROUTER_MOUNT_AUTOMATED | if router mounted automatically | True |
| HIDE_ENDPOINT_CONTAINER_IN_API | if endpoint container folder name showed in API | False |
| HIDE_ENDPOINT_IN_API | if endpoint name showed in API | Flase |
| HIDE_ENDPOINT_IN_TAG | if endpoint name showed in tag | False |


These configs are loaded automatically from convention, `hive.yaml` /
`hive.yml` / `hive.json` (beside the module that calls `bootstrap`, or in the
working directory), `.env` keys with a `HIVE_` prefix, and process
environment variables. Package paths in the file are relative to that file.
Precedence is:

defaults / folder convention < config file < `.env` < process env <
`settings=` / `hive.config.*`

`IoCFramework.bootstrap(app)` constructs the container and calls
`init_modules()`. Pass `settings={...}` or `config_path=` when you do not want
the working-directory file.

```python
from fastapi import FastAPI
from fastapi_hive.ioc_framework import IoCFramework

app = FastAPI()
IoCFramework.bootstrap(app)
```

```yaml
# example/hive.yaml
hive:
  api_prefix: /api
  cornerstone_package_path: ./cornerstone
  endpoint_package_paths:
    - ./endpoints_package1
    - ./endpoints_package2
  hide_endpoint_container_in_api: true
  hide_endpoint_in_tag: true
```

```python
# optional code override, still supported
hive = IoCFramework(app, settings={"API_PREFIX": "/api"})
hive.init_modules()
```

## module decorators

----

Decorate the hook class so the container can discover it. Undecorated classes are ignored.

| decorator | purpose |
| --- | --- |
| `@cornerstone(name, order=0, profiles=None, enabled_when=None)` | infrastructure module. `configure()` runs while the app is assembled and must be synchronous. Other hooks run from the async lifecycle. |
| `@endpoint(name, order=0, prefix=None, tags=None, mount=True, profiles=None, enabled_when=None)` | business module. `prefix` and `tags` override automatic router mounting. `mount=False` leaves mounting to `startup`. |
| `@provides(key, scope="app")` | register a factory method as a bean. `scope` is `app`, `request`, or `transient`. Lifecycle methods cannot use `@provides`. |
| `@component` | register a class constructor as a bean. Default key is the class. |
| `@autoconfigure(name, order=0, after=(), before=())` | mark a starter class. Loaded from scan, entry points, or `AUTOCONFIGURE_IMPORTS`. |
| `@conditional(...)` | AND conditions: `on_import`, `on_missing`, `on_bean`, `enabled_when`, `profiles`, `on_property`. |
| `Inject(key)` | FastAPI dependency that calls `HiveContext.get`. |

`profiles` must overlap `ACTIVE_PROFILES` when it is set. `enabled_when` is a dotted key in `FEATURES`.

Bean creation: request cache, then app cache, then factory. App-scoped beans are created at `refresh()`. Request-scoped beans are created on first `get` in that request. Duplicate keys without a single `primary` fail at startup. Cycles fail. Missing keys raise `KeyError`.

Conditions: first `on_import` / `profiles` / `enabled_when` / `on_property`; then autoconfigure `after`/`before`; then rounds of `on_bean` / `on_missing`. A user-provided bean with the same key suppresses a starter that declares `on_missing`.

Routes should use `Inject(key)` because FastAPI builds the dependency graph at import time. Hook parameters can use type hints. If a resolved value is a callable whose only required argument is `Request`, `Inject` calls it.

## router collection

----

Endpoint loading walks every submodule of the endpoint package and collects hooks and routers together. A module-level `APIRouter` named `router` becomes an `EndpointMeta.routers` entry (`RouterBinding`: the router, mount spec, order, and name). The same router object exported from more than one module is collected once. Automatic mounting consumes that list with the same order as endpoint hooks.

| helper | purpose |
| --- | --- |
| `collect_routers(module, mount_spec=..., order=..., name=...)` | pick module-level `APIRouter` objects named `router` from one module or a sequence |
| `select_routers(pairs)` | drop `mount=False` bindings and sort by order, then name |
| `resolve_router_target(meta, binding, config)` | build prefix and tags from `API_PREFIX`, `HIDE_*`, or an explicit `@endpoint` mount |

Set `prefix` / `tags` on `@endpoint` to override the generated URL. See `example/endpoints_package2/heart_beat2`.

## cornerstone hooks

----

The framework provides `CornerstoneHooks`. Decorate a subclass with `@cornerstone`. Hook methods may be `def` or `async def`, except `configure()`, which must stay synchronous. Blocking I/O should use `anyio.to_thread.run_sync`.

Hook methods and `__init__` receive dependencies by parameter. Built-in extras:

| name | type | meaning |
| --- | --- | --- |
| app | `FastAPI` | the FastAPI application |
| cornerstone | `CornerstoneMeta` | metadata of this cornerstone |
| request | `Request` | the incoming HTTP request (`pre_endpoint_call` / `post_endpoint_call` only) |

Published Hive keys are injected the same way: a type hint or `Inject(key)`. `self.app` / `self.cornerstone` / `self.request` remain available as context after bind.



please check in the code for usages.

hooks can be set in cornerstone init file.

example/cornerstone/db/__init__.py

```python
from fastapi import FastAPI
from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks
from fastapi_hive.ioc_framework.decorators import autoconfigure, conditional, cornerstone, provides
from example.cornerstone.db.implement import Base, create_all_tables, add_db_middleware
from fastapi_sqlalchemy import db


__all__ = ['Base']


class LazyDBSession:
    def __init__(self, database):
        self._database = database

    def __getattr__(self, name):
        return getattr(self._database.session, name)


@autoconfigure(name="hive.db")
@conditional(on_import="fastapi_sqlalchemy", enabled_when="db")
class SqlAlchemyAuto:

    def configure(self, app: FastAPI):
        add_db_middleware(app, None)

    @provides("db")
    def engine(self):
        return db

    @provides("db.session", scope="request")
    def session(self):
        return LazyDBSession(db)


@cornerstone(name="db", order=0)
class CornerstoneHooksImpl(CornerstoneHooks):

    def post_endpoint_startup(self):
        create_all_tables(self.app)
```


## endpoint hooks

----

The framework provides `EndpointHooks`. Decorate a subclass with `@endpoint`. `startup` and `shutdown` may be `def` or `async def`.

Hook methods and `__init__` receive dependencies by parameter. Built-in extras:

| name | type | meaning |
| --- | --- | --- |
| app | `FastAPI` | the FastAPI application |
| endpoint | `EndpointMeta` | metadata of this endpoint. `endpoint.routers` is the list collected from module-level `router` objects. |

Published Hive keys are injected the same way as on cornerstone hooks. `self.app` / `self.endpoint` remain available as context after bind.


please check in the code for usages.

hooks can be set in any submodule of the endpoint package. `@component` is scanned the same way, so it does not have to live under `db`, `router`, or `service`.

example/endpoints_package1/house_price/service/__init__.py

```python
from example.endpoints_package1.house_price.service.implement import HousePriceModel
from example.endpoints_package1.house_price.config import DEFAULT_MODEL_PATH
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks
from fastapi_hive.ioc_framework.decorators import endpoint, provides


@endpoint(name="house_price")
class EndpointHooksImpl(EndpointHooks):

    @provides(HousePriceModel)
    def model(self):
        return HousePriceModel(DEFAULT_MODEL_PATH)

    def startup(self):
        pass

    def shutdown(self):
        pass
```

The router receives the model with `Inject`:

```python
from fastapi_hive.ioc_framework.registry import Inject

def post_predict(model: HousePriceModel = Inject(HousePriceModel)):
    return model.predict(block_data)
```

