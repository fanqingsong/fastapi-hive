# Use Cases


## 1. Machine Learning model preloading during app startup.

---

For machine learning model, it is not suitable to load model during request, because the time cost of model loading may be too long, so the proposed method is to load model before request stage, i.e. during app startup stage.

### classical disadvantages

For the classical code layout example, it defines loading model logic func(start_app_handler) in core.event_handler.py file.

**Reference**: <a href="https://github.com/eightBEC/fastapi-ml-skeleton/tree/master/fastapi_skeleton" target="_blank">https://github.com/eightBEC/fastapi-ml-skeleton/tree/master/fastapi_skeleton</a>


```python
from typing import Callable

from fastapi import FastAPI
from loguru import logger

from fastapi_skeleton.core.config import DEFAULT_MODEL_PATH
from fastapi_skeleton.services.models import HousePriceModel


def _startup_model(app: FastAPI) -> None:
    model_path = DEFAULT_MODEL_PATH
    model_instance = HousePriceModel(model_path)
    app.state.model = model_instance


def _shutdown_model(app: FastAPI) -> None:
    app.state.model = None


def start_app_handler(app: FastAPI) -> Callable:
    def startup() -> None:
        logger.info("Running app start handler.")
        _startup_model(app)
    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        _shutdown_model(app)
    return shutdown
```

Then register start_app_handler as startup event in main.py, so model will be load when startup event happens.

```python
from fastapi import FastAPI

from fastapi_skeleton.api.routes.router import api_router
from fastapi_skeleton.core.config import (API_PREFIX, APP_NAME, APP_VERSION,
                                          IS_DEBUG)
from fastapi_skeleton.core.event_handlers import (start_app_handler,
                                                  stop_app_handler)


def get_app() -> FastAPI:
    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)
    fast_app.include_router(api_router, prefix=API_PREFIX)

    fast_app.add_event_handler("startup", start_app_handler(fast_app))
    fast_app.add_event_handler("shutdown", stop_app_handler(fast_app))

    return fast_app


app = get_app()
```

But for the ideal code structure, we take assumption that all codes of one service should be put in one folder together. 

### fastapi-hive advantages

FastAPI hive really support this code structure, and meet the preloading requirement which is implemented by regiser startup event.

in the below file, the setup hook loads the machine learning model before requests and registers it with `@provides`.

example/endpoints_package1/house_price/service/__init__.py


```python
from example.endpoints_package1.house_price.service.implement import HousePriceModel
from example.endpoints_package1.house_price.config import DEFAULT_MODEL_PATH
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks, EndpointAsyncHooks
from fastapi_hive.ioc_framework.decorators import endpoint, provides


@endpoint(name="house_price")
class EndpointHooksImpl(EndpointHooks):

    @provides(HousePriceModel)
    def setup(self):
        return HousePriceModel(DEFAULT_MODEL_PATH)

    def teardown(self):
        pass


@endpoint(name="house_price")
class EndpointAsyncHooksImpl(EndpointAsyncHooks):

    async def setup(self):
        pass

    async def teardown(self):
        pass
```

The predict route receives the loaded model through `DependsHive(HousePriceModel)`.

example/endpoints_package1/house_price/router/implement.py

```python
from fastapi import APIRouter, Depends

from example.cornerstone import auth
from fastapi_hive.ioc_framework.registry import DependsHive

from example.endpoints_package1.house_price.schema.payload import (
    HousePredictionPayload)
from example.endpoints_package1.house_price.schema.prediction import HousePredictionResult

from example.endpoints_package1.house_price.service import HousePriceModel


router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict")
def post_predict(
    authenticated: bool = Depends(auth.validate_request),
    block_data: HousePredictionPayload = None,
    model: HousePriceModel = DependsHive(HousePriceModel),
) -> HousePredictionResult:

    prediction: HousePredictionResult = model.predict(block_data)

    return prediction

```

---


## 2. DB ORM definition and table creation && db instance for endpoints.

---

### classical disadvantages


For db setting definition, sqlalchemy let user create a Base object.

https://fastapi.tiangolo.com/tutorial/sql-databases/

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

```

Then every service code which need db have to define ORM model inherited from Base object.

```python
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")

```

Then main.py call a sentance to create all tables in DB:

this sentance:
models.Base.metadata.create_all(bind=engine)


```python
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

```

But there is an implicit import dependency to care during coding:
in models.py file, import Base first, then define ORM model inherited from Base,
in main.py file, call create_all function to create tables in DB.
For large project, there are many ORM model to be defined, 
It is not suitable to define all of them in one file(models.py),
So it comes to fastapi-hive framework to decoupling db function module from endpoint service module.


```python
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
```

### fastapi-hive advantages

Let's see How to use fastapi-hive as of db part.

First, create one db setting file: example/cornerstone/db/implement.py

```python


from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from fastapi import FastAPI
from example.cornerstone.config import DATABASE_URL
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from fastapi_hive.ioc_framework.cornerstone_container import CornerstoneMeta

Base = declarative_base()
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def add_db_middleware(app: FastAPI, cornerstone: CornerstoneMeta):
    app.add_middleware(DBSessionMiddleware, db_url=DATABASE_URL)

    # cornerstone.state['db'] = db


def create_all_tables(app: FastAPI):
    Base.metadata.create_all(engine)  # Create tables
    print("-- call create all over ----")

```

Secondly, create db initial file, and implement hooks call.

example/cornerstone/db/__init__.py

```python
from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks, CornerstoneAsyncHooks
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
    def pre_endpoint_setup(self):
        add_db_middleware(self.app, self.cornerstone)
        self.app_state['db'] = db
        return db

    def post_endpoint_setup(self):
        create_all_tables(self.app)

    @request_provides("db.session")
    def pre_endpoint_call(self):
        self.request_state['db'] = db
        return LazyDBSession(db)


@cornerstone(name="db", order=0)
class CornerstoneAsyncHooksImpl(CornerstoneAsyncHooks):

    async def pre_endpoint_setup(self):
        pass
```


Third, create one endpoint db models file:

example/endpoints_package1/notes/db/implement.py

```python

from sqlalchemy import Column, Integer, String, Boolean

from example.cornerstone.db import Base


class Note(Base):
    __tablename__ = "note"

    id = Column(Integer, primary_key=True)
    text = Column(String)
    completed = Column(Boolean)

```


Lastly, create a router file to call db with ORM model:

```python
from fastapi import APIRouter
from typing import List
from example.endpoints_package1.notes import schemas
from example.endpoints_package1.notes import db as dbmodel
from fastapi_hive.ioc_framework.registry import DependsHive

router = APIRouter()


@router.get("", response_model=List[schemas.Note], name="query notes.")
def get_notes(skip: int = 0, limit: int = 100, db=DependsHive("db.session")):
    notes = db.query(dbmodel.Note).offset(skip).limit(limit).all()
    return notes


@router.post("", response_model=schemas.Note, name="create note")
def create_note(note: schemas.NoteIn, db=DependsHive("db.session")):
    db_note = dbmodel.Note(text=note.text, completed=note.completed)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

```
