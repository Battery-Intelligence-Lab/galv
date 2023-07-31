import json
import django.db.models
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


url_help_text = "Canonical URL for this object"


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
        return instance.value

    def to_internal_value(self, data):
        raise RuntimeError("GetOrCreateTextStringSerializer is read-only")


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
    additional_properties = serializers.JSONField(required=False, write_only=True, source='additional_properties')

    class Meta:
        model: django.db.models.Model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model_fields = {f.name for f in self.Meta.model._meta.fields}
        if 'additional_properties' not in model_fields:
            raise ValueError("AdditionalPropertiesModelSerializer must define additional_properties")

    def to_representation(self, instance):
        data = {k: v for k, v in super().to_representation(instance).items() if k != 'additional_properties'}
        for k, v in instance.additional_properties.items():
            if k in data:
                raise ValueError(f"Basic model property {k} duplicated in _additional_properties")
        return {**data, **instance.additional_properties}

    def to_internal_value(self, data):
        if "additional_properties" in data:
            new_data = {'additional_properties': {'additional_properties': data.pop('additional_properties')}}
        else:
            new_data = {'additional_properties': {}}
        for k, v in data.items():
            if k not in self.fields:
                if k in ['csrfmiddlewaretoken']:
                    continue
                try:
                    json.dumps(v)
                except BaseException:
                    raise ValidationError(f"Value {v} for key {k} is not JSON serializable")
                new_data['additional_properties'][k] = v
            else:
                new_data[k] = self.fields[k].to_internal_value(v)
        return new_data
