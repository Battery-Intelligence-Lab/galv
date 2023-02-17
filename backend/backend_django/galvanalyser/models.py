from django.db.models import F
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User, Group

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
    name = models.TextField(unique=True)
    api_key = models.TextField(null=True)
    last_check_in = models.DateTimeField(null=True)
    sleep_time = models.IntegerField(default=10)  # default to short time so updates happen quickly
    admin_group = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        null=True,
        related_name='editable_harvesters'
    )
    user_group = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        null=True,
        related_name='readable_harvesters'
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


class MonitoredPath(models.Model):
    harvester = models.ForeignKey(to=Harvester, related_name='monitored_paths', on_delete=models.SET_NULL, null=True)
    path = models.TextField()
    stable_time = models.PositiveSmallIntegerField(default=60)  # seconds files must remain stable to be processed
    admin_group = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        null=True,
        related_name='editable_paths'
    )
    user_group = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        null=True,
        related_name='readable_paths'
    )

    def __str__(self):
        return self.path

    class Meta:
        unique_together = [['harvester', 'path']]


class ObservedFile(models.Model):
    monitored_path = models.ForeignKey(to=MonitoredPath, related_name='files', on_delete=models.CASCADE)
    relative_path = models.TextField()
    last_observed_size = models.PositiveBigIntegerField(null=False, default=0)
    last_observed_time = models.DateTimeField(null=True)
    state = models.TextField(choices=FileState.choices, default=FileState.UNSTABLE, null=False)

    def __str__(self):
        return self.relative_path

    class Meta:
        unique_together = [['monitored_path', 'relative_path']]


class HarvestError(models.Model):
    harvester = models.ForeignKey(to=Harvester, related_name='paths', on_delete=models.CASCADE)
    path = models.ForeignKey(to=MonitoredPath, on_delete=models.DO_NOTHING)
    file = models.ForeignKey(to=ObservedFile, related_name='errors', on_delete=models.SET_NULL, null=True)
    error = models.TextField()
    timestamp = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        if self.path:
            if self.file:
                return f"{self.error} [Harvester_{self.harvester_id}/{self.path}/{self.file}]"
            return f"{self.error} [Harvester_{self.harvester_id}/{self.path}]"
        return f"{self.error} [Harvester_{self.harvester_id}]"


class CellFamily(models.Model):
    name = models.TextField(null=False, unique=True)
    form_factor = models.TextField()
    link_to_datasheet = models.TextField()
    anode_chemistry = models.TextField()
    cathode_chemistry = models.TextField()
    nominal_capacity = models.FloatField()
    nominal_cell_weight = models.FloatField()
    manufacturer = models.TextField()

    def __str__(self):
        return f"{self.name} [CellFamily {self.id}]"


class Cell(models.Model):
    display_name = models.TextField(null=True, unique=True)
    family = models.ForeignKey(to=CellFamily, related_name='cells', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.display_name} [Cell {self.id}]"


class Dataset(models.Model):
    cell = models.ForeignKey(to=Cell, related_name='datasets', on_delete=models.SET_NULL, null=True)
    file = models.ForeignKey(to=ObservedFile, on_delete=models.DO_NOTHING, related_name='datasets')
    name = models.TextField(null=True)
    date = models.DateTimeField(null=False)
    type = models.TextField(null=True)
    purpose = models.TextField()
    json_data = models.JSONField(null=True)

    def __str__(self):
        return f"{self.name} [Dataset {self.id}]"

    class Meta:
        unique_together = [['file', 'date']]


class Equipment(models.Model):
    name = models.TextField(null=False, unique=True)
    type = models.TextField()
    datasets = models.ManyToManyField(to=Dataset, related_name='equipment')

    def __str__(self):
        return f"{self.name} [Equipment {self.id}]"


class DataUnit(models.Model):
    name = models.TextField(null=False)
    symbol = models.TextField(null=False)
    description = models.TextField()
    is_default = models.BooleanField(default=False)

    def __str__(self):
        if self.symbol:
            return f"{self.symbol} | {self.name} - {self.description}"
        return f"{self.name} - {self.description}"


class DataColumnType(models.Model):
    unit = models.ForeignKey(to=DataUnit, on_delete=models.SET_NULL, null=True)
    name = models.TextField(null=False)
    description = models.TextField()
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = [['unit', 'name']]


class DataColumn(models.Model):
    dataset = models.ForeignKey(to=Dataset, related_name='columns', on_delete=models.CASCADE)
    type = models.ForeignKey(to=DataColumnType, on_delete=models.CASCADE)
    name = models.TextField(null=False)

    def __str__(self):
        return f"{self.name} ({self.type.unit.symbol})"

    class Meta:
        unique_together = [['dataset', 'name']]


class DataColumnStringKeys(models.Model):
    """
    String values are not allowed in TimeseriesData,
    so instead we store integer keys whose string values
    can be looked up in this table.
    """
    column = models.ForeignKey(to=DataColumn, related_name='string_keys', on_delete=models.CASCADE)
    key = models.PositiveBigIntegerField(null=False)
    string = models.TextField(null=False)

    class Meta:
        unique_together = [['column', 'key', 'string']]


class TimeseriesData(models.Model):
    sample = models.PositiveBigIntegerField(null=False)
    column_id = models.PositiveIntegerField(null=False)
    value = models.FloatField(null=False)

    class Meta:
        managed = False
        db_table = "timeseries_data"

    def __str__(self):
        return f"{self.column_id}[{self.sample}]: {self.value}"

    def __repr__(self):
        return str(self)


class TimeseriesRangeLabel(models.Model):
    dataset = models.ForeignKey(to=Dataset, related_name='range_labels', null=False, on_delete=models.CASCADE)
    label = models.TextField(null=False)
    range_start = models.PositiveBigIntegerField(null=False)
    range_end = models.PositiveBigIntegerField(null=False)
    info = models.TextField()
