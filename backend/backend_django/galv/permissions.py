# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
from django.db import models
from django.http import Http404
from django.urls import resolve, Resolver404
from urllib.parse import urlparse
from django.db.models import Q
from dry_rest_permissions.generics import DRYPermissionFiltersBase
from rest_framework import permissions
from .models import Harvester, MonitoredPath, user_labs, user_teams, ObservedFile, UserProxy, user_is_lab_admin
from .utils import get_monitored_paths

class HarvesterFilterBackend(DRYPermissionFiltersBase):
    action_routing = True

    def filter_list_queryset(self, request, queryset, view):
        key = request.META.get('HTTP_AUTHORIZATION', '')
        if key.startswith('Harvester '):
            return queryset.filter(api_key=key.split(' ')[1])
        labs = user_labs(request.user)
        if len(labs) == 0:
            return queryset.none()
        return queryset.filter(lab__in=labs)

    # def filter_config_queryset(self, request, queryset, view):
    #     key = request.META.get('HTTP_AUTHORIZATION', '')
    #     if key.startswith('Harvester '):
    #         return queryset.filter(api_key=key.split(' ')[1])
    #     return queryset.none()
    #
    # def filter_report_queryset(self, request, queryset, view):
    #     return self.filter_config_queryset(request, queryset, view)

class LabFilterBackend(DRYPermissionFiltersBase):
    action_routing = True
    def filter_list_queryset(self, request, queryset, view):
        labs = [l.pk for l in user_labs(request.user)]
        if len(labs) == 0:
            return queryset.none()
        return queryset.filter(pk__in=labs)

class TeamFilterBackend(DRYPermissionFiltersBase):
    action_routing = True
    def filter_list_queryset(self, request, queryset, view):
        teams = [t.pk for t in user_teams(request.user)]
        return queryset.filter(Q(pk__in=teams)|Q(lab__in=user_labs(request.user, True)))

class GroupFilterBackend(DRYPermissionFiltersBase):
    action_routing = True
    def filter_list_queryset(self, request, queryset, view):
        if request.user.is_superuser or request.user.is_staff:
            return queryset
        teams = user_teams(request.user)
        labs = user_labs(request.user)
        return queryset.filter(Q(editable_lab__in=labs) | Q(editable_team__in=teams) | Q(readable_team__in=teams))

class UserFilterBackend(DRYPermissionFiltersBase):
    action_routing = True
    def filter_list_queryset(self, request, queryset, view):
        if request.user.is_superuser or request.user.is_staff or user_is_lab_admin(request.user):
            return queryset
        labs = user_labs(request.user)
        all_users = UserProxy.objects.all()
        users_to_return = []
        for user in all_users:
            for lab in user_labs(user):
                if lab in labs:
                    users_to_return.append(user)
                    break
        return queryset.filter(pk__in=[u.pk for u in users_to_return])


class ObservedFileFilterBackend(DRYPermissionFiltersBase):
    action_routing = True
    def filter_list_queryset(self, request, queryset, view):
        files = ObservedFile.objects.filter(harvester__lab__in=user_labs(request.user))
        paths = MonitoredPath.objects.filter(team__in=user_teams(request.user))
        file_ids = []
        # Not sure there's a good way around checking every file against every path
        for file in files:
            for path in paths:
                if path.harvester == file.harvester and path.matches(file.path):
                    file_ids.append(file.pk)
                    break

        return queryset.filter(pk__in=file_ids)

class ResourceFilterBackend(DRYPermissionFiltersBase):
    action_routing = True
    def filter_list_queryset(self, request, queryset, view):
        labs = user_labs(request.user)
        user_approved = len(labs) > 0
        return queryset.filter(
            Q(team__in=user_teams(request.user)) |
            (Q(lab_members_can_read=True) & Q(team__lab__in=labs)) |
            (Q(any_user_can_read=True) & Q(any_user_can_read=user_approved)) |
            Q(anonymous_can_read=True)
        )

class SchemaValidationFilterBackend(ResourceFilterBackend):
    action_routing = True
    def filter_list_queryset(self, request, queryset, view):
        schemas = {q.schema for q in queryset}
        included_schemas = [s for s in schemas]
        for schema in schemas:
            if not schema.has_object_read_permission(request):
                included_schemas.remove(schema)
        return queryset.filter(schema__in=included_schemas)