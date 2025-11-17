from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# Register viewsets here when created

urlpatterns = [
    path('', include(router.urls)),
]
