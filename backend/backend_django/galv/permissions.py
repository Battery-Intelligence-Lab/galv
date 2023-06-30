# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

from django.urls import resolve
from urllib.parse import urlparse
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


class MonitoredPathAccess(permissions.BasePermission):
    """
    MonitoredPaths can be read by users in the user_group or admin_group.
    MonitoredPaths can be edited by users in the admin_group.

    MonitoredPaths can be created by users in the harvester's user_group and admin_group.
    """
    def has_object_permission(self, request, view, obj):
        user_groups = request.user.groups.all()
        if request.method in permissions.SAFE_METHODS:
            return obj.user_group in user_groups or obj.admin_group in user_groups
        return obj.admin_group in user_groups

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user_groups = request.user.groups.all()
        if view.action == 'create':
            harvester_id = resolve(urlparse(request.data.get('harvester')).path).kwargs.get('pk')
            harvester = Harvester.objects.get(id=harvester_id)
            return harvester.user_group in user_groups or harvester.admin_group in user_groups
        return True


class ReadOnlyIfInUse(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return not obj.in_use()
