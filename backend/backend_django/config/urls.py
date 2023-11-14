# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

"""backend_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import routers
from galv import views

router = routers.DefaultRouter()

router.register(r'labs', views.LabViewSet)
router.register(r'teams', views.TeamViewSet)
router.register(r'harvesters', views.HarvesterViewSet)
router.register(r'harvest_errors', views.HarvestErrorViewSet)
router.register(r'monitored_paths', views.MonitoredPathViewSet)
router.register(r'files', views.ObservedFileViewSet)
router.register(r'columns', views.DataColumnViewSet)
router.register(r'column_types', views.DataColumnTypeViewSet)
router.register(r'units', views.DataUnitViewSet)
router.register(r'cell_families', views.CellFamilyViewSet)
router.register(r'cells', views.CellViewSet)
router.register(r'equipment_families', views.EquipmentFamilyViewSet)
router.register(r'equipment', views.EquipmentViewSet)
router.register(r'schedule_families', views.ScheduleFamilyViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'cycler_tests', views.CyclerTestViewSet)
router.register(r'experiments', views.ExperimentViewSet)
router.register(r'validation_schemas', views.ValidationSchemaViewSet)
router.register(r'schema_validations', views.SchemaValidationViewSet)
router.register(r'users', views.UserViewSet, basename='userproxy')
router.register(r'tokens', views.TokenViewSet, basename='tokens')
router.register(r'groups', views.GroupViewSet, basename='groupproxy')
router.register(r'equipment_types', views.EquipmentTypesViewSet)
router.register(r'equipment_models', views.EquipmentModelsViewSet)
router.register(r'equipment_manufacturers', views.EquipmentManufacturersViewSet)
router.register(r'cell_models', views.CellModelsViewSet)
router.register(r'cell_manufacturers', views.CellManufacturersViewSet)
router.register(r'cell_chemistries', views.CellChemistriesViewSet)
router.register(r'cell_form_factors', views.CellFormFactorsViewSet)
router.register(r'schedule_identifiers', views.ScheduleIdentifiersViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    # path('data/{pk}/', views.TimeseriesDataViewSet.as_view({'get': 'detail'}), name='timeseriesdata-detail'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'login/', views.LoginView.as_view(), name='knox_login'),
    path(r'logout/', views.LogoutView.as_view(), name='knox_logout'),
    path(r'logoutall/', views.LogoutAllView.as_view(), name='knox_logoutall'),
    path(r'create_token/', views.CreateTokenView.as_view(), name='knox_create_token'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
pass
