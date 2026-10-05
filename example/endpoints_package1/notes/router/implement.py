
from fastapi import APIRouter
from typing import List
from example.endpoints_package1.notes import schemas
from example.endpoints_package1.notes import db as dbmodel
from example.endpoints_package1.notes.service import NoteComposer
from fastapi_hive.ioc_framework.registry import Inject

router = APIRouter()


@router.get("", response_model=List[schemas.Note], name="query notes.")
def get_notes(skip: int = 0, limit: int = 100, db=Inject("db.session")):
    notes = db.query(dbmodel.Note).offset(skip).limit(limit).all()
    return notes


@router.post("", response_model=schemas.Note, name="create note")
def create_note(
    note: schemas.NoteIn,
    db=Inject("db.session"),
    composer: NoteComposer = Inject(NoteComposer),
):
    db_note = dbmodel.Note(text=composer.compose(note.text), completed=note.completed)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note




