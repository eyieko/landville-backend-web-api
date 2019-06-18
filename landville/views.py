from django.http import JsonResponse


def error_404(request, exception):
    message = ("The endpoint you are trying to access might "
               "have been removed, "
               "had its name changed, or is temporarily unavailable. "
               "Please check the documentation here : "
               "https://landville-backend-web-api.herokuapp.com/ "
               "and try again later.")
    response = JsonResponse(data={"message": message})
    response.status_code = 404
    return response
