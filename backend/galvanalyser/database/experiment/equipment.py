from galvanalyser.database import Base
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, JSON,
)
from sqlalchemy.orm import relationship
from dataclasses import dataclass


@dataclass
class Equipment(Base):
    # __table__ = db.Model.metadata.tables['experiment.equipment']
    __tablename__ = 'equipment'
    __table_args__ = {'schema': 'experiment'}

    id: int
    name: str
    type: str

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
