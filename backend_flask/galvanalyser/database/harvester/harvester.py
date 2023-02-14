from galvanalyser.database import Base
from galvanalyser.database.cell_data import Cell
from galvanalyser.database.user_data import User
from galvanalyser.database.experiment import (
    Equipment, RangeLabel, TimeseriesData, Column as GColumn
)
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, Table, Boolean
)
from sqlalchemy.orm import object_session
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
import datetime
from typing import List
from dataclasses import dataclass

@dataclass
class Harvester(Base):
    __tablename__ = 'harvester'
    __table_args__ = {'schema': 'harvesters'}

    id: int
    machine_id: int
    harvester_name: str
    last_successful_run: datetime.datetime
    is_running: bool
    periodic_hour: int

    id = Column(Integer, primary_key=True)
    machine_id = Column(String)
    harvester_name = Column(String)
    last_successful_run = Column(DateTime)
    is_running = Column(Boolean)
    periodic_hour = Column(Integer)
    monitored_paths = relationship(
        'MonitoredPath',
        backref='harvester',
    )


