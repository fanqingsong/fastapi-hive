
from fastapi import APIRouter
from starlette.requests import Request
from typing import List
from example.endpoints_package1.notes import schemas
from example.endpoints_package1.notes import db as dbmodel

router = APIRouter()


@router.get("/", response_model=List[schemas.Note], name="query notes.")
def get_notes(req: Request, skip: int = 0, limit: int = 100):
    db = req.app.state.db.session

    notes = db.query(dbmodel.Note).offset(skip).limit(limit).all()
    return notes


@router.post("/", response_model=schemas.Note, name="create note")
def create_note(note: schemas.NoteIn, req: Request):
    db = req.app.state.db.session

    db_note = dbmodel.Note(text=note.text, completed=note.completed)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note




