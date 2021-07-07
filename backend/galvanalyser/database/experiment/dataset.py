from galvanalyser.database import Base
from galvanalyser.database.cell_data import Cell
from galvanalyser.database.user_data import User
from galvanalyser.database.experiment import Equipment, RangeLabel
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, Table
)
from sqlalchemy_utils import JSONType
from sqlalchemy.orm import relationship
import datetime
from typing import List
from dataclasses import dataclass


def dataset_equipment():
    return Table(
        'dataset_equipment', Base.metadata,
        Column(
            'dataset_id', Integer,
            ForeignKey('experiment.dataset.id')
        ),
        Column(
            'equipment_id', Integer,
            ForeignKey('experiment.equipment.id')
        ),
        schema='experiment'
    )


@dataclass
class Dataset(Base):
    __tablename__ = 'dataset'
    __table_args__ = {'schema': 'experiment'}

    id: int
    name: str
    date: datetime.datetime
    type: str
    cell: Cell = None
    owner: User = None
    purpose: str
    json_data: object
    equipment: List[Equipment]
    ranges: List[RangeLabel]
    columns: List[Column]

    id = Column(Integer, primary_key=True)
    name = Column(String)
    date = Column(DateTime)
    type = Column(String)
    cell_id = Column(Integer, ForeignKey('cell_data.cell.id'))
    owner_id = Column(Integer, ForeignKey('user_data.user.id'))
    purpose = Column(String)
    json_data = Column(JSONType)
    equipment = relationship(
        'Equipment',
        secondary=dataset_equipment,
        backref='datasets',
    )
    ranges = relationship(
        'RangeLabel',
        backref='dataset',
    )
    columns = relationship(
        'Column',
        backref='dataset',
    )
