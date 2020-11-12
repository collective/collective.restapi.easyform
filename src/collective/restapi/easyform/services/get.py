# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from collective.restapi.easyform.serializers.utils import get_json_schema_for_form_contents

class EasyFormSchemaGet(Service):
    def reply(self):
        result = get_json_schema_for_form_contents(self.context, self.request)
        self.content_type = "application/json+schema"
        return result
