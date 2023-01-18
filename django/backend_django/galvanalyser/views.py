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
    DataColumnStringKeys, \
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


def deserialize_datetime(serialized_value: str | float) -> timezone.datetime:
    if isinstance(serialized_value, str):
        return timezone.make_aware(timezone.datetime.fromisoformat(serialized_value))
    if isinstance(serialized_value, float):
        return timezone.make_aware(timezone.datetime.fromtimestamp(serialized_value))
    raise TypeError


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
    queryset = Harvester.objects.none().order_by('-last_check_in', '-id')

    def get_queryset(self):
        return Harvester.objects.filter(
            Q(user_group__in=self.request.user.groups.all()) |
            Q(admin_group__in=self.request.user.groups.all())
        ).order_by('-last_check_in', '-id')

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
            err = HarvestError.objects.create(
                harvester=harvester,
                path=path,
                error=str(error)
            )
            if request.data.get('file'):
                try:
                    file = ObservedFile.objects.get(monitored_path=path, relative_path=request.data['file'])
                    err.file = file
                    err.save()
                except ObservedFile.DoesNotExist:
                    pass
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
                            date = deserialize_datetime(content['test_date'])
                            # process metadata under 'begin'
                            core_metadata = content['core_metadata']
                            extra_metadata = content['extra_metadata']
                            defaults = {}
                            if 'Machine Type' in core_metadata:
                                defaults['type'] = core_metadata['Machine Type']
                            if 'Dataset Name' in core_metadata:
                                defaults['name'] = core_metadata['Dataset Name']
                            defaults['json_data'] = {}
                            if 'num_rows' in core_metadata:
                                defaults['json_data']['num_rows'] = core_metadata['num_rows']
                            if 'first_sample_no' in core_metadata:
                                defaults['json_data']['first_sample_no'] = core_metadata['first_sample_no']
                            if 'last_sample_no' in core_metadata:
                                defaults['json_data']['last_sample_no'] = core_metadata['last_sample_no']
                            defaults['json_data'] = {**defaults['json_data'], **extra_metadata}

                            dataset, _ = Dataset.objects.get_or_create(
                                defaults=defaults,
                                file=file,
                                date=date
                            )
                        elif content['status'] == 'complete':
                            if file.state == FileState.IMPORTING.value:
                                file.state = FileState.IMPORTED
                        else:
                            date = deserialize_datetime(content['test_date'])
                            dataset = Dataset.objects.get(file=file, date=date)
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
                                # Create a value map for string data
                                if 'value_map' in column_data:
                                    DataColumnStringKeys.objects.filter(column=column).delete()
                                    DataColumnStringKeys.objects.bulk_create(
                                        [DataColumnStringKeys(string=k, key=v, column=column)
                                         for k, v in column_data['value_map'].items()]
                                    )

                                # Enter data en masse to avoid numerous expensive database calls
                                TimeseriesData.objects.filter(
                                    column=column,
                                    sample__in=column_data['values'].keys()
                                ).delete()
                                TimeseriesData.objects.bulk_create(
                                    [TimeseriesData(sample=k, value=v, column=column)
                                     for k, v in column_data['values'].items()]
                                )

                    except BaseException as e:
                        file.state = FileState.IMPORT_FAILED
                        HarvestError.objects.create(harvester=harvester, path=path, file=file, error=str(e))
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
    queryset = MonitoredPath.objects.none().order_by('-id')

    # Access restrictions
    def get_queryset(self):
        return MonitoredPath.objects.filter(
            Q(user_group__in=self.request.user.groups.all()) |
            Q(admin_group__in=self.request.user.groups.all()) |
            Q(harvester__admin_group__in=self.request.user.groups.all())
        ).order_by('-id')

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


class ObservedFileViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = ObservedFileSerializer
    filterset_fields = ['monitored_path__id', 'relative_path', 'state']
    search_fields = ['@monitored_path__path', '@relative_path', 'state']
    queryset = ObservedFile.objects.none().order_by('-last_observed_time', '-id')

    # Access restrictions
    def get_queryset(self):
        return ObservedFile.objects.filter(
            Q(monitored_path__user_group__in=self.request.user.groups.all()) |
            Q(monitored_path__admin_group__in=self.request.user.groups.all()) |
            Q(monitored_path__harvester__admin_group__in=self.request.user.groups.all())
        ).order_by('-last_observed_time', '-id')

    @action(detail=True, methods=['GET'])
    def reimport(self, request, pk: int = None):
        try:
            file = self.get_queryset().get(id=pk)
        except ObservedFile.DoesNotExist:
            return error_response('Requested file not found')
        file.state = FileState.RETRY_IMPORT
        file.save()
        return Response(self.get_serializer(file, context={'request': request}).data)


class DatasetViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = DatasetSerializer
    filterset_fields = ['name', 'type', 'cell__name']
    search_fields = ['@name', 'type']
    queryset = Dataset.objects.none().order_by('-date', '-id')

    # Access restrictions
    def get_queryset(self):
        return Dataset.objects.filter(
            Q(file__monitored_path__user_group__in=self.request.user.groups.all()) |
            Q(file__monitored_path__admin_group__in=self.request.user.groups.all()) |
            Q(file__monitored_path__harvester__admin_group__in=self.request.user.groups.all())
        ).order_by('-date', '-id')


class CellDataViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = CellDataSerializer
    queryset = CellData.objects.all()


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
    filterset_fields = ['name', 'symbol', 'is_default']
    search_fields = ['@name', '@symbol', '@description']
    queryset = DataUnit.objects.all().order_by('id')


class DataColumnTypeViewSet(viewsets.ModelViewSet):
    """
    TODO: document
    """
    serializer_class = DataColumnTypeSerializer
    filterset_fields = ['name', 'unit__symbol', 'unit__name', 'is_default']
    search_fields = ['@name', '@description']
    queryset = DataColumnType.objects.all().order_by('id')


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
    queryset = Group.objects.none().order_by('-id')

    def get_queryset(self):
        return self.request.user.groups.all().order_by('-id')

    @action(detail=True, methods=['POST'])
    def remove(self, request, pk: int = None):
        # A user can be removed from a group if:
        # 1. The user removing them is an admin on that group or a senior group, AND
        # 2. The harvester's admin group will not be left without any members

        # Determine what kind of group we're in
        try:
            group = Group.objects.get(id=pk)
        except Group.DoesNotExist:
            return error_response(f"Group {pk} not found")

        def drop_user(target_group: Group, request):
            try:
                user = User.objects.get(id=request.data.get('user'))
            except User.DoesNotExist:
                return error_response(f"Could not find user {request.data.get('user')}")
            if not target_group.user_set.contains(user):
                return error_response(f"That user is not in that group")
            target_group.user_set.remove(user)
            target_group.save()
            return Response(GroupSerializer(target_group, context={'request': request}).data)

        if group.editable_harvesters.first() is not None:
            if not group.user_set.contains(self.request.user).exists():
                return error_response(f"You are not authorised to edit this group")
            if len(group.user_set.all()) <= 1:
                return error_response(f"Removing that user would leave the group empty")
            return drop_user(group, self.request)

        if group.readable_harvesters.first() is not None:
            harvester = group.readable_harvesters.first()
            if not group.user_set.contains(self.request.user) \
                    and not harvester.admin_group.user_set.contains(self.request.user):
                return error_response(f"You are not authorised to edit this group")
            return drop_user(group, self.request)

        if group.editable_paths.first() is not None:
            path = group.editable_paths.first()
            if not group.user_set.contains(self.request.user) \
                    and not path.harvester.admin_group.user_set.contains(self.request.user):
                return error_response(f"You are not authorised to edit this group")
            return drop_user(group, self.request)

        if group.readable_paths.first() is not None:
            path = group.readable_paths.first()
            if not group.user_set.contains(self.request.user) \
                    and not path.admin_group.user_set.contains(self.request.user) \
                    and not path.harvester.admin_group.user_set.contains(self.request.user):
                return error_response(f"You are not authorised to edit this group")
            return drop_user(group, self.request)

        return error_response(f"Not a valid group for editing")

    @action(detail=True, methods=['POST'])
    def add(self, request, pk: int = None):
        # Determine what kind of group we're in
        try:
            group = Group.objects.get(id=pk)
        except Group.DoesNotExist:
            return error_response(f"Group {pk} not found")

        def add_user(target_group: Group, request):
            try:
                user = User.objects.get(id=request.data.get('user'))
            except User.DoesNotExist:
                return error_response(f"Could not find user {request.data.get('user')}")
            if target_group.user_set.contains(user):
                return error_response(f"That user is already in that group")
            target_group.user_set.add(user)
            target_group.save()
            return Response(GroupSerializer(target_group, context={'request': request}).data)

        if group.editable_harvesters.first() is not None:
            if not group.user_set.contains(self.request.user).exists():
                return error_response(f"You are not authorised to edit this group")
            return add_user(group, self.request)

        if group.readable_harvesters.first() is not None:
            harvester = group.readable_harvesters.first()
            if not group.user_set.contains(self.request.user) \
                    and not harvester.admin_group.user_set.contains(self.request.user):
                return error_response(f"You are not authorised to edit this group")
            return add_user(group, self.request)

        if group.editable_paths.first() is not None:
            path = group.editable_paths.first()
            if not group.user_set.contains(self.request.user) \
                    and not path.harvester.admin_group.user_set.contains(self.request.user):
                return error_response(f"You are not authorised to edit this group")
            return add_user(group, self.request)

        if group.readable_paths.first() is not None:
            path = group.readable_paths.first()
            if not group.user_set.contains(self.request.user) \
                    and not path.admin_group.user_set.contains(self.request.user) \
                    and not path.harvester.admin_group.user_set.contains(self.request.user):
                return error_response(f"You are not authorised to edit this group")
            return add_user(group, self.request)

        return error_response(f"Not a valid group for editing")
