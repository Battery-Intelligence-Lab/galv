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
    TimeseriesData, \
    TimeseriesRangeLabel, \
    DataColumnStringKeys
from django.db import connection
from django.contrib.auth.models import User, Group
from django.conf.global_settings import DATA_UPLOAD_MAX_MEMORY_SIZE
from rest_framework import serializers


class HarvesterSerializer(serializers.HyperlinkedModelSerializer):
    user_sets = serializers.SerializerMethodField()

    def get_user_sets(self, instance):
        return [
            UserSetSerializer(
                instance.admin_group,
                context={
                    'request': self.context.get('request'),
                    'name': 'Admins',
                    'description': (
                        'Administrators can change harvester properties, '
                        'as well as any of the harvester\'s paths or datasets.'
                    ),
                    'is_admin': True
                }
            ).data,
            UserSetSerializer(
                instance.user_group,
                context={
                    'request': self.context.get('request'),
                    'name': 'Users',
                    'description': (
                        'Users can view harvester properties. '
                        'They can also add monitored paths.'
                    )
                }
            ).data,
        ]

    class Meta:
        model = Harvester
        fields = ['url', 'id', 'name', 'sleep_time', 'last_check_in', 'user_sets']
        read_only_fields = ['url', 'id', 'last_check_in', 'user_sets']


class HarvesterConfigSerializer(serializers.HyperlinkedModelSerializer):
    standard_units = serializers.SerializerMethodField()
    standard_columns = serializers.SerializerMethodField()
    max_upload_bytes = serializers.SerializerMethodField()

    def get_standard_units(self, instance):
        return DataUnitSerializer(
            DataUnit.objects.filter(is_default=True),
            many=True,
            context={'request': self.context['request']}
        ).data

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


class MonitoredPathSerializer(serializers.HyperlinkedModelSerializer):
    user_sets = serializers.SerializerMethodField()

    def get_user_sets(self, instance):
        return [
            UserSetSerializer(
                instance.harvester.admin_group,
                context={
                    'request': self.context.get('request'),
                    'name': 'Harvester admins',
                    'description': (
                        'Harvester administrators can alter any of the harvester\'s paths or datasets.'
                    ),
                    'is_admin': True
                }
            ).data,
            UserSetSerializer(
                instance.admin_group,
                context={
                    'request': self.context.get('request'),
                    'name': 'Admins',
                    'description': (
                        'Administrators can change paths and their datasets.'
                    ),
                    'is_admin': True
                }
            ).data,
            UserSetSerializer(
                instance.user_group,
                context={
                    'request': self.context.get('request'),
                    'name': 'Users',
                    'description': (
                        'Users can monitored paths and their datasets.'
                    )
                }
            ).data,
        ]

    class Meta:
        model = MonitoredPath
        fields = ['url', 'id', 'path', 'stable_time', 'harvester', 'user_sets']
        read_only_fields = ['url', 'id', 'harvester', 'user_sets']


class ObservedFileSerializer(serializers.HyperlinkedModelSerializer):
    upload_info = serializers.SerializerMethodField()

    def get_upload_info(self, instance):
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


class HarvestErrorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HarvestError
        fields = ['url', 'id', 'harvester', 'path', 'file', 'error', 'timestamp']


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


class CellSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Cell
        fields = ['url', 'id', 'display_name', 'family', 'datasets']
        read_only_fields = ['id', 'url', 'datasets']
        extra_kwargs = {'display_name': {'allow_blank': True, 'allow_null': True}}

    def validate_display_name(self, value):
        if isinstance(value, str):
            return value
        return ""

    def validate_family(self, value):
        if not isinstance(value, CellFamily):
            raise serializers.ValidationError("family property must be a CellFamily instance")
        return value

    def create(self, validated_data):
        display_name = validated_data.pop('display_name')
        family = validated_data.pop('family')
        if display_name == '':
            display_name = f"{family.name}_{family.cells.count()}"
        return Cell.objects.create(family=family, display_name=display_name)


class EquipmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Equipment
        fields = ['url', 'id', 'name', 'type', 'datasets']
        read_only_fields = ['url', 'id', 'datasets']


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    user_sets = serializers.SerializerMethodField()

    def get_user_sets(self, instance):
        return MonitoredPathSerializer(
            instance.file.monitored_path, context={'request': self.context.get('request')}
        ).data.get('user_sets')

    class Meta:
        model = Dataset
        fields = ['url', 'id', 'name', 'date', 'type', 'purpose', 'cell', 'equipment', 'file', 'user_sets']
        read_only_fields = ['date', 'file', 'id', 'url', 'user_sets']


class DataUnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataUnit
        fields = ['url', 'id', 'name', 'symbol', 'description', 'is_default']


class DataColumnTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataColumnType
        fields = ['url', 'id', 'name', 'description', 'is_default', 'unit']


class DataColumnSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataColumn
        fields = '__all__'


class TimeseriesDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TimeseriesData
        fields = '__all__'


class TimeseriesRangeLabelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TimeseriesRangeLabel
        fields = '__all__'


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    users = serializers.SerializerMethodField()

    def get_users(self, instance):
        return UserSerializer(instance.user_set.all(), many=True, context={'request': self.context['request']}).data

    class Meta:
        model = Group
        fields = [
            'url', 'name', 'users',
            'readable_paths', 'editable_paths', 'readable_harvesters', 'editable_harvesters'
        ]


class UserSetSerializer(serializers.HyperlinkedModelSerializer):
    description = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    def get_description(self, instance):
        return self.context.get('description')

    def get_users(self, instance):
        return UserSerializer(instance.user_set.all(), many=True, context={'request': self.context['request']}).data

    def get_name(self, instance):
        return self.context.get('name', instance.name)

    def get_is_admin(self, instance):
        """
        Admin groups can control their own members, as well as members in groups
        lower down the list of UserSets[]
        """
        return self.context.get('is_admin', False)

    class Meta:
        model = Group
        fields = ['url', 'id', 'name', 'description', 'is_admin', 'users']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            'url',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser',
        ]
