from galvanalyser.database import db
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, JSON, Table
)
from sqlalchemy.orm import relationship


class User(db.Model):
    # __table__ = db.Model.metadata.tables['experiment.database']
    __tablename__ = 'user_data.user'

    id = Column(Integer, primary_key=True)
    datasets = relationship(
        'Dataset', backref='owner',
    )
    username = Column(String)
    password = Column(String)
    salt = Column(String)
    email = Column(String)

