from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User, Group


class FileState(models.IntegerChoices):
    IMPORT_FAILED = -1
    UNSTABLE = 0
    GROWING = 1
    STABLE = 2
    IMPORTING = 3
    IMPORTED = 4


class Harvester(models.Model):
    machine_id = models.TextField(unique=True)
    name = models.TextField()
    last_successful_run = models.DateTimeField()
    is_running = models.BooleanField(default=False)
    periodic_hour = models.IntegerField(validators=[
        MinValueValidator(1), MaxValueValidator(24)
    ])


class MonitoredPath(models.Model):
    harvester = models.ForeignKey(to=Harvester, on_delete=models.CASCADE)
    path = models.TextField(unique=True)

    class Meta:
        unique_together = [['harvester', 'path']]


class MonitoredFor(models.Model):
    path = models.ForeignKey(to=MonitoredPath, on_delete=models.CASCADE)
    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE)


class ObservedFile(models.Model):
    monitored_path = models.ForeignKey(to=MonitoredPath, on_delete=models.DO_NOTHING)
    relative_path = models.TextField()
    last_observed_size = models.PositiveBigIntegerField(null=False)
    last_observed_time = models.DateTimeField()
    file_state = models.SmallIntegerField(choices=FileState.choices, default=FileState.UNSTABLE, null=False)

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
    cell_id = models.ForeignKey(to=CellData, on_delete=models.SET_NULL, null=True)
    owner_id = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
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


class DataColumnType(models.Model):
    unit = models.ForeignKey(to=DataUnit, on_delete=models.SET_NULL, null=True)
    name = models.TextField(null=False)
    description = models.TextField()

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
