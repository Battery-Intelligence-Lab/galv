# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import os
import re
from typing import Type

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import User, Group
import random

from dry_rest_permissions.generics import allow_staff_or_superuser

from .utils import AdditionalPropertiesModel, JSONModel, LDSources, render_pybamm_schedule, UUIDModel, \
    combine_rdf_props, ValidatableBySchemaMixin
from .autocomplete_entries import *


class FileState(models.TextChoices):
    RETRY_IMPORT = "RETRY IMPORT"
    IMPORT_FAILED = "IMPORT FAILED"
    UNSTABLE = "UNSTABLE"
    GROWING = "GROWING"
    STABLE = "STABLE"
    IMPORTING = "IMPORTING"
    IMPORTED = "IMPORTED"


# Proxy User and Group models so that we can apply DRYPermissions
class UserProxy(User):
    class Meta:
        proxy = True

    @staticmethod
    def has_create_permission(request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return request.user.is_staff or request.user.is_superuser

    def has_object_write_permission(self, request):
        return request.user.is_staff or request.user.is_superuser or self == request.user

    def has_object_read_permission(self, request):
        return request.user.is_staff or request.user.is_superuser or self == request.user

class GroupProxy(Group):
    class Meta:
        proxy = True

    @staticmethod
    def has_create_permission(request):
        return False

    @staticmethod
    def has_delete_permission(self, request):
        return False

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return request.user.is_staff or request.user.is_superuser

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        owner = self.editable_lab or self.editable_team or self.readable_team
        if owner is not None:
            return owner.has_object_write_permission(request) or self in request.user.groups.all()
        return False

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        owner = self.editable_lab or self.editable_team or self.readable_team
        if owner is not None:
            return owner.has_object_read_permission(request) or self in request.user.groups.all()
        return self in request.user.groups.all()

class Lab(models.Model):
    name = models.TextField(
        unique=True,
        help_text="Human-friendly Lab identifier"
    )
    description = models.TextField(
        null=True,
        help_text="Description of the Lab"
    )
    admin_group = models.OneToOneField(
        to=Group,
        on_delete=models.CASCADE,
        null=True,
        related_name='editable_lab',
        help_text="Users authorised to make changes to the Lab"
    )

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    def has_create_permission(request):
        return request.user.is_staff or request.user.is_superuser

    def has_object_read_permission(self, request):
        return (
                request.user.is_staff or
                request.user.is_superuser or
                self in user_labs(request.user, True) or
                self in user_teams(request.user)
        )

    def has_object_write_permission(self, request):
        return (
                request.user.is_staff or
                request.user.is_superuser or
                self in user_labs(request.user, True)
        )

    def __str__(self):
        return f"{self.name} [Lab {self.pk}]"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.admin_group is None:
            # Create groups for Lab
            self.admin_group = GroupProxy.objects.create(name=f"Lab {self.pk} admins")
        super(Lab, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        self.admin_group.delete()
        super(Lab, self).delete(using, keep_parents)


class Team(models.Model):
    name = models.TextField(
        unique=True,
        help_text="Human-friendly Team identifier"
    )
    description = models.TextField(
        null=True,
        help_text="Description of the Team"
    )
    lab = models.ForeignKey(
        to=Lab,
        on_delete=models.CASCADE,
        null=False,
        related_name='teams',
        help_text="Lab to which this Team belongs"
    )
    admin_group = models.OneToOneField(
        to=Group,
        on_delete=models.CASCADE,
        null=True,
        related_name='editable_team',
        help_text="Users authorised to make changes to the Team"
    )
    member_group = models.OneToOneField(
        to=Group,
        on_delete=models.CASCADE,
        null=True,
        related_name='readable_team',
        help_text="Users authorised to view this Team's Experiments"
    )

    @staticmethod
    def has_create_permission(request):
        return request.user.is_authenticated and len(user_labs(request.user, True)) > 0

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_read_permission(self, request):
        return (
                self.lab in user_labs(request.user, True) or
                self in user_teams(request.user)
        )

    def has_object_write_permission(self, request):
        return (
                self.lab in user_labs(request.user, True) or
                self in user_teams(request.user, True)
        )

    def __str__(self):
        return f"{self.name} [Team {self.pk}]"

    def save(
self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.admin_group is None:
            # Create groups for Team
            self.admin_group = GroupProxy.objects.create(name=f"Team {self.pk} admins")
        if self.member_group is None:
            self.member_group = GroupProxy.objects.create(name=f"Team {self.pk} members")
        super(Team, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        self.admin_group.delete()
        self.member_group.delete()
        super(Team, self).delete(using, keep_parents)


def user_teams(user, editable=False):
    """
    Return a list of all teams the user is a member of
    """
    try:
        teams = []
        for g in user.groups.all():
            teams += [t for t in g.editable_teams.all()]
            if not editable:
                teams += [t for t in g.readable_teams.all()]
    except AttributeError:
        return []
    return teams


def user_labs(user, editable=False):
    """
    Return a list of all labs the user is a member of
    """
    if not editable:
        return [t.lab for t in user_teams(user)]
    labs = []
    for g in user.groups.all():
        if hasattr(g, 'editable_lab') and g.editable_lab is not None:
            labs.append(g.editable_lab)
    return labs

def user_is_active(user):
    return len(user_labs(user)) > 0


class ResourceModelPermissionsMixin(models.Model):
    team = models.ForeignKey(
        to=Team,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="%(class)s_resources"
    )
    members_can_edit = models.BooleanField(default=True)
    any_user_can_read = models.BooleanField(default=False)
    any_user_can_edit = models.BooleanField(default=False)
    anonymous_can_read = models.BooleanField(default=False)

    def has_object_read_permission(self, request):
        return self.anonymous_can_read or \
            (self.any_user_can_read and user_is_active(request.user)) or \
            self.team.member_group in request.user.groups.all() or \
            self.team.admin_group in request.user.groups.all()

    def has_object_write_permission(self, request):
        return self.team.admin_group in request.user.groups.all() or \
            (self.members_can_edit and self.team.member_group in request.user.groups.all()) or \
            (self.any_user_can_edit and user_is_active(request.user))

    @staticmethod
    def has_create_permission(request):
        return request.user.is_authenticated and user_is_active(request.user)

    class Meta:
        abstract = True


class BibliographicInfo(models.Model):
    user = models.OneToOneField(to=UserProxy, on_delete=models.CASCADE, null=False, blank=False)
    bibjson = models.JSONField(null=False, blank=False)

    def has_object_read_permission(self, request):
        return self.user == request.user

    def has_object_write_permission(self, request):
        return self.user == request.user

    @staticmethod
    def has_create_permission(request):
        return request.user.is_authenticated and user_is_active(request.user)

    def __str__(self):
        return f"{self.user.username} byline"


class CellFamily(AdditionalPropertiesModel, ValidatableBySchemaMixin, ResourceModelPermissionsMixin):
    manufacturer = models.ForeignKey(to=CellManufacturers, help_text="Name of the manufacturer", null=True, blank=True, on_delete=models.CASCADE)
    model = models.ForeignKey(to=CellModels, help_text="Model number for the cells", null=False, on_delete=models.CASCADE)
    chemistry = models.ForeignKey(to=CellChemistries, help_text="Chemistry of the cells", null=True, blank=True, on_delete=models.CASCADE)
    form_factor = models.ForeignKey(to=CellFormFactors, help_text="Physical shape of the cells", null=True, blank=True, on_delete=models.CASCADE)
    datasheet = models.URLField(help_text="Link to the datasheet", null=True, blank=True)
    nominal_voltage = models.FloatField(help_text="Nominal voltage of the cells (in volts)", null=True, blank=True)
    nominal_capacity = models.FloatField(help_text="Nominal capacity of the cells (in amp hours)", null=True, blank=True)
    initial_ac_impedance = models.FloatField(help_text="Initial AC impedance of the cells (in ohms)", null=True, blank=True)
    initial_dc_resistance = models.FloatField(help_text="Initial DC resistance of the cells (in ohms)", null=True, blank=True)
    energy_density = models.FloatField(help_text="Energy density of the cells (in watt hours per kilogram)", null=True, blank=True)
    power_density = models.FloatField(help_text="Power density of the cells (in watts per kilogram)", null=True, blank=True)

    def in_use(self):
        return self.cells.count() > 0

    def __str__(self):
        return f"{str(self.manufacturer)} {str(self.model)} ({str(self.chemistry)}, {str(self.form_factor)})"

    class Meta(AdditionalPropertiesModel.Meta):
        unique_together = [['model', 'manufacturer']]

class Cell(JSONModel, ValidatableBySchemaMixin, ResourceModelPermissionsMixin):
    identifier = models.TextField(unique=True, help_text="Unique identifier (e.g. serial number) for the cell", null=False)
    family = models.ForeignKey(to=CellFamily, on_delete=models.CASCADE, null=False, help_text="Cell type", related_name="cells")

    def in_use(self):
        return self.cycler_tests.count() > 0

    def __str__(self):
        return f"{self.identifier} [{str(self.family)}]"

    def __json_ld__(self):
        return combine_rdf_props(
            super().__json_ld__(),
            {
                "_context": [LDSources.BattINFO, LDSources.SCHEMA],
                "@type": f"{LDSources.BattINFO}:BatteryCell",
                f"{LDSources.SCHEMA}:serialNumber": self.identifier,
                f"{LDSources.SCHEMA}:identifier": self.family.model.__json_ld__(),
                f"{LDSources.SCHEMA}:documentation": str(self.family.datasheet),
                f"{LDSources.SCHEMA}:manufacturer": self.family.manufacturer.__json_ld__()
                # TODO: Add more fields from CellFamily
            }
        )


class EquipmentFamily(AdditionalPropertiesModel, ValidatableBySchemaMixin, ResourceModelPermissionsMixin):
    type = models.ForeignKey(to=EquipmentTypes, on_delete=models.CASCADE, null=False, help_text="Type of equipment")
    manufacturer = models.ForeignKey(to=EquipmentManufacturers, on_delete=models.CASCADE, null=False, help_text="Manufacturer of equipment")
    model = models.ForeignKey(to=EquipmentModels, on_delete=models.CASCADE, null=False, help_text="Model of equipment")

    def in_use(self):
        return self.equipment.count() > 0

    def __str__(self):
        return f"{str(self.manufacturer)} {str(self.model)} ({str(self.type)})"

class Equipment(JSONModel, ValidatableBySchemaMixin, ResourceModelPermissionsMixin):
    identifier = models.TextField(unique=True, help_text="Unique identifier (e.g. serial number) for the equipment", null=False)
    family = models.ForeignKey(to=EquipmentFamily, on_delete=models.CASCADE, null=False, help_text="Equipment type", related_name="equipment")
    calibration_date = models.DateField(help_text="Date of last calibration", null=True, blank=True)

    def in_use(self):
        return self.cycler_tests.count() > 0

    def __str__(self):
        return f"{self.identifier} [{str(self.family)}]"

    def __json_ld__(self):
        return {
            "_context": [LDSources.BattINFO, LDSources.SCHEMA],
            "@type": self.family.type.__json_ld__(),
            f"{LDSources.SCHEMA}:serialNumber": self.identifier,
            f"{LDSources.SCHEMA}:identifier": str(self.family.model.__json_ld__()),
            f"{LDSources.SCHEMA}:manufacturer": str(self.family.manufacturer.__json_ld__())
        }


class ScheduleFamily(AdditionalPropertiesModel, ValidatableBySchemaMixin, ResourceModelPermissionsMixin):
    identifier = models.OneToOneField(to=ScheduleIdentifiers, unique=True, blank=False, null=False, help_text="Type of experiment, e.g. Constant-Current Discharge", on_delete=models.CASCADE)
    description = models.TextField(help_text="Description of the schedule")
    ambient_temperature = models.FloatField(help_text="Ambient temperature during the experiment (in degrees Celsius)", null=True, blank=True)
    pybamm_template = ArrayField(base_field=models.TextField(), help_text="Template for the schedule in PyBaMM format", null=True, blank=True)

    def pybamm_template_variable_names(self):
        template = "\n".join(self.pybamm_template)
        return re.findall(r"\{([\w_]+)}", template)

    def in_use(self):
        return self.schedules.count() > 0

    def __str__(self):
        return f"{str(self.identifier)}"


class Schedule(JSONModel, ValidatableBySchemaMixin, ResourceModelPermissionsMixin):
    family = models.ForeignKey(to=ScheduleFamily, on_delete=models.CASCADE, null=False, help_text="Schedule type", related_name="schedules")
    schedule_file = models.FileField(help_text="File containing the schedule", null=True, blank=True)
    pybamm_schedule_variables = models.JSONField(help_text="Variables used in the PyBaMM.Experiment representation of the schedule", null=True, blank=True)

    def in_use(self):
        return self.cycler_tests.count() > 0

    def __str__(self):
        return f"{str(self.uuid)} [{str(self.family)}]"

class Harvester(UUIDModel, ValidatableBySchemaMixin):
    name = models.TextField(
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
        default=120,
        help_text="Seconds to sleep between Harvester cycles"
    )  # default to short time so updates happen quickly
    active = models.BooleanField(
        default=True,
        help_text="Whether the Harvester is active"
    )
    lab = models.ForeignKey(
        to=Lab,
        on_delete=models.CASCADE,
        null=False,
        help_text="Lab to which this Harvester belongs"
    )

    class Meta:
        unique_together = [['name', 'lab']]

    @staticmethod
    def has_create_permission(request):
        return request.user.is_authenticated and len(user_labs(request.user, True)) > 0

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return self.is_valid_harvester(request) or self.lab.has_object_read_permission(request)

    def has_object_write_permission(self, request):
        return self.lab.has_object_write_permission(request)

    def is_valid_harvester(self, request):
        return self.api_key == request.META.get('HTTP_AUTHORIZATION', '').replace("Harvester ", "")

    def has_object_config_permission(self, request):
        return self.is_valid_harvester(request)

    def has_object_report_permission(self, request):
        return self.is_valid_harvester(request)

    def __str__(self):
        return f"{self.name} [Harvester {self.uuid}]"

    def save(self, *args, **kwargs):
        if self.api_key is None:
            # Create groups for Harvester
            text = 'abcdefghijklmnopqrstuvwxyz' + \
                   'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
                   '0123456789' + \
                   '!£$%^&*-=+'
            self.api_key = f"galv_hrv_{''.join(random.choices(text, k=60))}"
        super(Harvester, self).save(*args, **kwargs)


class ObservedFile(UUIDModel, ValidatableBySchemaMixin, ResourceModelPermissionsMixin):
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
    data_generation_date = models.DateTimeField(
        null=True,
        help_text="Date and time of generated data. Time will be midnight if not specified in raw data"
    )
    inferred_format = models.TextField(
        null=True,
        help_text="Format of the raw data"
    )
    name = models.TextField(
        null=True,
        help_text="Name of the file"
    )
    parser = models.TextField(
        null=True,
        help_text="Parser used by the harvester"
    )
    num_rows = models.PositiveIntegerField(
        null=True,
        help_text="Number of rows in the file"
    )
    first_sample_no = models.PositiveIntegerField(
        null=True,
        help_text="Number of the first sample in the file"
    )
    last_sample_no = models.PositiveIntegerField(
        null=True,
        help_text="Number of the last sample in the file"
    )
    extra_metadata = models.JSONField(
        null=True,
        help_text="Extra metadata from the harvester"
    )

    def has_object_read_permission(self, request):
        if self.harvester.is_valid_harvester(request):
            return True
        try:
            teams = [t for t in user_teams(request.user) if t.lab == self.harvester.lab]
            for team in teams:
                for path in team.monitored_paths.all():
                    if path.matches(self.path):
                        return True
        except AttributeError:
            return False
        return False

    def has_object_write_permission(self, request):
        return self.has_object_read_permission(request)

    def missing_required_columns(self):
        errors = []
        for required_column in DataColumnType.objects.filter(is_required=True):
            if not self.columns.filter(type=required_column).count() == 1:
                errors.append(f"Missing required column: {required_column.override_child_name or required_column.name}")
        return errors

    def has_required_columns(self):
        return len(self.missing_required_columns()) == 0

    def column_errors(self):
        errors = []
        names = []
        for c in self.columns.all():
            if c.get_name() in names:
                errors.append(f"Duplicate column name: {c.get_name()}")
            names.append(c.get_name())
        return [*self.missing_required_columns(), *errors]

    def __str__(self):
        return self.path

    class Meta(UUIDModel.Meta):
        unique_together = [['path', 'harvester']]


class CyclerTest(JSONModel, ValidatableBySchemaMixin, ResourceModelPermissionsMixin):
    cell_subject = models.ForeignKey(to=Cell, on_delete=models.CASCADE, null=False, help_text="Cell that was tested", related_name="cycler_tests")
    schedule = models.ForeignKey(to=Schedule, null=True, blank=True, on_delete=models.CASCADE, help_text="Schedule used to test the cell", related_name="cycler_tests")
    equipment = models.ManyToManyField(to=Equipment, help_text="Equipment used to test the cell", related_name="cycler_tests")
    file = models.ManyToManyField(to=ObservedFile,  help_text="Columns of data in the test", related_name="cycler_tests")

    def __str__(self):
        return f"{self.cell_subject} [CyclerTest {self.uuid}]"

    def rendered_pybamm_schedule(self, validate = True):
        """
        Return the PyBaMM representation of the schedule, with variables filled in.
        Variables are taken from the cell properties, cell family properties, and schedule variables (most preferred first).
        """
        return render_pybamm_schedule(self.schedule, self.cell_subject, validate = validate)


class Experiment(JSONModel, ValidatableBySchemaMixin, ResourceModelPermissionsMixin):
    title = models.TextField(help_text="Title of the experiment")
    description = models.TextField(help_text="Description of the experiment", null=True, blank=True)
    authors = models.ManyToManyField(to=UserProxy, help_text="Authors of the experiment")
    protocol = models.JSONField(help_text="Protocol of the experiment", null=True, blank=True)
    protocol_file = models.FileField(help_text="Protocol file of the experiment", null=True, blank=True)
    cycler_tests = models.ManyToManyField(to=CyclerTest, help_text="Cycler tests of the experiment", related_name="experiments")

    def __str__(self):
        return self.title


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

    def has_object_read_permission(self, request):
        return self.harvester.has_object_read_permission(request)

    def has_object_write_permission(self, request):
        return self.harvester.has_object_write_permission(request)

    def __str__(self):
        return f"{self.key}={self.value}{'*' if self.deleted else ''}"

    class Meta:
        unique_together = [['harvester', 'key']]


class MonitoredPath(UUIDModel, ResourceModelPermissionsMixin):
    harvester = models.ForeignKey(
        to=Harvester,
        related_name='monitored_paths',
        on_delete=models.DO_NOTHING,
        null=False,
        help_text="Harvester with access to this directory"
    )
    path = models.TextField(help_text="Directory location on Harvester")
    regex = models.TextField(
        null=True,
        blank=True,
        help_text="""
    Python.re regular expression to filter files by, 
    applied to full file name starting from this Path's directory"""
    )
    stable_time = models.PositiveSmallIntegerField(
        default=60,
        help_text="Number of seconds files must remain stable to be processed"
    )
    active = models.BooleanField(default=True, null=False)
    team = models.ForeignKey(
        to=Team,
        related_name='monitored_paths',
        on_delete=models.CASCADE,
        null=True,
        help_text="Team with access to this Path"
    )

    def __str__(self):
        return self.path

    def matches(self, path):
        if not self.regex:
            return path.startswith(self.path)
        return re.search(self.regex, os.path.relpath(path, self.path))

    class Meta(UUIDModel.Meta):
        unique_together = [['harvester', 'path', 'regex', 'team']]


class HarvestError(models.Model):
    harvester = models.ForeignKey(
        to=Harvester,
        related_name='upload_errors',
        on_delete=models.CASCADE,
        help_text="Harvester which reported the error"
    )
    file = models.ForeignKey(
        to=ObservedFile,
        related_name='upload_errors',
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

    def has_object_read_permission(self, request):
        return self.harvester.has_object_read_permission(request)

    def __str__(self):
        if self.file:
            return f"{self.error} [Harvester_{self.harvester_id}/{self.file}]"
        return f"{self.error} [Harvester_{self.harvester_id}]"


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

    @staticmethod
    def has_write_permission(request):
        for harvester in Harvester.objects.all():
            if harvester.is_valid_harvester(request):
                return True
        return request.user.is_staff or request.user.is_superuser

    @staticmethod
    def has_read_permission(request):
        return True

    def __str__(self):
        if self.symbol:
            return f"{self.symbol} | {self.name} - {self.description}"
        return f"{self.name} - {self.description}"


class DataColumnType(models.Model, ValidatableBySchemaMixin):
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
    is_required = models.BooleanField(
        default=False,
        help_text="Whether the Column must be present in every Dataset"
    )
    override_child_name = models.TextField(
        null=True,
        blank=True,
        help_text="If set, this name will be used instead of the Column name in Dataframes"
    )

    @staticmethod
    def has_write_permission(request):
        for harvester in Harvester.objects.all():
            if harvester.is_valid_harvester(request):
                return True
        return request.user.is_staff or request.user.is_superuser

    @staticmethod
    def has_read_permission(request):
        return True

    def __str__(self):
        if self.is_default:
            if self.is_required:
                return f"{self.name} ({self.unit.symbol}) [required]"
            return f"{self.name} ({self.unit.symbol} [default])"
        return f"{self.name} ({self.unit.symbol})"

    class Meta:
        unique_together = [['unit', 'name']]


class DataColumn(models.Model):
    file = models.ForeignKey(
        to=ObservedFile,
        related_name='columns',
        on_delete=models.CASCADE,
        help_text="File in which this Column appears"
    )
    type = models.ForeignKey(
        to=DataColumnType,
        on_delete=models.CASCADE,
        help_text="Column Type which this Column instantiates"
    )
    data_type = models.TextField(null=False, help_text="Type of the data in this column")
    name_in_file = models.TextField(null=False, help_text="Column title e.g. in .tsv file headers")

    @staticmethod
    def has_create_permission(request):
        for harvester in Harvester.objects.all():
            if harvester.is_valid_harvester(request):
                return True
        return request.user.is_staff or request.user.is_superuser

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_write_permission(self, request):
        return self.file.has_object_write_permission(request)

    def get_name(self):
        return self.type.override_child_name or self.name_in_file

    def __str__(self):
        return f"{self.get_name()} ({self.type.unit.symbol})"

    class Meta:
        unique_together = [['file', 'name_in_file']]

# Timeseries data comes in different types, so we need to store them separately.
# These helper functions reduce redundancy in the code that creates the models.
# TODO: could use Django's GenericColumn (GenericForeignKey?) here
class TimeseriesBase(models.Model):
    column = models.OneToOneField(
        to=DataColumn,
        on_delete=models.CASCADE,
        help_text="Column whose data are listed"
    )
    values = ArrayField(models.Field())
    def __str__(self):
        if not self.values:
            return f"{self.column_id}: []"
        if len(self.values) > 5:
            return f"{self.column_id}: [{','.join(self.values[:5])}...]"
        return f"{self.column_id}: [{','.join(self.values)}]"

    def __repr__(self):
        return str(self)

    def has_object_read_permission(self, request):
        return self.column.file.has_object_read_permission(request)

    def has_object_write_permission(self, request):
        return self.column.file.has_object_write_permission(request)

    class Meta:
        abstract = True

class TimeseriesDataFloat(TimeseriesBase):
    values = ArrayField(models.FloatField(null=True), null=True, help_text="Row values (floats) for Column")


class TimeseriesDataInt(TimeseriesBase):
    values = ArrayField(models.IntegerField(null=True), null=True, help_text="Row values (integers) for Column")


class TimeseriesDataStr(TimeseriesBase):
    values = ArrayField(models.TextField(null=True), null=True, help_text="Row values (str) for Column")


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
    file = models.ForeignKey(
        to=ObservedFile,
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

    def has_object_read_permission(self, request):
        return self.file.has_object_read_permission(request)

    def has_object_write_permission(self, request):
        return self.file.has_object_write_permission(request)

    def __str__(self) -> str:
        return f"{self.label} [{self.range_start}, {self.range_end}]: {self.info}"


class ValidationSchema(ResourceModelPermissionsMixin):
    """
    JSON schema that can be used for validating components.
    """
    name = models.TextField(null=False, help_text="Human-friendly identifier")
    schema = models.JSONField(help_text="JSON Schema")

    def __str__(self):
        return f"{self.name}"


class KnoxAuthToken(models.Model):
    knox_token_key = models.TextField(help_text="KnoxToken reference ([token_key]_[user_id]")
    name = models.TextField(help_text="Convenient human-friendly name")

    def __str__(self):
        return f"{self.knox_token_key}:{self.name}"
