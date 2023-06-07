# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import datetime

import knox.auth
import os
from django.db.models import Q

from .serializers import HarvesterSerializer, \
    HarvesterCreateSerializer, \
    HarvesterConfigSerializer, \
    MonitoredPathSerializer, \
    MonitoredPathCreateSerializer, \
    ObservedFileSerializer, \
    CellSerializer, \
    CellFamilySerializer, \
    DatasetSerializer, \
    EquipmentSerializer, \
    DataUnitSerializer, \
    DataColumnSerializer, \
    DataColumnTypeSerializer, \
    TimeseriesRangeLabelSerializer, \
    UserSerializer, \
    GroupSerializer, \
    HarvestErrorSerializer, \
    KnoxTokenSerializer, \
    KnoxTokenFullSerializer
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
    TimeseriesDataFloat, \
    TimeseriesDataInt, \
    TimeseriesDataStr, \
    DataColumn, \
    UnsupportedTimeseriesDataTypeError, \
    get_timeseries_handler_by_type, \
    TimeseriesRangeLabel, \
    FileState, \
    VouchFor, \
    KnoxAuthToken
from .permissions import HarvesterAccess, ReadOnlyIfInUse
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core import validators
from django.http import StreamingHttpResponse
from rest_framework import viewsets, serializers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from knox.views import LoginView as KnoxLoginView
from knox.views import LogoutView as KnoxLogoutView
from knox.views import LogoutAllView as KnoxLogoutAllView
from knox.models import AuthToken
from rest_framework.authentication import BasicAuthentication
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer, OpenApiResponse
import json
import time
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


GENERATE_HARVESTER_API_SCHEMA = os.getenv('GENERATE_HARVESTER_API_SCHEMA', "FALSE").upper()[0] != "F"


def checkpoint(msg: str, t: float, log_fun=logger.warning) -> float:
    t2 = time.time()
    log_fun(f"{msg} (in {round(t2 - t, 2)}s)")
    return t2


class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField(help_text="Description of the error")


def error_response(error: str, status: int = 400) -> Response:
    return Response({'error': error}, status=status)


def deserialize_datetime(serialized_value: str | float) -> timezone.datetime:
    if isinstance(serialized_value, str):
        return timezone.make_aware(timezone.datetime.fromisoformat(serialized_value))
    if isinstance(serialized_value, float):
        return timezone.make_aware(timezone.datetime.fromtimestamp(serialized_value))
    raise TypeError


@extend_schema(
    summary="Log in to retrieve an API Token for use elsewhere in the API.",
    description="""
Sign in with a username and password to obtain an API Token.
The token will allow you access to appropriate parts of the API in subsequent requests.

Subsequent requests should include the Authorization header with the content `Bearer token`
where token is the token you received in exchange for your credentials here.
    """,
    responses={
        200: inline_serializer(
            name='KnoxUser',
            fields={
                'expiry': serializers.DateTimeField(),
                'token': serializers.CharField(),
                'user': UserSerializer()
            }
        ),
        401: OpenApiResponse(description='Invalid username/password'),
    },
    request=None
)
class LoginView(KnoxLoginView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [BasicAuthentication]
    http_method_names = ['post', 'options']

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
    summary="Log out current API Token.",
    description="""
Send a logout request to remove the token used to authenticate the request.
    """,
    responses={204: None, 401: OpenApiResponse(description='Unauthorized')},
    request=None
)
class LogoutView(KnoxLogoutView):
    http_method_names = ['get', 'options']
    authentication_classes = [knox.auth.TokenAuthentication]


@extend_schema(
    summary="Log out all API Tokens.",
    description="""
Remove all tokens associated with your account.
If you have numerous old or leaked tokens spread across numerous programs,
you can use this endpoint to easily revoke them all.
    """,
    responses={204: None, 401: OpenApiResponse(description='Unauthorized')},
    request=None
)
class LogoutAllView(KnoxLogoutAllView):
    http_method_names = ['get', 'options']
    authentication_classes = [knox.auth.TokenAuthentication]


@extend_schema(
    summary="Create a new API Token",
    description="""
Access to the API is authenticated by API Tokens.
When you log into the web frontend, you are issued with a temporary token
to allow your browser session to function.
If you wish to access the API via the Python client, or similar programmatically routes,
you will likely want a token with a longer expiry time. Those tokens are created using
this endpoint.
    """,
    request=inline_serializer('CreateKnoxToken', {
        'ttl': serializers.IntegerField(required=False, help_text="Time to live (s)"),
        'name': serializers.CharField()
    }),
    responses={
        200: KnoxTokenFullSerializer,
    }
)
class CreateTokenView(KnoxLoginView):
    """
    Create a new Knox Token.
    """
    http_method_names = ['post', 'options']

    def get_queryset(self):
        return KnoxAuthToken.objects.none().order_by('-id')

    def get_token_ttl(self):
        try:
            ttl = self.get_context()['request'].data.get('ttl', None)
            if ttl is not None:
                ttl = datetime.timedelta(seconds=int(ttl))
            return ttl
        except (AttributeError, KeyError, ValueError):
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
        return KnoxTokenFullSerializer(token_wrapper, context={'request': request, 'token': token}).data


@extend_schema_view(
    list=extend_schema(
        summary="View tokens associated with your account.",
        description="""
List all API tokens associated with this user account.
You will not be able to see the value of the tokens themselves,
because these values are encrypted, but you can see the names you gave them and their expiry dates.

New Tokens cannot be created at this endpoint, use /create_token/ instead.
        """
    ),
    retrieve=extend_schema(
        summary="View a token associated with your account.",
        description="""
You will not be able to see the value of the token,
but you can see the name you gave it and its creation/expiry date.
        """,
    ),
    partial_update=extend_schema(
        summary="Change the name of a token associated with your account.",
        description="""
Token values and expiry dates are immutable, but you can change the name you
associated with a token.
        """
    ),
    destroy=extend_schema(
        summary="Revoke a token associated with your account.",
        description="""
Revoking a token renders that token invalid for authenticating requests to the API.
If you have tokens that are no longer needed, or that have been leaked (for example
by being included in a public Git Repository), you can should revoke them so that
other people cannot use them to access the API under your credentials.
        """
    )
)
class TokenViewSet(viewsets.ModelViewSet):
    """
    View and edit tokens associated with your account.
    """
    serializer_class = KnoxTokenSerializer
    queryset = KnoxAuthToken.objects.none().order_by('-id')
    http_method_names = ['get', 'patch', 'delete', 'options']

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
            self.check_object_permissions(self.request, token)
        except KnoxAuthToken.DoesNotExist:
            return error_response("Token not found")
        key, id = token.knox_token_key.split("_")
        AuthToken.objects.filter(user_id=int(id), token_key=key).delete()
        token.delete()
        return Response(status=204)


@extend_schema_view(
    list=extend_schema(
        summary="View all Harvesters",
        description="""
Harvesters monitor a set of MonitoredPaths and send reports about ObservedFiles within those paths.
You can view all Harvesters on which you are an Administrator or User,
and those which have MonitoredPaths on which you are an Administrator or User.

Searchable fields:
- name
        """
    ),
    mine=extend_schema(
        summary="View Harvesters to which you have access",
        description="""
View only Harvesters to which you have access.
On systems with multiple Harvesters, this view is more useful than /harvesters/.

This view will include Harvester environment variables, while /harvesters/ will not.

Searchable fields:
- name
        """
    ),
    retrieve=extend_schema(
        summary="View a single Harvester",
        description="""
Harvesters monitor a set of MonitoredPaths and send reports about ObservedFiles within those paths.
        """
    ),
    create=extend_schema(
        exclude=not GENERATE_HARVESTER_API_SCHEMA,
        summary="Register the creation of a Harvester",
        description="""
A new Harvester created with the harvester program's `start.py` script will register itself via this endpoint.
This endpoint will register the Harvester and set up the user and administrator groups.
        """,
        request=HarvesterCreateSerializer(),
        responses={201: HarvesterConfigSerializer()}
    ),
    partial_update=extend_schema(
        summary="Update Harvester details",
        description="""
Some Harvester details can be updated after the Harvester is created.
Those details are updated using this endpoint.

Only Harvester Administrators are authorised to make these changes.
        """
    ),
    destroy=extend_schema(
        summary="Delete a Harvester",
        description="""
**Use with caution.**

Only Harvester Administrators are authorised to delete harvesters.
Deleting a Harvester will not stop the harvester program running,
it will instead deactivate its API access.
Currently, harvesters cannot be recreated easily, so don't delete them if you might want them later.
Generally, a better solution is to stop the harvester program instead.
        """
    ),
    config=extend_schema(
        exclude=not GENERATE_HARVESTER_API_SCHEMA,
        summary="Full configuration information for a Harvester",
        description="""
Only accessible to Harvesters.

Returns the full configuration information required by the harvester program to do its work.
This includes the Harvester specification, the Paths to monitor,
and information about standard Columns and Units.
        """
    ),
    report=extend_schema(
        exclude=not GENERATE_HARVESTER_API_SCHEMA,
        summary="Harvester-API communication",
        description="""
The harvester programs use the report endpoint for all information they send to the API
(except initial self-registration).
Reports will be file size reports, file parsing reports, or error reports.
File parsing reports may contain metadata or data to store.
        """,
        request=inline_serializer('HarvesterReportSerializer', {
            # TODO
        }),
        responses={
            # TODO
        }
    )
)
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
    filterset_fields = ['name']
    search_fields = ['@name']
    queryset = Harvester.objects.all().order_by('-last_check_in', '-id')
    http_method_names = ['get', 'post', 'patch', 'delete', 'options']

    def get_serializer_class(self):
        if self.request.method.lower() == "post":
            return HarvesterCreateSerializer
        return HarvesterSerializer

    @action(detail=False, methods=['GET'])
    def mine(self, request):
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
        return Response(HarvesterSerializer(
            my_harvesters.order_by('-last_check_in', '-id'),
            many=True,
            context={'request': request}
        ).data)

    @action(detail=True, methods=['GET'])
    def config(self, request, pk: int = None):
        """
        Return a full configuration file including MonitoredPaths under paths.

        Only available to Harvesters.
        """
        harvester = get_object_or_404(Harvester, id=pk)
        self.check_object_permissions(self.request, harvester)
        return Response(HarvesterConfigSerializer(
            harvester,
            context={'request': request}
        ).data)

    @action(detail=True, methods=['POST'])
    def report(self, request, pk: int = None):
        """
        Process a Harvester's report on its activity.
        This will spawn various other database updates depending on payload content.

        Only Harvesters are authorised to issue reports.
        """
        harvester = get_object_or_404(Harvester, id=pk)
        self.check_object_permissions(self.request, harvester)
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

                                time_ts_prep = time.time()
                                # get timeseries handler
                                try:
                                    sample_data = column_data.get('sample_data')
                                except KeyError:
                                    return error_response(f"Could not find sample data for column {column.name}")
                                try:
                                    handler = get_timeseries_handler_by_type(type(sample_data))
                                except UnsupportedTimeseriesDataTypeError:
                                    return error_response(
                                        f'Unsupported variable type {type(sample_data)} in column {column.name}'
                                    )
                                try:
                                    # insert values
                                    timeseries, _ = handler.objects.get_or_create(column=column)
                                    data = timeseries.values if timeseries.values is not None else []
                                    data = [*data, *column_data["values"]]
                                    timeseries.values = data
                                    timeseries.save()
                                except Exception as e:
                                    return error_response(f"Error saving column {column_data['column_name']}. {type(e)}: {e.args[0]}")
                                checkpoint('created timeseries data', time_ts_prep)
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


@extend_schema_view(
    list=extend_schema(
        summary="View Paths to which you have access",
        description="""
A Path refers to a directory accessible by a Harvester in which
data files will reside. Those files will be scanned periodically by the Harvester,
becoming ObservedFiles once they are reported to Galvanalyser by the Harvester.

Paths can be created or updated by a Harvester's admins and users, as
well as any users who have been given explicit permissions to edit the MonitoredPath.

Searchable fields:
- path
        """
    ),
    retrieve=extend_schema(
        summary="View the details of a Path",
        description="""
A Path refers to a directory accessible by a Harvester in which
data files will reside. Those files will be scanned periodically by the Harvester,
becoming ObservedFiles once they are reported to Galvanalyser by the Harvester.
        """
    ),
    create=extend_schema(
        summary="Create a new Path",
        description="""
Register a new directory on for a Harvester to crawl.
Files in that directory will be scanned periodically by the Harvester,
becoming ObservedFiles once they are reported to Galvanalyser by the Harvester.
        """,
        request=MonitoredPathCreateSerializer(),
        responses={
            201: MonitoredPathSerializer()
        }
    ),
    partial_update=extend_schema(
        summary="Update a Path",
        description="""
Alter the path to the monitored directory,
or the time for which files need to be stable before being imported.
        """
    ),
    destroy=extend_schema(
        summary="Delete a Path",
        description="""
Stop a directory from being monitored by a Harvester.
This will not delete datasets imported from Files in this Path.
        """
    )
)
class MonitoredPathViewSet(viewsets.ModelViewSet):
    """
    A MonitoredPath refers to a directory accessible by a Harvester in which
    data files will reside. Those files will be scanned periodically by the Harvester,
    becoming ObservedFiles once they are reported to Galvanalyser by the Harvester.

    MonitoredPaths can be created or updated by a Harvester's admins and users, as
    well as any users who have been given explicit permissions to edit the MonitoredPath.
    """
    # serializer_class = MonitoredPathSerializer
    filterset_fields = ['path', 'harvester__id', 'harvester__name']
    search_fields = ['@path']
    queryset = MonitoredPath.objects.none().order_by('-id')
    http_method_names = ['get', 'post', 'patch', 'delete', 'options']

    def get_serializer_class(self):
        if self.request.method.lower() == "post":
            return MonitoredPathCreateSerializer
        return MonitoredPathSerializer

    # Access restrictions
    def get_queryset(self):
        return MonitoredPath.objects.filter(
            Q(user_group__in=self.request.user.groups.all()) |
            Q(admin_group__in=self.request.user.groups.all()) |
            Q(harvester__admin_group__in=self.request.user.groups.all())
        ).order_by('-id')


@extend_schema_view(
    list=extend_schema(
        summary="View Files on a Path you can access",
        description="""
Files are files in a directory marked as a monitored Path for a Harvester.

They are reported to Galvanalyser by the harvester program.
An File will have file metadata (size, modification time), and a
status representing its import state. It may be linked to HarvestErrors
encountered while importing the file, and/or to Datasets representing the content
of imported files.

You can see all files on any Path on which you are an Administrator or User.
Harvester Administrators have access to all Files on the Harvester's Paths.

Searchable fields:
- monitored_path__path
- relative_path
- state
        """
    ),
    retrieve=extend_schema(
        summary="View a File",
        description="""
Files are files in a directory marked as a monitored Path for a Harvester.
        """
    ),
    reimport=extend_schema(
        summary="Force a File to be re-imported",
        description="""
A File will usually only be imported once, provided it is created, written to,
and then left alone. Files will naturally be reimported if they grow in size
again.
If an error was encountered while processing a file, or you have other reasons
for wishing to repeat the import process, you can use this endpoint to force the
harvester program to rerun the import process when it next scans the file.

*Note*: This request may be overwritten if the file changes size before it is next scanned.
        """
    )
)
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
    http_method_names = ['get', 'options']

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
            self.check_object_permissions(self.request, file)
        except ObservedFile.DoesNotExist:
            return error_response('Requested file not found')
        file.state = FileState.RETRY_IMPORT
        file.save()
        return Response(self.get_serializer(file, context={'request': request}).data)


@extend_schema_view(
    list=extend_schema(
        summary="View Datasets",
        description="""
View the Datasets extracted from Files on Paths to which you have access.

Datasets consist of metadata and links to the Columns that link to the actual data themselves.

Searchable fields:
- name
- type
        """
    ),
    retrieve=extend_schema(
        summary="View a Dataset",
        description="""
Datasets consist of metadata and links to the Columns that link to the actual data themselves.
        """
    ),
    partial_update=extend_schema(
        summary="Alter a Dataset's metadata",
        description="""
Update a Dataset's metadata to associate it with the Cell or Experimental equipment that were
used in the experiment that generated the data, describe that experiment's purpose,
or amend an incorrect name or file type value.
        """
    )
)
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
    http_method_names = ['get', 'patch', 'options']

    # Access restrictions
    def get_queryset(self):
        return Dataset.objects.filter(
            Q(file__monitored_path__user_group__in=self.request.user.groups.all()) |
            Q(file__monitored_path__admin_group__in=self.request.user.groups.all()) |
            Q(file__monitored_path__harvester__admin_group__in=self.request.user.groups.all())
        ).order_by('-date', '-id')


@extend_schema_view(
    list=extend_schema(
        summary="View Errors encountered while Harvesting",
        description="""
View the Errors encountered by Harvesters to which you have access.

Harvesters report errors when they encounter them, either in crawling or in processing files.
If a File or Dataset is not appearing on a Path where you think it should be, this is the first place to check.

Searchable fields:
- error
        """
    ),
    retrieve=extend_schema(
        summary="View Error details",
        description="""
View an Error reported by a Harvester.
        """
    )
)
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


@extend_schema_view(
    list=extend_schema(
        summary="View Cell Families",
        description="""
Cell Families group together the general properties of a type of Cell.
Each Cell is associated with a Cell Family.

Searchable fields:
- name
- manufacturer
- form_factor
        """
    ),
    retrieve=extend_schema(
        summary="View a Cell Family",
        description="""
Cell Families group together the general properties of a type of Cell.
Each Cell is associated with a Cell Family.
        """
    ),
    create=extend_schema(
        summary="Create a Cell Family",
        description="""
Cell Families group together the general properties of a type of Cell.
Each Cell is associated with a Cell Family.
        """
    ),
    partial_update=extend_schema(
        summary="Update a Cell Family",
        description="""
Cell Families that do not have any Cells associated with them may be edited.
Cell Families that _do_ have Cells associated with them are locked,
to prevent accidental updating.
        """
    ),
    destroy=extend_schema(
        summary="Delete a Cell Family",
        description="""
Cell Families that do not have any Cells associated with them may be deleted.
Cell Families that _do_ have Cells associated with them are locked,
to prevent accidental updating.
        """
    )
)
class CellFamilyViewSet(viewsets.ModelViewSet):
    """
    CellFamilies describe types of Cell.
    """
    permission_classes = [ReadOnlyIfInUse]
    serializer_class = CellFamilySerializer
    filterset_fields = [
        'name', 'form_factor', 'anode_chemistry', 'cathode_chemistry', 'nominal_capacity',
        'nominal_cell_weight', 'manufacturer'
    ]
    search_fields = ['@name', '@manufacturer', 'form_factor']
    queryset = CellFamily.objects.all().order_by('-id')
    http_method_names = ['get', 'post', 'patch', 'delete', 'options']


@extend_schema_view(
    list=extend_schema(
        summary="View Cells",
        description="""
Cells are specific cells which generate data stored in Datasets/observed Files.

Searchable fields:
- display_name
        """
    ),
    retrieve=extend_schema(
        summary="View a Cell",
        description="""
Cells are specific cells which generate data stored in Datasets/observed Files.
        """
    ),
    create=extend_schema(
        summary="Create a Cell",
        description="""
Create an instance of a Cell by declaring its unique identifier and associated Cell Family.
        """
    ),
    partial_update=extend_schema(
        summary="Update a Cell",
        description="""
Cells that are not used in any Dataset may be edited.
Cells that _are_ used in a Dataset are locked to prevent accidental updating.
        """
    ),
    destroy=extend_schema(
        summary="Delete a Cell",
        description="""
Cells that are not used in any Dataset may be deleted.
Cells that _are_ used in a Dataset are locked to prevent accidental updating.
        """
    )
)
class CellViewSet(viewsets.ModelViewSet):
    """
    Cells are specific cells which have generated data stored in Datasets/ObservedFiles.
    """
    permission_classes = [ReadOnlyIfInUse]
    serializer_class = CellSerializer
    filterset_fields = ['display_name', 'uid', 'family__id']
    search_fields = ['@display_name']
    queryset = Cell.objects.all().order_by('-id')
    http_method_names = ['get', 'post', 'patch', 'delete', 'options']


@extend_schema_view(
    list=extend_schema(
        summary="View Equipment",
        description="""
Experimental equipment used in experiments which generate Files and their Datasets.

Searchable fields:
- name
- type
        """
    ),
    retrieve=extend_schema(
        summary="View specific Equipment",
        description="""
Experimental equipment used in experiments which generate Files and their Datasets.
        """
    ),
    create=extend_schema(
        summary="Create Equipment",
        description="""
Create Equipment by describing its role and purpose.
        """
    ),
    partial_update=extend_schema(
        summary="Update Equipment",
        description="""
Equipment that is not used in any Dataset may be edited.
Equipment that _is_ used in a Dataset is locked to prevent accidental updating.
        """
    ),
    destroy=extend_schema(
        summary="Delete Equipment",
        description="""
Equipment that is not used in any Dataset may be deleted.
Equipment that _is_ used in a Dataset is locked to prevent accidental updating.
        """
    )
)
class EquipmentViewSet(viewsets.ModelViewSet):
    """
    Equipment can be attached to Datasets and used to view Datasets which
    have used similar equipment.
    """
    permission_classes = [ReadOnlyIfInUse]
    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()
    filterset_fields = ['type']
    search_fields = ['@name', '@type']
    http_method_names = ['get', 'post', 'patch', 'delete', 'options']


@extend_schema_view(
    list=extend_schema(
        summary="View Units",
        description="""
Units are scientific (typically SI) units which describe how data map to quantities in the world.
Some Units are predefined (e.g. seconds, volts, amps, unitless quantities),
while others can be defined in experimental data.

Searchable fields:
- name
- symbol
- description
        """
    ),
    retrieve=extend_schema(
        summary="View a Unit",
        description="""
Units are scientific (typically SI) units which describe how data map to quantities in the world.
Some Units are predefined (e.g. seconds, volts, amps, unitless quantities),
while others can be defined in experimental data.
        """
    )
)
class DataUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    DataUnits are units used to characterise data in a DataColumn.
    """
    serializer_class = DataUnitSerializer
    filterset_fields = ['name', 'symbol', 'is_default']
    search_fields = ['@name', '@symbol', '@description']
    queryset = DataUnit.objects.all().order_by('id')


@extend_schema_view(
    list=extend_schema(
        summary="View Column Types",
        description="""
Column Types are generic Column templates. They hold the metadata for a Column,
while the individual Column instances link Column Types to the TimeseriesData they contain.

Some Column Types are innately recognised by Galvanalyser and its harvester parsers,
while others can be defined by the parsers during data processing.

Searchable fields:
- name
- description
        """
    ),
    retrieve=extend_schema(
        summary="View a Column Type",
        description="""
Column Types are generic Column templates. They hold the metadata for a Column,
while the individual Column instances link Column Types to the TimeseriesData they contain.

Some Column Types are innately recognised by Galvanalyser and its harvester parsers,
while others can be defined by the parsers during data processing.

Searchable fields:
- name
- description
        """
    )
)
class DataColumnTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    DataColumnTypes support reuse of DataColumns over multiple DataSets
    by abstracting their information.
    """
    serializer_class = DataColumnTypeSerializer
    filterset_fields = ['name', 'unit__symbol', 'unit__name', 'is_default']
    search_fields = ['@name', '@description']
    queryset = DataColumnType.objects.all().order_by('id')


@extend_schema_view(
    list=extend_schema(
        summary="View Columns to which you have access",
        description="""
Column instances link Column Types to the TimeseriesData they contain.
You can access any Column in any Dataset to which you have access.

Searchable fields:
- dataset__name
- type__name (Column Type name)
        """
    ),
    retrieve=extend_schema(
        summary="View a Column",
        description="""
Column instances link Column Types to the TimeseriesData they contain.

Searchable fields:
- dataset__name
- type__name (Column Type name)
        """
    ),
    data=extend_schema(
        summary="View Column data",
        description="""
View the TimeseriesData contents of the Column.

Data are presented as a dictionary of observations where keys are row numbers and values are observation values.

Can be filtered with querystring parameters `min` and `max`, and `mod` (modulo) by specifying a sample number.
        """
    ),
    data_listformat=extend_schema(
        summary="View Column data as a list",
        description="""
View the TimeseriesData contents of the Column as a list.

Data are presented as a list of observation values ordered by row number.

Can be filtered with querystring parameters `min` and `max`, and `mod` (modulo) by specifying a sample number.
        """
    )
)
class DataColumnViewSet(viewsets.ReadOnlyModelViewSet):
    """
    DataColumns describe which columns are in a Dataset's data.
    """
    serializer_class = DataColumnSerializer
    filterset_fields = ['dataset__name', 'type__unit__symbol', 'dataset__id', 'type__id', 'type__name']
    search_fields = ['@dataset__name', '@type__name']
    queryset = DataColumn.objects.none().order_by('-dataset_id', '-id')

    def get_queryset(self):
        datasets_ids = [d.id for d in Dataset.objects.filter(
            Q(file__monitored_path__user_group__in=self.request.user.groups.all()) |
            Q(file__monitored_path__admin_group__in=self.request.user.groups.all()) |
            Q(file__monitored_path__harvester__admin_group__in=self.request.user.groups.all())
        ).only('id')]
        return DataColumn.objects.filter(dataset_id__in=datasets_ids).order_by('-dataset_id', '-id')

    @action(methods=['GET'], detail=True)
    def values(self, request, pk: int = None):
        """
        Fetch the data for this column in an 'observations' dictionary of record_id: observed_value pairs.
        """
        column = get_object_or_404(DataColumn, id=pk)
        self.check_object_permissions(self.request, column)
        handlers = [TimeseriesDataFloat, TimeseriesDataInt, TimeseriesDataStr]
        for handler in handlers:
            if handler.objects.filter(column=column).exists():
                values = handler.objects.get(column=column).values
                # Handle querystring parameters
                if 'min' in request.query_params:
                    values = values[int(request.query_params['min']):]
                if 'max' in request.query_params:
                    values = values[:int(request.query_params['max'])]
                if 'mod' in request.query_params:
                    values = values[::int(request.query_params['mod'])]

                print(len(values))
                def stream():
                    for v in values:
                        print(f"{column.name}: yeilding {v}")
                        yield v
                return StreamingHttpResponse(stream())
        return error_response('No data found for this column.', 404)


@extend_schema_view(
    list=extend_schema(
        summary="View time-series range labels to which you have access",
        description="""
Labels marking blocks of contiguous time series data.

Searchable fields:
- label
        """
    ),
    retrieve=extend_schema(
        summary="View a specific label.",
        description="""
Labels marking blocks of contiguous time series data.
        """
    ),
    create=extend_schema(
        summary="Create a label.",
        description="""
Create a label with a description.
        """
    ),
    destroy=extend_schema(
        summary="Delete a label.",
        description="""
RangeLabels not used in any Dataset may be deleted.
        """
    )
)
class TimeseriesRangeLabelViewSet(viewsets.ModelViewSet):
    """
    TimeseriesRangeLabels mark contiguous observations using start and endpoints.
    """
    serializer_class = TimeseriesRangeLabelSerializer
    queryset = TimeseriesRangeLabel.objects.all().order_by('id')
    filterset_fields = ['label', 'info']
    search_fields = ['@label']
    http_method_names = ['get', 'post', 'patch', 'delete', 'options']


@extend_schema_view(
    list=extend_schema(
        summary="View Users awaiting approval",
        description="""
Users can be created freely, but cannot use the API until they are approved by an existing user account.
        """
    ),
    retrieve=extend_schema(
        summary="View a User awaiting approval",
        description="""
Users can be created freely, but cannot use the API until they are approved by an existing user account.
        """
    ),
    create=extend_schema(
        summary="Create a new User account",
        description="""
Users can be created freely, but cannot use the API until they are approved by an existing user account.
        """
    ),
    vouch_for=extend_schema(
        summary="Approve a User awaiting activation",
        description="""
Approving a User will allow them to access the API. A record will be kept of the approval.
        """
    )
)
class InactiveViewSet(viewsets.ModelViewSet):
    """
    Users are Django User instances custom-serialized for convenience.

    New users can be created at will, but they will be marked as is_active=False
    until vouched for by an existing active user.
    """
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=False).order_by('-id')
    http_method_names = ['get', 'post', 'options']

    def create(self, request, *args, **kwargs):
        # TODO: Move to serializer so only wanted fields appear in Django web form?
        try:
            username = request.data['username']
            email = validators.validate_email(request.data['email'])
            password = request.data['password']
        except (KeyError, validators.ValidationError):
            return error_response(f"Username, email, and password fields required.")
        if len(password) < 8:
            return error_response(f"Password must be at least 8 characters long")
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
            self.check_object_permissions(self.request, new_user)
        except User.DoesNotExist:
            return error_response(f"User not found")
        VouchFor.objects.create(new_user=new_user, vouching_user=request.user)
        new_user.is_active = True
        new_user.save()
        return Response(UserSerializer(new_user, context={'request': request}).data)


@extend_schema_view(
    partial_update=extend_schema(
        summary="Update User profile",
        description="""
Your User profile can be updated. You may change your email address and password.
All changes require your current password to be accepted.
        """,
        request=inline_serializer('UserUpdate', {
            'email': serializers.EmailField(help_text="Your updated email"),
            'password': serializers.CharField(help_text="Your new password"),
            'currentPassword': serializers.CharField(help_text="Your current password", required=True)
        }),
        responses={
            200: UserSerializer,
            401: ErrorSerializer,
            404: ErrorSerializer
        }
    )
)
class UserViewSet(viewsets.ModelViewSet):
    """
    Users are Django User instances custom-serialized for convenience.
    """
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)
    http_method_names = ['get', 'patch', 'options']

    def partial_update(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs.get('pk'))
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
            return error_response("Password must be at least 8 characters long")
        current_password = request.data.get('currentPassword')
        if not user.check_password(current_password):
            return error_response("You must include the correct current password", 401)
        if email:
            user.email = email
        if password:
            user.set_password(password)
        user.save()
        return Response(UserSerializer(user, context={'request': request}).data)


GroupUpdateSerializer = inline_serializer('GroupUpdateSerializer', {
    'user': serializers.CharField(help_text="Canonical URL of User to add")
})


@extend_schema_view(
    add=extend_schema(
        description='Add a user to a group',
        request=GroupUpdateSerializer
    ),
    remove=extend_schema(
        request=GroupUpdateSerializer,
        description="Remove a user from a group."
    )
)
class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Groups are Django Group instances custom-serialized for convenience.
    """
    serializer_class = GroupSerializer
    queryset = Group.objects.none().order_by('-id')
    http_method_names = ['post']

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
            self.check_object_permissions(self.request, group)
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
            self.check_object_permissions(self.request, group)
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
