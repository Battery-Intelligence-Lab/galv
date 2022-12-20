from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User, Group

from .parsers import *
from pathlib import Path
import os
import random


class FileState(models.IntegerChoices):
    IMPORT_FAILED = -1
    UNSTABLE = 0
    GROWING = 1
    STABLE = 2
    IMPORTING = 3
    IMPORTED = 4


class Harvester(models.Model):
    name = models.TextField(unique=True)
    api_key = models.TextField(null=True)
    last_check_in = models.DateTimeField(null=True)
    sleep_time = models.IntegerField(default=10)  # default to short time so updates happen quickly
    admin_group = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        null=True,
        related_name='harvester_admins'
    )
    user_group = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        null=True,
        related_name='harvester_users'
    )

    def save(self, *args, **kwargs):
        if self.id is None:
            # Create groups for Harvester
            text = 'abcdefghijklmnopqrstuvwxyz' + \
                   'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
                   '0123456789' + \
                   '!£$%^&*-=+'
            self.api_key = f"galv_hrv_{''.join(random.choices(text, k=60))}"
        super(Harvester, self).save(*args, **kwargs)

    # Perform harvesting
    def run(self):
        paths = MonitoredPath.objects.filter(harvester=self)
        for path in paths:
            files = ObservedFile.objects.filter(monitored_path=path)
            for file in files:
                if file.state == FileState.STABLE:
                    file.import_content()
        self.last_successful_run = timezone.now()


class MonitoredPath(models.Model):
    harvester = models.ForeignKey(to=Harvester, on_delete=models.CASCADE)
    path = models.TextField(unique=True)

    class Meta:
        unique_together = [['harvester', 'path']]


class MonitoredFor(models.Model):
    path = models.ForeignKey(to=MonitoredPath, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)


class ObservedFile(models.Model):
    monitored_path = models.ForeignKey(to=MonitoredPath, on_delete=models.DO_NOTHING)
    relative_path = models.TextField()
    last_observed_size = models.PositiveBigIntegerField(null=False)
    last_observed_time = models.DateTimeField()
    state = models.SmallIntegerField(choices=FileState.choices, default=FileState.UNSTABLE, null=False)

    def inspect_size(self):
        path = Path(os.path.join(self.monitored_path.path, self.relative_path))
        last_observed_size = path.stat().st_size
        if last_observed_size > self.last_observed_size:
            self.last_observed_size = last_observed_size
            self.state = FileState.GROWING
        elif last_observed_size == self.last_observed_size:
            if self.last_observed_time + timezone.timedelta(minutes=5) < timezone.now():
                self.state = FileState.STABLE
            else:
                self.state = FileState.UNSTABLE

        self.last_observed_time = timezone.now()

    def import_content(self):
        path = Path(os.path.join(self.monitored_path.path, self.relative_path))
        self.state = FileState.IMPORTING
        try:
            if not os.path.isfile(path):
                raise FileNotFoundError
            print(f"Importing {path}")
            parse(path, DataColumnType.objects.filter(is_default=True))
            self.state = FileState.IMPORTED
        except BaseException as e:
            self.state = FileState.IMPORT_FAILED
            raise e

    class Meta:
        unique_together = [['monitored_path', 'relative_path']]


class CellData(models.Model):
    name = models.TextField(null=False, unique=True)
    form_factor = models.TextField()
    link_to_datasheet = models.TextField()
    anode_chemistry = models.TextField()
    cathode_chemistry = models.TextField()
    nominal_capacity = models.FloatField()
    nominal_cell_weight = models.FloatField()
    manufacturer = models.TextField()


class Dataset(models.Model):
    cell = models.ForeignKey(to=CellData, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    access_group = models.ForeignKey(to=Group, on_delete=models.CASCADE)
    name = models.TextField(null=False)
    date = models.DateTimeField(null=False)
    type = models.TextField(null=False)
    purpose = models.TextField()
    json_data = models.JSONField()

    class Meta:
        unique_together = [['name', 'date']]


class Equipment(models.Model):
    name = models.TextField(null=False, unique=True)
    type = models.TextField()


class DatasetEquipment(models.Model):
    dataset = models.ForeignKey(to=Dataset, on_delete=models.CASCADE)
    equipment = models.ForeignKey(to=Equipment, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['dataset', 'equipment']]


class DataUnit(models.Model):
    name = models.TextField(null=False)
    symbol = models.TextField(null=False)
    description = models.TextField()

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
    dataset = models.ForeignKey(to=Dataset, on_delete=models.CASCADE)
    type = models.ForeignKey(to=DataColumnType, on_delete=models.RESTRICT)
    name = models.TextField(null=False)

    class Meta:
        unique_together = [['dataset', 'name']]


class TimeseriesData(models.Model):
    sample = models.PositiveBigIntegerField(null=False)
    column = models.ForeignKey(to=DataColumn, null=False, on_delete=models.RESTRICT)
    value = models.FloatField(null=False)

    class Meta:
        unique_together = [['sample', 'column']]


class TimeseriesRangeLabel(models.Model):
    dataset = models.ForeignKey(to=Dataset, null=False, on_delete=models.CASCADE)
    label = models.TextField(null=False)
    range_start = models.PositiveBigIntegerField(null=False)
    range_end = models.PositiveBigIntegerField(null=False)
    info = models.TextField()
