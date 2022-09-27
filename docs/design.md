# FastAPI Modules Framework

![architecture](./architecture.png)

<p align="center">
    <em>FastAPI Module Framework, packages&modules code struture, developer-friendly, easy to be integrated</em>
</p>

---

**Documentation**: <a href="https://fanqingsong.github.io/fastapi-ml-skeleton/" target="_blank">https://fanqingsong.github.io/fastapi-ml-skeleton/</a>

**Source Code**: <a href="https://github.com/fanqingsong/fastapi-ml-skeleton" target="_blank">https://github.com/fanqingsong/fastapi-ml-skeleton</a>

---

FastAPI Modules Framework is a developer friendly and easy to be integrated framework for mananging your code by packages/modules structure.

The key features are:

* **Packages**: a top-level folder to contain all codes by service. 
* **Modules**: a sub-folder in packages, contains functional code in service.
* **Router Mounting Automatically**: the router defined by module will be mounted into app automatically.
* **Service Mounting Automatically**: the service(such as ML model) defined by module will be mounted into app automatically, to reduce loading time during call.
* **Developer-Friendly**: all one-module codes are put in one same folders, all modules are managed by different services.
* **Easy-to-be-Integrated**: Just servral line code to integrate in your app.

<small>estimation based on tests by author, have a look at demo folder.</small>

## Requirements

Python 3.7+

FastAPI Modules Framework stands on the shoulders of giants:

* <a href="https://fastapi.tiangolo.com/" class="external-link" target="_blank">FastAPI</a> web framework.

## Installation 

First, git clone this repo.

```bash
git clone git@github.com:fanqingsong/fastapi-ml-skeleton.git
```

Second, install IoC Container Package<br/>
<small>Note: If just treat it as a library, and want to integrate it into your app, you can just run this command. </small>

```bash
python3 setup.py install
```

Third, install the required packages for running demo in your local environment (ideally virtualenv, conda, etc.).
<small>Note: You can reference demo code to make up your own app in anywhere. </small>

```bash
pip3 install -r requirements.txt
``` 


## Setup
1. Duplicate the `.env.example` file and rename it to `.env` 


2. In the `.env` file configure the `API_KEY` entry. The key is used for authenticating our API. <br>
   A sample API key can be generated using Python REPL:
```python
import uuid
print(str(uuid.uuid4()))
```

## Run DEMO APP

1. Start demo app with: 

production running command:

```bash
uvicorn demo.main:app
```

developing running command:
```bash
uvicorn demo.main:app --reload
```

2. Go to [http://localhost:8000/docs](http://localhost:8000/docs).
   
3. Click `Authorize` and enter the API key as created in the Setup step.
![Authroization](./authorize.png)
   
4. You can use the sample payload from the `docs/sample_payload.json` file when trying out the house price prediction model using the API.
   ![Prediction with example payload](./sample_payload.png)

## Run Tests

If you're not using `tox`, please install with:
```bash
pip3 install tox
```

Run your tests with: 
```bash
tox
```

This runs tests and coverage for Python 3.6 and Flake8, Autopep8, Bandit.


## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
