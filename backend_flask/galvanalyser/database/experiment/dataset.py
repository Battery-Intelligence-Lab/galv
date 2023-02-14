from galvanalyser.database import Base
from galvanalyser.database.cell_data import Cell
from galvanalyser.database.user_data import User
from galvanalyser.database.experiment import (
    Equipment, RangeLabel, TimeseriesData, Column as GColumn
)
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    DateTime, Table
)
from sqlalchemy.orm import object_session
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_utils import JSONType
from sqlalchemy.orm import relationship
import datetime
from typing import List
from dataclasses import dataclass
# from marshmallow import Schema, fields, ValidationError, pre_load


def dataset_equipment():
    return Table(
        'dataset_equipment', Base.metadata,
        Column(
            'dataset_id', Integer,
            ForeignKey('experiment.dataset.id'),
            primary_key=True,
        ),
        Column(
            'equipment_id', Integer,
            ForeignKey('experiment.equipment.id'),
            primary_key=True,
        ),
        schema='experiment'
    )


@dataclass
class Dataset(Base):
    __tablename__ = 'dataset'
    __table_args__ = {'schema': 'experiment'}

    id: int
    name: str
    date: datetime.datetime
    type: str
    cell: Cell = None
    owner: User = None
    purpose: str
    json_data: object
    equipment: List[Equipment]
    ranges: List[RangeLabel]
    columns: List[Column]

    id = Column(Integer, primary_key=True)
    name = Column(String)
    date = Column(DateTime)
    type = Column(String)
    cell_id = Column(Integer, ForeignKey('cell_data.cell.id'))
    owner_id = Column(Integer, ForeignKey('user_data.user.id'))
    purpose = Column(String)
    json_data = Column(JSONType)
    equipment = relationship(
        'Equipment',
        secondary=dataset_equipment,
        backref='datasets',
    )
    ranges = relationship(
        'RangeLabel',
        backref='dataset',
    )
    columns = relationship(
        'Column',
        backref='dataset',
    )

    #columns = association_proxy("timeseries_data", "column")

    # @property
    # def columns(self):
    #     return (
    #         object_session(self).query(GColumn).
    #         join(TimeseriesData,
    #              GColumn.id == TimeseriesData.column_id).
    #         filter(TimeseriesData.dataset_id == self.id).distinct().all()
    #     )

# class DatasetSchema(Schema):
#    id = fields.Int(dump_only=True)
#    name = fields.Str()
#    date = fields.DateTime()
#    type = fields.Str()
#    cell = fields.Nested(CellSchema())
#    cell_id = fields.Int(load_only=True)
#    owner = fields.Nested(UserSchema())
#    owner_id = fields.Int(load_only=True)
#    purpose = fields.Str()
#    json_data = fields.Dict()
#    equipment_ids = fields.Int(many=True, load_only=True)
#    equipment = fields.Nested(
#        EquipmentSchema(), many=True, dump_only=True
#    )
#    ranges = fields.Nested(RangeSchema(), many=True, dump_only=True)
#    columns = fields.Nested(
#        ColumnSchema(), many=True, dump_only=True
#    )
