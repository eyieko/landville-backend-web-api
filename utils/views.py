from django.http import JsonResponse


def error_500(response):
    """
    Customized view to handle server failure.
    params: the request
    returns: custom response for server failure
    """
    response = JsonResponse(data={"errors": "Server Failure"})
    response.status_code = 500
    return response
