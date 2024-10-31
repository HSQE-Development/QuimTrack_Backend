from .models import Arl
from django.db import transaction


class ArlService:
    @staticmethod
    @transaction.atomic
    def get_or_create(arl_data: dict):
        arl_name = arl_data["name"].upper()
        arl, creado = Arl.objects.get_or_create(name=arl_name)
        return arl
