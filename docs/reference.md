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
| `@provides(key)` | register the method return value on the application registry. `key` is a type or a string. |
| `@request_provides(key)` | register the method return value on the current request registry. |

`profiles` must overlap `ACTIVE_PROFILES` when it is set. `enabled_when` is a dotted key in `FEATURES`; a missing or false value skips the module. Hooks in one phase run by ascending `order`, then by name.

Routes read a published value with `DependsHive(key)`. The request registry is checked first, then the application registry.

## router collection

----

Endpoint loading collects hooks and routers together. A `router` subpackage that exports `APIRouter` as `router` becomes an `EndpointMeta.routers` entry (`RouterBinding`: the router, mount spec, order, and name). Automatic mounting consumes that list with the same order as endpoint hooks.

| helper | purpose |
| --- | --- |
| `collect_routers(module, mount_spec=..., order=..., name=...)` | pick the conventional `router` attribute |
| `select_routers(pairs)` | drop `mount=False` bindings and sort by order, then name |
| `resolve_router_target(meta, binding, config)` | build prefix and tags from `API_PREFIX`, `HIDE_*`, or an explicit `@endpoint` mount |

Set `prefix` / `tags` on `@endpoint` to override the generated URL. See `example/endpoints_package2/heart_beat2`.

## cornerstone hooks

----

The framework provides `CornerstoneHooks`. Decorate a subclass with `@cornerstone`. Hook methods may be `def` or `async def`, except `configure()`, which must stay synchronous. Blocking I/O should use `anyio.to_thread.run_sync`.

the following is the visibility of dependency objects regarding to each hook.

| hook name | app | cornerstone | request | app_state  | request_state |
| --- | --- | --- | --- | --- | --- |
| configure | Yes | Yes | No | Yes | No |
| pre_endpoint_startup | Yes | Yes | No | Yes | No |
| post_endpoint_startup | Yes | Yes | No | Yes | No |
| pre_endpoint_shutdown | Yes | Yes | No | Yes | No |
| post_endpoint_shutdown | Yes | Yes | No | Yes |  No |
| pre_endpoint_call | Yes | Yes | Yes | Yes | Yes |
| post_endpoint_call | Yes | Yes | Yes | Yes | Yes |

If the visibility of one dependency object is Yes to one hook, i.e. this dependency can be used in the hook.

dependency objects are injected by framework, each object has its meaning like below:

| name | meaning |
| --- | --- |
| app | the instance of FastAPI |
| cornerstone | the meta data of the cornerstone that hook belong to |
| request | the incoming http request object |
| app_state | this cornerstone's dict in `app.state.cornerstones`. Prefer `@provides` and `DependsHive` when a router needs the value. |
| request_state | this cornerstone's dict in `request.state.cornerstones`. Prefer `@request_provides` and `DependsHive` for request-scoped values. |



please check in the code for usages.

hooks can be set in cornerstone init file.

example/cornerstone/db/__init__.py

```python
from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks
from fastapi_hive.ioc_framework.decorators import cornerstone, provides, request_provides
from example.cornerstone.db.implement import Base, create_all_tables, add_db_middleware
from fastapi_sqlalchemy import db


__all__ = ['Base']


class LazyDBSession:
    def __init__(self, database):
        self._database = database

    def __getattr__(self, name):
        return getattr(self._database.session, name)


@cornerstone(name="db", order=0)
class CornerstoneHooksImpl(CornerstoneHooks):

    @provides("db")
    def configure(self):
        add_db_middleware(self.app, self.cornerstone)
        self.app_state['db'] = db
        return db

    def post_endpoint_startup(self):
        create_all_tables(self.app)

    @request_provides("db.session")
    def pre_endpoint_call(self):
        self.request_state['db'] = db
        return LazyDBSession(db)
```


## endpoint hooks

----

The framework provides `EndpointHooks`. Decorate a subclass with `@endpoint`. `startup` and `shutdown` may be `def` or `async def`.

the following is the visibility of dependency objects regarding to each hook.

| hook name | app | endpoint | app_state |
| --- | --- | --- | --- |
| startup | Yes | Yes | Yes |
| shutdown | Yes | Yes | Yes |

If the visibility of one dependency object is Yes to one hook, i.e. this dependency can be used in the hook.

dependency objects are injected by framework, each object has its meaning like below:

| name | meaning |
| --- | --- |
| app | the instance of FastAPI |
| endpoint | the meta data of the endpoint that hook belong to. `endpoint.routers` is the list collected from the `router` subpackage. |
| app_state | this endpoint's dict in `app.state.endpoints`. Prefer `@provides` and `DependsHive` when a router needs the value. |


please check in the code for usages.

hooks can be set in endpoint init file and three sub-modules(db/service/router) init file.

example/endpoints_package1/house_price/service/__init__.py

```python
from example.endpoints_package1.house_price.service.implement import HousePriceModel
from example.endpoints_package1.house_price.config import DEFAULT_MODEL_PATH
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks
from fastapi_hive.ioc_framework.decorators import endpoint, provides


@endpoint(name="house_price")
class EndpointHooksImpl(EndpointHooks):

    @provides(HousePriceModel)
    def startup(self):
        return HousePriceModel(DEFAULT_MODEL_PATH)

    def shutdown(self):
        pass
```

The router receives the model with `DependsHive`:

```python
from fastapi_hive.ioc_framework.registry import DependsHive

def post_predict(model: HousePriceModel = DependsHive(HousePriceModel)):
    return model.predict(block_data)
```

