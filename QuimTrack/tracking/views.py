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


def safe_strip(value):
    return value.strip() if isinstance(value, str) else value


# Create your views here.
class TrackingViewSet(viewsets.ModelViewSet, BaseController):
    permission_classes = [IsAuthenticated]

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
