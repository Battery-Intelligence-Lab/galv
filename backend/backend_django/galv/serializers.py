# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import json
import os.path
import re

import django.db.models
from django.urls import reverse, resolve
from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import ValidationError
from urllib.parse import urlparse

from .models import Harvester, \
    HarvesterEnvVar, \
    HarvestError, \
    MonitoredPath, \
    ObservedFile, \
    Cell, \
    CellFamily, \
    Dataset, \
    Equipment, \
    DataUnit, \
    DataColumnType, \
    DataColumn, \
    TimeseriesRangeLabel, \
    KnoxAuthToken, CellFamily, EquipmentTypes, CellFormFactors, CellChemistries, CellModels, CellManufacturers
from .utils import get_monitored_paths
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.conf.global_settings import DATA_UPLOAD_MAX_MEMORY_SIZE
from rest_framework import serializers
from knox.models import AuthToken


url_help_text = "Canonical URL for this object"


def augment_extra_kwargs(extra_kwargs: dict[str, dict] = None):
    def _augment(name: str, content: dict):
        if name == 'url':
            return {'help_text': url_help_text, 'read_only': True, **content}
        if name == 'id':
            return {'help_text': "Auto-assigned object identifier", 'read_only': True, **content}
        return {**content}

    if extra_kwargs is None:
        extra_kwargs = {}
    extra_kwargs = {'url': {}, 'id': {}, **extra_kwargs}
    return {k: _augment(k, v) for k, v in extra_kwargs.items()}


def get_model_field(model: django.db.models.Model, field_name: str) -> django.db.models.Field:
    """
    Get a field from a Model.
    Works, but generates type warnings because Django uses hidden Metaclass ModelBase for models.
    """
    fields = {f.name: f for f in model._meta.fields}
    return fields[field_name]


class GetOrCreateTextField(serializers.CharField):
    """
    A CharField that will create a new object if it does not exist.
    """
    def __init__(self, foreign_model, foreign_model_field: str = 'value', **kwargs):
        super().__init__(**kwargs)
        self.foreign_model = foreign_model
        self.foreign_model_field = foreign_model_field

    def to_internal_value(self, data):
        # Let CharField do the basic validation
        data = super().to_internal_value(data)
        return self.foreign_model.objects.get_or_create(**{self.foreign_model_field: data})[0]
    def to_representation(self, value):
        return getattr(value, self.foreign_model_field)


class GetOrCreateTextFieldList(serializers.ListField):
    """
    Adapt serializers.ListField to use GetOrCreateTextField.
    Solves ManyRelatedManager is not iterable error.
    """
    def to_representation(self, data):
        return super().to_representation(data.all())


class AdditionalPropertiesModelSerializer(serializers.HyperlinkedModelSerializer):
    """
    A ModelSerializer that maps unrecognised properties in the input to an 'additional_properties' JSONField,
    and unpacks the 'additional_properties' JSONField into the output.
    """
    additional_properties = serializers.JSONField(required=False, write_only=True, source='additional_properties')

    class Meta:
        model: django.db.models.Model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model_fields = {f.name for f in self.Meta.model._meta.fields}
        if 'additional_properties' not in model_fields:
            raise ValueError("AdditionalPropertiesModelSerializer must define additional_properties")

    def to_representation(self, instance):
        data = {k: v for k, v in super().to_representation(instance).items() if k != '_additional_properties'}
        for k, v in instance.additional_properties.items():
            if k in data:
                raise ValueError(f"Basic model property {k} duplicated in _additional_properties")
        return {**data, **instance.additional_properties}


    def to_internal_value(self, data):
        if "additional_properties" in data:
            new_data = {'additional_properties': {'additional_properties': data.pop('additional_properties')}}
        else:
            new_data = {'additional_properties': {}}
        for k, v in data.items():
            if k not in self.fields:
                try:
                    json.dumps(v)
                except BaseException:
                    raise ValidationError(f"Value {v} for key {k} is not JSON serializable")
                new_data['additional_properties'][k] = v
            else:
                new_data[k] = v
        return new_data


class CellSerializer(AdditionalPropertiesModelSerializer):
    class Meta:
        model = Cell
        fields = ['url', 'uuid', 'Identifier', 'CellFamily']
        read_only_fields = ['url', 'uuid']

class CellFamilySerializer(serializers.HyperlinkedModelSerializer):
    manufacturer = GetOrCreateTextField(foreign_model=CellManufacturers, help_text="Manufacturer name")
    model = GetOrCreateTextField(foreign_model=CellModels, help_text="Model number")
    chemistry = GetOrCreateTextField(foreign_model=CellChemistries, help_text="Chemistry type")
    form_factor = GetOrCreateTextField(foreign_model=CellFormFactors, help_text="Physical form factor")

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
        ]
        read_only_fields = ['url', 'uuid', 'Cells']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField(help_text=url_help_text)

    def get_url(self, instance) -> str:
        uri = self.context['request'].build_absolute_uri
        if instance.is_active:
            return uri(reverse('user-detail', args=(instance.id,)))
        return uri(reverse('inactive_user-detail', args=(instance.id,)))

    class Meta:
        model = User
        write_fields = ['username', 'email', 'first_name', 'last_name']
        read_only_fields = ['url', 'id', 'is_active', 'is_staff', 'is_superuser']
        fields = [*write_fields, *read_only_fields]
        extra_kwargs = augment_extra_kwargs()


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    users = serializers.SerializerMethodField(help_text="Users in the group")

    @extend_schema_field(UserSerializer(many=True))
    def get_users(self, instance):
        return UserSerializer(
            instance.user_set.filter(is_active=True),
            many=True,
            context={'request': self.context['request']}
        ).data

    class Meta:
        model = Group
        fields = [
            'id',
            'url',
            'name',
            'users',
            'readable_paths',
            'editable_paths',
            'readable_harvesters',
            'editable_harvesters'
        ]
        extra_kwargs = augment_extra_kwargs({
            'readable_paths': {'help_text': "Paths on which this Group are Users"},
            'editable_paths': {'help_text': "Paths on which this Group are Admins"},
            'readable_harvesters': {'help_text': "Harvesters for which this Group are Users"},
            'editable_harvesters': {'help_text': "Harvesters for which this Group are Admins"},
        })


class UserSetSerializer(GroupSerializer):
    description = serializers.SerializerMethodField(help_text="Permissions granted to users with this role")
    users = serializers.SerializerMethodField(help_text="Users in this group")
    name = serializers.SerializerMethodField(help_text="Group name")
    is_admin = serializers.SerializerMethodField(help_text="Whether this is an administrator group")

    def my_context(self, instance, key: str, default=None):
        return self.context.get(instance.id, {}).get(key, default)

    def get_description(self, instance) -> str | None:
        return self.my_context(instance, 'description')

    def get_name(self, instance) -> str:
        return self.my_context(instance, 'name', instance.name)

    def get_is_admin(self, instance) -> bool:
        """
        Admin groups can control their own members, as well as members in groups
        lower down the list of UserSets[]
        """
        return self.my_context(instance, 'is_admin', False)

    class Meta:
        model = Group
        fields = ['url', 'id', 'name', 'description', 'is_admin', 'users']
        read_only_fields = fields
        extra_kwargs = augment_extra_kwargs()


class HarvesterSerializer(serializers.HyperlinkedModelSerializer):
    class EnvField(serializers.DictField):
        # respresentation for json
        def to_representation(self, value) -> dict[str, str]:
            view = self.context.get('view')
            if view and view.action == 'list':
                return {}
            return {v.key: v.value for v in value.all() if not v.deleted}

        # respresentation for python object
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

    user_sets = serializers.SerializerMethodField(help_text="Roles and the Users assigned to them")
    environment_variables = EnvField(help_text="Environment variables set on this Harvester")

    @extend_schema_field(UserSetSerializer(many=True))
    def get_user_sets(self, instance):
        group_ids = [instance.admin_group.id, instance.user_group.id]
        return UserSetSerializer(
            Group.objects.filter(id__in=group_ids).order_by('id'),
            context={
                'request': self.context.get('request'),
                instance.admin_group.id: {
                    'name': 'Admins',
                    'description': (
                        'Administrators can change harvester properties, '
                        'as well as any of the harvester\'s paths or datasets.'
                    ),
                    'is_admin': True
                },
                instance.user_group.id: {
                    'name': 'Users',
                    'description': (
                        'Users can view harvester properties. '
                        'They can also add monitored paths.'
                    )
                }
            },
            many=True
        ).data

    def validate_name(self, value):
        harvesters = Harvester.objects.filter(name=value)
        if self.instance is not None:
            harvesters = harvesters.exclude(id=self.instance.id)
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
        fields = ['url', 'id', 'name', 'sleep_time', 'last_check_in', 'user_sets', 'environment_variables']
        read_only_fields = ['url', 'id', 'last_check_in', 'user_sets']
        extra_kwargs = augment_extra_kwargs()


class MonitoredPathSerializer(serializers.HyperlinkedModelSerializer):
    user_sets = serializers.SerializerMethodField(help_text="Roles and the Users assigned to them")

    @extend_schema_field(UserSetSerializer(many=True))
    def get_user_sets(self, instance):
        group_ids = [instance.admin_group.id, instance.user_group.id]
        return UserSetSerializer(
            Group.objects.filter(id__in=group_ids).order_by('id'),
            context={
                'request': self.context.get('request'),
                instance.admin_group.id: {
                    'name': 'Admins',
                    'description': (
                        'Administrators can change paths and their datasets.'
                    ),
                    'is_admin': True
                },
                instance.user_group.id: {
                    'name': 'Users',
                    'description': (
                        'Users can view monitored paths and edit their datasets.'
                    )
                }
            },
            many=True
        ).data

    def validate_path(self, value):
        try:
            value = str(value).lower().lstrip().rstrip()
        except BaseException as e:
            raise ValidationError(f"Invalid path: {e.__context__}")
        abs_path = os.path.abspath(value)
        if self.instance is None:
            try:
                pk = resolve(urlparse(self.initial_data['harvester']).path).kwargs['pk']
                Harvester.objects.get(id=pk)
            except BaseException:
                raise ValidationError("Harvester not found")
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
        # Verify user is allowed to create/modify paths
        if self.instance is not None:
            harvester = self.instance.harvester
        else:
            try:
                pk = resolve(urlparse(self.initial_data['harvester']).path).kwargs['pk']
                harvester = Harvester.objects.get(id=pk)
            except BaseException:
                raise ValidationError("Harvester not found")
        if not self.context['request'].user.groups.filter(id=harvester.admin_group_id).exists():
            if self.instance is None or \
                    not self.context['request'].user.groups.filter(id=self.instance.admin_group_id).exists():
                raise ValidationError("Access denied")
        return attrs

    class Meta:
        model = MonitoredPath
        fields = ['url', 'id', 'path', 'regex', 'stable_time', 'active', 'harvester', 'user_sets']
        read_only_fields = ['url', 'id', 'harvester', 'user_sets']
        extra_kwargs = augment_extra_kwargs()


class MonitoredPathCreateSerializer(MonitoredPathSerializer):

    def create(self, validated_data):
        stable_time = validated_data.get('stable_time', 60)
        regex = validated_data.get('regex', '.*')
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
        monitored_path.admin_group = Group.objects.create(
            name=f"path_{validated_data['harvester'].id}_{monitored_path.id}_admins"
        )
        monitored_path.user_group = Group.objects.create(
            name=f"path_{validated_data['harvester'].id}_{monitored_path.id}_users"
        )
        monitored_path.save()
        # Add user as admin
        self.context['request'].user.groups.add(monitored_path.admin_group)
        return monitored_path

    def to_representation(self, instance):
        return MonitoredPathSerializer(context=self.context).to_representation(instance)

    class Meta:
        model = MonitoredPath
        fields = ['path', 'regex', 'stable_time', 'harvester']
        extra_metadata = {
            'regex': {'required': False},
            'stable_time': {'required': False},
        }


class ObservedFileSerializer(serializers.HyperlinkedModelSerializer):
    upload_info = serializers.SerializerMethodField(
        help_text="Metadata required for harvester program to resume file parsing"
    )

    def get_upload_info(self, instance) -> dict | None:
        if not self.context.get('with_upload_info'):
            return None
        try:
            last_record = 0
            columns = DataColumn.objects.filter(dataset__file=instance)
            column_data = []
            for c in columns:
                column_data.append({'name': c.name, 'id': c.id})
                if c.official_sample_counter:
                    last_record = c.values[:-1] if len(c.values) > 0 else 0
            return {
                'columns': column_data,
                'last_record_number': last_record
            }
        except BaseException as e:
            return {'columns': [], 'last_record_number': None, 'error': str(e)}

    class Meta:
        model = ObservedFile
        fields = [
            'url', 'id', 'harvester', 'path',
            'state', 'last_observed_time', 'last_observed_size', 'errors',
            'datasets', 'upload_info'
        ]
        read_only_fields = [
            'url', 'id', 'harvester', 'path',
            'last_observed_time', 'last_observed_size', 'datasets',
            'errors'
        ]
        extra_kwargs = augment_extra_kwargs({
            'errors': {'help_text': "Errors associated with this File"},
            'datasets': {'help_text': "Datasets extracted from this File"}
        })


class HarvestErrorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HarvestError
        fields = ['url', 'id', 'harvester', 'file', 'error', 'timestamp']
        extra_kwargs = augment_extra_kwargs()


# class CellFamilySerializer(serializers.HyperlinkedModelSerializer):
#
#     class Meta:
#         model = CellFamily
#         fields = [
#             'url', 'id', 'name',
#             'form_factor', 'link_to_datasheet',
#             'anode_chemistry', 'cathode_chemistry',
#             'nominal_capacity', 'nominal_cell_weight', 'manufacturer',
#             'cells', 'in_use'
#         ]
#         read_only_fields = ['id', 'url', 'cells', 'in_use']
#         extra_kwargs = augment_extra_kwargs({'cells': {'help_text': "Cells in this Family"}})


# class CellSerializer(serializers.HyperlinkedModelSerializer):
#
#     def validate_display_name(self, value):
#         if isinstance(value, str):
#             return value
#         return ""
#
#     def validate_family(self, value):
#         if not isinstance(value, CellFamily):
#             raise serializers.ValidationError("family property must be a CellFamily instance")
#         return value
#
#     def create(self, validated_data):
#         uid = validated_data.pop('uid')
#         display_name = validated_data.pop('display_name', "")
#         family = validated_data.pop('family')
#         if display_name == '':
#             display_name = f"{family.name}_{family.cells.count()}"
#         return Cell.objects.create(uid=uid, family=family, display_name=display_name)
#
#     class Meta:
#         model = Cell
#         fields = ['url', 'id', 'uid', 'display_name', 'family', 'datasets', 'in_use']
#         read_only_fields = ['id', 'url', 'datasets', 'in_use']
#         extra_kwargs = augment_extra_kwargs({
#             'family': {'help_text': "Cell Family to which this Cell belongs"},
#             'datasets': {'help_text': "Datasets generated in experiments using this Cell"}
#         })


class EquipmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Equipment
        fields = ['url', 'id', 'name', 'type', 'datasets', 'in_use']
        read_only_fields = ['url', 'id', 'datasets', 'in_use']
        extra_kwargs = augment_extra_kwargs({
            'datasets': {'help_text': "Datasets generated in experiments using this Equipment"}
        })


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    user_sets = serializers.SerializerMethodField(help_text="Roles and the Users assigned to them")

    @extend_schema_field(UserSetSerializer(many=True))
    def get_user_sets(self, instance):
        monitored_paths = get_monitored_paths(instance.file.path, instance.file.harvester)
        user_sets = []
        ids = []
        for mp in monitored_paths:
            sets = MonitoredPathSerializer(mp, context=self.context).data.get('user_sets')
            sets = [{**s, 'name': f"MonitoredPath_{mp.id}-{s['name']}"} for s in sets]
            sets = [s for s in sets if s['id'] not in ids]
            ids += [s['id'] for s in sets]
            user_sets = [user_sets, *sets]
        return user_sets

    class Meta:
        model = Dataset
        fields = ['url', 'id', 'name', 'date', 'type', 'purpose', 'cell', 'equipment', 'file', 'user_sets', 'columns']
        read_only_fields = ['date', 'file', 'id', 'url', 'user_sets', 'columns']
        extra_kwargs = augment_extra_kwargs({
            'equipment': {'help_text': "Equipment used in this Dataset's experiment"},
            'columns': {'help_text': "Columns in this Dataset"}
        })


class DataUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataUnit
        fields = ['url', 'id', 'name', 'symbol', 'description']
        extra_kwargs = augment_extra_kwargs()


class TimeseriesRangeLabelSerializer(serializers.HyperlinkedModelSerializer):
    data = serializers.SerializerMethodField()

    class Meta:
        model = TimeseriesRangeLabel
        fields = '__all__'
        extra_kwargs = augment_extra_kwargs()


class DataColumnTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataColumnType
        fields = ['url', 'id', 'name', 'description', 'is_default', 'unit']
        extra_kwargs = augment_extra_kwargs()


class DataColumnSerializer(serializers.HyperlinkedModelSerializer):
    """
    A column contains metadata and data. Data are an ordered list of values.
    """
    # name = serializers.SerializerMethodField(help_text=get_model_field(DataColumn, 'name').help_text)
    # dataset = serializers.SerializerMethodField(help_text=get_model_field(DataColumn, 'dataset').help_text)
    # type_name = serializers.SerializerMethodField(help_text=get_model_field(DataColumnType, 'name').help_text)
    # description = serializers.SerializerMethodField(help_text=get_model_field(DataColumnType, 'description').help_text)
    # unit = serializers.SerializerMethodField(help_text=get_model_field(DataColumnType, 'unit').help_text)
    # values = serializers.SerializerMethodField(help_text="Column values")

    def uri(self, rel_url: str) -> str:
        return self.context['request'].build_absolute_uri(rel_url)

    def get_name(self, instance) -> str:
        return instance.name

    def get_dataset(self, instance) -> str:
        return self.uri(reverse('dataset-detail', args=(instance.dataset.id,)))

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
            'dataset',
            'data_type',
            'type_name',
            'description',
            'official_sample_counter',
            'unit',
            'values',
        ]
        read_only_fields = fields
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


class HarvesterConfigSerializer(HarvesterSerializer):
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
        return []
        # return DataColumnTypeSerializer(
        #     DataColumnType.objects.filter(is_default=True),
        #     many=True,
        #     context={'request': self.context['request']}
        # ).data

    def get_max_upload_bytes(self, instance):
        return DATA_UPLOAD_MAX_MEMORY_SIZE

    def get_deleted_environment_variables(self, instance):
        return [v.key for v in instance.environment_variables.all() if v.deleted]

    class Meta:
        model = Harvester
        fields = [
            'url', 'id', 'api_key', 'name', 'sleep_time', 'monitored_paths',
            'standard_units', 'standard_columns', 'max_upload_bytes',
            'environment_variables', 'deleted_environment_variables'
        ]
        read_only_fields = fields
        extra_kwargs = augment_extra_kwargs({
            'environment_variables': {'help_text': "Envvars set on this Harvester"}
        })
        depth = 1


class HarvesterCreateSerializer(HarvesterSerializer):
    user = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        required=True,
        queryset=User.objects.filter(is_active=True)
    )

    def create(self, validated_data):
        """
        Create a Harvester and the user Groups required to control it.
        """
        # Create Harvester
        harvester = Harvester.objects.create(name=validated_data['name'])
        # Create user/admin groups
        harvester.admin_group = Group.objects.create(name=f"harvester_{harvester.id}_admins")
        harvester.user_group = Group.objects.create(name=f"harvester_{harvester.id}_users")
        harvester.save()
        # Add user as admin
        user = validated_data['user']
        user.groups.add(harvester.admin_group)
        user.save()

        return harvester

    def to_representation(self, instance):
        return HarvesterConfigSerializer(context=self.context).to_representation(instance)

    class Meta:
        model = Harvester
        fields = ['name', 'user']
        extra_kwargs = {'name': {'required': True}}
