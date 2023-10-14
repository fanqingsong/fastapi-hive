
from sqlalchemy import Column, Integer, String, Boolean

from example.cornerstone.db import Base


class Note(Base):
    __tablename__ = "note"

    id = Column(Integer, primary_key=True)
    text = Column(String)
    completed = Column(Boolean)



