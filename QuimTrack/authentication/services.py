from authentication.models import User, Role
from .services_interface import IAuthService
from typing import Optional
from QuimTrack.exceptions import NotFoundError, UnauthenticatedException
from django.db import transaction
from django.db.models.functions import Upper
from django.db.models import Q


class RoleService:
    @staticmethod
    def get_all_roles():
        return Role.objects.all()

    @staticmethod
    def get_role_by_id(id: int) -> Optional[Role]:
        try:
            return Role.objects.get(id=id)
        except Role.DoesNotExist:
            raise NotFoundError("Rol no encontrado", code=404)

    @staticmethod
    @transaction.atomic
    def assign_role_to_user(user: User, role_id: int):
        role = RoleService.get_role_by_id(role_id)
        user.role = role  # Asignar el rol al usuario
        user.save()
        return user


class UserService:
    @staticmethod
    def get_all_users():
        return User.objects.all()

    @staticmethod
    def get_user_by_id(id: int) -> Optional[User]:
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            raise NotFoundError("Usuario no encontrado o inactivo", code=404)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise NotFoundError("Usuario no encontrado o inactivo", code=404)

    @staticmethod
    def get_user_by_name(full_name: str) -> Optional[User]:
        try:
            names = full_name.strip().split(" ", 1)

            if len(names) < 2:
                raise ValueError("El nombre completo debe incluir nombre y apellido.")
            first_name, last_name = names[0].upper(), names[1].upper()
            return User.objects.annotate(
                first_name_upper=Upper("first_name"), last_name_upper=Upper("last_name")
            ).get(Q(first_name_upper=first_name) & Q(last_name_upper=last_name))
        except User.DoesNotExist:
            raise NotFoundError(
                f"Usuario no encontrado o inactivo {first_name} {last_name}", code=404
            )
        except ValueError as e:
            raise NotFoundError(f"{str(e)} -eeee", code=400)

    @staticmethod
    @transaction.atomic
    def create_user(**user_data) -> User:
        user = User.objects.create_user(**user_data)
        return user

    @staticmethod
    def delete_user(*, user: User):
        user.delete()

    @staticmethod
    def update_user(*, user: User, password=None, **user_data) -> User:
        for attr, value in user_data.items():
            setattr(user, attr, value)

        if password is not None:
            user.set_password(password)

        user.save()
        return user


class AuthService(IAuthService):
    user_service = UserService()

    @transaction.atomic
    def login(self, email: str, password: str):
        user = self.user_service.get_user_by_email(email)
        if user and user.check_password(password):
            token_data = self.generate_token(user)
            return {"token": token_data, "user": user}
        raise UnauthenticatedException("Credenciales inválidas", 401)

    def generate_token(self, user: User):
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user=user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

    @transaction.atomic
    def register(self, user_data):
        role_id = user_data.pop("role_id", None)
        user = self.user_service.create_user(**user_data)
        if role_id:
            user = RoleService.assign_role_to_user(user, role_id)
        return user

    @staticmethod
    def logout():
        return None
