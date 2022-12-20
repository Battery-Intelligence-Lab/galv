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
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from knox.views import LoginView as KnoxLoginView
from rest_framework.authentication import BasicAuthentication
from .tasks import get_env


class LoginView(KnoxLoginView):
    permission_classes = [AllowAny]
    authentication_classes = [BasicAuthentication]


class HarvesterViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = HarvesterSerializer
    queryset = Harvester.objects.all().order_by('last_check_in', 'id')

    def create(self, request, *args, **kwargs):
        # Validate input
        if not request.data['name']:
            return Response({'error': 'No name specified for Harvester.'}, status=400)
        if not request.data['user']:
            return Response({'error': 'No administrator id specified for Harvester.'}, status=400)
        if len(Harvester.objects.filter(name=request.data['name'])):
            return Response({'error': 'Harvester with that name already exists'}, status=400)
        if len(User.objects.filter(id=int(request.data['user']))) != 1:
            return Response({'error': f'No user exists with id {request.data["user"]}'}, status=400)

        # Create Harvester
        harvester = Harvester.objects.create(name=request.data['name'])
        # Create user/admin groups
        harvester.user_group = Group.objects.create(name=f"harvester_{harvester.id}_users")
        harvester.admin_group = Group.objects.create(name=f"harvester_{harvester.id}_admins")
        harvester.save()
        # Add user as admin
        user = User.objects.get(id=int(request.data['user']))
        user.groups.add(harvester.admin_group)
        user.save()

        return Response(self.get_serializer(harvester).data)

    @action(detail=True, methods=['GET'])
    def env(self, request, pk: int = None):
        harvester = Harvester.objects.get(id=pk)
        result = get_env.apply_async(queue=harvester.name)
        return Response(result.get())

    @action(detail=False, methods=['GET'])
    def by_name(self, request):
        """
        Used by the harvesters' init.py call to check their prospective name is free.
        Returns a list of Harvesters with the specified name (should be length 1 or 0).
        """
        name = request.query_params.get('name', '')
        harvester = self.paginate_queryset(Harvester.objects.filter(name=name))
        return self.get_paginated_response(self.get_serializer(harvester, many=True).data)


class MonitoredPathViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = MonitoredPathSerializer
    queryset = MonitoredPath.objects.all().order_by('id')


class MonitoredForViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = MonitoredForSerializer
    queryset = MonitoredFor.objects.all()


class ObservedFileViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = ObservedFileSerializer
    queryset = ObservedFile.objects.all()


class CellDataViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = CellDataSerializer
    queryset = CellData.objects.all()


class DatasetViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = DatasetSerializer
    queryset = Dataset.objects.all()


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()


class DatasetEquipmentViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = DatasetEquipmentSerializer
    queryset = DatasetEquipment.objects.all()


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


class TimeseriesDataViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = TimeseriesDataSerializer
    queryset = TimeseriesData.objects.all()


class TimeseriesRangeLabelViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = TimeseriesRangeLabelSerializer
    queryset = TimeseriesRangeLabel.objects.all()


class UserViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()


class GroupViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

