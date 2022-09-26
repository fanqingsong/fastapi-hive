# WHY fastapi modules framework?


## Regular project layout & its cons.

---

Lets look at the regular project folder layout.<br/>
There are two modules in the app, and the folders are arranged by functions, such as routes/models/services.<br/>
No problem if folders are set as this for small project.<br/>

But when it comes to large scale project which contains to many modules, it will bring tough task to maintain modules, because those modules' code files are existent in different folders.

Beyond the problem, developer also need to register some functions in main.py, such as router registering.

So it is ideal for developer to maintain all functianal code files in one module folder, and register all function into app automatically.

**DEMO**: <a href="https://github.com/eightBEC/fastapi-ml-skeleton/tree/master/fastapi_skeleton" target="_blank">https://github.com/eightBEC/fastapi-ml-skeleton/tree/master/fastapi_skeleton</a>


    app
        api
            routes
                heartbeat.py
                prediction.py
        models
            heartbeat.py
            prediction.py
        services
            heartbeat.py
            prediction.py
        main.py



---


## Ideal project layout.

---

Here is ideal folders layout from developers' perspective.
For each of modules(heartbeat and prediction), there is one module folder for containing all functional code files.

Furthermore, developers do not have to register function into app, such as router.


    app
        packages
            heartbeat
                api.py
                models.py
                service.py
            prediction
                api.py
                models.py
                service.py
        main.py

