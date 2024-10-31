from django.db import transaction
from .models import Company


class CompanyService:
    @staticmethod
    @transaction.atomic
    def get_or_create(company_data: dict):
        company_name = company_data["name"].upper()
        company, creado = Company.objects.get_or_create(name=company_name)
        return company
