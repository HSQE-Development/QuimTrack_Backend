from abc import ABC, abstractmethod
from .models import User
from typing import Dict


class IAuthService(ABC):
    @abstractmethod
    def login(self, email: str, password: str) -> Dict[str, User | str]:
        """Autenticar Usuario

        Args:
            email (str)
            password (str)
        """
        pass

    @abstractmethod
    def generate_token(self, user: User) -> Dict[str, str]:
        """Generar Token JWT al usuario"""
        pass

    @abstractmethod
    def register(self, user_data: dict):
        pass
