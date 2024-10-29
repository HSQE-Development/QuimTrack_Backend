from rest_framework.exceptions import APIException


class NotFoundError(APIException):
    status_code = 404
    default_detail = "Recurso no encontrado."
    default_code = "not_found"


class UnauthenticatedException(APIException):
    status_code = 401
    default_detail = "Error con la petición."
    default_code = "unauthenticated"


class ResponseException(APIException):
    status_code = 400
    default_detail = "Error con la petición."
    default_code = "bad_request"
