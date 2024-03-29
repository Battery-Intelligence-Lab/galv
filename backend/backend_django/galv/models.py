# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
from typing import Type

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import User, Group
from knox.models import AuthToken
import random


class FileState(models.TextChoices):
    RETRY_IMPORT = "RETRY IMPORT"
    IMPORT_FAILED = "IMPORT FAILED"
    UNSTABLE = "UNSTABLE"
    GROWING = "GROWING"
    STABLE = "STABLE"
    IMPORTING = "IMPORTING"
    IMPORTED = "IMPORTED"


class Harvester(models.Model):
    name = models.TextField(
        unique=True,
        help_text="Human-friendly Harvester identifier"
    )
    api_key = models.TextField(
        null=True,
        help_text="API access token for the Harvester"
    )
    last_check_in = models.DateTimeField(
        null=True,
        help_text="Date and time of last Harvester contact"
    )
    sleep_time = models.IntegerField(
        default=10,
        help_text="Seconds to sleep between Harvester cycles"
    )  # default to short time so updates happen quickly
    admin_group = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        null=True,
        related_name='editable_harvesters',
        help_text="Users authorised to make changes to the Harvester"
    )
    user_group = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        null=True,
        related_name='readable_harvesters',
        help_text="Users authorised to create Paths on the Harvester"
    )

    def __str__(self):
        return f"{self.name} [Harvester {self.id}]"

    def save(self, *args, **kwargs):
        if self.id is None:
            # Create groups for Harvester
            text = 'abcdefghijklmnopqrstuvwxyz' + \
                   'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
                   '0123456789' + \
                   '!£$%^&*-=+'
            self.api_key = f"galv_hrv_{''.join(random.choices(text, k=60))}"
        super(Harvester, self).save(*args, **kwargs)


class HarvesterEnvVar(models.Model):
    harvester = models.ForeignKey(
        to=Harvester,
        related_name='environment_variables',
        on_delete=models.CASCADE,
        null=False,
        help_text="Harvester whose environment this describes"
    )
    key = models.TextField(help_text="Name of the variable")
    value = models.TextField(help_text="Variable value")
    deleted = models.BooleanField(help_text="Whether this variable was deleted", default=False, null=False)

    def __str__(self):
        return f"{self.key}={self.value}{'*' if self.deleted else ''}"

    class Meta:
        unique_together = [['harvester', 'key']]


class MonitoredPath(models.Model):
    harvester = models.ForeignKey(
        to=Harvester,
        related_name='monitored_paths',
        on_delete=models.SET_NULL,
        null=True,
        help_text="Harvester with access to this directory"
    )
    path = models.TextField(help_text="Directory location on Harvester")
    regex = models.TextField(
        null=True,
        help_text="""
    Python.re regular expression to filter files by, 
    applied to full file name starting from this Path's directory"""
    )
    stable_time = models.PositiveSmallIntegerField(
        default=60,
        help_text="Number of seconds files must remain stable to be processed"
    )
    active = models.BooleanField(default=True, null=False)
    admin_group = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        null=True,
        related_name='editable_paths',
        help_text="Users authorised to remove and edit this Path. Harvester admins are also authorised"
    )
    user_group = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        null=True,
        related_name='readable_paths',
        help_text="Users authorised to view this Path and child Datasets"
    )

    def __str__(self):
        return self.path

    class Meta:
        unique_together = [['harvester', 'path', 'regex']]


class ObservedFile(models.Model):
    path = models.TextField(help_text="Absolute file path")
    harvester = models.ForeignKey(
        to=Harvester,
        on_delete=models.CASCADE,
        help_text="Harvester that harvested the File"
    )
    last_observed_size = models.PositiveBigIntegerField(
        null=False,
        default=0,
        help_text="Size of the file as last reported by Harvester"
    )
    last_observed_time = models.DateTimeField(
        null=True,
        help_text="Date and time of last Harvester report on file"
    )
    state = models.TextField(
        choices=FileState.choices,
        default=FileState.UNSTABLE,
        null=False,
        help_text=f"File status; autogenerated but can be manually set to {FileState.RETRY_IMPORT}"
    )

    def __str__(self):
        return self.path

    class Meta:
        unique_together = [['path', 'harvester']]


class HarvestError(models.Model):
    harvester = models.ForeignKey(
        to=Harvester,
        related_name='paths',
        on_delete=models.CASCADE,
        help_text="Harvester which reported the error"
    )
    file = models.ForeignKey(
        to=ObservedFile,
        related_name='errors',
        on_delete=models.SET_NULL,
        null=True,
        help_text="File where error originated"
    )
    error = models.TextField(help_text="Text of the error report")
    timestamp = models.DateTimeField(
        auto_now=True,
        null=True,
        help_text="Date and time error was logged in the database"
    )

    def __str__(self):
        if self.path:
            if self.file:
                return f"{self.error} [Harvester_{self.harvester_id}/{self.path}/{self.file}]"
            return f"{self.error} [Harvester_{self.harvester_id}/{self.path}]"
        return f"{self.error} [Harvester_{self.harvester_id}]"


class CellFamily(models.Model):
    name = models.TextField(
        null=False,
        unique=True,
        help_text="Human-friendly identifier"
    )
    form_factor = models.TextField(help_text="Physical shape of the cells")
    link_to_datasheet = models.TextField(help_text="Link to a detailed datasheet for these cells")
    anode_chemistry = models.TextField(help_text="Chemistry of the cells' anode")
    cathode_chemistry = models.TextField(help_text="Chemistry of the cells' cathode")
    nominal_capacity = models.FloatField(help_text="Nominal capacity of the cells (in amp hours)")
    nominal_cell_weight = models.FloatField(help_text="Nominal weight of the cells (in kilograms)")
    manufacturer = models.TextField(help_text="Name of the cells' manufacturer")

    def __str__(self):
        return f"{self.name} [CellFamily {self.id}]"

    def in_use(self) -> bool:
        return self.cells.count() > 0


class Cell(models.Model):
    display_name = models.TextField(
        null=True,
        unique=True,
        help_text="Human-friendly identifier"
    )
    uid = models.TextField(
        null=False,
        unique=True,
        help_text="Serial number or similar. Should be globally unique"
    )
    family = models.ForeignKey(
        to=CellFamily,
        related_name='cells',
        on_delete=models.DO_NOTHING,
        null=False,
        help_text="Family to which this cell belongs"
    )

    def __str__(self):
        if self.display_name:
            return f"{self.uid} ({self.display_name})"
        return self.uid

    def in_use(self) -> bool:
        return self.datasets.count() > 0


class Dataset(models.Model):
    cell = models.ForeignKey(
        to=Cell,
        related_name='datasets',
        on_delete=models.SET_NULL,
        null=True,
        help_text="Cell that generated this Dataset"
    )
    file = models.ForeignKey(
        to=ObservedFile,
        on_delete=models.DO_NOTHING,
        related_name='datasets',
        help_text="File storing raw data"
    )
    name = models.TextField(
        null=True,
        help_text="Human-friendly identifier"
    )
    date = models.DateTimeField(
        null=False,
        help_text="Date and time of experiment. Time will be midnight if not specified in raw data"
    )
    type = models.TextField(
        null=True,
        help_text="Format of the raw data"
    )
    purpose = models.TextField(help_text="Type of the experiment")
    json_data = models.JSONField(
        null=True,
        help_text="Arbitrary additional metadata"
    )

    def __str__(self):
        return f"{self.name} [Dataset {self.id}]"

    class Meta:
        unique_together = [['file', 'date']]


class Equipment(models.Model):
    name = models.TextField(
        null=False,
        unique=True,
        help_text="Specific identifier"
    )
    type = models.TextField(help_text="Generic name")
    datasets = models.ManyToManyField(
        to=Dataset,
        related_name='equipment',
        help_text="Datasets the Equipment is used in"
    )

    def __str__(self):
        return f"{self.name} [Equipment {self.id}]"

    def in_use(self) -> bool:
        return self.datasets.count() > 0


class DataUnit(models.Model):
    name = models.TextField(
        null=False,
        help_text="Common name"
    )
    symbol = models.TextField(
        null=False,
        help_text="Symbol"
    )
    description = models.TextField(help_text="What the Unit signifies, and how it is used")
    is_default = models.BooleanField(
        default=False,
        help_text="Whether the Unit is included in the initial list of Units"
    )

    def __str__(self):
        if self.symbol:
            return f"{self.symbol} | {self.name} - {self.description}"
        return f"{self.name} - {self.description}"


class DataColumnType(models.Model):
    unit = models.ForeignKey(
        to=DataUnit,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Unit used for measuring the values in this column"
    )
    name = models.TextField(null=False, help_text="Human-friendly identifier")
    description = models.TextField(help_text="Origins and purpose")
    is_default = models.BooleanField(
        default=False,
        help_text="Whether the Column is included in the initial list of known Column Types"
    )

    class Meta:
        unique_together = [['unit', 'name']]


class DataColumn(models.Model):
    dataset = models.ForeignKey(
        to=Dataset,
        related_name='columns',
        on_delete=models.CASCADE,
        help_text="Dataset in which this Column appears"
    )
    type = models.ForeignKey(
        to=DataColumnType,
        on_delete=models.CASCADE,
        help_text="Column Type which this Column instantiates"
    )
    official_sample_counter = models.BooleanField(default=False)
    data_type = models.TextField(null=False, help_text="Type of the data in this column")
    name = models.TextField(null=False, help_text="Column title e.g. in .tsv file headers")

    def __str__(self):
        return f"{self.name} ({self.type.unit.symbol})"

    class Meta:
        unique_together = [['dataset', 'name']]

# Timeseries data comes in different types, so we need to store them separately.
# These helper functions reduce redundancy in the code that creates the models.


def _timeseries_column_field():
    return models.OneToOneField(
        to=DataColumn,
        on_delete=models.CASCADE,
        help_text="Column whose data are listed"
    )


def _timeseries_str(self):
    if not self.values:
        return f"{self.column_id}: []"
    if len(self.values) > 5:
        return f"{self.column_id}: [{','.join(self.values[:5])}...]"
    return f"{self.column_id}: [{','.join(self.values)}]"


def _timeseries_repr(self):
    return str(self)


class TimeseriesDataFloat(models.Model):
    column = _timeseries_column_field()
    values = ArrayField(models.FloatField(null=True), null=True, help_text="Row values (floats) for Column")
    __str__ = _timeseries_str
    __repr__ = _timeseries_repr


class TimeseriesDataInt(models.Model):
    column = _timeseries_column_field()
    values = ArrayField(models.IntegerField(null=True), null=True, help_text="Row values (integers) for Column")
    __str__ = _timeseries_str
    __repr__ = _timeseries_repr


class TimeseriesDataStr(models.Model):
    column = _timeseries_column_field()
    values = ArrayField(models.TextField(null=True), null=True, help_text="Row values (str) for Column")
    __str__ = _timeseries_str
    __repr__ = _timeseries_repr


class UnsupportedTimeseriesDataTypeError(TypeError):
    pass


def get_timeseries_handler_by_type(data_type: str) -> Type[TimeseriesDataFloat | TimeseriesDataStr | TimeseriesDataInt]:
    """
    Returns the appropriate TimeseriesData model for the given data type.
    """
    if data_type == "float":
        return TimeseriesDataFloat
    if data_type == "str":
        return TimeseriesDataStr
    if data_type == "int":
        return TimeseriesDataInt
    raise UnsupportedTimeseriesDataTypeError


class TimeseriesRangeLabel(models.Model):
    dataset = models.ForeignKey(
        to=Dataset,
        related_name='range_labels',
        null=False,
        on_delete=models.CASCADE,
        help_text="Dataset to which the Range applies"
    )
    label = models.TextField(
        null=False,
        help_text="Human-friendly identifier"
    )
    range_start = models.PositiveBigIntegerField(
        null=False,
        help_text="Row (sample number) at which the range starts"
    )
    range_end = models.PositiveBigIntegerField(
        null=False,
        help_text="Row (sample number) at which the range ends"
    )
    info = models.TextField(help_text="Additional information")

    def __str__(self) -> str:
        return f"{self.label} [{self.range_start}, {self.range_end}]: {self.info}"


class VouchFor(models.Model):
    new_user = models.ForeignKey(
        to=User,
        related_name='vouched_for',
        null=False,
        on_delete=models.DO_NOTHING,
        help_text="User needing approval"
    )
    vouching_user = models.ForeignKey(
        to=User,
        related_name='vouched_by',
        null=False,
        on_delete=models.DO_NOTHING,
        help_text="User doing approving"
    )

    def __str__(self):
        return f"{self.new_user.username} approved by {self.vouching_user.username}"


class KnoxAuthToken(models.Model):
    knox_token_key = models.TextField(help_text="KnoxToken reference ([token_key]_[user_id]")
    name = models.TextField(help_text="Convenient human-friendly name")

    def __str__(self):
        return f"{self.knox_token_key}:{self.name}"
