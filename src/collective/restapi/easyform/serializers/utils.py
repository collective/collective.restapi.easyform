# -*- coding: utf-8 -*-
from plone.restapi.types.utils import get_form_fieldsets, iter_fields, get_jsonschema_properties, get_fieldset_infos
from collective.easyform.api import get_schema
from zope.globalrequest import getRequest
from zope.component import queryMultiAdapter
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import IJsonCompatible
from collections import OrderedDict
from plone.restapi.types.interfaces import IJsonSchemaProvider
from zope.component import getMultiAdapter

def get_field_value(field, excluded_fields, form, request, prefix):
    fieldname = field.__name__
    if fieldname not in excluded_fields:

        adapter = queryMultiAdapter(
            (field, form, request),
            interface=IJsonSchemaProvider,
            name=field.__name__,
        )

        if adapter is None:
            adapter = queryMultiAdapter(
                (field, form, request), interface=IJsonSchemaProvider
            )

        adapter.prefix = prefix
        if prefix:
            fieldname = ".".join([prefix, fieldname])

        return adapter.get_schema()




def get_json_schema_for_form_contents(context, request, prefix="", excluded_fields=None):
    view = getMultiAdapter((context, request), name='view')
    formview = view.form(context, request)
    formview.update()
    fieldsets = get_form_fieldsets(formview)
    # Build JSON schema properties
    properties = get_jsonschema_properties(
        context, request, fieldsets, excluded_fields=excluded_fields
    )

    # Determine required fields
    required = []
    for field in iter_fields(fieldsets):
        if field.field.required:
            required.append(field.field.getName())

    # Include field modes
    for field in iter_fields(fieldsets):
        if field.mode:
            properties[field.field.getName()]["mode"] = field.mode

    return {
        "type": "object",
        "title": context.Title(),
        "properties": IJsonCompatible(properties),
        "required": required,
        "fieldsets": get_fieldset_infos(fieldsets),
        "description": get_serialized_version_of(context, "description"),
        "formPrologue": get_serialized_version_of(context, "formPrologue"),
        "formEpilogue": get_serialized_version_of(context, "formEpilogue"),

    }


def get_serialized_version_of(context, fieldname):
    request = getRequest()
    field = context.get(fieldname)
    serializer = queryMultiAdapter((field, context, request), IFieldSerializer)
    if serializer is not None:
        return serializer()
    return None
