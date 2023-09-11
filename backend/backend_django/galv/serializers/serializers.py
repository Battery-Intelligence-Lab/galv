# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import os.path
import re

from django.db.models import Q
from django.urls import reverse, resolve
from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import ValidationError
from urllib.parse import urlparse

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
    render_pybamm_schedule, ScheduleFamily, ValidationSchema, Experiment, Lab, Team, GroupProxy, UserProxy
from ..models.utils import ScheduleRenderError
from django.utils import timezone
from django.conf.global_settings import DATA_UPLOAD_MAX_MEMORY_SIZE
from rest_framework import serializers
from knox.models import AuthToken

from .utils import AdditionalPropertiesModelSerializer, GetOrCreateTextField, augment_extra_kwargs, url_help_text, \
    get_model_field, PermissionsMixin, HyperlinkedRelatedIdField, GroupHyperlinkedRelatedIdListField, \
    UserHyperlinkedRelatedIdListField, TruncatedUserHyperlinkedRelatedIdField, \
    TruncatedGroupHyperlinkedRelatedIdField, serializer_class_from_string, TruncatedHyperlinkedRelatedIdField


class UserSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    groups = TruncatedGroupHyperlinkedRelatedIdField(
        'GroupSerializer',
        ['url', 'id', 'name'],
        'groupproxy-detail',
        queryset=GroupProxy.objects.all(),
        many=True,
        help_text="Groups this user belongs to"
    )

    is_active = serializers.SerializerMethodField(help_text="Whether this user is active")
    def get_is_active(self, instance):
        return instance.is_active

    class Meta:
        model = UserProxy
        write_fields = ['username', 'email', 'first_name', 'last_name']
        write_only_fields = ['password']
        read_only_fields = ['url', 'id', 'is_active', 'is_staff', 'is_superuser', 'groups', 'permissions']
        fields = [*write_fields, *read_only_fields, *write_only_fields]
        extra_kwargs = augment_extra_kwargs({
            'password': {'write_only': True, 'help_text': "Password (8 characters minimum)"},
        })


class GroupSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    users = TruncatedUserHyperlinkedRelatedIdField(
        UserSerializer,
        ['url', 'id', 'username', 'first_name', 'last_name', 'permissions'],
        'userproxy-detail',
        queryset=UserProxy.objects.all(),
        source='user_set',
        many=True,
        help_text="Users in the group"
    )
    add_user = serializers.HyperlinkedRelatedField(
        view_name='userproxy-detail',
        queryset=UserProxy.objects.all(),
        write_only=True,
        required=False,
        help_text="User to add"
    )
    remove_user = serializers.HyperlinkedRelatedField(
        view_name='userproxy-detail',
        queryset=UserProxy.objects.all(),
        write_only=True,
        required=False,
        help_text="User to remove"
    )

    @staticmethod
    def validate_remove_user(value):
        # Only Lab admin groups have to have at least one user
        if value.editable_labs is None:
            return value
        if len(value.user_set.all()) <= 1:
            raise ValidationError(f"Labs must always have at least one administrator")
        return value

    class Meta:
        model = GroupProxy
        read_only_fields = ['id', 'url', 'name', 'users', 'permissions']
        fields = [*read_only_fields, 'add_user', 'remove_user']

class TeamSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    member_group = GroupSerializer(help_text="Members of this Team")
    admin_group = GroupSerializer(help_text="Administrators of this Team")
    cellfamily_resources = TruncatedHyperlinkedRelatedIdField(
        'CellFamilySerializer',
        ['manufacturer', 'model', 'chemistry', 'form_factor'],
        'cellfamily-detail',
        queryset=CellFamily.objects.all(),
        many=True,
        help_text="Cell Families belonging to this Team"
    )
    cell_resources = TruncatedHyperlinkedRelatedIdField(
        'CellSerializer',
        ['identifier', 'family'],
        'cell-detail',
        queryset=Cell.objects.all(),
        many=True,
        help_text="Cells belonging to this Team"
    )
    equipmentfamily_resources = TruncatedHyperlinkedRelatedIdField(
        'EquipmentFamilySerializer',
        ['type', 'manufacturer', 'model'],
        'equipmentfamily-detail',
        queryset=EquipmentFamily.objects.all(),
        many=True,
        help_text="Equipment Families belonging to this Team"
    )
    equipment_resources = TruncatedHyperlinkedRelatedIdField(
        'EquipmentSerializer',
        ['identifier', 'family'],
        'equipment-detail',
        queryset=Equipment.objects.all(),
        many=True,
        help_text="Equipment belonging to this Team"
    )
    schedulefamily_resources = TruncatedHyperlinkedRelatedIdField(
        'ScheduleFamilySerializer',
        ['identifier', ],
        'schedulefamily-detail',
        queryset=ScheduleFamily.objects.all(),
        many=True,
        help_text="Schedule Families belonging to this Team"
    )
    schedule_resources = TruncatedHyperlinkedRelatedIdField(
        'ScheduleSerializer',
        ['family', ],
        'schedule-detail',
        queryset=Schedule.objects.all(),
        many=True,
        help_text="Schedules belonging to this Team"
    )
    cyclertest_resources = TruncatedHyperlinkedRelatedIdField(
        'CyclerTestSerializer',
        ['cell_subject', 'equipment', 'schedule'],
        'cyclertest-detail',
        queryset=CyclerTest.objects.all(),
        many=True,
        help_text="Cycler Tests belonging to this Team"
    )
    experiment_resources = TruncatedHyperlinkedRelatedIdField(
        'ExperimentSerializer',
        ['title'],
        'experiment-detail',
        queryset=Experiment.objects.all(),
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
        queryset=Team.objects.all(),
        many=True,
        help_text="Teams in this Lab"
    )

    class Meta:
        model = Lab
        fields = ['url', 'id', 'name', 'description', 'admin_group', 'teams', 'permissions']
        read_only_fields = ['url', 'id', 'teams', 'admins', 'permissions']

class WithTeamMixin(serializers.Serializer):
    team = TruncatedHyperlinkedRelatedIdField(
        'TeamSerializer',
        ['name'],
        'team-detail',
        queryset=Team.objects.all(),
        help_text="Team this resource belongs to"
    )

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
        queryset=CyclerTest.objects.all(),
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
        queryset=Cell.objects.all(),
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
        queryset=Equipment.objects.all(),
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
        ['cell_subject', 'schedule'],
        'cyclertest-detail',
        queryset=CyclerTest.objects.all(),
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
        queryset=Schedule.objects.all(),
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
        ['cell_subject', 'equipment'],
        'cyclertest-detail',
        queryset=CyclerTest.objects.all(),
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
    cell_subject = TruncatedHyperlinkedRelatedIdField(
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

    def get_rendered_schedule(self, instance):
        if instance.schedule is None:
            return None
        return instance.rendered_pybamm_schedule(False)

    def validate(self, data):
        if data.get('schedule') is not None:
            try:
                render_pybamm_schedule(data['schedule'], data['cell_subject'])
            except ScheduleRenderError as e:
                raise ValidationError(e)
        return data

    class Meta:
        model = CyclerTest
        fields = [
            'url', 'uuid', 'cell_subject', 'equipment', 'schedule', 'rendered_schedule', 'team', 'permissions'
        ]
        read_only_fields = ['url', 'uuid', 'rendered_schedule', 'permissions']


class HarvesterSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    lab = TruncatedHyperlinkedRelatedIdField(
        'LabSerializer',
        ['name'],
        'lab-detail',
        queryset=Lab.objects.all(),
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


class MonitoredPathSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin, WithTeamMixin):
    harvester = serializers.SerializerMethodField(help_text="Harvester this MonitoredPath belongs to")

    def validate_path(self, value):
        try:
            value = str(value).lower().lstrip().rstrip()
        except BaseException as e:
            raise ValidationError(f"Invalid path: {e.__context__}")
        abs_path = os.path.abspath(value)
        # if self.instance is None:
        #     try:
        #         pk = resolve(urlparse(self.initial_data['harvester']).path).kwargs['pk']
        #         Harvester.objects.get(id=pk)
        #     except BaseException:
        #         raise ValidationError("Harvester not found")
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
        read_only_fields = ['url', 'uuid', 'harvester', 'team', 'permissions']
        extra_kwargs = augment_extra_kwargs()


class MonitoredPathCreateSerializer(MonitoredPathSerializer, PermissionsMixin):

    def create(self, validated_data):
        stable_time = validated_data.get('stable_time', 60)
        regex = validated_data.get('regex')
        # Default path admin is requesting user or harvester's first admin (if Harvester is requesting path creation)
        admin = self.context['request'].user
        if admin is None or not admin.is_authenticated:
            if self.context['request'].META.get('HTTP_AUTHORIZATION', '') == \
                    f"Harvester {validated_data['harvester'].api_key}":
                admin = validated_data['harvester'].admin_group.user_set.all().first()
        if admin is None:
            raise ValidationError("Unable to determine admin user for path creation")
        # Create Path
        try:
            monitored_path = MonitoredPath.objects.create(
                path=validated_data['path'],
                harvester=validated_data['harvester'],
                stable_time=stable_time,
                regex=regex
            )
        except (TypeError, ValueError):
            monitored_path = MonitoredPath.objects.create(
                path=validated_data['path'],
                harvester=validated_data['harvester'],
                regex=regex
            )
        # Create user/admin groups
        monitored_path.admin_group = GroupProxy.objects.create(
            name=f"path_{monitored_path.uuid}_admins"
        )
        monitored_path.user_group = GroupProxy.objects.create(
            name=f"path_{monitored_path.uuid}_users"
        )
        monitored_path.save()
        admin.groups.add(monitored_path.admin_group)
        return monitored_path

    def to_representation(self, instance):
        return MonitoredPathSerializer(context=self.context).to_representation(instance)

    class Meta:
        model = MonitoredPath
        fields = ['path', 'regex', 'stable_time', 'harvester', 'team', 'permissions']
        read_only_fields = ['permissions']
        extra_kwargs = augment_extra_kwargs({
            'stable_time': {'required': False},
        })


class ObservedFileSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin, WithTeamMixin):
    upload_info = serializers.SerializerMethodField(
        help_text="Metadata required for harvester program to resume file parsing"
    )
    has_required_columns = serializers.SerializerMethodField(
        help_text="Whether the file has all required columns"
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
        fields = [*read_only_fields, 'name', 'team']
        extra_kwargs = augment_extra_kwargs({
            'upload_errors': {'help_text': "Errors associated with this File"},
            'columns': {'help_text': "Columns extracted from this File"}
        })


class HarvestErrorSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    harvester = serializers.SerializerMethodField(help_text="Harvester this HarvestError belongs to")
    file = serializers.SerializerMethodField(help_text="File this HarvestError belongs to")

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

    @extend_schema_field(DataUnitSerializer())
    def get_unit(self, instance):
        return DataUnitSerializer(instance.type.unit, context=self.context).data

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


class ExperimentSerializer(serializers.HyperlinkedModelSerializer, PermissionsMixin):
    cycler_tests = serializers.SerializerMethodField(help_text="Cycler Tests using this Experiment")

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
            'permissions'
        ]
        read_only_fields = ['url', 'uuid', 'permissions']
        extra_kwargs = augment_extra_kwargs()


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

    def create(self, validated_data):
        """
        Create a Harvester and the user Groups required to control it.
        """
        # Create Harvester
        harvester = Harvester.objects.create(name=validated_data['name'], lab=validated_data['lab'])
        harvester.save()
        # Add user as admin

        return harvester

    def to_representation(self, instance):
        return HarvesterConfigSerializer(context=self.context).to_representation(instance)

    class Meta:
        model = Harvester
        fields = ['name', 'lab', 'permissions']
        read_only_fields = ['permissions']
        extra_kwargs = {'name': {'required': True}}
