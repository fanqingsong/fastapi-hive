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

1. exposes cornerstone and endpoint state through the FastAPI application;
2. registers synchronous and asynchronous startup/shutdown hooks;
3. mounts every discovered endpoint router when automatic mounting is enabled;
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
- **Automatic router mounting** — derive URL prefixes and OpenAPI tags from the
  folder structure.
- **Lifecycle hooks** — run sync or async setup and teardown code at application,
  module, and request boundaries.
- **Shared and isolated state** — make cornerstone resources and endpoint-owned
  resources available through `app.state` and `request.state`.
- **Incremental adoption** — wrap an existing FastAPI app with only a small
  bootstrap block.

## Quick start

### 1. Install

```bash
pip install fastapi-hive
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

An endpoint router package exports a regular FastAPI `APIRouter`:

```python
# my_app/endpoints/heartbeat/router/__init__.py
from .implement import router
```

### 3. Initialize the hive

```python
from fastapi import FastAPI
from fastapi_hive.ioc_framework import IoCFramework

app = FastAPI(title="My API")

hive = IoCFramework(app)
hive.config.CORNERSTONE_PACKAGE_PATH = "./my_app/cornerstones"
hive.config.ENDPOINT_PACKAGE_PATHS = ["./my_app/endpoints"]
hive.config.API_PREFIX = "/api/v1"
hive.config.ROUTER_MOUNT_AUTOMATED = True
hive.init_modules()
```

Given an endpoint at `my_app/endpoints/heartbeat`, its router is mounted at:

```text
/api/v1/endpoints/heartbeat/...
```

Set `HIDE_ENDPOINT_CONTAINER_IN_API` or `HIDE_ENDPOINT_IN_API` to simplify the
generated URL. Set `HIDE_ENDPOINT_IN_TAG` to control OpenAPI tag names.

### 4. Add lifecycle behavior

Define `EndpointHooksImpl` in an endpoint package to preload an endpoint-owned
resource:

```python
# my_app/endpoints/house_price/service/__init__.py
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks

from .implement import HousePriceModel


class EndpointHooksImpl(EndpointHooks):
    def setup(self):
        self.app_state["model"] = HousePriceModel("model.joblib")

    def teardown(self):
        self.app_state.pop("model", None)
```

The resource is then available to that endpoint:

```python
model = request.app.state.endpoints[
    "endpoints.house_price"
]["model"]
prediction = model.predict(payload)
```

Cornerstones use `CornerstoneHooksImpl` and additionally support
`pre_endpoint_call` / `post_endpoint_call` hooks for request-scoped behavior.
Async equivalents are available through `EndpointAsyncHooks` and
`CornerstoneAsyncHooks`.

## Run the example

The included application demonstrates:

- API-key authentication as a cornerstone;
- database setup and request-scoped access as a cornerstone;
- heartbeat endpoints;
- ML model preloading and house-price prediction;
- endpoint discovery across two endpoint packages.

```bash
git clone https://github.com/fanqingsong/fastapi-hive.git
cd fastapi-hive
pip install -r requirements.txt
cp .env.example .env
uvicorn example.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) to explore the
generated OpenAPI interface. Configure `API_KEY` in `.env` before trying
authenticated endpoints; `docs/sample_payload.json` contains a prediction
request example.

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
