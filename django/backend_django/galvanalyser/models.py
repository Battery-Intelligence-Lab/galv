from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User, Group

import random


class FileState(models.Choices):
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
    harvester = models.ForeignKey(to=Harvester, related_name='monitored_paths', on_delete=models.CASCADE)
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

    class Meta:
        unique_together = [['harvester', 'path']]


class HarvestError(models.Model):
    harvester = models.ForeignKey(to=Harvester, related_name='paths', on_delete=models.CASCADE)
    path = models.ForeignKey(to=MonitoredPath, on_delete=models.DO_NOTHING)
    file = models.TextField(null=True)
    error = models.TextField()
    timestamp = models.DateTimeField(auto_now=True, null=True)


class ObservedFile(models.Model):
    monitored_path = models.ForeignKey(to=MonitoredPath, related_name='files', on_delete=models.DO_NOTHING)
    relative_path = models.TextField()
    last_observed_size = models.PositiveBigIntegerField(null=False, default=0)
    last_observed_time = models.DateTimeField(null=True)
    state = models.TextField(choices=FileState.choices, default=FileState.UNSTABLE, null=False)

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
    file = models.ForeignKey(to=ObservedFile, on_delete=models.DO_NOTHING, related_name='datasets')
    name = models.TextField(null=True)
    date = models.DateTimeField(null=False)
    type = models.TextField(null=True)
    purpose = models.TextField()
    json_data = models.JSONField(null=True)

    class Meta:
        unique_together = [['file', 'date']]


class Equipment(models.Model):
    name = models.TextField(null=False, unique=True)
    type = models.TextField()


class DatasetEquipment(models.Model):
    dataset = models.ForeignKey(to=Dataset, related_name='equipment', on_delete=models.CASCADE)
    equipment = models.ForeignKey(to=Equipment, related_name='datasets', on_delete=models.CASCADE)

    class Meta:
        unique_together = [['dataset', 'equipment']]


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
    column = models.ForeignKey(to=DataColumn, related_name='values', null=False, on_delete=models.CASCADE)
    value = models.FloatField(null=False)

    class Meta:
        unique_together = [['sample', 'column']]


class TimeseriesRangeLabel(models.Model):
    dataset = models.ForeignKey(to=Dataset, related_name='range_labels', null=False, on_delete=models.CASCADE)
    label = models.TextField(null=False)
    range_start = models.PositiveBigIntegerField(null=False)
    range_end = models.PositiveBigIntegerField(null=False)
    info = models.TextField()
