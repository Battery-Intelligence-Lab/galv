from galvanalyser.database import Base
from galvanalyser.database.experiment import Unit
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, JSON,
)
from sqlalchemy.orm import relationship
from dataclasses import dataclass


@dataclass
class ColumnType(Base):
    __tablename__ = 'column_type'
    __table_args__ = {'schema': 'experiment'}

    id: int
    name: str
    unit: Unit = None

    id = Column(Integer, primary_key=True)
    name = Column(String)
    unit_id = Column(Integer, ForeignKey('experiment.unit.id'))
