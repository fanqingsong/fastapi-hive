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
| `@endpoint(name, order=0, profiles=None, enabled_when=None)` | business module. Define the class in the endpoint package root. Mount routers in `startup` with `self.app.include_router`. |
| `@provides(key, scope="app")` | register a factory method as a bean. `scope` is `app`, `request`, or `transient`. Lifecycle methods cannot use `@provides`. |
| `@component` | register a class constructor as a bean. Default key is the class. |
| `@autoconfigure(name, order=0, after=(), before=())` | mark a starter class. Loaded from scan, entry points, or `AUTOCONFIGURE_IMPORTS`. |
| `@conditional(...)` | AND conditions: `on_import`, `on_missing`, `on_bean`, `enabled_when`, `profiles`, `on_property`. |
| `Inject(key)` | FastAPI dependency that calls `HiveContext.get`. |

`profiles` must overlap `ACTIVE_PROFILES` when it is set. `enabled_when` is a dotted key in `FEATURES`.

Bean creation: request cache, then app cache, then factory. App-scoped beans are created at `refresh()`. Request-scoped beans are created on first `get` in that request. Duplicate keys without a single `primary` fail at startup. Cycles fail. Missing keys raise `KeyError`.

Conditions: first `on_import` / `profiles` / `enabled_when` / `on_property`; then autoconfigure `after`/`before`; then rounds of `on_bean` / `on_missing`. A user-provided bean with the same key suppresses a starter that declares `on_missing`.

Routes should use `Inject(key)` because FastAPI builds the dependency graph at import time. Hook parameters can use type hints. If a resolved value is a callable whose only required argument is `Request`, `Inject` calls it.

## endpoint routers

----

The framework does not collect or mount `APIRouter` objects. In an `@endpoint`
`startup` hook, call `self.app.include_router(router, prefix=..., tags=...)`.
See `example/endpoints_package1/house_price/__init__.py`.


## cornerstone hooks

----

The framework provides `CornerstoneHooks`. Decorate a subclass with `@cornerstone`. Hook methods may be `def` or `async def`, except `configure()`, which must stay synchronous. Blocking I/O should use `anyio.to_thread.run_sync`.

Hook methods and `__init__` receive dependencies by parameter. Built-in extras:

| name | type | meaning |
| --- | --- | --- |
| app | `FastAPI` | the FastAPI application |
| cornerstone | `CornerstoneMeta` | metadata of this cornerstone |

Published Hive keys are injected the same way: a type hint or `Inject(key)`. `self.app` and `self.cornerstone` remain available as context after bind. Per-request work belongs in middleware registered from `configure()`.



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

    def after_endpoint_startup(self):
        create_all_tables(self.app)
```


## endpoint hooks

----

The framework provides `EndpointHooks`. Decorate a subclass with `@endpoint`. `startup` and `shutdown` may be `def` or `async def`.

Hook methods and `__init__` receive dependencies by parameter. Built-in extras:

| name | type | meaning |
| --- | --- | --- |
| app | `FastAPI` | the FastAPI application |
| endpoint | `EndpointMeta` | metadata of this endpoint |

Published Hive keys are injected the same way as on cornerstone hooks. `self.app` / `self.endpoint` remain available as context after bind.


please check in the code for usages.

`@endpoint` classes must be defined in the endpoint package root (`__init__.py`).
A class in a submodule such as `router/` fails at load time. `@component` and
`@autoconfigure` are still scanned from every submodule, so a bean factory does
not have to live on the hook class.

example/endpoints_package1/house_price/service/__init__.py

```python
from example.endpoints_package1.house_price.service.implement import HousePriceModel
from example.endpoints_package1.house_price.config import DEFAULT_MODEL_PATH
from fastapi_hive.ioc_framework.decorators import autoconfigure, provides


@autoconfigure(name="house_price.model")
class HousePriceModelAuto:

    @provides(HousePriceModel)
    def model(self):
        return HousePriceModel(DEFAULT_MODEL_PATH)
```

The router receives the model with `Inject`:

```python
from fastapi_hive.ioc_framework.registry import Inject

def post_predict(model: HousePriceModel = Inject(HousePriceModel)):
    return model.predict(block_data)
```

