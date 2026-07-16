from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class Conflict(APIException):
    status_code = 409
    default_detail = 'Ресурс уже существует'


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        detail = response.data.get("detail")

        if isinstance(detail, dict):
            detail = list(detail.values())[0]

        if isinstance(detail, list):
            detail = detail[0]

        response.data = {'message': detail}
    return response
