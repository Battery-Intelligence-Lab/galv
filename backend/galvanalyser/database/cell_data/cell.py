from galvanalyser.database import Base
# from galvanalyser.database.experiment import Dataset
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, JSON, Table
)
from sqlalchemy.orm import relationship
from dataclasses import dataclass
from typing import List


@dataclass
class Cell(Base):
    # __table__ = db.Model.metadata.tables['experiment.database']
    __tablename__ = 'cell'
    __table_args__ = {'schema': 'cell_data'}

    id: int
    # datasets: List[Dataset]
    name: str
    manufacturer: str
    form_factor: str
    link_to_datasheet: str
    anode_chemistry: str
    cathode_chemistry: str
    nominal_capacity: str
    nominal_cell_weight: str

    id = Column(Integer, primary_key=True)
    datasets = relationship(
        'Dataset', backref='cell'
    )
    name = Column(String)
    manufacturer = Column(String)
    form_factor = Column(String)
    link_to_datasheet = Column(String)
    anode_chemistry = Column(String)
    cathode_chemistry = Column(String)
    nominal_capacity = Column(String)
    nominal_cell_weight = Column(String)
