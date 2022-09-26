# FastAPI Modules Framework

![architecture](./architecture.png)

<p align="center">
    <em>FastAPI Module Framework, packages/modules code struture, developer-friendly, easy to be integrated</em>
</p>

---

**Documentation**: <a href="https://fanqingsong.github.io/fastapi-ml-skeleton/" target="_blank">https://fanqingsong.github.io/fastapi-ml-skeleton/</a>

**Source Code**: <a href="https://github.com/fanqingsong/fastapi-ml-skeleton" target="_blank">https://github.com/fanqingsong/fastapi-ml-skeleton</a>

---

FastAPI Modules Framework is a developer friendly and easy to be integrated framework for mananging your code by packages/modules.

The key features are:

* **Packages**: a top-level folder to contain all codes by service. 
* **Modules**: a sub-folder in packages, contains functional code in service.
* **Developer-Friendly**: all one-module codes are put in one same folders, all modules are managed by different services.
* **Easy-to-be-Integrated**: Just servral line code to integrate in your app.

<small>* estimation based on tests by author, have a look at demo folder.</small>


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

