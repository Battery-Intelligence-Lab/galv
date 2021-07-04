from galvanalyser.database import db
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
        'experiment.dataset_equipment', db.metadata,
        Column(
            'dataset_id', Integer,
            ForeignKey('experiment.dataset.id')
        ),
        Column(
            'equipment_id', Integer,
            ForeignKey('experiment.equipment.id')
        )
    )


@dataclass
class Dataset(db.Model):
    # __table__ = db.Model.metadata.tables['experiment.database']
    __tablename__ = 'experiment.dataset'

    id: int
    name: str
    date: datetime.datetime
    dataset_type: str
    cell: Cell = None
    owner: User = None
    purpose: str
    json_data: object
    equipment: List[Equipment]

    id = Column(Integer, primary_key=True)
    name = Column(String)
    date = Column(DateTime)
    dataset_type = Column(String)
    cell_id = Column(Integer, ForeignKey('cell_data.cell.id'))
    owner_id = Column(Integer, ForeignKey('user_data.user.id'))
    purpose = Column(String)
    json_data = Column(JSON)
    equipment = relationship(
        'Equipment',
        secondary=dataset_equipment,
        backref='datasets',
    )
