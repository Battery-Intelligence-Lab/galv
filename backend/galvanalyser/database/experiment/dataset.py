from galvanalyser.database import Base
from galvanalyser.database.cell_data import Cell
from galvanalyser.database.user_data import User
from galvanalyser.database.experiment import Equipment
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, JSON, Table
)
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
    # __table__ = Base.metadata.tables['experiment.dataset']
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

    id = Column(Integer, primary_key=True)
    name = Column(String)
    date = Column(DateTime)
    type = Column(String)
    cell_id = Column(Integer, ForeignKey('cell_data.cell.id'))
    owner_id = Column(Integer, ForeignKey('user_data.user.id'))
    purpose = Column(String)
    json_data = Column(JSON)
    equipment = relationship(
        'Equipment',
        secondary=dataset_equipment,
        backref='datasets',
    )
