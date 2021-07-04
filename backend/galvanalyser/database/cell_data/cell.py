from galvanalyser.database import db
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, JSON, Table
)
from sqlalchemy.orm import relationship


class Cell(db.Model):
    # __table__ = db.Model.metadata.tables['experiment.database']
    __tablename__ = 'cell_data.cell'

    id = Column(Integer, primary_key=True)
    datasets = relationship(
        'Dataset', backref='cell',
    )
    name = Column(String)
    manufacturer = Column(String)
    form_factor = Column(String)
    link_to_datasheet = Column(String)
    anode_chemistry = Column(String)
    cathode_chemistry = Column(String)
    nominal_capacity = Column(String)
    nominal_cell_weight = Column(String)
