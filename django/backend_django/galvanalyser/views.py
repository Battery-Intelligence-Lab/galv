from django.db.models import Q

from .serializers import HarvesterSerializer, \
    HarvesterConfigSerializer, \
    MonitoredPathSerializer, \
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
    HarvestError, \
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
    TimeseriesRangeLabel, \
    FileState
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from knox.views import LoginView as KnoxLoginView
from rest_framework.authentication import BasicAuthentication
import json


def error_response(error: str, status: int = 400) -> Response:
    return Response({'error': error}, status=status)


class LoginView(KnoxLoginView):
    permission_classes = [AllowAny]
    authentication_classes = [BasicAuthentication]


class HarvesterViewSet(viewsets.ModelViewSet):
    """
    Harvesters monitor a set of MonitoredPaths and send reports about ObservedFiles
    within those paths.
    A Harvester has Users and Admins, managed by Django's inbuilt User and Group models.

    When Harvesters communicate with the API they do so using special Harvester API Keys.
    These provide access to the report and configuration endpoints.
    """
    serializer_class = HarvesterSerializer
    filterset_fields = ['name']
    search_fields = ['@name']
    queryset = Harvester.objects.none().order_by('last_check_in', 'id')

    def get_queryset(self):
        return Harvester.objects.filter(
            Q(user_group__in=self.request.user.groups.all()) |
            Q(admin_group__in=self.request.user.groups.all())
        ).order_by('last_check_in', 'id')

    def create(self, request, *args, **kwargs):
        """
        Create a Harvester and the user Groups required to control it.
        """

        # Validate input
        if not request.data['name']:
            return error_response('No name specified for Harvester.')
        if not request.data['user']:
            return error_response('No administrator id specified for Harvester.')
        if len(Harvester.objects.filter(name=request.data['name'])):
            return error_response('Harvester with that name already exists')
        if len(User.objects.filter(id=int(request.data['user']))) != 1:
            return error_response('No user exists with id {request.data["user"]}')

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

    def update(self, request, *args, **kwargs):
        try:
            harvester = Harvester.objects.get(id=kwargs.get('pk'))
        except Harvester.DoesNotExist:
            return error_response(f'Harvester with id {request.data["id"]} not found.')
        if not request.user.groups.filter(id=harvester.admin_group_id).exists():
            return error_response(f'Access denied.')

        name = request.data.get('name')
        if name != harvester.name:
            if Harvester.objects.filter(name=name).exists():
                return error_response(f'Another Harvester already has the name {name}')
            harvester.name = name
        sleep_time = request.data.get('sleep_time', None)
        if sleep_time is not None:
            try:
                sleep_time = int(sleep_time)
                assert sleep_time > 0
            except (TypeError, ValueError, AssertionError):
                return error_response('sleep_time must be an integer greater than 0')
            if sleep_time != harvester.sleep_time:
                harvester.sleep_time = sleep_time

        harvester.save()
        return Response(self.get_serializer(harvester).data)

    # @action(detail=True, methods=['GET'])
    # def env(self, request, pk: int = None):
    #     harvester = Harvester.objects.get(id=pk)
    #     result = get_env.apply_async(queue=harvester.name)
    #     return Response(result.get())

    @action(detail=True, methods=['GET'])
    def config(self, request, pk: int = None):
        """
        Return a full configuration file including MonitoredPaths under paths.
        Used by the API for updating the Harvester.
        """
        # TODO: Restrict access to Harvester or harvester user
        harvester = get_object_or_404(Harvester, id=pk)
        return Response(HarvesterConfigSerializer(harvester, context={'request': request}).data)

    @action(detail=True, methods=['POST'])
    def report(self, request, pk: int = None):
        """
        Process a harvester's report on its activity.
        This will spawn various other database updates depending on payload content.

        Only harvesters are authorised to issue reports.
        """
        # TODO access class Harvester
        harvester = Harvester.objects.get(id=pk)
        if request.data.get('status') is None:
            return Response({'error': 'Badly formatted request'}, status=400)
        try:
            path = MonitoredPath.objects.get(path=request.data['path'], harvester=harvester)
        except MonitoredPath.DoesNotExist:
            return Response({'error': 'Unrecognized path'}, status=400)
        if request.data['status'] == 'error':
            error = request.data['error']
            if not isinstance(error, str):
                try:
                    error = json.dumps(error)
                except json.JSONDecodeError:
                    error = str(error)
            HarvestError.objects.create(
                harvester=harvester,
                path=path,
                error=str(error)
            )
            return Response({})
        elif request.data['status'] == 'success':
            # Figure out what we succeeded in doing!
            content = request.data['content']
            if content['task'] == 'file_size':
                # Harvester is reporting the size of a file
                # Update our database record and return a file status
                file, _ = ObservedFile.objects.get_or_create(monitored_path=path, relative_path=request.data['file'])

                size = content['size']
                if size < file.last_observed_size:
                    file.state = FileState.UNSTABLE
                elif size > file.last_observed_size:
                    file.state = FileState.GROWING

                if size != file.last_observed_size:
                    file.last_observed_size = size
                    file.last_observed_time = timezone.now()
                else:
                    # Recent changes
                    if file.last_observed_time + timezone.timedelta(seconds=path.stable_time) > timezone.now():
                        file.state = FileState.UNSTABLE
                    # Stable file -- already imported?
                    elif file.state not in [FileState.IMPORTED.value, FileState.IMPORT_FAILED.value]:
                        file.state = FileState.STABLE

                file.save()
                return Response(ObservedFileSerializer(file, context={'request': self.request}).data)
            elif content['task'] == 'import':
                try:
                    file = ObservedFile.objects.get(monitored_path=path, relative_path=request.data['file'])
                except ObservedFile.DoesNotExist:
                    return error_response("ObservedFile does not exist")
                if content['status'] in ['begin', 'in_progress', 'complete']:
                    try:
                        if content['status'] == 'begin':
                            file.state = FileState.IMPORTING
                            # TODO: process metadata under 'begin'?
                            dataset, _ = Dataset.objects.get_or_create(
                                defaults={'date': timezone.now()},
                                file=file
                            )
                        elif content['status'] == 'complete':
                            file.state = FileState.IMPORTED
                        else:
                            dataset = Dataset.objects.get(file=file)
                            for column_data in content['data']:
                                try:
                                    column_type = DataColumnType.objects.get(id=column_data['column_id'])
                                    column, _ = DataColumn.objects.get_or_create(
                                        name=column_type.name,
                                        type=column_type,
                                        dataset=dataset
                                    )
                                except KeyError:
                                    if 'unit_id' in column_data:
                                        unit = DataUnit.objects.get(id=column_data['unit_id'])
                                    else:
                                        unit, _ = DataUnit.objects.get_or_create(symbol=column_data['unit_symbol'])
                                    try:
                                        column_type = DataColumnType.objects.get(unit=unit)
                                    except DataColumnType.DoesNotExist:
                                        column_type = DataColumnType.objects.create(
                                            name=column_data['column_name'],
                                            unit=unit
                                        )
                                    column, _ = DataColumn.objects.get_or_create(
                                        name=column_data['column_name'],
                                        type=column_type,
                                        dataset=dataset
                                    )
                                TimeseriesData.objects.bulk_create([
                                    TimeseriesData(sample=k, value=v, column_id=column.id)
                                    for k, v in column_data['values'].items()
                                ])

                    except BaseException as e:
                        file.state = FileState.IMPORT_FAILED
                        HarvestError.objects.create(harvester=harvester, path=path, error=str(e))
                        file.save()
                        return error_response(f"Error importing data: {e.args}")
                if content['status'] == 'failed':
                    file.state = FileState.IMPORT_FAILED

                file.save()

                return Response(ObservedFileSerializer(file, context={'request': self.request}).data)
            else:
                return error_response('Unrecognised task')
        else:
            return error_response('Unrecognised status')


class MonitoredPathViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = MonitoredPathSerializer
    filterset_fields = ['path', 'harvester__id', 'harvester__name']
    search_fields = ['@path']
    queryset = MonitoredPath.objects.all().order_by('id')

    # Access restrictions
    def get_queryset(self):
        return MonitoredPath.objects.filter(
            Q(user_group__in=self.request.user.groups.all()) |
            Q(admin_group__in=self.request.user.groups.all()) |
            Q(harvester__admin_group__in=self.request.user.groups.all())
        ).order_by('id')

    def create(self, request, *args, **kwargs):
        """
        Create a MonitoredPath for a Harvester and the user Groups required to control it.
        """

        # Validate input
        path = str(request.data['path']).lower().lstrip().rstrip()
        if not path:
            return Response({'error': 'No path specified.'}, status=400)
        try:
            harvester = Harvester.objects.get(id=request.data['harvester'])
        except (Harvester.DoesNotExist, AttributeError):
            return Response({'error': 'Harvester not found.'})
        if len(MonitoredPath.objects.filter(path=path, harvester=harvester)):
            return Response({'error': 'Path already exists on Harvester.'}, status=400)
        # Check user is authorised to create paths on Harvester
        if not request.user.groups.filter(id=harvester.user_group_id).exists() and \
                not request.user.groups.filter(id=harvester.admin_group_id).exists():
            return Response({'error': f'Permission denied to {request.user.username} for {harvester.name}'})

        # Create Path
        try:
            stable_time = int(request.data['stable_time'])
            monitored_path = MonitoredPath.objects.create(path=path, harvester=harvester, stable_time=stable_time)
        except (TypeError, ValueError):
            monitored_path = MonitoredPath.objects.create(path=path, harvester=harvester)
        # Create user/admin groups
        monitored_path.user_group = Group.objects.create(name=f"path_{harvester.id}_{monitored_path.id}_users")
        monitored_path.admin_group = Group.objects.create(name=f"path_{harvester.id}_{monitored_path.id}_admins")
        monitored_path.save()
        # Add user as admin
        request.user.groups.add(monitored_path.admin_group)
        request.user.save()

        return Response(self.get_serializer(monitored_path).data)

    def update(self, request, *args, **kwargs):
        try:
            path = MonitoredPath.objects.get(id=kwargs.get('pk'))
        except MonitoredPath.DoesNotExist:
            return error_response(f'Path with id {request.data["id"]} not found.')
        if not request.user.groups.filter(id=path.admin_group_id).exists():
            if not request.user.groups.filter(id=path.harvester.admin_group_id).exists():
                return error_response(f'Access denied.')

        path_str = request.data.get('path')
        if path_str != path.path:
            if MonitoredPath.objects.filter(path=path_str, harvester=path.harvester).exists():
                return error_response(f'Path {path_str} already exists on {path.harvester.name}')
            path.path = path_str
        stable_time = request.data.get('stable_time', None)
        if stable_time is not None:
            try:
                stable_time = int(stable_time)
                assert stable_time > 0
            except (TypeError, ValueError, AssertionError):
                return error_response('stable_time must be an integer greater than 0')
            if stable_time != path.stable_time:
                path.stable_time = stable_time

        path.save()
        return Response(self.get_serializer(path).data)

    @action(detail=True, methods=['GET'])
    def files(self, request, pk: int = None):
        """
        ObservedFiles for the MonitoredPath.
        """
        # TODO: Restrict access to Harvester or harvester user
        monitored_path = get_object_or_404(MonitoredPath, id=pk)
        paths = ObservedFile.objects.filter(monitored_path=monitored_path).order_by('id')
        paths = self.paginate_queryset(paths)
        return self.get_paginated_response(ObservedFileSerializer(paths, many=True).data)

    @action(detail=True, methods=['GET'])
    def users(self, request, pk: int = None):
        """
        Users able to access the Harvester. Users can create MonitoredPaths.
        """
        # TODO: Restrict access to Harvester or harvester user
        monitored_path = get_object_or_404(Harvester, id=pk)
        users = User.objects.filter(groups__in=[monitored_path.admin_group, monitored_path.user_group])
        users = self.paginate_queryset(users)
        return self.get_paginated_response(UserSerializer(users, context={'request': request}, many=True).data)

    @action(detail=True, methods=['GET'])
    def admins(self, request, pk: int = None):
        """
        Users able to edit the Harvester.
        """
        # TODO: Restrict access to Harvester or harvester user
        monitored_path = get_object_or_404(Harvester, id=pk)
        admins = User.objects.filter(groups__in=[monitored_path.admin_group])
        admins = self.paginate_queryset(admins)
        return self.get_paginated_response(UserSerializer(admins, context={'request': request}, many=True).data)


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

