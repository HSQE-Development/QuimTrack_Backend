from rest_framework import serializers
from .models import Arl


class ArlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arl
        fields = ["id", "name", "identify"]
