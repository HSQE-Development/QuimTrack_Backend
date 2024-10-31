from utils.object_manager import SoftDeleteModel, TimeStampedModel
from django.db import models
from utils.lower_replace_whitespaces import lower_replace_whitespaces


# Create your models here.
class Arl(SoftDeleteModel, TimeStampedModel):
    name = models.CharField(max_length=100)
    identify = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        if self.name:
            self.identify = lower_replace_whitespaces(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
