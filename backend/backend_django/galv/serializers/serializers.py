# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import os.path
import re

import jsonschema
from django.db.models import Q
from django.urls import reverse, resolve
from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import ValidationError
from urllib.parse import urlparse

from rest_framework.status import HTTP_403_FORBIDDEN

from ..models import Harvester, \
    HarvesterEnvVar, \
    HarvestError, \
    MonitoredPath, \
    ObservedFile, \
    Cell, \
    Equipment, \
    DataUnit, \
    DataColumnType, \
    DataColumn, \
    TimeseriesRangeLabel, \
    KnoxAuthToken, CellFamily, EquipmentTypes, CellFormFactors, CellChemistries, CellModels, CellManufacturers, \
    EquipmentManufacturers, EquipmentModels, EquipmentFamily, Schedule, ScheduleIdentifiers, CyclerTest, \
    render_pybamm_schedule, ScheduleFamily, ValidationSchema, Experiment, Lab, Team, GroupProxy, UserProxy, user_labs, \
    user_teams
from ..models.utils import ScheduleRenderError
from django.utils import timezone
from django.conf.global_settings import DATA_UPLOAD_MAX_MEMORY_SIZE
from rest_framework import serializers
from knox.models import AuthToken

from .utils import AdditionalPropertiesModelSerializer, GetOrCreateTextField, augment_extra_kwargs, url_help_text, \
    get_model_field, PermissionsMixin, TruncatedUserHyperlinkedRelatedIdField, \
    TruncatedGroupHyperlinkedRelatedIdField, TruncatedHyperlinkedRelatedIdField, \
    CreateOnlyMixin


class UserSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    current_password = serializers.CharField(
        write_only=True,
        allow_blank=True,
        required=False,
        style={'input_type': 'password'},
        help_text="Current password"
    )
    groups = TruncatedGroupHyperlinkedRelatedIdField(
        'GroupSerializer',
        ['url', 'id', 'name'],
        'groupproxy-detail',
        read_only=True,
        many=True,
        help_text="Groups this user belongs to"
    )

    @staticmethod
    def validate_password(value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters")
        return value

    def validate(self, attrs):
        current_password = attrs.pop('current_password', None)
        if self.instance and not self.instance.check_password(current_password):
            raise ValidationError(f"Current password is incorrect")
        return attrs

    def create(self, validated_data):
        user = UserProxy.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)

    class Meta:
        model = UserProxy
        write_fields = ['username', 'email', 'first_name', 'last_name']
        write_only_fields = ['password', 'current_password']
        read_only_fields = ['url', 'id', 'is_staff', 'is_superuser', 'groups', 'permissions']
        fields = [*write_fields, *read_only_fields, *write_only_fields]
        extra_kwargs = augment_extra_kwargs({
            'password': {'write_only': True, 'help_text': "Password (8 characters minimum)"},
        })


class GroupSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    users = TruncatedUserHyperlinkedRelatedIdField(
        UserSerializer,
        ['url', 'id', 'username', 'first_name', 'last_name', 'permissions'],
        view_name='userproxy-detail',
        read_only=True,
        source='user_set',
        many=True,
        help_text="Users in the group"
    )
    add_users = TruncatedUserHyperlinkedRelatedIdField(
        UserSerializer,
        ['url', 'id', 'username', 'first_name', 'last_name', 'permissions'],
        view_name='userproxy-detail',
        queryset=UserProxy.objects.all(),
        many=True,
        write_only=True,
        required=False,
        help_text="Users to add"
    )
    remove_users = TruncatedUserHyperlinkedRelatedIdField(
        UserSerializer,
        ['url', 'id', 'username', 'first_name', 'last_name', 'permissions'],
        view_name='userproxy-detail',
        queryset=UserProxy.objects.all(),
        many=True,
        write_only=True,
        required=False,
        help_text="Users to remove"
    )

    def validate_remove_users(self, value):
        # Only Lab admin groups have to have at least one user
        if hasattr(self.instance, 'editable_lab'):
            if len(self.instance.user_set.all()) <= len(value):
                raise ValidationError(f"Labs must always have at least one administrator")
        return value

    def update(self, instance, validated_data):
        if 'add_users' in validated_data:
            [instance.user_set.add(u) for u in validated_data.pop('add_users')]
        if 'remove_users' in validated_data:
            [instance.user_set.remove(u) for u in validated_data.pop('remove_users')]
        return instance

    class Meta:
        model = GroupProxy
        read_only_fields = ['id', 'url', 'name', 'users', 'permissions']
        fields = [*read_only_fields, 'add_users', 'remove_users']

class TeamSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    member_group = GroupSerializer(read_only=True, help_text="Members of this Team")
    admin_group = GroupSerializer(read_only=True, help_text="Administrators of this Team")
    cellfamily_resources = TruncatedHyperlinkedRelatedIdField(
        'CellFamilySerializer',
        ['manufacturer', 'model', 'chemistry', 'form_factor'],
        'cellfamily-detail',
        read_only=True,
        many=True,
        help_text="Cell Families belonging to this Team"
    )
    cell_resources = TruncatedHyperlinkedRelatedIdField(
        'CellSerializer',
        ['identifier', 'family'],
        'cell-detail',
        read_only=True,
        many=True,
        help_text="Cells belonging to this Team"
    )
    equipmentfamily_resources = TruncatedHyperlinkedRelatedIdField(
        'EquipmentFamilySerializer',
        ['type', 'manufacturer', 'model'],
        'equipmentfamily-detail',
        read_only=True,
        many=True,
        help_text="Equipment Families belonging to this Team"
    )
    equipment_resources = TruncatedHyperlinkedRelatedIdField(
        'EquipmentSerializer',
        ['identifier', 'family'],
        'equipment-detail',
        read_only=True,
        many=True,
        help_text="Equipment belonging to this Team"
    )
    schedulefamily_resources = TruncatedHyperlinkedRelatedIdField(
        'ScheduleFamilySerializer',
        ['identifier', ],
        'schedulefamily-detail',
        read_only=True,
        many=True,
        help_text="Schedule Families belonging to this Team"
    )
    schedule_resources = TruncatedHyperlinkedRelatedIdField(
        'ScheduleSerializer',
        ['family', ],
        'schedule-detail',
        read_only=True,
        many=True,
        help_text="Schedules belonging to this Team"
    )
    cyclertest_resources = TruncatedHyperlinkedRelatedIdField(
        'CyclerTestSerializer',
        ['cell', 'equipment', 'schedule'],
        'cyclertest-detail',
        read_only=True,
        many=True,
        help_text="Cycler Tests belonging to this Team"
    )
    experiment_resources = TruncatedHyperlinkedRelatedIdField(
        'ExperimentSerializer',
        ['title'],
        'experiment-detail',
        read_only=True,
        many=True,
        help_text="Experiments belonging to this Team"
    )
    lab = TruncatedHyperlinkedRelatedIdField(
        'LabSerializer',
        ['name'],
        'lab-detail',
        queryset=Lab.objects.all(),
        help_text="Lab this Team belongs to"
    )

    def validate_lab(self, value):
        """
        Only lab admins can create teams in their lab
        """
        try:
            assert value in user_labs(self.context['request'].user, True)
        except:
            raise ValidationError("You may only create Teams in your own lab(s)")
        return value

    class Meta:
        model = Team
        read_only_fields = [
            'url', 'id',
            'member_group', 'admin_group',
            'monitored_paths',
            'cellfamily_resources', 'cell_resources',
            'equipmentfamily_resources', 'equipment_resources',
            'schedulefamily_resources', 'schedule_resources',
            'cyclertest_resources', 'experiment_resources',
            'permissions'
        ]
        fields = [*read_only_fields, 'name', 'description', 'lab']

class LabSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    admin_group = GroupSerializer(help_text="Group of users who can edit this Lab")
    teams = TruncatedHyperlinkedRelatedIdField(
        'TeamSerializer',
        ['name', 'admin_group', 'member_group'],
        'team-detail',
        read_only=True,
        many=True,
        help_text="Teams in this Lab"
    )

    class Meta:
        model = Lab
        fields = ['url', 'id', 'name', 'description', 'admin_group', 'teams', 'permissions']
        read_only_fields = ['url', 'id', 'teams', 'admin_group', 'permissions']

class WithTeamMixin(serializers.Serializer):
    team = TruncatedHyperlinkedRelatedIdField(
        'TeamSerializer',
        ['name'],
        'team-detail',
        queryset=Team.objects.all(),
        help_text="Team this resource belongs to"
    )

    def validate_team(self, value):
        """
        Only team members can create resources in their team.
        If a resource is being moved from one team to another, the user must be a member of both teams.
        """
        teams = user_teams(self.context['request'].user)
        try:
            assert value in teams
        except:
            raise ValidationError("You may only create resources in your own team(s)")
        if self.instance is not None:
            try:
                assert self.instance.team in teams
            except:
                raise ValidationError("You may only edit resources in your own team(s)")
        return value

class CellSerializer(AdditionalPropertiesModelSerializer, PermissionsMixin, WithTeamMixin):
    family = TruncatedHyperlinkedRelatedIdField(
        'CellFamilySerializer',
        ['manufacturer', 'model', 'chemistry', 'form_factor'],
        'cellfamily-detail',
        queryset=CellFamily.objects.all(),
        help_text="Cell Family this Cell belongs to"
    )
    cycler_tests = TruncatedHyperlinkedRelatedIdField(
        'CyclerTestSerializer',
        ['equipment', 'schedule'],
        'cyclertest-detail',
        read_only=True,
        many=True,
        help_text="Cycler Tests using this Cell"
    )

    class Meta:
        model = Cell
        fields = ['url', 'uuid', 'identifier', 'family', 'cycler_tests', 'in_use', 'team', 'permissions']
        read_only_fields = ['url', 'uuid', 'cycler_tests', 'in_use', 'permissions']


class CellFamilySerializer(AdditionalPropertiesModelSerializer, PermissionsMixin, WithTeamMixin):
    manufacturer = GetOrCreateTextField(foreign_model=CellManufacturers, help_text="Manufacturer name")
    model = GetOrCreateTextField(foreign_model=CellModels, help_text="Model number")
    chemistry = GetOrCreateTextField(foreign_model=CellChemistries, help_text="Chemistry type")
    form_factor = GetOrCreateTextField(foreign_model=CellFormFactors, help_text="Physical form factor")
    cells = TruncatedHyperlinkedRelatedIdField(
        'CellSerializer',
        ['identifier'],
        'cell-detail',
        read_only=True,
        many=True,
        help_text="Cells belonging to this Cell Family"
    )

    class Meta:
        model = CellFamily
        fields = [
            'url',
            'uuid',
            'manufacturer',
            'model',
            'datasheet',
            'chemistry',
            'nominal_voltage',
            'nominal_capacity',
            'initial_ac_impedance',
            'initial_dc_resistance',
            'energy_density',
            'power_density',
            'form_factor',
            'cells',
            'in_use',
            'team',
            'permissions'
        ]
        read_only_fields = ['url', 'uuid', 'cells', 'in_use', 'permissions']


class EquipmentFamilySerializer(AdditionalPropertiesModelSerializer, PermissionsMixin, WithTeamMixin):
    type = GetOrCreateTextField(foreign_model=EquipmentTypes, help_text="Equipment type")
    manufacturer = GetOrCreateTextField(foreign_model=EquipmentManufacturers, help_text="Manufacturer name")
    model = GetOrCreateTextField(foreign_model=EquipmentModels, help_text="Model number")
    equipment = TruncatedHyperlinkedRelatedIdField(
        'EquipmentSerializer',
        ['identifier'],
        'equipment-detail',
        read_only=True,
        many=True,
        help_text="Equipment belonging to this Equipment Family"
    )

    class Meta:
        model = EquipmentFamily
        fields = [
            'url',
            'uuid',
            'type',
            'manufacturer',
            'model',
            'in_use',
            'team',
            'equipment',
            'permissions'
        ]
        read_only_fields = ['url', 'uuid', 'in_use', 'equipment', 'permissions']


class EquipmentSerializer(AdditionalPropertiesModelSerializer, PermissionsMixin, WithTeamMixin):
    family = TruncatedHyperlinkedRelatedIdField(
        'EquipmentFamilySerializer',
        ['type', 'manufacturer', 'model'],
        'equipmentfamily-detail',
        queryset=EquipmentFamily.objects.all(),
        help_text="Equipment Family this Equipment belongs to"
    )
    cycler_tests = TruncatedHyperlinkedRelatedIdField(
        'CyclerTestSerializer',
        ['cell', 'schedule'],
        'cyclertest-detail',
        read_only=True,
        many=True,
        help_text="Cycler Tests using this Equipment"
    )

    class Meta:
        model = Equipment
        fields = ['url', 'uuid', 'identifier', 'family', 'calibration_date', 'in_use', 'team', 'cycler_tests', 'permissions']
        read_only_fields = ['url', 'uuid', 'datasets', 'in_use', 'cycler_tests', 'permissions']

class ScheduleFamilySerializer(AdditionalPropertiesModelSerializer, PermissionsMixin, WithTeamMixin):
    identifier = GetOrCreateTextField(foreign_model=ScheduleIdentifiers)
    schedules = TruncatedHyperlinkedRelatedIdField(
        'ScheduleSerializer',
        ['family'],
        'schedule-detail',
        read_only=True,
        many=True,
        help_text="Schedules belonging to this Schedule Family"
    )

    def validate_pybamm_template(self, value):
        # TODO: validate pybamm template against pybamm.step.string
        return value

    class Meta:
        model = ScheduleFamily
        fields = [
            'url', 'uuid', 'identifier', 'description',
            'ambient_temperature', 'pybamm_template',
            'in_use', 'team', 'schedules', 'permissions'
        ]
        read_only_fields = ['url', 'uuid', 'in_use', 'schedules', 'permissions']


class ScheduleSerializer(AdditionalPropertiesModelSerializer, PermissionsMixin, WithTeamMixin):
    family = TruncatedHyperlinkedRelatedIdField(
        'ScheduleFamilySerializer',
        ['identifier'],
        'schedulefamily-detail',
        queryset=ScheduleFamily.objects.all(),
        help_text="Schedule Family this Schedule belongs to"
    )
    cycler_tests = TruncatedHyperlinkedRelatedIdField(
        'CyclerTestSerializer',
        ['cell', 'equipment'],
        'cyclertest-detail',
        read_only=True,
        many=True,
        help_text="Cycler Tests using this Schedule"
    )

    def validate_pybamm_schedule_variables(self, value):
        template = self.instance.family.pybamm_template
        if template is None and value is not None:
            raise ValidationError("pybamm_schedule_variables has no effect if pybamm_template is not set")
        if value is None:
            return value
        keys = self.instance.family.pybamm_template_variable_names()
        for k, v in value.items():
            if k not in keys:
                raise ValidationError(f"Schedule variable {k} is not in the template")
            try:
                float(v)
            except (ValueError, TypeError):
                raise ValidationError(f"Schedule variable {k} must be a number")
        return value

    def validate(self, data):
        if data.get('schedule_file') is None:
            try:
                family = data.get('family') or self.instance.family
                assert family.pybamm_template is not None
            except (AttributeError, AssertionError):
                raise ValidationError("Schedule_file must be provided where pybamm_template is not set")
        return data

    class Meta:
        model = Schedule
        fields = [
            'url', 'uuid', 'family',
            'schedule_file', 'pybamm_schedule_variables',
            'in_use', 'team', 'cycler_tests', 'permissions'
        ]
        read_only_fields = ['url', 'uuid', 'in_use', 'cycler_tests', 'permissions']


class CyclerTestSerializer(AdditionalPropertiesModelSerializer, PermissionsMixin, WithTeamMixin):
    rendered_schedule = serializers.SerializerMethodField(help_text="Rendered schedule")
    schedule = TruncatedHyperlinkedRelatedIdField(
        'ScheduleSerializer',
        ['family'],
        'schedule-detail',
        queryset=Schedule.objects.all(),
        help_text="Schedule this Cycler Test uses"
    )
    cell = TruncatedHyperlinkedRelatedIdField(
        'CellSerializer',
        ['identifier', 'family'],
        'cell-detail',
        queryset=Cell.objects.all(),
        help_text="Cell this Cycler Test uses"
    )
    equipment = TruncatedHyperlinkedRelatedIdField(
        'EquipmentSerializer',
        ['identifier', 'family'],
        'equipment-detail',
        queryset=Equipment.objects.all(),
        many=True,
        help_text="Equipment this Cycler Test uses"
    )

    def get_rendered_schedule(self, instance) -> str | None:
        if instance.schedule is None:
            return None
        return instance.rendered_pybamm_schedule(False)

    def validate(self, data):
        if data.get('schedule') is not None:
            try:
                render_pybamm_schedule(data['schedule'], data['cell'])
            except ScheduleRenderError as e:
                raise ValidationError(e)
        return data

    class Meta:
        model = CyclerTest
        fields = [
            'url', 'uuid', 'cell', 'equipment', 'schedule', 'rendered_schedule', 'team', 'permissions'
        ]
        read_only_fields = ['url', 'uuid', 'rendered_schedule', 'permissions']


class HarvesterSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    lab = TruncatedHyperlinkedRelatedIdField(
        'LabSerializer',
        ['name'],
        'lab-detail',
        read_only=True,
        help_text="Lab this Harvester belongs to"
    )

    class EnvField(serializers.DictField):
        # respresentation for json
        def to_representation(self, value) -> dict[str, str]:
            view = self.context.get('view')
            if view and view.action == 'list':
                return {}
            return {v.key: v.value for v in value.all() if not v.deleted}

        # representation for python object
        def to_internal_value(self, values):
            for k in values.keys():
                if not re.match(r'^[a-zA-Z0-9_]+$', k):
                    raise ValidationError(f'Key {k} is not alpha_numeric')
            for k, v in values.items():
                k = k.upper()
                try:
                    env = HarvesterEnvVar.objects.get(harvester=self.root.instance, key=k)
                    env.value = v
                    env.deleted = False
                    env.save()
                except HarvesterEnvVar.DoesNotExist:
                    HarvesterEnvVar.objects.create(harvester=self.root.instance, key=k, value=v)
            envvars = HarvesterEnvVar.objects.filter(harvester=self.root.instance, deleted=False)
            input_keys = [k.upper() for k in values.keys()]
            for v in envvars.all():
                if v.key not in input_keys:
                    v.deleted = True
                    v.save()
            return HarvesterEnvVar.objects.filter(harvester=self.root.instance, deleted=False)

    environment_variables = EnvField(help_text="Environment variables set on this Harvester")

    def validate_name(self, value):
        harvesters = Harvester.objects.filter(name=value)
        if self.instance is not None:
            harvesters = harvesters.exclude(uuid=self.instance.uuid)
            harvesters = harvesters.filter(lab=self.instance.lab)
        if harvesters.exists():
            raise ValidationError('Harvester with that name already exists')
        return value

    def validate_sleep_time(self, value):
        try:
            value = int(value)
            assert value > 0
            return value
        except (TypeError, ValueError, AssertionError):
            return ValidationError('sleep_time must be an integer greater than 0')

    class Meta:
        model = Harvester
        read_only_fields = ['url', 'uuid', 'last_check_in', 'lab', 'permissions']
        fields = [*read_only_fields, 'name', 'sleep_time', 'environment_variables', 'active']
        extra_kwargs = augment_extra_kwargs()


class MonitoredPathSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin, WithTeamMixin, CreateOnlyMixin):
    harvester = TruncatedHyperlinkedRelatedIdField(
        'HarvesterSerializer',
        ['name'],
        'harvester-detail',
        queryset=Harvester.objects.all(),
        help_text="Harvester this MonitoredPath belongs to"
    )

    def validate_path(self, value):
        try:
            value = str(value).lower().lstrip().rstrip()
        except BaseException as e:
            raise ValidationError(f"Invalid path: {e.__context__}")
        abs_path = os.path.abspath(value)
        return abs_path

    def validate_stable_time(self, value):
        try:
            v = int(value)
            assert v > 0
            return v
        except (TypeError, ValueError, AssertionError):
            raise ValidationError(f"stable_time value '{value}' is not a positive integer")

    def validate_regex(self, value):
        try:
            re.compile(value)
            return value
        except BaseException as e:
            raise ValidationError(f"Invalid regex: {e.__context__}")

    def validate(self, attrs):
        return attrs

    class Meta:
        model = MonitoredPath
        fields = ['url', 'uuid', 'path', 'regex', 'stable_time', 'active', 'harvester', 'team', 'permissions']
        read_only_fields = ['url', 'uuid', 'team', 'permissions']
        extra_kwargs = augment_extra_kwargs({
            'harvester': {'create_only': True}
        })


class ObservedFileSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    harvester = TruncatedHyperlinkedRelatedIdField(
        'HarvesterSerializer',
        ['name'],
        'harvester-detail',
        read_only=True,
        help_text="Harvester this File belongs to"
    )
    upload_info = serializers.SerializerMethodField(
        help_text="Metadata required for harvester program to resume file parsing"
    )
    has_required_columns = serializers.SerializerMethodField(
        help_text="Whether the file has all required columns"
    )
    columns = TruncatedHyperlinkedRelatedIdField(
        'DataColumnSerializer',
        ['name', 'data_type', 'unit', 'values'],
        view_name='datacolumn-detail',
        read_only=True,
        many=True,
        help_text="Columns extracted from this File"
    )
    column_errors = serializers.SerializerMethodField(
        help_text="Errors in uploaded columns"
    )

    def get_upload_info(self, instance) -> dict | None:
        if not self.context.get('with_upload_info'):
            return None
        try:
            last_record = 0
            columns = DataColumn.objects.filter(file=instance)
            column_data = []
            for c in columns:
                column_data.append({'name': c.name, 'id': c.id})
                if c.type.override_child_name == 'Sample_number':
                    last_record = c.values[:-1] if len(c.values) > 0 else 0
            return {
                'columns': column_data,
                'last_record_number': last_record
            }
        except BaseException as e:
            return {'columns': [], 'last_record_number': None, 'error': str(e)}

    def get_has_required_columns(self, instance) -> bool:
        return instance.has_required_columns()

    def get_column_errors(self, instance) -> list:
        return instance.column_errors()

    class Meta:
        model = ObservedFile
        read_only_fields = [
            'url', 'uuid', 'harvester', 'path',
            'state',
            'parser',
            'num_rows',
            'first_sample_no',
            'last_sample_no',
            'num_rows',
            'extra_metadata',
            'has_required_columns',
            'last_observed_time', 'last_observed_size', 'upload_errors',
            'column_errors',
            'upload_info', 'columns', 'permissions'
        ]
        fields = [*read_only_fields, 'name']
        extra_kwargs = augment_extra_kwargs({
            'upload_errors': {'help_text': "Errors associated with this File"}
        })


class HarvestErrorSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    harvester = TruncatedHyperlinkedRelatedIdField(
        'HarvesterSerializer',
        ['name', 'lab'],
        'harvester-detail',
        read_only=True,
        help_text="Harvester this HarvestError belongs to"
    )
    file = TruncatedHyperlinkedRelatedIdField(
        'ObservedFileSerializer',
        ['path'],
        'observedfile-detail',
        read_only=True,
        help_text="File this HarvestError belongs to"
    )

    class Meta:
        model = HarvestError
        fields = ['url', 'id', 'harvester', 'file', 'error', 'timestamp', 'permissions']
        extra_kwargs = augment_extra_kwargs()


class DataUnitSerializer(serializers.ModelSerializer, PermissionsMixin):
    class Meta:
        model = DataUnit
        fields = ['url', 'id', 'name', 'symbol', 'description', 'permissions']
        extra_kwargs = augment_extra_kwargs()


class TimeseriesRangeLabelSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    data = serializers.SerializerMethodField()

    class Meta:
        model = TimeseriesRangeLabel
        fields = '__all__'
        extra_kwargs = augment_extra_kwargs()


class DataColumnTypeSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    class Meta:
        model = DataColumnType
        fields = ['url', 'id', 'name', 'description', 'is_default', 'unit', 'permissions']
        extra_kwargs = augment_extra_kwargs()


class DataColumnSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    """
    A column contains metadata and data. Data are an ordered list of values.
    """
    name = serializers.SerializerMethodField(help_text="Column name (assigned by harvester but overridden by Galv for core fields)")
    is_required_column = serializers.SerializerMethodField(help_text="Whether the column is one of those required by Galv")
    type_name = serializers.SerializerMethodField(help_text=get_model_field(DataColumnType, 'name').help_text)
    description = serializers.SerializerMethodField(help_text=get_model_field(DataColumnType, 'description').help_text)
    unit = serializers.SerializerMethodField(help_text=get_model_field(DataColumnType, 'unit').help_text)
    values = serializers.SerializerMethodField(help_text="Column values")
    file = TruncatedHyperlinkedRelatedIdField(
        'ObservedFileSerializer',
        ['harvester', 'path'],
        view_name='observedfile-detail',
        read_only=True,
        help_text="File this Column belongs to"
    )


    def uri(self, rel_url: str) -> str:
        return self.context['request'].build_absolute_uri(rel_url)

    def get_name(self, instance) -> str:
        return instance.get_name()

    def get_is_required_column(self, instance) -> bool:
        return instance.type.is_required

    def get_type_name(self, instance) -> str:
        return instance.type.name

    def get_description(self, instance) -> str:
        return instance.type.description

    def get_unit(self, instance) -> dict[str, str] | None:
        return {
            k: v for k, v in
            DataUnitSerializer(instance.type.unit, context=self.context).data.items() \
            if k in ['url', 'id', 'name', 'symbol']
        }


    def get_values(self, instance) -> str:
        return self.uri(reverse('datacolumn-values', args=(instance.id,)))

    class Meta:
        model = DataColumn
        fields = [
            'id',
            'url',
            'name',
            'name_in_file',
            'is_required_column',
            'file',
            'data_type',
            'type_name',
            'description',
            'unit',
            'values',
            'permissions'
        ]
        read_only_fields = fields
        extra_kwargs = augment_extra_kwargs()


class ExperimentSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin, WithTeamMixin):
    cycler_tests = TruncatedHyperlinkedRelatedIdField(
        'CyclerTestSerializer',
        ['cell', 'equipment', 'schedule'],
        'cyclertest-detail',
        queryset=CyclerTest.objects.all(),
        many=True,
        help_text="Cycler Tests using this Experiment"
    )
    authors = TruncatedHyperlinkedRelatedIdField(
        'UserSerializer',
        ['username', 'first_name', 'last_name'],
        'userproxy-detail',
        queryset=UserProxy.objects.all(),
        many=True,
        help_text="Users who created this Experiment"
    )

    class Meta:
        model = Experiment
        fields = [
            'url',
            'uuid',
            'title',
            'description',
            'authors',
            'protocol',
            'protocol_file',
            'cycler_tests',
            'team',
            'permissions'
        ]
        read_only_fields = ['url', 'uuid', 'permissions']
        extra_kwargs = augment_extra_kwargs()

class ValidationSchemaSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin, WithTeamMixin):
    def validate_schema(self, value):
        try:
            jsonschema.validate({}, value)
        except jsonschema.exceptions.SchemaError as e:
            raise ValidationError(e)
        except jsonschema.exceptions.ValidationError:
            pass
        return value

    class Meta:
        model = ValidationSchema
        fields = ['url', 'uuid', 'team', 'name', 'schema', 'permissions']

class KnoxTokenSerializer(serializers.HyperlinkedModelSerializer):
    created = serializers.SerializerMethodField(help_text="Date and time of creation")
    expiry = serializers.SerializerMethodField(help_text="Date and time token expires (blank = never)")
    url = serializers.SerializerMethodField(help_text=url_help_text)

    def knox_token(self, instance):
        key, id = instance.knox_token_key.split('_')
        if not int(id) == self.context['request'].user.id:
            raise ValueError('Bad user ID for token access')
        return AuthToken.objects.get(user_id=int(id), token_key=key)

    def get_created(self, instance) -> timezone.datetime:
        return self.knox_token(instance).created

    def get_expiry(self, instance) -> timezone.datetime | None:
        return self.knox_token(instance).expiry

    def get_url(self, instance) -> str:
        return self.context['request'].build_absolute_uri(reverse('tokens-detail', args=(instance.id,)))

    class Meta:
        model = KnoxAuthToken
        fields = ['url', 'id', 'name', 'created', 'expiry']
        read_only_fields = ['url', 'id', 'created', 'expiry']
        extra_kwargs = augment_extra_kwargs()


class KnoxTokenFullSerializer(KnoxTokenSerializer):
    token = serializers.SerializerMethodField(help_text="Token value")

    def get_token(self, instance) -> str:
        return self.context['token']

    class Meta:
        model = KnoxAuthToken
        fields = ['url', 'id', 'name', 'created', 'expiry', 'token']
        read_only_fields = fields
        extra_kwargs = augment_extra_kwargs()


class HarvesterConfigSerializer(HarvesterSerializer, PermissionsMixin):
    standard_units = serializers.SerializerMethodField(help_text="Units recognised by the initial database")
    standard_columns = serializers.SerializerMethodField(help_text="Column Types recognised by the initial database")
    max_upload_bytes = serializers.SerializerMethodField(help_text="Maximum upload size (bytes)")
    deleted_environment_variables = serializers.SerializerMethodField(help_text="Envvars to unset")
    monitored_paths = MonitoredPathSerializer(many=True, read_only=True, help_text="Directories to harvest")

    @extend_schema_field(DataUnitSerializer(many=True))
    def get_standard_units(self, instance):
        return DataUnitSerializer(
            DataUnit.objects.filter(is_default=True),
            many=True,
            context={'request': self.context['request']}
        ).data

    @extend_schema_field(DataColumnTypeSerializer(many=True))
    def get_standard_columns(self, instance):
        # return []
        return DataColumnTypeSerializer(
            DataColumnType.objects.filter(is_default=True),
            many=True,
            context={'request': self.context['request']}
        ).data

    def get_max_upload_bytes(self, instance):
        return DATA_UPLOAD_MAX_MEMORY_SIZE

    def get_deleted_environment_variables(self, instance):
        return [v.key for v in instance.environment_variables.all() if v.deleted]

    class Meta:
        model = Harvester
        fields = [
            'url', 'uuid', 'api_key', 'name', 'sleep_time', 'monitored_paths',
            'standard_units', 'standard_columns', 'max_upload_bytes',
            'environment_variables', 'deleted_environment_variables', 'permissions'
        ]
        read_only_fields = fields
        extra_kwargs = augment_extra_kwargs({
            'environment_variables': {'help_text': "Envvars set on this Harvester"}
        })
        depth = 1


class HarvesterCreateSerializer(HarvesterSerializer, PermissionsMixin):
    lab = TruncatedHyperlinkedRelatedIdField(
        'LabSerializer',
        ['name'],
        'lab-detail',
        queryset=Lab.objects.all(),
        required=True,
        help_text="Lab this Harvester belongs to"
    )

    def validate_lab(self, value):
        try:
            if value in user_labs(self.context['request'].user, True):
                return value
        except:
            pass
        raise ValidationError("You may only create Harvesters in your own lab(s)")

    def to_representation(self, instance):
        return HarvesterConfigSerializer(context=self.context).to_representation(instance)

    class Meta:
        model = Harvester
        fields = ['name', 'lab', 'permissions']
        read_only_fields = ['permissions']
        extra_kwargs = {'name': {'required': True}, 'lab': {'required': True}}
