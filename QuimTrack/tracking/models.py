from django.db import models
from utils.object_manager import SoftDeleteModel, TimeStampedModel
from authentication.models import User
from utils.lower_replace_whitespaces import lower_replace_whitespaces
from company.models import Company
from arl.models import Arl


class TrackingClassification(models.Model):
    name = models.CharField(max_length=100)
    identify = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        if self.name:
            self.identify = lower_replace_whitespaces(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TrackingState(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Create your models here.
class Tracking(SoftDeleteModel, TimeStampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="users",
        blank=False,
        default=None,
        null=True,
    )
    classification = models.ForeignKey(
        TrackingClassification,
        on_delete=models.CASCADE,
        related_name="classifications",
        blank=False,
        default=None,
        null=True,
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="companies",
        blank=False,
        default=None,
        null=True,
    )
    arl = models.ForeignKey(
        Arl,
        on_delete=models.CASCADE,
        related_name="arls",
        blank=False,
        default=None,
        null=True,
    )
    resource_hours = models.IntegerField(null=True)
    expiration_date = models.DateField(null=True)
    state = models.ForeignKey(
        TrackingState,
        on_delete=models.CASCADE,
        related_name="state",
        blank=False,
        default=None,
        null=True,
    )
    date_radicate = models.DateField(null=True)
