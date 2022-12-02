from .serializers import HarvesterSerializer, \
    MonitoredPathSerializer, \
    MonitoredForSerializer, \
    ObservedFileSerializer, \
    CellDataSerializer, \
    DatasetSerializer, \
    EquipmentSerializer, \
    DatasetEquipmentSerializer, \
    DataUnitSerializer, \
    DataColumnTypeSerializer, \
    DataColumnSerializer, \
    TimeseriesDataSerializer, \
    TimeseriesRangeLabelSerializer, \
    UserSerializer, \
    GroupSerializer
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
from rest_framework import viewsets
from rest_framework import permissions

class HarvesterViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = HarvesterSerializer
    queryset = Harvester.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class MonitoredPathViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = MonitoredPathSerializer
    queryset = MonitoredPath.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class MonitoredForViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = MonitoredForSerializer
    queryset = MonitoredFor.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class ObservedFileViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = ObservedFileSerializer
    queryset = ObservedFile.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class CellDataViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = CellDataSerializer
    queryset = CellData.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class DatasetViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = DatasetSerializer
    queryset = Dataset.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class DatasetEquipmentViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = DatasetEquipmentSerializer
    queryset = DatasetEquipment.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class DataUnitViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = DataUnitSerializer
    queryset = DataUnit.objects.all()


class DataColumnTypeViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = DataColumnTypeSerializer
    queryset = DataColumnType.objects.all()


class DataColumnViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = DataColumnSerializer
    queryset = DataColumn.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class TimeseriesDataViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = TimeseriesDataSerializer
    queryset = TimeseriesData.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class TimeseriesRangeLabelViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = TimeseriesRangeLabelSerializer
    queryset = TimeseriesRangeLabel.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    permission_classes = [permissions.IsAuthenticated]

