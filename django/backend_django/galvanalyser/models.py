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


class Machine(models.Model):
    pass


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


# -- Add required column
#
# INSERT INTO experiment.unit (id, name, symbol, description) VALUES (0, 'Unitless', '', 'A value with no units');
# INSERT INTO experiment.unit (id, name, symbol, description) VALUES (1, 'Time', 's', 'Time in seconds');
# INSERT INTO experiment.unit (id, name, symbol, description) VALUES (2, 'Volts', 'V', 'Voltage');
# INSERT INTO experiment.unit (id, name, symbol, description) VALUES (3, 'Amps', 'A', 'Current');
# INSERT INTO experiment.unit (id, name, symbol, description) VALUES (4, 'Energy', 'Wh', 'Energy in Watt-Hours');
# INSERT INTO experiment.unit (id, name, symbol, description) VALUES (5, 'Charge', 'Ah', 'Charge in Amp-Hours');
# INSERT INTO experiment.unit (id, name, symbol, description) VALUES (6, 'Temperature', '°c', 'Temperature in Centigrade');
# INSERT INTO experiment.unit (id, name, symbol, description) VALUES (7, 'Power', 'W', 'Power in Watts');
# INSERT INTO experiment.unit (id, name, symbol, description) VALUES (8, 'Ohm', 'Ω', 'Resistance or impediance in Ohms');
# INSERT INTO experiment.unit (id, name, symbol, description) VALUES (9, 'Degrees', '°', 'Angle in degrees');
# INSERT INTO experiment.unit (id, name, symbol, description) VALUES (10, 'Frequency', 'Hz', 'Frequency in Hz');
# SELECT setval('experiment.unit_id_seq'::regclass, 10);
#
# INSERT INTO experiment.column_type (id, name, description, unit_id) VALUES (-1, 'Unknown', 'unknown column type', NULL);
# INSERT INTO experiment.column_type (id, name, description, unit_id) VALUES (0, 'Sample Number', 'The sample or record number. Is increased by one each time a test machine records a reading. Usually counts from 1 at the start of a test', 0);
# INSERT INTO experiment.column_type (id, name, description, unit_id) VALUES (1, 'Time', 'The time in seconds since the test run began.', 1);
# INSERT INTO experiment.column_type (id, name, description, unit_id) VALUES (2, 'Volts', 'The voltage of the cell.', 2);
# INSERT INTO experiment.column_type (id, name, description, unit_id) VALUES (3, 'Amps', 'The current current.', 3);
# INSERT INTO experiment.column_type (id, name, description, unit_id) VALUES (4, 'Energy Capacity', 'The Energy Capacity.', 4);
# INSERT INTO experiment.column_type (id, name, description, unit_id) VALUES (5, 'Charge Capacity', 'The Charge Capacity.', 5);
# INSERT INTO experiment.column_type (id, name, description, unit_id) VALUES (6, 'Temperature', 'The temperature.', 6);
# INSERT INTO experiment.column_type (id, name, description, unit_id) VALUES (7, 'Step Time', 'The time in seconds since the current step began.', 1);
# INSERT INTO experiment.column_type (id, name, description, unit_id) VALUES (8, 'Impedence Magnitude', 'The magnitude of the impedence (EIS).', 8);
# INSERT INTO experiment.column_type (id, name, description, unit_id) VALUES (9, 'Impedence Phase', 'The phase of the impedence (EIS).', 9);
# INSERT INTO experiment.column_type (id, name, description, unit_id) VALUES (10, 'Frequency', 'The frequency of the input EIS voltage signal.', 10);
# SELECT setval('experiment.column_type_id_seq'::regclass, 10);