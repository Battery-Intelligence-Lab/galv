from rest_framework import permissions
from .models import Harvester


class HarvesterAccess(permissions.BasePermission):
    """
    Object-level permission to only allow Harvester to edit its own attributes.
    """
    message = "Invalid AUTHORIZATION header. Required 'Harvester [api_key]'."

    endpoints = ['config', 'report']

    def has_permission(self, request, view):
        if view.action in self.endpoints:
            try:
                harvester = Harvester.objects.get(id=view.kwargs['pk'])
                key = request.META.get('HTTP_AUTHORIZATION', '')
                key = key[len('Harvester '):]
                return key == harvester.api_key
            except (Harvester.DoesNotExist, AttributeError, TypeError, ValueError):
                return False

        return True
