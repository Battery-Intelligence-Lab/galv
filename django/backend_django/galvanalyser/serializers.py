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
from rest_framework.reverse import reverse_lazy


class HarvesterSerializer(serializers.HyperlinkedModelSerializer):
    links = serializers.SerializerMethodField()

    def get_links(self, harvester):
        return {}
        #     'monitored_paths': reverse_lazy(
        #         'harvester-paths',
        #         request=self.context.get('request'),
        #         kwargs={'pk': harvester.id}
        #     ),
        #     'users': reverse_lazy(
        #         'harvester-users',
        #         request=self.context.get('request'),
        #         kwargs={'pk': harvester.id}
        #     ),
        #     'admins': reverse_lazy(
        #         'harvester-admins',
        #         request=self.context.get('request'),
        #         kwargs={'pk': harvester.id}
        #     ),
        # }

    class Meta:
        model = Harvester
        fields = ['url', 'id', 'name', 'sleep_time', 'last_check_in', 'links']
        read_only_fields = ['url', 'id', 'last_check_in']


class HarvesterConfigSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Harvester
        fields = ['url', 'id', 'api_key', 'name', 'last_check_in', 'sleep_time', 'paths']
        depth = 10  # max depth


class MonitoredPathSerializer(serializers.HyperlinkedModelSerializer):
    links = serializers.SerializerMethodField()

    def get_links(self, monitored_path):
        return {
            'files': reverse_lazy(
                'monitored_path-files',
                request=self.context.get('request'),
                kwargs={'pk': monitored_path.id}
            ),
            'users': reverse_lazy(
                'monitored_path-users',
                request=self.context.get('request'),
                kwargs={'pk': monitored_path.id}
            ),
            'admins': reverse_lazy(
                'monitored_path-admins',
                request=self.context.get('request'),
                kwargs={'pk': monitored_path.id}
            ),
        }

    class Meta:
        model = MonitoredPath
        fields = '__all__'
        read_only_fields = ['admin_group', 'user_group']


class ObservedFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ObservedFile
        fields = '__all__'


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
        fields = '__all__'


class DataColumnTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataColumnType
        fields = '__all__'


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
    class Meta:
        model = Group
        fields = '__all__'


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
            'groups',
        ]
        depth = 1
