# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

from django.db.models import Q
from rest_framework import permissions
from .models import Harvester, MonitoredPath


class HarvesterAccess(permissions.BasePermission):
    """
    Object-level permission to only allow Harvester to edit its own attributes.
    """
    message = "Invalid AUTHORIZATION header. Required 'Harvester [api_key]' or 'Bearer [api_token]'."

    endpoints = ['config', 'report']

    def has_object_permission(self, request, view, obj):
        if view.action in self.endpoints:
            return obj.id == int(view.kwargs['pk']) and \
                   request.META.get('HTTP_AUTHORIZATION', '') == f"Harvester {obj.api_key}"
        # /harvesters/ returns all harvesters because their envvars are redacted
        if view.action == 'list' and request.method == 'GET':
            return True
        # Read/write detail test
        user_groups = request.user.groups.all()
        # Allow access to Harvesters where we have a Path
        path_harvesters = [p.harvester.id for p in MonitoredPath.objects.filter(
            Q(user_group__in=user_groups) | Q(admin_group__in=user_groups)
        )]
        user_harvesters = Harvester.objects.filter(
            Q(user_group__in=user_groups) |
            Q(id__in=path_harvesters)
        )
        admin_harvesters = Harvester.objects.filter(admin_group__in=user_groups)
        if request.method in permissions.SAFE_METHODS:
            return obj in user_harvesters or obj in admin_harvesters
        return obj in admin_harvesters


class ReadOnlyIfInUse(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return not obj.in_use()
