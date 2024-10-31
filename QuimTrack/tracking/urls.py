from django.urls import path, include
from .views import TrackingViewSet
from rest_framework.routers import DefaultRouter

# Crea un enrutador y registra los ViewSets
router = DefaultRouter()
router.register(
    r"tracking", TrackingViewSet, basename="tracking"
)  # Registra el UserViewSet

# Define urlpatterns
urlpatterns = [
    path("", include(router.urls)),  # Incluye las rutas del enrutador
]
