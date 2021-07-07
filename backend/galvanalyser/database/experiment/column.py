from galvanalyser.database import Base
from galvanalyser.database.experiment import ColumnType
from sqlalchemy import (
    Column as SqlColumn, ForeignKey, Integer, String,
    DateTime, JSON,
)
from sqlalchemy.orm import relationship
from dataclasses import dataclass


@dataclass
class Column(Base):
    __tablename__ = 'column'
    __table_args__ = {'schema': 'experiment'}

    id: int
    name: str
    description: str
    type: ColumnType = None

    id = SqlColumn(Integer, primary_key=True)
    type_id = SqlColumn(Integer, ForeignKey('experiment.column_type.id'))
    name = SqlColumn(String)
    description = SqlColumn(String)
