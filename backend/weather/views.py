"""
API Views for the Weather application.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Min, Max, Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import WeatherStation, HourlyObservation
from .serializers import (
    WeatherStationSerializer,
    WeatherStationListSerializer,
    HourlyObservationSerializer,
    HourlyObservationListSerializer,
    StationWithObservationsSerializer,
    WeatherStatisticsSerializer,
)


class WeatherStationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing weather stations.
    
    list: Get all weather stations
    retrieve: Get a specific station by ID
    with_observations: Get a station with its recent observations
    statistics: Get statistical summary for a station
    """
    queryset = WeatherStation.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return WeatherStationListSerializer
        elif self.action == 'with_observations':
            return StationWithObservationsSerializer
        return WeatherStationSerializer
    
    def get_queryset(self):
        """
        Filter stations based on query parameters.
        
        Query params:
        - active: Filter by active status (true/false)
        - has_data: Only show stations with observations (true/false)
        - search: Search by name (case-insensitive)
        """
        queryset = WeatherStation.objects.all()
        
        # Filter by active status
        active = self.request.query_params.get('active')
        if active is not None:
            is_active = active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        
        # Filter stations with data
        has_data = self.request.query_params.get('has_data')
        if has_data and has_data.lower() == 'true':
            queryset = queryset.filter(observations__isnull=False).distinct()
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def with_observations(self, request, pk=None):
        """
        Get a station with its recent observations.
        
        Query params:
        - hours: Number of recent hours to include (default: 24)
        """
        station = self.get_object()
        serializer = StationWithObservationsSerializer(station)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get statistical summary for a station.
        
        Query params:
        - start_date: Start date (ISO format, default: 7 days ago)
        - end_date: End date (ISO format, default: now)
        - days: Alternative to start_date - number of days back (default: 7)
        """
        station = self.get_object()
        
        # Parse date range
        end_date = timezone.now()
        start_date_param = request.query_params.get('start_date')
        days_param = request.query_params.get('days', '7')
        
        if start_date_param:
            from dateutil import parser
            start_date = parser.parse(start_date_param)
        else:
            days = int(days_param)
            start_date = end_date - timedelta(days=days)
        
        # Get observations in date range
        observations = station.observations.filter(
            observation_time__gte=start_date,
            observation_time__lte=end_date
        )
        
        # Calculate statistics
        stats = observations.aggregate(
            avg_temperature=Avg('temperature'),
            min_temperature=Min('temperature'),
            max_temperature=Max('temperature'),
            total_precipitation=Sum('precipitation'),
            avg_precipitation=Avg('precipitation'),
            avg_humidity=Avg('relative_humidity'),
            min_humidity=Min('relative_humidity'),
            max_humidity=Max('relative_humidity'),
            avg_wind_speed=Avg('wind_speed'),
            max_wind_speed=Max('wind_speed'),
            total_observations=Count('id'),
        )
        
        # Add station info and date range
        stats['station_code'] = station.station_code
        stats['station_name'] = station.name
        stats['start_date'] = start_date
        stats['end_date'] = end_date
        
        serializer = WeatherStatisticsSerializer(data=stats)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)


class HourlyObservationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing hourly observations.
    
    list: Get observations with filtering
    retrieve: Get a specific observation
    recent: Get recent observations across all stations
    """
    serializer_class = HourlyObservationSerializer
    
    def get_queryset(self):
        """
        Filter observations based on query parameters.
        
        Query params:
        - station: Filter by station ID
        - station_id: Filter by station's station_id field
        - start_date: Filter observations after this date (ISO format)
        - end_date: Filter observations before this date (ISO format)
        - hours: Get observations from last N hours
        - limit: Limit number of results (default: 100, max: 1000)
        """
        queryset = HourlyObservation.objects.select_related('station').all()
        
        # Filter by station (database ID)
        station = self.request.query_params.get('station')
        if station:
            queryset = queryset.filter(station_id=station)
        
        # Filter by station_code (BCWS station code)
        station_code = self.request.query_params.get('station_code')
        if station_code:
            queryset = queryset.filter(station__station_code=station_code)
        
        # Date range filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        hours = self.request.query_params.get('hours')
        
        if hours:
            cutoff = timezone.now() - timedelta(hours=int(hours))
            queryset = queryset.filter(observation_time__gte=cutoff)
        else:
            if start_date:
                from dateutil import parser
                queryset = queryset.filter(observation_time__gte=parser.parse(start_date))
            if end_date:
                from dateutil import parser
                queryset = queryset.filter(observation_time__lte=parser.parse(end_date))
        
        # Apply limit
        limit = self.request.query_params.get('limit', '100')
        try:
            limit = min(int(limit), 1000)  # Max 1000 results
        except ValueError:
            limit = 100
        
        return queryset[:limit]
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get most recent observations across all stations.
        
        Query params:
        - hours: Number of hours back (default: 1)
        - limit: Max results per station (default: 1)
        """
        hours = int(request.query_params.get('hours', '1'))
        limit = int(request.query_params.get('limit', '1'))
        
        cutoff = timezone.now() - timedelta(hours=hours)
        
        # Get most recent observation for each station
        observations = []
        stations = WeatherStation.objects.filter(
            observations__observation_time__gte=cutoff
        ).distinct()
        
        for station in stations:
            recent = station.observations.filter(
                observation_time__gte=cutoff
            )[:limit]
            observations.extend(recent)
        
        # Sort by time
        observations.sort(key=lambda x: x.observation_time, reverse=True)
        
        serializer = HourlyObservationSerializer(observations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Get the single most recent observation for each station.
        Returns a map of station_code -> observation.
        """
        latest_observations = {}
        
        # Get stations with data
        stations = WeatherStation.objects.filter(
            observations__isnull=False
        ).distinct()
        
        for station in stations:
            latest = station.observations.first()
            if latest:
                latest_observations[station.station_code] = HourlyObservationSerializer(latest).data
        
        return Response(latest_observations)
