from django.db import models
from utils.object_manager import SoftDeleteModel, TimeStampedModel
from utils.lower_replace_whitespaces import lower_replace_whitespaces


# Create your models here.
class Company(SoftDeleteModel, TimeStampedModel):
    name = models.CharField(unique=True, max_length=250)
    nit = models.CharField(unique=True, max_length=10, null=True)

    def __str__(self):
        return self.name
