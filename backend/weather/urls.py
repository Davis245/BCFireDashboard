"""
URL configuration for the Weather API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WeatherStationViewSet, HourlyObservationViewSet

router = DefaultRouter()
router.register(r'stations', WeatherStationViewSet, basename='station')
router.register(r'observations', HourlyObservationViewSet, basename='observation')

urlpatterns = [
    path('', include(router.urls)),
]
