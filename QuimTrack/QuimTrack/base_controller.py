from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class BaseController(APIView):
    """
    Controlador base para manejar respuestas API.
    """

    def send_response(self, result, message, code=status.HTTP_200_OK):
        """
        Método para respuesta exitosa.
        """
        response = {"success": True, "data": result, "message": message, "status": code}
        return Response(response, status=code)

    def send_error(
        self, error, error_messages=None, code=status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        """
        Método para manejar errores.
        """
        try:
            code = int(code)
        except ValueError:
            code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if code < 100 or code > 599:
            code = status.HTTP_500_INTERNAL_SERVER_ERROR

        response = {"success": False, "message": error, "status": code, "data": None}
        if error_messages:
            response["data"] = error_messages

        return Response(response, status=code)
