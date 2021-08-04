from galvanalyser.database import Base
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime,
)
from sqlalchemy.orm import relationship
from dataclasses import dataclass, field
from sqlalchemy.dialects.postgresql import INT8RANGE
from typing import List
from sqlalchemy_utils import Int8RangeType
from intervals import IntInterval

@dataclass
class RangeLabel(Base):
    __tablename__ = 'range_label'
    __table_args__ = {'schema': 'experiment'}

    id: int
    label_name: str
    sample_range: IntInterval
    info: str

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey('experiment.dataset.id'))
    label_name = Column(String)

    sample_range = Column(Int8RangeType)
    info = Column(String)
