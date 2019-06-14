import json

from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
from property.models import Property


class PropertyJSONRenderer(JSONRenderer):
    """Properly render the responses for property views.
    Note that errors are not handled by the renderer but instead
    handled by default DRF exception handlers."""
    charset = 'utf-8'

    def single_property_format(self, data):
        """When returning property, fields choices should be returned as human readable values.
        For example, instead or returning `purchase_plan` as `I`, we should return `Installments`"""

        # We should only format responses. Because reqeusts don't have the `id` we skip all requests
        if data.get('id'):
            instance = Property.objects.get(pk=data.get('id'))
            data['property_type'] = instance.get_property_type_display().title()
            data['purchase_plan'] = instance.get_purchase_plan_display().title()
            client = instance.client
            client_data = {
                'client_name': client.client_name,
                'phone': client.phone,
                'email': client.email,
                'address': client.address
            }
            data['client'] = client_data

    def render(self, data, media_type=None, renderer_context=None):
        if isinstance(data, dict):
            errors = data.get('errors')

            if errors:
                return super().render(data)

            if renderer_context and renderer_context['request'].method == 'PATCH':
                self.single_property_format(data)
                return json.dumps({
                    'data': {'property': data,
                             'message': 'Successfully updated your property.'}
                })

            if type(data) == ReturnDict:
                self.single_property_format(data)
                return json.dumps({
                    'data': {'property': data}
                })

            results = data.get('results')

            # when getting multiple items, the actual payload is contained in the
            # `results` key because they will be paginated
            if isinstance(results, list):
                for item in results:
                    self.single_property_format(item)
                return json.dumps({
                    'data': {'properties': data}
                })

        return json.dumps({
            'data': {'property': data}
        })
