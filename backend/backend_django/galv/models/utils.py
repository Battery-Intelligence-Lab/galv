# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import os
import re
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
    namespace = os.environ.get('RDF_HOST_ROOT', os.environ.get('VIRTUAL_HOST_ROOT'))
    if namespace is None:
        raise ValueError("RDF_HOST_ROOT or VIRTUAL_HOST_ROOT environment variable must be set")
    return f"https://rdf.{namespace}/"



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


class UUIDModel(models.Model):
    uuid = UUIDFieldLD()

    class Meta:
        abstract = True


class AdditionalPropertiesModel(UUIDModel):
    additional_properties = models.JSONField(null=False, default=dict)
    class Meta(UUIDModel.Meta):
        abstract = True


def unpack_rdf(obj: dict) -> dict:
    """
    Unpack any RDF properties from a dictionary of properties
    """
    rdf_props = {}
    for k, v in obj.items():
        if isinstance(v, dict) and '@rdf-predicate-uri' in v and 'value' in v:
            rdf_props[v['@rdf-predicate-uri']] = v['value']
    return rdf_props


def combine_rdf_props(*args) -> dict:
    """
    Combine multiple dictionaries of RDF properties into a single dictionary
    """
    rdf_props = {"@context": []}
    for obj in args:
        for k, v in obj.items():
            if k == "_context":
                rdf_props["@context"] = [*rdf_props["@context"], *v]
            else:
                rdf_props[k] = v
    if len(rdf_props["@context"]) == 0:
        del rdf_props["@context"]
    return rdf_props

class JSONModel(AdditionalPropertiesModel):
    def __json_ld__(self) -> dict:
        # Complain if not implemented by subclass
        if not hasattr(self, '__json_ld__'):
            raise NotImplementedError((
                "JSONModel subclasses must implement __json_ld__, ",
                "returning a dict of JSON-LD representation. ",
                "Should include '@type' field, and triples where this model is the source node. ",
                "@id is automatically inserted using the UUID. ",
                "LDSources.* can be used to reference known sources, and any used should be included"
                "in the '_context' field as a simple list."
            ))
        # Unpack any RDF properties from the additional properties
        additional_properties = self.additional_properties.copy()
        return combine_rdf_props(
            {'@id': f"{get_namespace()}{str(self.uuid)}"},
            unpack_rdf(additional_properties)
        )

    class Meta(AdditionalPropertiesModel.Meta):
        abstract = True


class AutoCompleteEntry(models.Model):
    value = models.TextField(null=False, unique=True)
    ld_value = models.JSONField(null=True, unique=False, blank=True)
    include_in_autocomplete = models.BooleanField(default=True)

    def __str__(self):
        return self.value

    def __json_ld__(self):
        return self.ld_value or self.value

    class Meta:
        abstract = True


class ScheduleRenderError(ValueError):
    pass


def render_pybamm_schedule(schedule, cell, validate = True):
    """
    Return the PyBaMM representation of the schedule, with variables filled in.
    Variables are taken from the cell properties, cell family properties, and schedule variables (most preferred first).
    """
    if not schedule.family.pybamm_template:
        return None
    variables = {
        **(schedule.pybamm_schedule_variables or {}),
        **(cell.family.__dict__ or {}),
        **(cell.family.additional_properties or {}),
        **(cell.__dict__ or {}),
        **(cell.additional_properties or {})
    }
    rendered_schedule = [t.format(**variables) for t in schedule.family.pybamm_template]
    if validate:
        # TODO: validate the schedule properly

        # Check all filled values are numeric
        for v in schedule.family.pybamm_template_variable_names():
            if not isinstance(variables[v], (int, float)):
                if v in cell.additional_properties:
                    source = f"{str(cell)} (additional properties)"
                elif v in cell.__dict__:
                    source = cell
                elif v in cell.family.additional_properties:
                    source = f"{str(cell.family)} (additional properties)"
                elif v in cell.family.__dict__:
                    source = cell.family
                else:
                    source = "schedule variables"
                raise ScheduleRenderError(f"Schedule variable {v} is not numeric (got {variables[v]} from {source})")

        # Check that all variables have been filled in
        as_string = "\n".join(rendered_schedule)
        if re.search(r"\{([\w_]+)}", as_string):
            missing = re.findall(r"\{([\w_]+)}", as_string)
            raise ScheduleRenderError(f"Schedule variables {missing} not filled in")
    return rendered_schedule
