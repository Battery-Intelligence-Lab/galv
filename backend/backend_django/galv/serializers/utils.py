import json
from collections import OrderedDict

import django.db.models
from drf_spectacular.utils import extend_schema_field
from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError

from galv.models import ValidationSchema, GroupProxy, UserProxy, user_teams, VALIDATION_MOCK_ENDPOINT
from rest_framework.fields import DictField


url_help_text = "Canonical URL for this object"

OUTPUT_STYLE_FLAT = 'flat'
OUTPUT_STYLE_CONTEXT = 'context'

def get_output_style(request):
    if request.path == VALIDATION_MOCK_ENDPOINT:
        return OUTPUT_STYLE_FLAT
    if request.query_params.get('style') in [OUTPUT_STYLE_FLAT, OUTPUT_STYLE_CONTEXT]:
        return request.query_params['style']
    if 'html' in request.accepted_media_type or request.query_params.get('format') == 'html':
        return OUTPUT_STYLE_CONTEXT
    return OUTPUT_STYLE_FLAT

def serializer_class_from_string(class_name: str):
    """
    Get a class from a string.
    """
    if class_name not in [
        'UserSerializer', 'GroupSerializer', 'LabSerializer', 'TeamSerializer', 'HarvesterSerializer',
        'HarvestErrorSerializer', 'MonitoredPathSerializer', 'ObservedFileSerializer', 'DataColumnSerializer',
        'DataColumnTypeSerializer', 'DataUnitSerializer', 'CellFamilySerializer', 'CellSerializer',
        'EquipmentFamilySerializer', 'EquipmentSerializer', 'ScheduleFamilySerializer', 'ScheduleSerializer',
        'CyclerTestSerializer', 'ExperimentSerializer', 'ValidationSchemaSerializer', 'EquipmentTypesSerializer',
        'EquipmentModelsSerializer', 'EquipmentManufacturersSerializer', 'CellModelsSerializer',
        'CellManufacturersSerializer', 'CellChemistriesSerializer', 'CellFormFactorsSerializer',
        'ScheduleIdentifiersSerializer'
    ]:
        raise ValueError(f"serializer_class_from_string will only retrieve custom Serializers, not {class_name}")
    s = __import__('galv.serializers', fromlist=[class_name])
    return getattr(s, class_name)

class CreateOnlyMixin(serializers.ModelSerializer):
    """
    A Serializer that supports create_only fields.
    create_only fields will be marked as 'read_only' if the view.action is not 'create'.
    Otherwise, they will retain their original keywords such as 'required' and 'allow_null'.
    """
    def get_extra_kwargs(self):
        extra_kwargs_for_edit = super().get_extra_kwargs()
        if "view" not in self.context or self.context['view'].action != 'create':
            for field_name in extra_kwargs_for_edit:
                kwargs = extra_kwargs_for_edit.get(field_name, {})
                kwargs['read_only'] = True
                extra_kwargs_for_edit[field_name] = kwargs

        return extra_kwargs_for_edit


def augment_extra_kwargs(extra_kwargs: dict[str, dict] = None):
    def _augment(name: str, content: dict):
        if name == 'url':
            return {'help_text': url_help_text, 'read_only': True, **content}
        if name in ['id', 'uuid']:
            return {'help_text': "Auto-assigned object identifier", 'read_only': True, **content}
        return {**content}

    if extra_kwargs is None:
        extra_kwargs = {}
    extra_kwargs = {'url': {}, 'id': {}, **extra_kwargs}
    return {k: _augment(k, v) for k, v in extra_kwargs.items()}


def get_model_field(model: django.db.models.Model, field_name: str) -> django.db.models.Field:
    """
    Get a field from a Model.
    Works, but generates type warnings because Django uses hidden Metaclass ModelBase for models.
    """
    fields = {f.name: f for f in model._meta.fields}
    return fields[field_name]


class GetOrCreateTextSerializer(serializers.HyperlinkedModelSerializer):
    """
    Expose a full AutoCompleteEntry model.
    """
    def __init__(self, model):
        super().__init__()
        self.Meta.model = model

    class Meta:
        model = None
        fields = ['url', 'id', 'value', 'ld_value']


class GetOrCreateTextStringSerializer(serializers.ModelSerializer):
    """
    For use with AutoCompleteEntry models: Simply returns the value field. Read-only.
    """
    def to_representation(self, instance):
        if get_output_style(self.context['request']) != OUTPUT_STYLE_CONTEXT:
            return super().to_representation(instance)
        return instance.value

    def to_internal_value(self, data):
        raise RuntimeError("GetOrCreateTextStringSerializer is read-only")

    class Meta:
        fields = '__all__'

def get_GetOrCreateTextStringSerializer(django_model):
    """
    Return a concrete child class for GetOrCreateTextStringSerializer linking it to a model.
    """
    return type(
        f"{django_model.__name__}TextSerializer",
        (GetOrCreateTextStringSerializer,),
        {
            'Meta': type('Meta', (GetOrCreateTextStringSerializer.Meta,), {'model': django_model})
        })

class GetOrCreateTextField(serializers.CharField):
    """
    A CharField that will create a new object if it does not exist.
    Objects are created with the value of the CharField in the table specified by `foreign_model`.

    The model field must be a ForeignKey to the table specified by `foreign_model`,
    and the latter will typically be an AutoCompleteEntry model.

    If the table uses a different field name for the value, specify it with `foreign_model_field`.
    """
    def __init__(self, foreign_model, foreign_model_field: str = 'value', **kwargs):
        super().__init__(**kwargs)
        self.foreign_model = foreign_model
        self.foreign_model_field = foreign_model_field

    def to_internal_value(self, data):
        # Let CharField do the basic validation
        data = super().to_internal_value(data)
        return self.foreign_model.objects.get_or_create(**{self.foreign_model_field: data})[0]
    def to_representation(self, value):
        return getattr(value, self.foreign_model_field)


class GetOrCreateTextFieldList(serializers.ListField):
    """
    Adaptation of serializers.ListField to use GetOrCreateTextField.
    Solves 'ManyRelatedManager is not iterable' error.

    Use to support ManyToMany relationships with AutoCompleteEntry models.
    """
    def to_representation(self, data):
        return super().to_representation(data.all())


class AdditionalPropertiesModelSerializer(serializers.HyperlinkedModelSerializer):
    """
    A ModelSerializer that maps unrecognised properties in the input to an 'additional_properties' JSONField,
    and unpacks the 'additional_properties' JSONField into the output.

    The Meta.model must have an additional_properties JSONField.
    """
    class Meta:
        model: django.db.models.Model
        include_additional_properties = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model_fields = {f.name for f in self.Meta.model._meta.fields}
        if 'additional_properties' not in model_fields:
            raise ValueError("AdditionalPropertiesModelSerializer must define additional_properties")

    def to_representation(self, instance):
        if hasattr(self.Meta, 'include_additional_properties') and not self.Meta.include_additional_properties:
            return super().to_representation(instance)
        data = {k: v for k, v in super().to_representation(instance).items() if k != 'additional_properties'}
        for k, v in instance.additional_properties.items():
            if k in data:
                raise ValueError(f"Basic model property '{k}' duplicated in additional_properties")
        return {**data, **instance.additional_properties}

    def to_internal_value(self, data):
        new_data = {'additional_properties': {}}
        for k, v in data.items():
            if k not in self.fields or k == 'additional_properties':
                if k in ['csrfmiddlewaretoken']:
                    continue
                try:
                    json.dumps(v)
                except BaseException:
                    raise ValidationError(f"Value {v} for key {k} is not JSON serializable")
                new_data['additional_properties'][k] = v

        leftover_data = {k: v for k, v in data.items() if k not in new_data['additional_properties']}

        # Let the superclass do the rest
        new_data = {**new_data, **super().to_internal_value(leftover_data)}
        return new_data


@extend_schema_field({
        'type': 'object',
        'properties': {
            'read': {'type': 'boolean'},
            'write': {'type': 'boolean'},
            'create': {'type': 'boolean'},
        }
    })
class DRYPermissionsFieldWrapper(DRYPermissionsField):
    pass

class PermissionsMixin(serializers.Serializer):
    permissions: DictField = DRYPermissionsFieldWrapper()


class GroupProxyField(serializers.Field):
    """
    Fetch proxied User/Group objects.
    """
    def to_internal_value(self, data):
        target = super().to_internal_value(data)
        target.__class__ = GroupProxy
        return target

class UserProxyField(serializers.Field):
    """
    Fetch proxied User/Group objects.
    """
    def to_internal_value(self, data):
        target = super().to_internal_value(data)
        target.__class__ = UserProxy
        return target


class HyperlinkedRelatedIdField(serializers.HyperlinkedRelatedField):
    """
    A HyperlinkedRelatedField that can be written to more flexibly.
    Lookup priority is, in order:
    A string or integer primary key value
    An object with a 'pk', 'id', or 'uuid' property
    An object with a 'url' property
    A URL string
    """
    def to_internal_value(self, data):
        if isinstance(data, dict):
            if 'pk' in data:
                data = data['pk']
            elif 'id' in data:
                data = data['id']
            elif 'uuid' in data:
                data = data['uuid']
            elif 'url' in data:
                data = data['url']
            else:
                raise ValidationError("Object must have a 'pk', 'id', 'uuid', or 'url' property")
        elif isinstance(data, str):
            # Try to parse as an integer, but don't fail if it's not because uuids are stringy
            try:
                data = int(data)
            except ValueError:
                pass
        try:
            return self.get_queryset().get(pk=data)
        except (TypeError, ValueError, DjangoValidationError, self.queryset.model.DoesNotExist):
            return super().to_internal_value(data)

    def to_representation(self, value):
        return super().to_representation(value)

class GroupHyperlinkedRelatedIdListField(HyperlinkedRelatedIdField, GroupProxyField):
    pass

class UserHyperlinkedRelatedIdListField(HyperlinkedRelatedIdField, UserProxyField):
    pass

class TruncatedHyperlinkedRelatedIdField(HyperlinkedRelatedIdField):
    """
    A HyperlinkedRelatedField that reads as a truncated representation of the target object,
    and writes as the target object's URL.

    The 'url' and '[id|uuid]' fields are always included.
    Other fields are specified by the 'fields' argument to the constructor.
    """
    def __init__(self, child_serializer_class, fields, *args, **kwargs):
        self.child_serializer_class = child_serializer_class
        if isinstance(fields, str):
            fields = [fields]
        if not isinstance(fields, list):
            raise ValueError("fields must be a list")
        self.child_fields = fields
        # Support create_only=True by removing queryset and applying read_only=True
        self.create_only = kwargs.pop('create_only', False)
        super().__init__(*args, **kwargs)

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        if self.create_only and 'view' in self.context and self.context['view'].action != 'create':
            self.read_only = True
            self.queryset = None

    def to_representation(self, instance):
        try:
            if get_output_style(self.context['request']) != OUTPUT_STYLE_CONTEXT:
                return super().to_representation(instance)
        except (AttributeError, KeyError):
            pass
        if isinstance(self.child_serializer_class, str):
            child = serializer_class_from_string(self.child_serializer_class)
            self.child_serializer_class = child  # cache result
        else:
            child = self.child_serializer_class
        fields = list({
            *[f for f in self.child_serializer_class.Meta.fields if f in ['url', 'id', 'uuid']],# 'permissions']],
            *self.child_fields
        })

        class TruncatedSerializer(child):
            def __init__(self, obj, include_fields, *args, **kwargs):
                self.Meta.fields = include_fields
                self.Meta.read_only_fields = include_fields
                super().__init__(obj, *args, **kwargs)
            class Meta(child.Meta):
                include_additional_properties = False
                include_validation = False

        serializer = TruncatedSerializer(instance, fields, context=self.context)
        return serializer.data

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            # Ensure that field.choices returns something sensible
            # even when accessed with a read-only field.
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return OrderedDict([
            (
                item.pk,
                self.display_value(item)
            )
            for item in queryset
        ])

    def use_pk_only_optimization(self):
        return False


class TruncatedGroupHyperlinkedRelatedIdField(TruncatedHyperlinkedRelatedIdField, GroupProxyField):
    def to_representation(self, instance):
        instance.__class__ = GroupProxy
        return super().to_representation(instance)

class TruncatedUserHyperlinkedRelatedIdField(TruncatedHyperlinkedRelatedIdField, UserProxyField):
    def to_representation(self, instance):
        instance.__class__ = UserProxy
        return super().to_representation(instance)


class ValidationPresentationMixin(serializers.Serializer):
    """
    Resources with families perform inline expansion of family properties during validation.
    """
    def to_representation(self, instance):
        try:
            if self.context['request'].path == VALIDATION_MOCK_ENDPOINT and hasattr(instance, 'family'):
                representation = super().to_representation(instance)
                family_serializer = self.fields['family'].child_serializer_class
                if isinstance(family_serializer, str):
                    family_serializer = serializer_class_from_string(family_serializer)
                representation.pop('family')
                return {**family_serializer(instance.family, context=self.context).data, **representation}
        except Exception as e:
            print(e)
            pass
        return super().to_representation(instance)
