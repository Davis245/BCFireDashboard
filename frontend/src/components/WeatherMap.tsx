import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { WeatherStation, HourlyObservation, LatestObservationsMap } from '../types/weather';

// Fix for default marker icon
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

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

      const observation = latestObservations[station.id];
      const temp = observation?.temperature;
      const color = getTemperatureColor(temp);

      const marker = L.circleMarker([station.latitude, station.longitude], {
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
            <p>Temperature: ${observation.temperature?.toFixed(1) || 'N/A'}°C</p>
            <p>Humidity: ${observation.rel_humidity?.toFixed(0) || 'N/A'}%</p>
            <p>Wind: ${observation.wind_speed?.toFixed(1) || 'N/A'} km/h</p>
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
