from galvanalyser.database import Base
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, Table, Boolean
)
from sqlalchemy.orm import relationship
import datetime
from typing import List
from dataclasses import dataclass

association_table = Table(
    'monitored_for',
    Base.metadata,
    Column(
        'path_id',
        ForeignKey('harvesters.monitored_path.id'),
        primary_key=True
    ),
    Column('user_id', ForeignKey('user_data.user.id'), primary_key=True),
    schema='harvesters',
)


@dataclass
class MonitoredPath(Base):
    __tablename__ = 'monitored_path'
    __table_args__ = {'schema': 'harvesters'}

    id: int
    harvester_id: int
    path: str

    id = Column(Integer, primary_key=True)
    harvester_id = Column(Integer)
    path = Column(String)
    monitored_for = relationship(
        "User",
        secondary=association_table,
    )
