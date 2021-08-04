from galvanalyser.database import Base
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, JSON, Float
)
from sqlalchemy.orm import relationship
from dataclasses import dataclass


@dataclass
class TimeseriesData(Base):
    __tablename__ = 'timeseries_data'
    __table_args__ = {'schema': 'experiment'}

    sample_no: int
    column_id: int
    value: float

    sample_no = Column(Integer, primary_key=True)
    column_id = Column(
        Integer,
        ForeignKey('experiment.column.id'), primary_key=True
    )
    value = Column(Float)
    column = relationship(
        'Column',
        backref='timeseries_data'
    )
