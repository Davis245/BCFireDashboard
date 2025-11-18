from django.contrib import admin
from .models import WeatherStation, HourlyObservation


@admin.register(WeatherStation)
class WeatherStationAdmin(admin.ModelAdmin):
    list_display = ['station_id', 'name', 'province', 'latitude', 'longitude', 'is_active', 'last_updated']
    list_filter = ['is_active', 'province']
    search_fields = ['station_id', 'name']
    readonly_fields = ['created_at', 'last_updated']


@admin.register(HourlyObservation)
class HourlyObservationAdmin(admin.ModelAdmin):
    list_display = ['station', 'observation_time', 'temperature', 'relative_humidity', 'wind_speed', 'precipitation']
    list_filter = ['station', 'observation_time']
    search_fields = ['station__name', 'station__station_id']
    readonly_fields = ['created_at']
    date_hierarchy = 'observation_time'
