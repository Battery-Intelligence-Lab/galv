from .models import Harvester, \
    MonitoredPath, \
    ObservedFile, \
    CellData, \
    Dataset, \
    Equipment, \
    DatasetEquipment, \
    DataUnit, \
    DataColumnType, \
    DataColumn, \
    TimeseriesData, \
    TimeseriesRangeLabel
from django.contrib.auth.models import User, Group
from rest_framework import serializers


class HarvesterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Harvester
        fields = ['url', 'id', 'name', 'sleep_time', 'last_check_in']
        read_only_fields = ['url', 'id', 'last_check_in']


class HarvesterConfigSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Harvester
        fields = ['url', 'id', 'api_key', 'name', 'last_check_in', 'sleep_time', 'monitored_paths']
        depth = 1  # max depth


class MonitoredPathSerializer(serializers.HyperlinkedModelSerializer):
    users = serializers.SerializerMethodField()

    def get_users(self, instance):
        harvester_admins = instance.harvester.admin_group.user_set.all()
        admins = instance.admin_group.user_set.all()
        users = instance.user_group.user_set.all()
        return {
            'harvester_admins': UserSerializer(
                harvester_admins,
                many=True,
                context={'request': self.context['request']}
            ).data,
            'admins': UserSerializer(
                admins,
                many=True,
                context={'request': self.context['request']}
            ).data,
            'users': UserSerializer(
                users,
                many=True,
                context={'request': self.context['request']}
            ).data,
        }

    class Meta:
        model = MonitoredPath
        fields = ['url', 'id', 'path', 'stable_time', 'harvester', 'users']
        read_only_fields = ['users']
        depth = 1


class ObservedFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ObservedFile
        fields = [
            'url', 'id',
            'monitored_path', 'relative_path',
            'state', 'last_observed_time', 'last_observed_size',
            'datasets'
        ]


class CellDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CellData
        fields = '__all__'


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dataset
        fields = '__all__'


class EquipmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'


class DatasetEquipmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DatasetEquipment
        fields = '__all__'


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
        fields = ['url', 'name', 'users']
        depth = 1


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            'url',
            'username',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser',
        ]
