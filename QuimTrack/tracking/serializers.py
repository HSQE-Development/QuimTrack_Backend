from rest_framework import serializers
from .models import TrackingClassification, TrackingState, ServiceType, Tracking
from authentication.serializers import UserReadSerializer
from arl.serializers import ArlSerializer
from company.serializers import CompanySerializer


class TrackingClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingClassification
        fields = ["id", "name", "identify"]


class TrackingStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingState
        fields = ["id", "name"]


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ["id", "name", "identify"]


class TrackingSerializer(serializers.ModelSerializer):
    user = UserReadSerializer()  # Si necesitas solo el ID del usuario
    classification = TrackingClassificationSerializer()
    service_type = ServiceTypeSerializer()
    company = CompanySerializer()
    arl = ArlSerializer()
    state = TrackingStateSerializer()

    class Meta:
        model = Tracking
        fields = [
            "id",
            "user",
            "classification",
            "service_type",
            "company",
            "arl",
            "resource_hours",
            "asigned_resource",
            "expiration_date",
            "state",
            "date_radicate",
        ]
