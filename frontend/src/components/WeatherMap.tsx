import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { WeatherStation, LatestObservationsMap } from '../types/weather';

// Fix for default marker icon
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface WeatherMapProps {
  stations: WeatherStation[];
  latestObservations: LatestObservationsMap;
  selectedStation: WeatherStation | null;
  onStationSelect: (station: WeatherStation) => void;
}

export const WeatherMap = ({
  stations,
  latestObservations,
  selectedStation,
  onStationSelect,
}: WeatherMapProps) => {
  const mapRef = useRef<L.Map | null>(null);
  const markersRef = useRef<Map<number, L.CircleMarker>>(new Map());

  useEffect(() => {
    // Initialize map
    if (!mapRef.current) {
      mapRef.current = L.map('weather-map').setView([54.0, -125.0], 6);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
      }).addTo(mapRef.current);
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;

    // Clear existing markers
    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current.clear();

    // Add markers for each station
    stations.forEach((station) => {
      if (!station.latitude || !station.longitude) return;

      const lat = parseFloat(station.latitude);
      const lon = parseFloat(station.longitude);
      
      if (isNaN(lat) || isNaN(lon)) return;

      const observation = latestObservations[station.station_code];
      const temp = observation?.temperature ? parseFloat(observation.temperature) : null;
      const color = getTemperatureColor(temp);

      const marker = L.circleMarker([lat, lon], {
        radius: selectedStation?.id === station.id ? 10 : 6,
        fillColor: color,
        color: '#fff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8,
      }).addTo(mapRef.current!);

      // Add popup
      const popupContent = `
        <div class="map-popup">
          <h3>${station.name}</h3>
          ${
            observation
              ? `
            <p>Temperature: ${observation.temperature ? parseFloat(observation.temperature).toFixed(1) : 'N/A'}°C</p>
            <p>Humidity: ${observation.relative_humidity || 'N/A'}%</p>
            <p>Wind: ${observation.wind_speed ? parseFloat(observation.wind_speed).toFixed(1) : 'N/A'} km/h</p>
          `
              : '<p>No recent data</p>'
          }
        </div>
      `;
      marker.bindPopup(popupContent);

      // Add click handler
      marker.on('click', () => {
        onStationSelect(station);
      });

      markersRef.current.set(station.id, marker);
    });
  }, [stations, latestObservations, selectedStation, onStationSelect]);

  return <div id="weather-map" style={{ height: '500px', width: '100%' }} />;
};

const getTemperatureColor = (temp: number | null | undefined): string => {
  if (temp === null || temp === undefined) return '#999';
  if (temp < -20) return '#0000ff';
  if (temp < -10) return '#4169e1';
  if (temp < 0) return '#87ceeb';
  if (temp < 10) return '#90ee90';
  if (temp < 15) return '#ffff00';
  if (temp < 20) return '#ffa500';
  if (temp < 25) return '#ff6347';
  if (temp < 30) return '#ff0000';
  if (temp < 35) return '#8b0000';
  return '#4b0000';
};
