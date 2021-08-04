from galvanalyser.database import Base
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, JSON, Table
)
from sqlalchemy.orm import relationship
from dataclasses import dataclass


@dataclass
class User(Base):
    # __table__ = db.Model.metadata.tables['experiment.database']
    __tablename__ = 'user'
    __table_args__ = {'schema': 'user_data'}

    id: int
    username: str
    email: str

    id = Column(Integer, primary_key=True)
    datasets = relationship(
        'Dataset', backref='owner',
    )
    username = Column(String)
    password = Column(String)
    salt = Column(String)
    email = Column(String)
