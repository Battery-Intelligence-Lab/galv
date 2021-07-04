from galvanalyser.database import db
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, JSON,
)
from sqlalchemy.orm import relationship


class Equipment(db.Model):
    # __table__ = db.Model.metadata.tables['experiment.equipment']
    __tablename__ = 'experiment.equipment'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
