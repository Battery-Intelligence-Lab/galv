from .models import Harvester, \
    MonitoredPath, \
    MonitoredFor, \
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
        fields = '__all__'


class MonitoredPathSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonitoredPath
        fields = '__all__'


class MonitoredForSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonitoredFor
        fields = '__all__'


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


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
