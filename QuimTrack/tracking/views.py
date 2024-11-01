from rest_framework import status as http_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from QuimTrack.base_controller import BaseController
import pandas as pd
from io import BytesIO
import base64
from .services import TrackingService
from .serializers import TrackingSerializer
from django.db.models import Count, Sum


def safe_strip(value):
    return value.strip() if isinstance(value, str) else value


# Create your views here.
class TrackingViewSet(viewsets.ModelViewSet, BaseController):
    permission_classes = [IsAuthenticated]
    serializer_class = TrackingSerializer

    def get_queryset(self):
        # Obtiene todos los objetos Tracking
        queryset = TrackingService.get_all_trackings()

        # Filtrar por usuario si el parámetro está presente
        user_id = self.request.query_params.get("user", None)
        if user_id is not None:
            queryset = queryset.filter(user=user_id)

        # Filtrar por clasificación si el parámetro está presente
        classification_id = self.request.query_params.get("classification", None)
        if classification_id is not None:
            queryset = queryset.filter(classification=classification_id)

        service_type_id = self.request.query_params.get("service_type", None)
        if service_type_id is not None:
            queryset = queryset.filter(service_type=service_type_id)

        company_id = self.request.query_params.get("company", None)
        if company_id is not None:
            queryset = queryset.filter(company=company_id)

        arl_id = self.request.query_params.get("arl", None)
        if arl_id is not None:
            queryset = queryset.filter(arl=arl_id)

        state_id = self.request.query_params.get("state", None)
        if state_id is not None:
            queryset = queryset.filter(state=state_id)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.send_response({"trackings": serializer.data}, "trackings")

    @action(detail=False, methods=["get"], url_path="state_by_arl")
    def state_by_arl(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        tracking_data = queryset.values("arl__name", "state__name").annotate(
            company_count=Count("company", distinct=True)
        )

        result = {}
        for entry in tracking_data:
            arl_name = entry["arl__name"]
            state_name = entry["state__name"]
            company_count = entry["company_count"]

            if arl_name not in result:
                result[arl_name] = {}

            result[arl_name][state_name] = company_count

        return self.send_response({"trackings_state_by_arl": result}, "state_by_arl")

    @action(detail=False, methods=["get"], url_path="user_allocation_by_arl")
    def user_allocation_by_arl(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        company_count_data = queryset.values(
            "user__first_name", "user__last_name", "arl__name"
        ).annotate(company_count=Count("company", distinct=True))

        result = {}

        for entry in company_count_data:
            user_name = f"{entry['user__first_name']} {entry['user__last_name']}"
            arl_name = entry["arl__name"]
            company_count = entry["company_count"]
            if user_name not in result:
                result[user_name] = {}

            result[user_name][arl_name] = company_count

        return self.send_response(
            {"trackings_user_allocation_by_arl": result}, "user_allocation_by_arl"
        )

    @action(detail=False, methods=["get"], url_path="user_resource_by_arl")
    def user_resource_by_arl(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        resource_count_data = queryset.values(
            "user__first_name", "user__last_name", "arl__name"
        ).annotate(resource_sum=Sum("asigned_resource"))

        result = {}

        for entry in resource_count_data:
            user_name = f"{entry['user__first_name']} {entry['user__last_name']}"
            arl_name = entry["arl__name"]
            resource_sum = entry["resource_sum"]
            if user_name not in result:
                result[user_name] = {}

            result[user_name][arl_name] = resource_sum

        return self.send_response(
            {"trackings_user_resource_by_arl": result}, "user_resource_by_arl"
        )

    @action(detail=False, methods=["get"], url_path="resource_by_arl")
    def resource_by_arl(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        tracking_data = queryset.values("arl__name", "state__name").annotate(
            resource_sum=Sum("resource_hours")
        )
        result = {}

        for entry in tracking_data:
            arl_name = entry["arl__name"]
            state_name = entry["state__name"]
            resource_sum = entry["resource_sum"]
            if arl_name not in result:
                result[arl_name] = {}

            result[arl_name][state_name] = resource_sum

        return self.send_response(
            {"trackings_resource_by_arl": result}, "resource_by_arl"
        )

    @action(detail=False, methods=["get"], url_path="asigned_resource_by_arl")
    def asigned_resource_by_arl(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        tracking_data = queryset.values("arl__name").annotate(
            resource_sum=Sum("resource_hours")
        )
        total_resources = queryset.aggregate(total_resource_hours=Sum("resource_hours"))
        total_hours = total_resources["total_resource_hours"]
        result = {}
        for entry in tracking_data:
            arl_name = entry["arl__name"]
            resource_sum = entry["resource_sum"]
            if arl_name not in result:
                result[arl_name] = {}

            result[arl_name] = round((resource_sum / total_hours) * 100, 1)

        return self.send_response(
            {"trackings_asigned_resource_by_arl": result}, "asigned_resource_by_arl"
        )

    @action(detail=False, methods=["get"], url_path="asigned_resource_by_user")
    def asigned_resource_by_user(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        tracking_data = queryset.values("user__first_name", "user__last_name").annotate(
            total_resources=Sum("asigned_resource"),  # Sumar recursos asignados
            total_hours=Sum("resource_hours"),  # Sumar horas de recursos
        )
        result = {}
        for entry in tracking_data:
            user_name = f"{entry["user__first_name"]} {entry["user__last_name"]}"
            total_resources = entry["total_resources"]
            total_hours = entry["total_hours"]
            if user_name not in result:
                result[user_name] = {}

            result[user_name] = {
                "RECURSO ASIGNADO": total_resources,
                "TOTAL RECURSO": total_hours,
            }

        return self.send_response(
            {"trackings_asigned_resource_by_user": result}, "asigned_resource_by_user"
        )

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        excel_base64 = request.data.get("excel_base64", None)

        if not excel_base64:
            return self.send_error(
                "Debe Proporcionar el excel en base64",
                code=http_status.HTTP_400_BAD_REQUEST,
            )
        excel_data = base64.b64decode(excel_base64)
        df = pd.read_excel(BytesIO(excel_data))
        df.columns = (
            df.columns.str.strip()
            .str.replace("\n", "")
            .str.replace(" ", "_")
            .str.replace("#", "numero")
            .str.upper()
        )

        trackings = []
        for index, row in df.iterrows():
            hour_resource = row.get("RECURSO_(NUMERO_DE_HORAS)")
            if pd.isnull(hour_resource):
                hour_resource = 0
            asigned_resource = row.get("RECURSO_ASIGNADO")
            if pd.isnull(asigned_resource):
                asigned_resource = 0

            expiration_date = row.get("FECHA_DE_VENCIMIENTO")
            if pd.isna(expiration_date) or expiration_date is pd.NaT:
                expiration_date = None
            else:
                expiration_date = pd.to_datetime(expiration_date).date()

            date_radicate = row.get("FECHA_FINALIZADO_O_CARGADO_PARA_RADICAR")
            if pd.isna(date_radicate) or date_radicate is pd.NaT:
                date_radicate = None
            else:
                date_radicate = pd.to_datetime(date_radicate).date()
            # Extraer los datos de cada columna
            assigned = row.get("ASIGNADO_A")
            if pd.isna(assigned) or assigned is pd.NaT:
                assigned = None
            else:
                assigned = row.get("ASIGNADO_A")

            tracking_data = {
                "user_name": row["CONSULTOR"],
                "user_asigned": assigned,
                "classification_name": row["CLASIFICACIÓN"],
                "typeservice_name": row["TIPO_DE_SERVICIO"],
                "company_name": row["EMPRESA_USUARIA"],
                "arl_name": row["ARL"],
                "resource_hour": hour_resource,  # Usa get para manejar valores faltantes
                "expiration_date": expiration_date,
                "asigned_resource": asigned_resource,  # Valores por defecto en caso de que falten
                "tracking_state_name": row["ESTADO"],
                "date_radicate": date_radicate,
                # Puedes agregar aquí más campos si el servicio `create` los soporta
            }
            try:
                tracking = TrackingService.create(tracking_data)
                trackings.append(tracking)
            except Exception as e:
                print(f"Error al crear tracking en la fila {index}: {str(e)}")
        serializer = TrackingSerializer(trackings, many=True)
        return self.send_response(
            {"trakcings": serializer.data}, "Archivo cargado correctamente"
        )
