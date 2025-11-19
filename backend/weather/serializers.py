"""
Serializers for the Weather API.
"""
from rest_framework import serializers
from .models import WeatherStation, HourlyObservation


class WeatherStationSerializer(serializers.ModelSerializer):
    """Serializer for WeatherStation model."""
    
    observation_count = serializers.SerializerMethodField()
    latest_observation = serializers.SerializerMethodField()
    
    class Meta:
        model = WeatherStation
        fields = [
            'id',
            'station_code',
            'name',
            'province',
            'latitude',
            'longitude',
            'elevation',
            'is_active',
            'last_updated',
            'observation_count',
            'latest_observation',
        ]
    
    def get_observation_count(self, obj):
        """Return the total number of observations for this station."""
        return obj.observations.count()
    
    def get_latest_observation(self, obj):
        """Return the timestamp of the most recent observation."""
        latest = obj.observations.first()  # Already ordered by -observation_time
        return latest.observation_time if latest else None


class WeatherStationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for station lists (without observation counts)."""
    
    class Meta:
        model = WeatherStation
        fields = [
            'id',
            'station_code',
            'name',
            'province',
            'latitude',
            'longitude',
            'elevation',
            'is_active',
        ]


class HourlyObservationSerializer(serializers.ModelSerializer):
    """Serializer for HourlyObservation model."""
    
    station_name = serializers.CharField(source='station.name', read_only=True)
    station_code = serializers.CharField(source='station.station_code', read_only=True)
    
    class Meta:
        model = HourlyObservation
        fields = [
            'id',
            'station',
            'station_code',
            'station_name',
            'observation_time',
            'temperature',
            'relative_humidity',
            'precipitation',
            'wind_direction',
            'wind_speed',
            'wind_gust',
            'hourly_ffmc',
            'hourly_isi',
            'hourly_fwi',
            'ffmc',
            'dmc',
            'dc',
            'isi',
            'bui',
            'fwi',
            'danger_rating',
            'snow_depth',
            'solar_radiation',
        ]


class HourlyObservationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for observation lists (without station details)."""
    
    class Meta:
        model = HourlyObservation
        fields = [
            'id',
            'observation_time',
            'temperature',
            'relative_humidity',
            'precipitation',
            'wind_direction',
            'wind_speed',
            'wind_gust',
        ]


class StationWithObservationsSerializer(serializers.ModelSerializer):
    """Serializer for a station with its recent observations."""
    
    recent_observations = serializers.SerializerMethodField()
    
    class Meta:
        model = WeatherStation
        fields = [
            'id',
            'station_code',
            'name',
            'province',
            'latitude',
            'longitude',
            'elevation',
            'is_active',
            'last_updated',
            'recent_observations',
        ]
    
    def get_recent_observations(self, obj):
        """Return the most recent 24 observations (last 24 hours)."""
        recent = obj.observations.all()[:24]
        return HourlyObservationListSerializer(recent, many=True).data


class WeatherStatisticsSerializer(serializers.Serializer):
    """Serializer for weather statistics."""
    
    station_code = serializers.CharField()
    station_name = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    
    # Temperature stats
    avg_temperature = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    min_temperature = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    max_temperature = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    
    # Precipitation stats
    total_precipitation = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    avg_precipitation = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    
    # Humidity stats
    avg_humidity = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    min_humidity = serializers.IntegerField(allow_null=True)
    max_humidity = serializers.IntegerField(allow_null=True)
    
    # Wind stats
    avg_wind_speed = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    max_wind_speed = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    
    # Data completeness
    total_observations = serializers.IntegerField()
