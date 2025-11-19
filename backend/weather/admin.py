from django.contrib import admin
from .models import WeatherStation, HourlyObservation


@admin.register(WeatherStation)
class WeatherStationAdmin(admin.ModelAdmin):
    list_display = ['station_code', 'name', 'province', 'latitude', 'longitude', 'is_active', 'last_updated']
    list_filter = ['is_active', 'province']
    search_fields = ['station_code', 'name']
    readonly_fields = ['created_at', 'last_updated']


@admin.register(HourlyObservation)
class HourlyObservationAdmin(admin.ModelAdmin):
    list_display = ['station', 'observation_time', 'temperature', 'relative_humidity', 'wind_speed', 'fwi', 'danger_rating']
    list_filter = ['station', 'danger_rating']
    search_fields = ['station__name', 'station__station_code']
    readonly_fields = ['created_at']
    date_hierarchy = 'observation_time'
