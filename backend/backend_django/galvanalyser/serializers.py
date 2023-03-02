import django.db.models
from django.urls import reverse
from drf_spectacular.utils import extend_schema_field

from .models import Harvester, \
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
    DataColumnStringKeys, \
    KnoxAuthToken
from django.db import connection
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
    user_sets = serializers.SerializerMethodField(help_text="Roles and the Users assigned to them")

    @extend_schema_field(UserSetSerializer(many=True))
    def get_user_sets(self, instance):
        group_ids = [instance.admin_group.id, instance.user_group.id]
        return UserSetSerializer(
            Group.objects.filter(id__in=group_ids),
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

    class Meta:
        model = Harvester
        fields = ['url', 'id', 'name', 'sleep_time', 'last_check_in', 'user_sets']
        read_only_fields = ['url', 'id', 'last_check_in', 'user_sets']
        extra_kwargs = augment_extra_kwargs()


class MonitoredPathSerializer(serializers.HyperlinkedModelSerializer):
    user_sets = serializers.SerializerMethodField(help_text="Roles and the Users assigned to them")

    @extend_schema_field(UserSetSerializer(many=True))
    def get_user_sets(self, instance):
        group_ids = [instance.harvester.admin_group.id, instance.admin_group.id, instance.user_group.id]
        return UserSetSerializer(
            Group.objects.filter(id__in=group_ids),
            context={
                'request': self.context.get('request'),
                instance.harvester.admin_group.id: {
                    'name': 'Harvester admins',
                    'description': (
                        'Harvester administrators can alter any of the harvester\'s paths or datasets.'
                    ),
                    'is_admin': True
                },
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
                        'Users can monitored paths and their datasets.'
                    )
                }
            },
            many=True
        ).data

    class Meta:
        model = MonitoredPath
        fields = ['url', 'id', 'path', 'stable_time', 'harvester', 'user_sets']
        read_only_fields = ['url', 'id', 'harvester', 'user_sets']
        extra_kwargs = augment_extra_kwargs()


class ObservedFileSerializer(serializers.HyperlinkedModelSerializer):
    upload_info = serializers.SerializerMethodField(
        help_text="Metadata required for harvester program to resume file parsing"
    )

    def get_upload_info(self, instance) -> dict | None:
        if not self.context.get('with_upload_info'):
            return None
        try:
            columns = DataColumn.objects.filter(dataset__file=instance)
            column_data = []
            for c in columns:
                keys = DataColumnStringKeys.objects.filter(column=c).order_by('key')
                column_data.append({
                    'name': c.name,
                    'id': c.id,
                    'keymap': [{'key': k.key, 'value': k.string} for k in keys]
                })
            with connection.cursor() as cur:
                cur.execute(f"SELECT sample FROM timeseries_data WHERE column_id={columns.first().id} ORDER BY sample DESC LIMIT 1")
                last_record = cur.fetchone()[0]
            return {
                'columns': column_data,
                'last_record_number': last_record
            }
        except BaseException as e:
            return {'columns': [], 'last_record_number': None, 'error': str(e)}

    class Meta:
        model = ObservedFile
        fields = [
            'url', 'id',
            'monitored_path', 'relative_path',
            'state', 'last_observed_time', 'last_observed_size', 'errors',
            'datasets', 'upload_info'
        ]
        read_only_fields = [
            'url', 'id', 'monitored_path', 'relative_path',
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
        fields = ['url', 'id', 'harvester', 'path', 'file', 'error', 'timestamp']
        extra_kwargs = augment_extra_kwargs()


class CellFamilySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CellFamily
        fields = [
            'url', 'id', 'name',
            'form_factor', 'link_to_datasheet',
            'anode_chemistry', 'cathode_chemistry',
            'nominal_capacity', 'nominal_cell_weight', 'manufacturer',
            'cells'
        ]
        read_only_fields = ['id', 'url', 'cells']
        extra_kwargs = augment_extra_kwargs({'cells': {'help_text': "Cells in this Family"}})


class CellSerializer(serializers.HyperlinkedModelSerializer):

    def validate_display_name(self, value):
        if isinstance(value, str):
            return value
        return ""

    def validate_family(self, value):
        if not isinstance(value, CellFamily):
            raise serializers.ValidationError("family property must be a CellFamily instance")
        return value

    def create(self, validated_data):
        uid = validated_data.pop('uid')
        display_name = validated_data.pop('display_name')
        family = validated_data.pop('family')
        if display_name == '':
            display_name = f"{family.name}_{family.cells.count()}"
        return Cell.objects.create(uid=uid, family=family, display_name=display_name)

    class Meta:
        model = Cell
        fields = ['url', 'id', 'uid', 'display_name', 'family', 'datasets']
        read_only_fields = ['id', 'url', 'datasets']
        extra_kwargs = augment_extra_kwargs({
            'family': {'help_text': "Cell Family to which this Cell belongs"},
            'datasets': {'help_text': "Datasets generated in experiments using this Cell"}
        })


class EquipmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Equipment
        fields = ['url', 'id', 'name', 'type', 'datasets']
        read_only_fields = ['url', 'id', 'datasets']
        extra_kwargs = augment_extra_kwargs({
            'datasets': {'help_text': "Datasets generated in experiments using this Equipment"}
        })


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    user_sets = serializers.SerializerMethodField(help_text="Roles and the Users assigned to them")

    @extend_schema_field(UserSetSerializer(many=True))
    def get_user_sets(self, instance):
        return MonitoredPathSerializer(
            instance.file.monitored_path, context={'request': self.context.get('request')}
        ).data.get('user_sets')

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


class TimeseriesDataSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="Auto-assigned object identifier")
    url = serializers.CharField(help_text=url_help_text)
    observations = serializers.DictField(help_text="row_number:value dictionary of observations")

    def to_representation(self, instance):
        with connection.cursor() as cur:
            cur.execute(f"SELECT sample, value FROM timeseries_data WHERE column_id={instance.id} ORDER BY sample")
            data = cur.fetchall()
        keys = DataColumnStringKeys.objects.filter(column_id=instance.id)
        if keys.exists():
            key_map = {k.key: k.string for k in keys}
            obs = {x[0]: key_map[x[1]] for x in data}
        else:
            obs = {x[0]: x[1] for x in data}
        return {
            'id': instance.id,
            'url': self.context['request'].build_absolute_uri(reverse('datacolumn-data', args=(instance.id,))),
            'observations': obs
        }


class TimeseriesDataListSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="Auto-assigned object identifier")
    url = serializers.CharField(help_text=url_help_text)
    observations = serializers.ListField(help_text="List of observation values ordered by row number")

    def to_representation(self, instance):
        with connection.cursor() as cur:
            cur.execute(f"SELECT value FROM timeseries_data WHERE column_id={instance.id} ORDER BY sample")
            data = cur.fetchall()
        keys = DataColumnStringKeys.objects.filter(column_id=instance.id)
        if keys.exists():
            key_map = {k.key: k.string for k in keys}
            obs = [key_map[x[0]] for x in data]
        else:
            obs = [x[0] for x in data]
        return {
            'id': instance.id,
            'url': self.context['request'].build_absolute_uri(
                reverse('datacolumn-data-listformat', args=(instance.id,))
            ),
            'observations': obs
        }


class DataColumnTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataColumnType
        fields = ['url', 'id', 'name', 'description', 'is_default', 'unit']
        extra_kwargs = augment_extra_kwargs()


class DataColumnSerializer(serializers.HyperlinkedModelSerializer):
    """
    A column contains metadata and data. Data are an ordered list of values.
    """
    name = serializers.SerializerMethodField(help_text=get_model_field(DataColumn, 'name').help_text)
    dataset = serializers.SerializerMethodField(help_text=get_model_field(DataColumn, 'dataset').help_text)
    is_numeric = serializers.SerializerMethodField(help_text="true for numeric columns, false for string columns")
    type_name = serializers.SerializerMethodField(help_text=get_model_field(DataColumnType, 'name').help_text)
    description = serializers.SerializerMethodField(help_text=get_model_field(DataColumnType, 'description').help_text)
    unit = serializers.SerializerMethodField(help_text=get_model_field(DataColumnType, 'unit').help_text)
    data = serializers.SerializerMethodField(help_text="Dictionary of row_number:value observations")
    data_list = serializers.SerializerMethodField(help_text="List of observation values ordered by row number")

    def uri(self, rel_url: str) -> str:
        return self.context['request'].build_absolute_uri(rel_url)

    def get_name(self, instance) -> str:
        return instance.name

    def get_dataset(self, instance) -> str:
        return self.uri(reverse('dataset-detail', args=(instance.dataset.id,)))

    def get_is_numeric(self, instance) -> bool:
        return not DataColumnStringKeys.objects.filter(column_id=instance.id).exists()

    def get_type_name(self, instance) -> str:
        return instance.type.name

    def get_description(self, instance) -> str:
        return instance.type.description

    @extend_schema_field(DataUnitSerializer())
    def get_unit(self, instance):
        return DataUnitSerializer(instance.type.unit, context=self.context).data

    def get_data(self, instance) -> str:
        return self.uri(reverse('datacolumn-data', args=(instance.id,)))

    def get_data_list(self, instance) -> str:
        return self.uri(reverse('datacolumn-data-listformat', args=(instance.id,)))

    class Meta:
        model = DataColumn
        fields = [
            'id',
            'url',
            'name',
            'dataset',
            'is_numeric',
            'type_name',
            'description',
            'unit',
            'data',
            'data_list'
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


class HarvesterConfigSerializer(serializers.HyperlinkedModelSerializer):
    standard_units = serializers.SerializerMethodField(help_text="Units recognised by the initial database")
    standard_columns = serializers.SerializerMethodField(help_text="Column Types recognised by the initial database")
    max_upload_bytes = serializers.SerializerMethodField(help_text="Maximum upload size (bytes)")

    @extend_schema_field(DataUnitSerializer(many=True))
    def get_standard_units(self, instance):
        return DataUnitSerializer(
            DataUnit.objects.filter(is_default=True),
            many=True,
            context={'request': self.context['request']}
        ).data

    @extend_schema_field(DataColumnTypeSerializer(many=True))
    def get_standard_columns(self, instance):
        return DataColumnTypeSerializer(
            DataColumnType.objects.filter(is_default=True),
            many=True,
            context={'request': self.context['request']}
        ).data

    def get_max_upload_bytes(self, instance):
        return DATA_UPLOAD_MAX_MEMORY_SIZE

    class Meta:
        model = Harvester
        fields = [
            'url', 'id', 'api_key', 'name', 'sleep_time', 'monitored_paths',
            'standard_units', 'standard_columns', 'max_upload_bytes'
        ]
        read_only_fields = fields
        depth = 1
