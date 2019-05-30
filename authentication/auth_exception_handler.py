from rest_framework.views import exception_handler
from rest_framework import status


def custom_exception_handler(exc, context):
    # raising a NotAuthenticatedError should send a 401 response status code,
    # however due to the Authentication scheme used by our application it raises 403
    # instead,this calls for the need to write a custom exception handler and make
    # it send a 401 in the context of login

    # We Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    # Now we add the HTTP status code to the response when its in the context of the LoginAPIVIew.
    if response is not None:
        if "LoginAPIView" in str(context['view']):
            response.status_code = status.HTTP_401_UNAUTHORIZED
    return response
