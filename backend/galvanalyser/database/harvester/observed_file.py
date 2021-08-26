from galvanalyser.database import Base
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, Table, Boolean
)
from sqlalchemy.orm import relationship
import datetime
from typing import List
from dataclasses import dataclass


@dataclass
class ObservedFile(Base):
    __tablename__ = 'monitored_path'
    __table_args__ = {'schema': 'harvesters'}

    monitor_path_id: int
    path: str
    last_observed_size: int
    last_observed_time: datetime.datetime

    monitor_path_id = Column(Integer, primary_key=True)
    path = Column(String, primary_key=True)
    last_observed_size = Column(Integer)
    last_observed_time = Column(DateTime)
