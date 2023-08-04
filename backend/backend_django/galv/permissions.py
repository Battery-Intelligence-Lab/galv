# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
from django.http import Http404
from django.urls import resolve, Resolver404
from urllib.parse import urlparse
from django.db.models import Q
from rest_framework import permissions
from .models import Harvester, MonitoredPath
from .utils import get_monitored_paths


class HarvesterAccess(permissions.BasePermission):
    """
    Object-level permission to only allow Harvester to edit its own attributes.
    """
    message = "Invalid AUTHORIZATION header. Required 'Harvester [api_key]' or 'Bearer [api_token]'."

    endpoints = ['config', 'report']

    def has_object_permission(self, request, view, obj):
        if view.action in self.endpoints:
            return str(obj.uuid) == view.kwargs['pk'] and \
                   request.META.get('HTTP_AUTHORIZATION', '') == f"Harvester {obj.api_key}"

        user_groups = request.user.groups.all()
        if request.method in permissions.SAFE_METHODS:
            return obj.user_group in user_groups or obj.admin_group in user_groups
        return obj.admin_group in user_groups


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
        if view.action == 'create' and request.data.get('harvester') is not None:
            try:
                harvester_uuid = resolve(urlparse(request.data.get('harvester')).path).kwargs.get('pk')
            except Resolver404:
                # raise Http404(f"Invalid harvester URL '{request.data.get('harvester')}'")
                return False
            harvester = Harvester.objects.get(uuid=harvester_uuid)
            # Allow harvesters to create MonitoredPaths for themselves
            if request.META.get('HTTP_AUTHORIZATION', '') == f"Harvester {harvester.api_key}":
                return True
            # Allow users in the harvester's user_group or admin_group to create MonitoredPaths
            user_groups = request.user.groups.all()
            return harvester.user_group in user_groups or harvester.admin_group in user_groups
        return True


class ObservedFileAccess(permissions.BasePermission):
    """
    Object-level permission to allow or deny access to a MonitoredPath based on ObservedFile path.
    """
    def has_object_permission(self, request, view, obj):
        paths = get_monitored_paths(obj.path, obj.harvester)
        for path in paths:
            if path.user_group in request.user.groups.all() or path.admin_group in request.user.groups.all():
                return True
        return False


class VicariousObservedFileAccess(permissions.BasePermission):
    """
    Object-level permission to allow or deny access to a MonitoredPath based on an object's ObservedFile.
    """
    def has_object_permission(self, request, view, obj):
        return ObservedFileAccess().has_object_permission(request, view, obj.file)


class ReadOnlyIfInUse(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return not obj.in_use()
