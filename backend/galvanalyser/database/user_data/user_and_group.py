from galvanalyser.database import Base
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, JSON, Table
)
from typing import List
from sqlalchemy.orm import relationship
from dataclasses import dataclass

association_table = Table(
    'membership',
    Base.metadata,
    Column('user_id', ForeignKey('user_data.user.id'), primary_key=True),
    Column('group_id', ForeignKey('user_data.group.id'), primary_key=True),
    schema='user_data',
)

access_association_table = Table(
    'access',
    Base.metadata,
    Column(
        'dataset_id',
        ForeignKey('experiment.dataset.id'),
        primary_key=True
    ),
    Column('user_id', ForeignKey('user_data.user.id'), primary_key=True),
    schema='experiment',
)

@dataclass
class User(Base):
    # __table__ = db.Model.metadata.tables['experiment.database']
    __tablename__ = 'user'
    __table_args__ = {'schema': 'user_data'}

    id: int
    username: str
    email: str
    groups: List['Group']

    id = Column(Integer, primary_key=True)
    datasets = relationship(
        'Dataset', backref='owner',
    )
    accessible_datasets = relationship(
        'Dataset',
        secondary=access_association_table,
    )
    groups = relationship(
        "Group",
        secondary=association_table,
        back_populates="users"
    )
    username = Column(String)
    password = Column(String)
    salt = Column(String)
    email = Column(String)


@dataclass
class Group(Base):
    __tablename__ = 'group'
    __table_args__ = {'schema': 'user_data'}

    id: int
    groupname: str
    users: List[User]

    id = Column(Integer, primary_key=True)
    users = relationship(
        "User",
        secondary=association_table,
        back_populates="groups"
    )
    groupname = Column(String)
