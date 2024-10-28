from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Role(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="roles")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
