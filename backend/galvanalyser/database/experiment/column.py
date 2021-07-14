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
    unit: str
    type_id: int
    type: ColumnType = None

    id = SqlColumn(Integer, primary_key=True)
    type_id = SqlColumn(
        Integer, ForeignKey('experiment.column_type.id')
    )
    dataset_id = SqlColumn(
        Integer, ForeignKey('experiment.dataset.id')
    )
    name = SqlColumn(String)
    type = relationship(
        'ColumnType',
        backref='columns',
    )

    @property
    def unit(self):
        if self.type_id != -1:
            return self.type.unit.symbol



