from .models import Tracking, ServiceType, TrackingState, TrackingClassification
from django.db import transaction
from authentication.services import UserService
from company.services import CompanyService
from arl.services import ArlService


class ServiceTypeService:
    @staticmethod
    @transaction.atomic
    def get_or_create(name: str) -> ServiceType:
        serviceType, creado = ServiceType.objects.get_or_create(name=name.upper())
        return serviceType


class TrackingStateService:
    @staticmethod
    @transaction.atomic
    def get_or_create(name: str) -> TrackingState:
        trackingState, creado = TrackingState.objects.get_or_create(name=name.upper())
        return trackingState


class TrackingClassificationService:
    @staticmethod
    @transaction.atomic
    def get_or_create(name: str) -> TrackingClassification:
        trackingClassification, creado = TrackingClassification.objects.get_or_create(
            name=name.upper()
        )
        return trackingClassification


class TrackingService:
    def get_all_trackings():
        return Tracking.objects.all()

    @staticmethod
    @transaction.atomic
    def create(tracking_data: dict):
        user_name = tracking_data["user_name"]
        user_asigned = tracking_data.get("user_asigned", None)
        classification_name = tracking_data["classification_name"]
        typeservice_name = tracking_data["typeservice_name"]
        company_name = tracking_data["company_name"]
        arl_name = tracking_data["arl_name"]
        tracking_state_name = tracking_data["tracking_state_name"]
        resource_hour = tracking_data["resource_hour"]
        expiration_date = tracking_data["expiration_date"]
        asigned_resource = tracking_data["asigned_resource"]
        date_radicate = tracking_data["date_radicate"]
        user = UserService.get_user_by_name(user_name)
        if user:
            trackingClassification = TrackingClassificationService.get_or_create(
                classification_name
            )
            trackingServiceType = ServiceTypeService.get_or_create(typeservice_name)
            company = CompanyService.get_or_create({"name": company_name})
            arl = ArlService.get_or_create({"name": arl_name})
            trackingState = TrackingStateService.get_or_create(tracking_state_name)
            newResourceHour = resource_hour
            userFinally = user
            if user_asigned:
                userFinally = UserService.get_user_by_name(user_asigned)
        tracking = Tracking(
            user=userFinally,
            classification=trackingClassification,
            service_type=trackingServiceType,
            company=company,
            arl=arl,
            state=trackingState,
            resource_hours=newResourceHour,
            expiration_date=expiration_date,
            asigned_resource=asigned_resource,
            date_radicate=date_radicate,
        )
        tracking.save()  # Guarda el objeto en la base de datos
        return tracking
