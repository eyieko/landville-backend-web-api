import json

from rest_framework.renderers import JSONRenderer


class UserJSONRenderer(JSONRenderer):
    charset = "utf-8"

    def render(self, data, media_type=None, renderer_context=None):
        response = json.dumps(data)
        return response


class ClientJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        # If the view throws an error (such as the user can't be authenticated
        # or something similar), `data` will contain an `errors` key. We want
        # the default JSONRenderer to handle rendering errors, so we need to
        # check for this case.
        if isinstance(data, dict):
            errors = data.get('errors', None)

            if errors is not None:
                # As mentioned about, we will let the default JSONRenderer
                # handle
                # rendering errors.
                return super(ClientJSONRenderer, self).render(data)

            # Finally, we can render our data under the "data" namespace.
            return json.dumps({
                'data': data
            })

        return json.dumps({
            'message': data
        })
