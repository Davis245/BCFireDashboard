from django.db import models
from django.utils import timezone


class WeatherStation(models.Model):
    """
    Represents an ECCC climate station in BC.
    """
    station_id = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text="ECCC Climate ID (7 digits)"
    )
    name = models.CharField(max_length=200)
    province = models.CharField(max_length=2, default='BC')
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    elevation = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Elevation in meters"
    )
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Weather Station"
        verbose_name_plural = "Weather Stations"
    
    def __str__(self):
        return f"{self.name} ({self.station_id})"


class HourlyObservation(models.Model):
    """
    Stores hourly weather observations from ECCC climate stations.
    """
    station = models.ForeignKey(
        WeatherStation,
        on_delete=models.CASCADE,
        related_name='observations'
    )
    observation_time = models.DateTimeField(
        db_index=True,
        help_text="Observation time in UTC"
    )
    
    # Temperature measurements
    temperature = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Temperature in °C"
    )
    dew_point = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Dew point temperature in °C"
    )
    relative_humidity = models.IntegerField(
        null=True,
        blank=True,
        help_text="Relative humidity in %"
    )
    
    # Precipitation
    precipitation = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Precipitation in mm"
    )
    
    # Wind measurements
    wind_direction = models.IntegerField(
        null=True,
        blank=True,
        help_text="Wind direction in tens of degrees (0-36)"
    )
    wind_speed = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Wind speed in km/h"
    )
    
    # Other atmospheric measurements
    visibility = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Visibility in km"
    )
    station_pressure = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Station pressure in kPa"
    )
    
    # Calculated indices
    humidex = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Humidex index"
    )
    wind_chill = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Wind chill index"
    )
    
    # Weather description
    weather_description = models.TextField(
        null=True,
        blank=True,
        help_text="Weather conditions description"
    )
    
    # Data quality tracking
    data_quality = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Data quality flags"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-observation_time']
        verbose_name = "Hourly Observation"
        verbose_name_plural = "Hourly Observations"
        indexes = [
            models.Index(fields=['station', 'observation_time']),
            models.Index(fields=['observation_time']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['station', 'observation_time'],
                name='unique_station_observation'
            )
        ]
    
    def __str__(self):
        return f"{self.station.name} - {self.observation_time}"
