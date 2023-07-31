# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import os
import uuid

from django.db import models

LD_SOURCE_MAP = {
    "schema": "https://schema.org/",
    "emmo": "https://github.com/emmo-repo/EMMO/blob/master/emmo.ttl",
    "battinfo": "https://github.com/emmo-repo/domain-battery/blob/master/battery.ttl"
}


class LDSources(models.TextChoices):
    SCHEMA = "schema"
    EMMO = "emmo"
    BattINFO = "battinfo"


def get_namespace():
    namespace = os.environ.get('VIRTUAL_HOST_ROOT')
    if namespace is None:
        raise ValueError("VIRTUAL_HOST_ROOT environment variable must be set")
    return namespace



class UUIDFieldLD(models.UUIDField):
    def __init__(self, **kwargs):
        super().__init__(**{
            'default': uuid.uuid4,
            'editable': False,
            'primary_key': True,
            'unique': True,
            'null': False,
            **kwargs
        })
        self.namespace = get_namespace()

    def as_id(self):
        return f"{self.namespace}{self.__str__()}"


class UUIDModel(models.Model):
    uuid = UUIDFieldLD()
    class Meta:
        abstract = True


class AdditionalPropertiesModel(UUIDModel):
    additional_properties = models.JSONField(null=False, default=dict)
    class Meta(UUIDModel.Meta):
        abstract = True


class JSONModel(AdditionalPropertiesModel):
    def __json_ld__(self):
        raise NotImplementedError((
            "JSONModel subclasses must implement __json_ld__, ",
            "returning a dict of JSON-LD representation. ",
            "Should include '@id' and '@type' field, and triples where this model is the source node. ",
            "@id can be generated using self.uuid.as_id(). ",
            "LDSources.* can be used to reference known sources, and any used should be included"
            "in the '_context' field as a simple list."
        ))

    class Meta(AdditionalPropertiesModel.Meta):
        abstract = True


class AutoCompleteEntry(models.Model):
    value = models.TextField(null=False, unique=True)
    ld_value = models.TextField(null=True, unique=False, blank=True)
    include_in_autocomplete = models.BooleanField(default=True)

    def __str__(self):
        return self.value

    class Meta:
        abstract = True
