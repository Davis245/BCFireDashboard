from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from weather.models import WeatherStation, HourlyObservation


class WeatherStationModelTest(TestCase):
    """Test the WeatherStation model."""
    
    def setUp(self):
        """Set up test data."""
        self.station_data = {
            'station_id': '1108395',
            'name': 'VANCOUVER INTL A',
            'province': 'BC',
            'latitude': Decimal('49.19'),
            'longitude': Decimal('-123.18'),
            'elevation': Decimal('4.30'),
        }
    
    def test_create_weather_station(self):
        """Test creating a weather station."""
        station = WeatherStation.objects.create(**self.station_data)
        
        self.assertEqual(station.station_id, '1108395')
        self.assertEqual(station.name, 'VANCOUVER INTL A')
        self.assertEqual(station.province, 'BC')
        self.assertEqual(station.latitude, Decimal('49.19'))
        self.assertEqual(station.longitude, Decimal('-123.18'))
        self.assertTrue(station.is_active)
    
    def test_station_id_unique(self):
        """Test that station_id must be unique."""
        WeatherStation.objects.create(**self.station_data)
        
        # Try to create another station with same ID
        with self.assertRaises(IntegrityError):
            WeatherStation.objects.create(**self.station_data)
    
    def test_station_str_representation(self):
        """Test the string representation of a station."""
        station = WeatherStation.objects.create(**self.station_data)
        expected = 'VANCOUVER INTL A (1108395)'
        self.assertEqual(str(station), expected)
    
    def test_station_default_values(self):
        """Test default values for optional fields."""
        station = WeatherStation.objects.create(
            station_id='1234567',
            name='Test Station'
        )
        
        self.assertEqual(station.province, 'BC')
        self.assertTrue(station.is_active)
        self.assertIsNone(station.latitude)
        self.assertIsNone(station.longitude)
        self.assertIsNone(station.elevation)
        self.assertIsNone(station.last_updated)
    
    def test_station_ordering(self):
        """Test that stations are ordered by name."""
        WeatherStation.objects.create(station_id='1', name='Zebra Station')
        WeatherStation.objects.create(station_id='2', name='Alpha Station')
        WeatherStation.objects.create(station_id='3', name='Beta Station')
        
        stations = list(WeatherStation.objects.all())
        self.assertEqual(stations[0].name, 'Alpha Station')
        self.assertEqual(stations[1].name, 'Beta Station')
        self.assertEqual(stations[2].name, 'Zebra Station')


class HourlyObservationModelTest(TestCase):
    """Test the HourlyObservation model."""
    
    def setUp(self):
        """Set up test data."""
        self.station = WeatherStation.objects.create(
            station_id='1108395',
            name='VANCOUVER INTL A',
            province='BC'
        )
        
        self.obs_time = timezone.make_aware(
            datetime(2025, 11, 17, 12, 0),
            timezone.utc
        )
        
        self.observation_data = {
            'station': self.station,
            'observation_time': self.obs_time,
            'temperature': Decimal('15.5'),
            'dew_point': Decimal('12.3'),
            'relative_humidity': 75,
            'precipitation': Decimal('0.2'),
            'wind_direction': 18,  # 180 degrees
            'wind_speed': Decimal('12.5'),
            'visibility': Decimal('24.1'),
            'station_pressure': Decimal('101.32'),
            'humidex': Decimal('18.2'),
            'wind_chill': None,
            'weather_description': 'Cloudy',
        }
    
    def test_create_observation(self):
        """Test creating an hourly observation."""
        obs = HourlyObservation.objects.create(**self.observation_data)
        
        self.assertEqual(obs.station, self.station)
        self.assertEqual(obs.temperature, Decimal('15.5'))
        self.assertEqual(obs.relative_humidity, 75)
        self.assertEqual(obs.weather_description, 'Cloudy')
    
    def test_observation_nullable_fields(self):
        """Test that observation fields can be null."""
        obs = HourlyObservation.objects.create(
            station=self.station,
            observation_time=self.obs_time
        )
        
        self.assertIsNone(obs.temperature)
        self.assertIsNone(obs.relative_humidity)
        self.assertIsNone(obs.precipitation)
        self.assertIsNone(obs.wind_speed)
    
    def test_unique_station_observation_constraint(self):
        """Test that station + observation_time must be unique."""
        HourlyObservation.objects.create(**self.observation_data)
        
        # Try to create duplicate observation
        with self.assertRaises(IntegrityError):
            HourlyObservation.objects.create(**self.observation_data)
    
    def test_multiple_observations_same_station(self):
        """Test that a station can have multiple observations at different times."""
        obs1 = HourlyObservation.objects.create(
            station=self.station,
            observation_time=self.obs_time,
            temperature=Decimal('15.0')
        )
        
        obs2 = HourlyObservation.objects.create(
            station=self.station,
            observation_time=self.obs_time + timedelta(hours=1),
            temperature=Decimal('16.0')
        )
        
        self.assertEqual(self.station.observations.count(), 2)
    
    def test_observation_ordering(self):
        """Test that observations are ordered by time (newest first)."""
        obs1 = HourlyObservation.objects.create(
            station=self.station,
            observation_time=self.obs_time,
            temperature=Decimal('15.0')
        )
        
        obs2 = HourlyObservation.objects.create(
            station=self.station,
            observation_time=self.obs_time + timedelta(hours=1),
            temperature=Decimal('16.0')
        )
        
        obs3 = HourlyObservation.objects.create(
            station=self.station,
            observation_time=self.obs_time - timedelta(hours=1),
            temperature=Decimal('14.0')
        )
        
        observations = list(HourlyObservation.objects.all())
        # Should be ordered newest to oldest
        self.assertEqual(observations[0].temperature, Decimal('16.0'))
        self.assertEqual(observations[1].temperature, Decimal('15.0'))
        self.assertEqual(observations[2].temperature, Decimal('14.0'))
    
    def test_observation_str_representation(self):
        """Test the string representation of an observation."""
        obs = HourlyObservation.objects.create(**self.observation_data)
        expected = f'VANCOUVER INTL A - {self.obs_time}'
        self.assertEqual(str(obs), expected)
    
    def test_cascade_delete(self):
        """Test that observations are deleted when station is deleted."""
        HourlyObservation.objects.create(**self.observation_data)
        HourlyObservation.objects.create(
            station=self.station,
            observation_time=self.obs_time + timedelta(hours=1)
        )
        
        self.assertEqual(HourlyObservation.objects.count(), 2)
        
        # Delete the station
        self.station.delete()
        
        # Observations should be deleted too
        self.assertEqual(HourlyObservation.objects.count(), 0)
    
    def test_related_name_access(self):
        """Test accessing observations through station's related name."""
        HourlyObservation.objects.create(**self.observation_data)
        HourlyObservation.objects.create(
            station=self.station,
            observation_time=self.obs_time + timedelta(hours=1)
        )
        
        # Access through related name
        observations = self.station.observations.all()
        self.assertEqual(observations.count(), 2)


class WeatherDataIntegrityTest(TestCase):
    """Test data integrity and business logic."""
    
    def setUp(self):
        """Set up test data."""
        self.station = WeatherStation.objects.create(
            station_id='1108395',
            name='VANCOUVER INTL A'
        )
    
    def test_temperature_range_valid(self):
        """Test that valid temperature ranges are accepted."""
        # Test extreme but valid temperatures
        obs_cold = HourlyObservation.objects.create(
            station=self.station,
            observation_time=timezone.now(),
            temperature=Decimal('-50.0')
        )
        
        obs_hot = HourlyObservation.objects.create(
            station=self.station,
            observation_time=timezone.now() + timedelta(hours=1),
            temperature=Decimal('45.0')
        )
        
        self.assertEqual(obs_cold.temperature, Decimal('-50.0'))
        self.assertEqual(obs_hot.temperature, Decimal('45.0'))
    
    def test_humidity_valid_range(self):
        """Test that humidity values are in valid range."""
        obs = HourlyObservation.objects.create(
            station=self.station,
            observation_time=timezone.now(),
            relative_humidity=0
        )
        self.assertEqual(obs.relative_humidity, 0)
        
        obs2 = HourlyObservation.objects.create(
            station=self.station,
            observation_time=timezone.now() + timedelta(hours=1),
            relative_humidity=100
        )
        self.assertEqual(obs2.relative_humidity, 100)
    
    def test_wind_direction_valid_range(self):
        """Test that wind direction is in valid range (0-36)."""
        # 0 = calm
        obs_calm = HourlyObservation.objects.create(
            station=self.station,
            observation_time=timezone.now(),
            wind_direction=0
        )
        self.assertEqual(obs_calm.wind_direction, 0)
        
        # 36 = 360 degrees (north)
        obs_north = HourlyObservation.objects.create(
            station=self.station,
            observation_time=timezone.now() + timedelta(hours=1),
            wind_direction=36
        )
        self.assertEqual(obs_north.wind_direction, 36)
    
    def test_bulk_observation_creation(self):
        """Test creating multiple observations efficiently."""
        observations = []
        base_time = timezone.now()
        
        for i in range(100):
            obs = HourlyObservation(
                station=self.station,
                observation_time=base_time + timedelta(hours=i),
                temperature=Decimal('15.0') + i * Decimal('0.1')
            )
            observations.append(obs)
        
        # Bulk create
        HourlyObservation.objects.bulk_create(observations)
        
        # Verify all created
        self.assertEqual(HourlyObservation.objects.count(), 100)
    
    def test_station_last_updated_timestamp(self):
        """Test that last_updated can be set and retrieved."""
        now = timezone.now()
        self.station.last_updated = now
        self.station.save()
        
        # Retrieve from database
        station = WeatherStation.objects.get(station_id='1108395')
        self.assertIsNotNone(station.last_updated)
        self.assertEqual(station.last_updated.date(), now.date())
