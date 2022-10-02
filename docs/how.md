# How to Use?

FastAPI Hive Framework is the solution to the problems in why chapter.

---

## Install it.

```bash
pip3 install fastapi_hive
```


---

## Integrate it into your app

Note: You can reference demo code to complete this part. 

First, create or refactor you code into module:

![module folders](img/module_folders.png)

Second, setup the initial sentence of ioc_container in main.py

```Python
from fastapi import FastAPI
from loguru import logger
from demo.core.config import (APP_NAME, APP_VERSION, API_PREFIX,
                              IS_DEBUG)

from fastapi_hive.ioc_framework import IoCFramework


def get_app() -> FastAPI:
    logger.info("app is starting.")

    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    ioc_framework = IoCFramework(fast_app)
    ioc_framework.config.API_PREFIX = API_PREFIX
    ioc_framework.config.MODULE_PACKAGE_PATHS = ["./demo/package1", "./demo/package2"]
    ioc_framework.config.HIDE_PACKAGE_IN_URL = True
    ioc_framework.init_modules()

    # ioc_framework.delete_modules_by_packages(["./demo/package1"])
    # ioc_framework.add_modules_by_packages(["./demo/package2"])

    @fast_app.get("/")
    def get_root():
        return "Go to docs URL to look up API: http://localhost:8000/docs"

    return fast_app


app = get_app()

```

## URL MAPPING

As you know, this framework will discover all modules of all packages automatically.
So the API URLs contain package folder name and module folder name.

If the folder structure likes below

```text
    app
        packages
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
{API_PREFIX}/heartbeat/xxx
{API_PREFIX}/prediction/yyy
```

Note:

1. xxx is defined in packages/heartbeat/router.py
2. yyy is defined in packages/prediction/router.py

if your app set several packages, you can turn off HIDE_PACKAGE_IN_URL of configuration.

```text
{API_PREFIX}/packages/heartbeat/xxx
{API_PREFIX}/packages/prediction/yyy
```
