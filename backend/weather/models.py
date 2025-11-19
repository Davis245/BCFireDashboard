from django.db import models
from django.utils import timezone


class WeatherStation(models.Model):
    """
    Represents a BC Wildfire Service fire weather station.
    """
    station_code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text="BCWS Station Code"
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
        verbose_name = "Fire Weather Station"
        verbose_name_plural = "Fire Weather Stations"
    
    def __str__(self):
        return f"{self.name} ({self.station_code})"


class HourlyObservation(models.Model):
    """
    Stores hourly fire weather observations from BC Wildfire Service.
    """
    station = models.ForeignKey(
        WeatherStation,
        on_delete=models.CASCADE,
        related_name='observations'
    )
    observation_time = models.DateTimeField(
        db_index=True,
        help_text="Observation time"
    )
    
    # Basic weather measurements
    temperature = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Temperature in °C"
    )
    relative_humidity = models.IntegerField(
        null=True,
        blank=True,
        help_text="Relative humidity in %"
    )
    precipitation = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Precipitation in mm"
    )
    
    # Wind measurements
    wind_speed = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Wind speed in km/h"
    )
    wind_direction = models.IntegerField(
        null=True,
        blank=True,
        help_text="Wind direction in degrees"
    )
    wind_gust = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Wind gust in km/h"
    )
    
    # Hourly Fire Weather Indices
    hourly_ffmc = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Hourly Fine Fuel Moisture Code"
    )
    hourly_isi = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Hourly Initial Spread Index"
    )
    hourly_fwi = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Hourly Fire Weather Index"
    )
    
    # Daily Fire Weather Indices
    ffmc = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Fine Fuel Moisture Code"
    )
    dmc = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Duff Moisture Code"
    )
    dc = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Drought Code"
    )
    isi = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Initial Spread Index"
    )
    bui = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Buildup Index"
    )
    fwi = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Fire Weather Index"
    )
    
    # Fire danger rating
    danger_rating = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Fire danger rating (Low, Moderate, High, Very High, Extreme)"
    )
    
    # Additional measurements
    snow_depth = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Snow depth in cm"
    )
    solar_radiation = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Solar radiation"
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
