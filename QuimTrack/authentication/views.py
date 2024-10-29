from rest_framework import status as http_status
from rest_framework import viewsets
from rest_framework.decorators import action
from .serializers import UserWriteSerializer, UserReadSerializer, AuthUserSerializer
from rest_framework.permissions import AllowAny
from QuimTrack.base_controller import BaseController
from QuimTrack.exceptions import NotFoundError, UnauthenticatedException
from .services import AuthService


# Create your views here.
class AuthViewSet(viewsets.ModelViewSet, BaseController):
    permission_classes = [AllowAny]
    auth_service = AuthService()

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        try:
            serializer = UserWriteSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return self.send_response(
                    {"user": UserReadSerializer(user).data},
                    "Usuario Registrado correctamente.",
                    http_status.HTTP_201_CREATED,
                )
            return self.send_error(
                "Error al registrar usuario",
                serializer.errors,
                http_status.HTTP_400_BAD_REQUEST,
            )
        except NotFoundError as e:  # Captura NotFoundError específicamente
            return self.send_error(
                str(e), code=e.status_code
            )  # Usa el código de la excepción
        except Exception as e:
            # Usa un código de error 500 por defecto
            return self.send_error(
                str(e), code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"], url_path="sign_in")
    def sign_in(self, request):
        try:
            email = request.data.get("email", None)
            password = request.data.get("password", None)

            user_data = self.auth_service.login(email=email, password=password)
            response_data = {
                "user": user_data["user"],
                "token": user_data[
                    "token"
                ],  # Este es el diccionario con "refresh" y "access"
            }

            auth_user_serializer = AuthUserSerializer(response_data)

            return self.send_response(
                {"auth_user": auth_user_serializer.data}, "Inicio Correcto."
            )
        except UnauthenticatedException as e:
            return self.send_error(str(e), code=e.status_code)
        except NotFoundError as e:  # Captura NotFoundError específicamente
            return self.send_error(str(e), code=e.status_code)
        except Exception as e:
            # Usa un código de error 500 por defecto
            return self.send_error(
                str(e), code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
            )
