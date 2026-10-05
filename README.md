# FastAPI Hive

<p align="center">
  <strong>Organize FastAPI applications around business capabilities, not technical layers.</strong>
</p>

<p align="center">
  Keep each API, schema, service, and model together; share infrastructure through reusable cornerstones.
</p>

<p align="center">
  <a href="https://github.com/fanqingsong/fastapi-hive/actions"><img alt="Build status" src="https://github.com/fanqingsong/fastapi-hive/workflows/pytest_flake8/badge.svg"></a>
  <a href="https://codecov.io/gh/fanqingsong/fastapi-hive"><img alt="Coverage" src="https://codecov.io/gh/fanqingsong/fastapi-hive/branch/master/graph/badge.svg"></a>
  <a href="https://www.python.org/"><img alt="Supported Python versions: 3.8–3.13" src="https://img.shields.io/badge/python-3.8--3.13-blue.svg"></a>
  <a href="https://pypi.org/project/fastapi-hive/"><img alt="PyPI version" src="https://badge.fury.io/py/fastapi-hive.svg"></a>
  <a href="https://github.com/fanqingsong/fastapi-hive/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/fanqingsong/fastapi-hive.svg"></a>
  <a href="https://pepy.tech/project/fastapi-hive"><img alt="Downloads" src="https://pepy.tech/badge/fastapi-hive"></a>
</p>

<p align="center">
  <a href="https://fanqingsong.github.io/fastapi-hive/">Documentation</a>
  ·
  <a href="https://github.com/fanqingsong/fastapi-hive/tree/master/example">Example application</a>
  ·
  <a href="https://pypi.org/project/fastapi-hive/">PyPI</a>
</p>

![FastAPI Hive concept](docs/img/fastapi-hive-concept.svg)

## Why FastAPI Hive?

Layer-based layouts work well at first, but related code becomes scattered as an
application grows:

```text
app/                             app/
├── routers/                     ├── cornerstones/
│   ├── heartbeat.py             │   ├── auth/
│   └── house_price.py           │   └── db/
├── schemas/          ──────▶    └── endpoints/
│   ├── heartbeat.py                 ├── heartbeat/
│   └── house_price.py               │   ├── router/
├── services/                        │   ├── schema/
│   └── house_price.py               │   └── service/
└── main.py                          └── house_price/
                                         ├── router/
                                         ├── schema/
                                         └── service/
```

In the layout on the left, changing one business capability often means jumping
between `routers`, `schemas`, and `services`. FastAPI Hive enables the
capability-oriented layout on the right:

- **Endpoints are the bees** — each endpoint folder owns one business
  capability, including its router, schemas, service, and optional database
  models.
- **Cornerstones build the hive** — shared concerns such as authentication and
  database access live in independently initialized modules.
- **The IoC framework is the beekeeper** — it discovers modules, runs their
  lifecycle hooks, exposes their state, and mounts routers automatically.

The result is less registration code in `main.py`, clearer ownership, and
modules that are easier to review, test, move, or remove.

## How it works

![FastAPI Hive architecture](docs/img/fastapi-hive-architecture.svg)

At initialization, `IoCFramework` scans the configured package paths and imports
each child module. It then:

1. discovers decorated modules and each endpoint's `router` module in the same scan,
   then exposes published values through the hive registry;
2. registers synchronous and asynchronous startup/shutdown hooks;
3. mounts the collected routers when automatic mounting is enabled;
4. installs request middleware that runs cornerstone hooks before and after
   each request.

![FastAPI Hive lifecycle](docs/img/fastapi-hive-lifecycle.svg)

This lifecycle is useful for resources that must be prepared once—such as an ML
model, a database connection, or an authentication provider—and for resources
that must be attached to each request.

## Core capabilities

- **Capability-oriented modules** — colocate all code for one endpoint.
- **Automatic discovery** — load cornerstones and multiple endpoint packages
  from configurable paths.
- **Automatic router mounting** — collect each endpoint's `APIRouter` with its
  hooks, then derive URL prefixes and OpenAPI tags from the folder structure
  or from `@endpoint(prefix=..., tags=...)`.
- **Lifecycle hooks** — run sync or async startup and shutdown code at application,
  module, and request boundaries.
- **Shared and isolated state** — publish process-level values with `@provides`
  and request-scoped values with `@request_provides`. Routes read them through
  `DependsHive`.
- **Incremental adoption** — wrap an existing FastAPI app with only a small
  bootstrap block.

## Quick start

### 1. Install

The package published on PyPI can lag behind this repository. Install from the local source:

```bash
git clone https://github.com/fanqingsong/fastapi-hive.git
cd fastapi-hive
pip3 install .
```

FastAPI Hive supports Python 3.8 through Python 3.13.

### 2. Organize the application

```text
my_app/
├── cornerstones/
│   ├── auth/
│   │   ├── __init__.py
│   │   └── implement.py
│   └── db/
│       ├── __init__.py
│       └── implement.py
├── endpoints/
│   ├── heartbeat/
│   │   ├── router/
│   │   ├── schema/
│   │   └── service/
│   └── house_price/
│       ├── router/
│       ├── schema/
│       └── service/
└── main.py
```

An endpoint router package exports a regular FastAPI `APIRouter` named `router`.
The container collects that object while it loads the endpoint—the same pass
that collects `@endpoint` hooks:

```python
# my_app/endpoints/heartbeat/router/__init__.py
from .implement import router
```

Override the generated prefix and OpenAPI tag on the hook class:

```python
# example/endpoints_package2/heart_beat2/router/__init__.py
from .implement import router
from fastapi_hive.ioc_framework.decorators import endpoint
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks


@endpoint(name="heart_beat2", prefix="/api/hb2", tags=["heartbeat-v2"])
class EndpointHooksImpl(EndpointHooks):
    def startup(self):
        # self.endpoint.routers is the collected RouterBinding list
        pass
```

### 3. Initialize the hive

If `cornerstone`/`cornerstones` and `endpoints` sit next to `main.py`, the
container picks them up by convention:

```python
from fastapi import FastAPI
from fastapi_hive.ioc_framework import IoCFramework

app = FastAPI(title="My API")
IoCFramework.bootstrap(app)
```

Override convention with `hive.yaml` beside the module that calls `bootstrap`
(the example keeps it at `example/hive.yaml`) or in the working directory.
`HIVE_*` environment variables override the file:

```yaml
# hive.yaml
hive:
  api_prefix: /api/v1
  hide_endpoint_container_in_api: true
  endpoint_package_paths:
    - ./my_app/endpoints
```

```bash
export HIVE_API_PREFIX=/api/v1
export HIVE_ENDPOINT_PACKAGE_PATHS=./pkg1,./pkg2
```

You can still assign `hive.config.*` in code, or pass `settings={...}` to
`IoCFramework` / `bootstrap`. Code overrides win over env, which wins over the
file.

Given an endpoint at `my_app/endpoints/heartbeat`, its router is mounted at:

```text
/api/v1/endpoints/heartbeat/...
```

Set `HIDE_ENDPOINT_CONTAINER_IN_API` or `HIDE_ENDPOINT_IN_API` to simplify the
generated URL. Set `HIDE_ENDPOINT_IN_TAG` to control OpenAPI tag names.

### 4. Add lifecycle behavior

Decorate a hook class in the endpoint package. `@provides` registers the
return value for later injection:

```python
# my_app/endpoints/house_price/service/__init__.py
from fastapi_hive.ioc_framework.decorators import endpoint, provides
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks

from .implement import HousePriceModel


@endpoint(name="house_price")
class HousePriceService(EndpointHooks):
    @provides(HousePriceModel)
    def startup(self):
        return HousePriceModel("model.joblib")
```

The route receives that object through `DependsHive`:

```python
from fastapi_hive.ioc_framework.registry import DependsHive

def predict(model: HousePriceModel = DependsHive(HousePriceModel)):
    return model.predict(payload)
```

Cornerstones use `@cornerstone`. `pre_endpoint_call` and `post_endpoint_call`
run around each request; mark a return value with `@request_provides` to
publish it for that request only. `DependsHive` reads the request registry
before the application registry.

`order` controls hook order and the order collected routers are mounted.
`profiles` and `enabled_when` skip a module unless `ACTIVE_PROFILES` or
`FEATURES` enables it. Set `mount=False` on `@endpoint` to register the router
yourself.

Hook methods may be `def` or `async def`. The framework always invokes them
from an async lifecycle. `CornerstoneHooks.configure()` is the exception: it
runs while the app is assembled and must stay synchronous so middleware can
be registered. Blocking I/O in a hook should use `anyio.to_thread.run_sync`.

## Run the example

The included application demonstrates:

- API-key authentication as a cornerstone;
- database setup and request-scoped access as a cornerstone;
- heartbeat endpoints (package2 uses `@endpoint(prefix=..., tags=...)`);
- ML model preloading and house-price prediction;
- endpoint discovery across two endpoint packages.

```bash
git clone https://github.com/fanqingsong/fastapi-hive.git
cd fastapi-hive
pip3 install -e .
pip install -r requirements.txt
cp example/.env.example example/.env
uvicorn example.main:app --reload
```

`pip3 install -e .` installs this checkout in editable mode, so the example imports the local `fastapi_hive` package. `make run-example` runs that install and then starts the app.

Open [http://localhost:8000/docs](http://localhost:8000/docs) to explore the
generated OpenAPI interface. `GET /hive/routers` lists every router collected
during the endpoint scan (`heart_beat2` mounts at `/api/hb2/heartbeat`).
Configure `API_KEY` in `example/.env` before trying authenticated endpoints;
`docs/sample_payload.json` contains a prediction request example.

## Test

```bash
tox
```

## Learn more

- [Why a capability-oriented layout?](https://fanqingsong.github.io/fastapi-hive/why/)
- [Integration guide](https://fanqingsong.github.io/fastapi-hive/how/)
- [Architecture and hook lifecycle](https://fanqingsong.github.io/fastapi-hive/design/)
- [Practical use cases](https://fanqingsong.github.io/fastapi-hive/usecases/)

## License

FastAPI Hive is released under the [Apache License 2.0](LICENSE).
