import datetime

import knox.auth
from django.db.models import Q

from .serializers import HarvesterSerializer, \
    HarvesterConfigSerializer, \
    MonitoredPathSerializer, \
    ObservedFileSerializer, \
    CellSerializer, \
    CellFamilySerializer, \
    DatasetSerializer, \
    EquipmentSerializer, \
    DataUnitSerializer, \
    DataColumnSerializer, \
    DataColumnTypeSerializer, \
    TimeseriesDataSerializer, \
    TimeseriesDataListSerializer, \
    TimeseriesRangeLabelSerializer, \
    UserSerializer, \
    GroupSerializer, \
    HarvestErrorSerializer, \
    KnoxTokenSerializer
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
    DataColumnStringKeys, \
    DataColumn, \
    TimeseriesRangeLabel, \
    FileState, \
    VouchFor, \
    KnoxAuthToken
from .auth import HarvesterAccess
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core import validators
from rest_framework import viewsets, serializers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from knox.views import LoginView as KnoxLoginView
from knox.views import LogoutView as KnoxLogoutView
from knox.views import LogoutAllView as KnoxLogoutAllView
from knox.models import AuthToken
from rest_framework.authentication import BasicAuthentication
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer, OpenApiResponse
from .utils import IteratorFile
import json
import time
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def checkpoint(msg: str, t: float, log_fun=logger.warning) -> float:
    t2 = time.time()
    log_fun(f"{msg} (in {round(t2 - t, 2)}s)")
    return t2


def error_response(error: str, status: int = 400) -> Response:
    return Response({'error': error}, status=status)


def deserialize_datetime(serialized_value: str | float) -> timezone.datetime:
    if isinstance(serialized_value, str):
        return timezone.make_aware(timezone.datetime.fromisoformat(serialized_value))
    if isinstance(serialized_value, float):
        return timezone.make_aware(timezone.datetime.fromtimestamp(serialized_value))
    raise TypeError


@extend_schema(
    description="Log in to retrieve a Knox Token for use elsewhere in the API.",
    responses={
        200: inline_serializer(
            name='KnoxUser',
            fields={
                'expiry': serializers.DateTimeField(),
                'token': serializers.CharField(),
                'user': UserSerializer
            }
        ),
        401: OpenApiResponse(description='Invalid username/password'),
    },
    request=None
)
class LoginView(KnoxLoginView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [BasicAuthentication]

    def post(self, request, fmt=None):
        if isinstance(request.user, User):
            return super(LoginView, self).post(request=request, format=fmt)
        return Response({'detail': "Anonymous login not allowed"}, status=401)

    def get_post_response_data(self, request, token, instance):
        return {
            **UserSerializer(request.user, context={'request': request}).data,
            'token': token
        }

@extend_schema(
    description="Log out current Knox Token.",
    responses={204: None, 401: OpenApiResponse(description='Unauthorized')},
    request=None
)
class LogoutView(KnoxLogoutView):
    authentication_classes = [knox.auth.TokenAuthentication]


@extend_schema(
    description="Log out all Knox Tokens.",
    responses={204: None, 401: OpenApiResponse(description='Unauthorized')},
    request=None
)
class LogoutAllView(KnoxLogoutAllView):
    authentication_classes = [knox.auth.TokenAuthentication]


@extend_schema(
    description="Create a new Knox Token. May specify ttl (s) and name in POST request.",
    responses={
        200: inline_serializer(
            name='KnoxUser',
            fields={
                'expiry': serializers.DateTimeField(),
                'token': serializers.CharField(),
                'user': UserSerializer
            }
        )
    }
)
class CreateTokenView(KnoxLoginView):
    def get_token_ttl(self):
        try:
            ttl = self.get_context()['request'].data.get('ttl', None)
            if ttl is not None:
                ttl = datetime.timedelta(seconds=ttl)
            return ttl
        except (AttributeError, KeyError):
            return None

    def get_post_response_data(self, request, token, instance):
        error = None
        name = request.data.get('name')
        if not name:
            error = KeyError("Token must have a name")
        elif KnoxAuthToken.objects.filter(name=name, knox_token_key__regex=f"_{request.user.id}$").exists():
            error = ValueError("You already have a token with that name")
        if error:
            instance.delete()
            raise error
        else:
            token_wrapper = KnoxAuthToken.objects.create(
                name=name,
                knox_token_key=f"{instance.token_key}_{request.user.id}"
            )
        return {
            'token': token,
            **KnoxTokenSerializer(token_wrapper, context={'request': request}).data
        }


class TokenViewSet(viewsets.ModelViewSet):
    serializer_class = KnoxTokenSerializer
    queryset = KnoxAuthToken.objects.none().order_by('-id')

    def get_queryset(self):
        token_keys = [f"{t.token_key}_{t.user_id}" for t in AuthToken.objects.filter(user_id=self.request.user.id)]
        # Create entries for temporary browser tokens
        for k in token_keys:
            if not KnoxAuthToken.objects.filter(knox_token_key=k).exists():
                KnoxAuthToken.objects.create(knox_token_key=k, name=f"Browser session [{k}]")
        return KnoxAuthToken.objects.filter(knox_token_key__in=token_keys).order_by('-id')

    def destroy(self, request, *args, **kwargs):
        try:
            token = KnoxAuthToken.objects.get(
                pk=kwargs.get('pk'),
                knox_token_key__regex=f"_{request.user.id}$"
            )
        except KnoxAuthToken.DoesNotExist:
            return error_response("Token not found")
        key, id = token.knox_token_key.split("_")
        AuthToken.objects.filter(user_id=int(id), token_key=key).delete()
        token.delete()
        return Response(status=204)


class HarvesterViewSet(viewsets.ModelViewSet):
    """
    Harvesters monitor a set of MonitoredPaths and send reports about ObservedFiles
    within those paths.
    A Harvester has Users and Admins, managed by Django's inbuilt User and Group models.

    When Harvesters communicate with the API they do so using special Harvester API Keys.
    These provide access to the report and configuration endpoints.

    Harvesters are created by a separate software package available within Galvanalyser.
    """
    permission_classes = [HarvesterAccess]
    serializer_class = HarvesterSerializer
    filterset_fields = ['name']
    search_fields = ['@name']
    queryset = Harvester.objects.none().order_by('-last_check_in', '-id')

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        # Allow access to Harvesters where we have a Path
        path_harvesters = [p.harvester.id for p in MonitoredPath.objects.filter(
            Q(user_group__in=user_groups) | Q(admin_group__in=user_groups)
        )]
        my_harvesters = Harvester.objects.filter(
            Q(user_group__in=user_groups) |
            Q(admin_group__in=user_groups) |
            Q(id__in=path_harvesters)
        )
        return my_harvesters.order_by('-last_check_in', '-id')

    def create(self, request, *args, **kwargs):
        """
        Create a Harvester and the user Groups required to control it.
        """
        # TODO: move to serializer?
        # Validate input
        if not request.data.get('name'):
            return error_response('No name specified for Harvester.')
        if not request.data.get('user'):
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

        return Response(HarvesterConfigSerializer(harvester, context={'request': request}).data)

    def update(self, request, *args, **kwargs):
        """Update Harvester properties."""
        try:
            harvester = Harvester.objects.get(id=kwargs.get('pk'))
        except Harvester.DoesNotExist:
            return error_response(f'Harvester with id {request.data["id"]} not found.')
        if not request.user.groups.contains(harvester.admin_group):
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

    # TODO: handle harvester envvars?

    @action(detail=True, methods=['GET'])
    def config(self, request, pk: int = None):
        """
        Return a full configuration file including MonitoredPaths under paths.

        Only available to Harvesters.
        """
        harvester = get_object_or_404(Harvester, id=pk)
        return Response(HarvesterConfigSerializer(harvester, context={'request': request}).data)

    @action(detail=True, methods=['POST'])
    def report(self, request, pk: int = None):
        """
        Process a Harvester's report on its activity.
        This will spawn various other database updates depending on payload content.

        Only Harvesters are authorised to issue reports.
        """
        harvester = get_object_or_404(Harvester, id=pk)
        harvester.last_check_in = timezone.now()
        harvester.save()
        if request.data.get('status') is None:
            return error_response('Badly formatted request')
        try:
            path = MonitoredPath.objects.get(path=request.data['path'], harvester=harvester)
        except MonitoredPath.DoesNotExist:
            return error_response('Unrecognized path')
        except KeyError:
            return error_response('Harvester report must specify a path')
        if request.data['status'] == 'error':
            error = request.data.get('error')
            if not isinstance(error, str):
                try:
                    error = json.dumps(error)
                except json.JSONDecodeError:
                    error = str(error)
            file_rel_path = request.data.get('file')
            if file_rel_path:
                HarvestError.objects.create(
                    harvester=harvester,
                    path=path,
                    file=ObservedFile.objects.get_or_create(
                        monitored_path=path,
                        relative_path=file_rel_path,
                        defaults={'state': FileState.IMPORT_FAILED}
                    )[0],
                    error=str(error)
                )
            else:
                HarvestError.objects.create(
                    harvester=harvester,
                    path=path,
                    error=str(error)
                )
            return Response({})
        elif request.data['status'] == 'success':
            # Figure out what we succeeded in doing!
            content = request.data.get('content')
            if content is None:
                return error_response('content field required when status=success')
            if content['task'] == 'file_size':
                # Harvester is reporting the size of a file
                # Update our database record and return a file status
                file, _ = ObservedFile.objects.get_or_create(monitored_path=path, relative_path=request.data['file'])

                if content.get('size') is None:
                    return error_response('file_size task requires content to include size field')

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
                    elif file.state not in [FileState.IMPORTED, FileState.IMPORT_FAILED]:
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
                            if file.state == FileState.IMPORTING:
                                file.state = FileState.IMPORTED
                        else:
                            time_start = time.time()
                            date = deserialize_datetime(content['test_date'])
                            dataset = Dataset.objects.get(file=file, date=date)
                            for column_data in content['data']:
                                time_col_start = time.time()
                                logger.warning(f"Column {column_data.get('column_name', column_data.get('column_id'))}")
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
                                    time_value_rm = time.time()
                                    DataColumnStringKeys.objects.filter(column=column).delete()
                                    time_value_add = checkpoint('deleted existing value map', time_value_rm)
                                    DataColumnStringKeys.objects.bulk_create(
                                        [DataColumnStringKeys(string=k, key=v, column=column)
                                         for k, v in column_data['value_map'].items()]
                                    )
                                    checkpoint('created value map', time_value_add)

                                time_ts_prep = time.time()
                                from django.db import connection

                                rows = []
                                for s, v in column_data['values'].items():
                                    rows.append(f"{int(s)}\t{column.id}\t{int(v)}")

                                iter_file = IteratorFile(rows.__iter__())
                                time_ts_add = checkpoint('prepared ts objects', time_ts_prep)
                                with connection.cursor() as cursor:
                                    cursor.copy_expert(
                                        'COPY timeseries_data FROM STDIN',
                                        iter_file
                                    )
                                checkpoint('created timeseries data', time_ts_add)
                                checkpoint('column complete', time_col_start)

                            checkpoint('complete', time_start)
                    except BaseException as e:
                        file.state = FileState.IMPORT_FAILED
                        HarvestError.objects.create(harvester=harvester, path=path, file=file, error=str(e))
                        file.save()
                        return error_response(f"Error importing data: {e.args}")
                if content['status'] == 'failed':
                    file.state = FileState.IMPORT_FAILED

                file.save()

                return Response(ObservedFileSerializer(file, context={
                    'request': self.request,
                    'with_upload_info': content['status'] == 'begin'
                }).data)
            else:
                return error_response('Unrecognised task')
        else:
            return error_response('Unrecognised status')


class MonitoredPathViewSet(viewsets.ModelViewSet):
    """
    A MonitoredPath refers to a directory accessible by a Harvester in which
    data files will reside. Those files will be scanned periodically by the Harvester,
    becoming ObservedFiles once they are reported to Galvanalyser by the Harvester.

    MonitoredPaths can be created or updated by a Harvester's admins and users, as
    well as any users who have been given explicit permissions to edit the MonitoredPath.
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
        path = str(request.data.get('path')).lower().lstrip().rstrip()
        if not path:
            return error_response('No path specified.')
        try:
            harvester = Harvester.objects.get(id=request.data['harvester'])
        except (Harvester.DoesNotExist, AttributeError):
            return error_response('Harvester not found.')
        if len(MonitoredPath.objects.filter(path=path, harvester=harvester)):
            return error_response('Path already exists on Harvester.')
        # Check user is authorised to create paths on Harvester
        if not request.user.groups.filter(id=harvester.user_group_id).exists() and \
                not request.user.groups.filter(id=harvester.admin_group_id).exists():
            return error_response(f'Permission denied to {request.user.username} for {harvester.name}')

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
    ObservedFiles are files that exist (or have existed) in a MonitoredPath and have
    been reported to Galvanalyser by the Harvester.

    An ObservedFile instance will have file metadata (size, modification time), and a
    status representing its import state. It may be linked to HarvestErrors
    encountered while importing the file, and/or to Datasets representing the content
    of imported files.
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
    A Dataset contains structured data from an ObservedFile.

    Datasets are decomposed within Galvanalyser into columns and datapoints,
    providing an ability flexibly handle any kind of tabular data.
    """
    serializer_class = DatasetSerializer
    filterset_fields = ['name', 'type', 'cell__family__name']
    search_fields = ['@name', 'type']
    queryset = Dataset.objects.none().order_by('-date', '-id')

    # Access restrictions
    def get_queryset(self):
        return Dataset.objects.filter(
            Q(file__monitored_path__user_group__in=self.request.user.groups.all()) |
            Q(file__monitored_path__admin_group__in=self.request.user.groups.all()) |
            Q(file__monitored_path__harvester__admin_group__in=self.request.user.groups.all())
        ).order_by('-date', '-id')


class HarvestErrorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    HarvestErrors are problems encountered by Harvesters during the crawling of
    MonitoredPaths or the importing or inspection of ObservedFiles.
    """
    serializer_class = HarvestErrorSerializer
    filterset_fields = ['file', 'path', 'harvester']
    search_fields = ['@error']
    queryset = HarvestError.objects.none().order_by('-timestamp')

    # Access restrictions
    def get_queryset(self):
        return HarvestError.objects.filter(
            Q(path__user_group__in=self.request.user.groups.all()) |
            Q(path__admin_group__in=self.request.user.groups.all()) |
            Q(harvester__admin_group__in=self.request.user.groups.all())
        ).order_by('-timestamp')


class CellFamilyViewSet(viewsets.ModelViewSet):
    """
    CellFamilies describe types of Cell.
    """
    serializer_class = CellFamilySerializer
    filterset_fields = [
        'name', 'form_factor', 'anode_chemistry', 'cathode_chemistry', 'nominal_capacity',
        'nominal_cell_weight', 'manufacturer'
    ]
    search_fields = ['@name', '@manufacturer', 'form_factor']
    queryset = CellFamily.objects.all().order_by('-id')


class CellViewSet(viewsets.ModelViewSet):
    """
    Cells are specific cells which have generated data stored in Datasets/ObservedFiles.
    """
    serializer_class = CellSerializer
    filterset_fields = ['display_name', 'uid', 'family__id']
    search_fields = ['@display_name']
    queryset = Cell.objects.all().order_by('-id')


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    Equipment can be attached to Datasets and used to view Datasets which
    have used similar equipment.
    """
    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()


class DataUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    DataUnits are units used to characterise data in a DataColumn.
    """
    serializer_class = DataUnitSerializer
    filterset_fields = ['name', 'symbol', 'is_default']
    search_fields = ['@name', '@symbol', '@description']
    queryset = DataUnit.objects.all().order_by('id')


class DataColumnTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    DataColumnTypes support reuse of DataColumns over multiple DataSets
    by abstracting their information.
    """
    serializer_class = DataColumnTypeSerializer
    filterset_fields = ['name', 'unit__symbol', 'unit__name', 'is_default']
    search_fields = ['@name', '@description']
    queryset = DataColumnType.objects.all().order_by('id')


class DataColumnViewSet(viewsets.ReadOnlyModelViewSet):
    """
    DataColumns describe which columns are in a Dataset's data.
    """
    serializer_class = DataColumnSerializer
    filterset_fields = ['dataset__name', 'type__unit__symbol']
    search_fields = ['@dataset__name']
    queryset = DataColumn.objects.all()

    def get_queryset(self):
        datasets_ids = [d.id for d in Dataset.objects.filter(
            Q(file__monitored_path__user_group__in=self.request.user.groups.all()) |
            Q(file__monitored_path__admin_group__in=self.request.user.groups.all()) |
            Q(file__monitored_path__harvester__admin_group__in=self.request.user.groups.all())
        ).only('id')]
        return DataColumn.objects.filter(dataset_id__in=datasets_ids)

    @action(methods=['GET'], detail=True)
    def data(self, request, pk: int = None):
        """
        Fetch the data for this column in an 'observations' dictionary of record_id: observed_value pairs.
        """
        column = get_object_or_404(DataColumn, id=pk)
        return Response(TimeseriesDataSerializer(column, context={'request': self.request}).data)

    @action(methods=['GET'], detail=True)
    def data_list(self, request, pk: int = None):
        """
        Fetch the data for this column in an 'observations' dictionary of record_id: observed_value pairs.
        """
        column = get_object_or_404(DataColumn, id=pk)
        return Response(TimeseriesDataListSerializer(column, context={'request': self.request}).data)


class TimeseriesRangeLabelViewSet(viewsets.ModelViewSet):
    """
    TimeseriesRangeLabels mark contiguous observations using start and endpoints.
    """
    serializer_class = TimeseriesRangeLabelSerializer
    queryset = TimeseriesRangeLabel.objects.all()


class InactiveViewSet(viewsets.ModelViewSet):
    """
    Users are Django User instances custom-serialized for convenience.

    New users can be created at will, but they will be marked as is_active=False
    until vouched for by an existing active user.
    """
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=False)

    def create(self, request, *args, **kwargs):
        # TODO: Move to serializer so only wanted fields appear in Django web form?
        try:
            username = request.data['username']
            email = validators.validate_email(request.data['email'])
            password = request.data['password']
        except (KeyError, validators.ValidationError):
            return error_response(f"Username, email, and password fields required.")
        if User.objects.filter(username=username).exists():
            return error_response(f"User {username} already exists.")
        try:
            new_user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
        except:
            return error_response(error='Error creating user')
        return Response(UserSerializer(new_user, context={'request': request}).data)

    @action(methods=['GET'], detail=True)
    def vouch_for(self, request, pk: int = None):
        try:
            new_user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return error_response(f"User not found")
        VouchFor.objects.create(new_user=new_user, vouching_user=request.user)
        new_user.is_active = True
        new_user.save()
        return Response(UserSerializer(new_user, context={'request': request}).data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Users are Django User instances custom-serialized for convenience.
    """
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)

    @action(detail=True, methods=['PATCH'])
    def update_profile(self, request, pk: int = None):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return error_response("User not found", 404)
        if user != request.user:
            return error_response("You may only edit your own details", 401)
        email = request.data.get('email')
        if email:
            try:
                validators.validate_email(email)
            except validators.ValidationError:
                return error_response("Invalid email")
        password = request.data.get('password')
        if password and not len(password) > 7:
            return error_response("Password must be at least 7 characters")
        current_password = request.data.get('currentPassword')
        if not user.check_password(current_password):
            return error_response("You must include the correct current password", 401)
        if email:
            user.email = email
        if password:
            user.set_password(password)
        user.save()
        return Response(UserSerializer(user, context={'request': request}).data)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Groups are Django Group instances custom-serialized for convenience.
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
            return Response(GroupSerializer(target_group, context={'request': request}).data)

        if group.editable_harvesters.first() is not None:
            if not group.user_set.contains(self.request.user):
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
            return Response(GroupSerializer(target_group, context={'request': request}).data)

        if group.editable_harvesters.first() is not None:
            if not group.user_set.contains(self.request.user):
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
