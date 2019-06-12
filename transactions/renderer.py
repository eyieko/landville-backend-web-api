import json

from rest_framework.renderers import JSONRenderer


class AccountDetailsJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):

        if isinstance(data, dict):
            errors = data.get('errors', None)

            if errors:
                return super().render(data)

        return json.dumps({
            'data': {"account_detail(s)": data}
        })
