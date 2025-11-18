import { Link } from 'react-router-dom';
import type { WeatherStation, HourlyObservation } from '../types/weather';

interface WeatherSummaryProps {
  station: WeatherStation | null;
  observation: HourlyObservation | null;
}

export const WeatherSummary = ({ station, observation }: WeatherSummaryProps) => {
  if (!station) {
    return (
      <div className="weather-summary">
        <p>Select a station to view current conditions</p>
      </div>
    );
  }

  if (!observation) {
    return (
      <div className="weather-summary">
        <h2>{station.name}</h2>
        <p>No recent observations available</p>
      </div>
    );
  }

  const windDirectionToCompass = (dir: string | null): string => {
    return dir || 'N/A';
  };

  return (
    <div className="weather-summary">
      <div className="summary-header">
        <h2>{station.name}</h2>
        <Link to={`/station/${station.id}`} className="details-link">
          View Details →
        </Link>
      </div>

      <div className="summary-grid">
        <div className="summary-card">
          <h3>Temperature</h3>
          <div className="summary-value">
            {observation.temperature?.toFixed(1) ?? 'N/A'}°C
          </div>
          <div className="summary-details">
            {observation.dew_point && (
              <div>Dew Point: {observation.dew_point.toFixed(1)}°C</div>
            )}
            {observation.humidex && (
              <div>Humidex: {observation.humidex.toFixed(1)}</div>
            )}
            {observation.wind_chill && (
              <div>Wind Chill: {observation.wind_chill.toFixed(1)}°C</div>
            )}
          </div>
        </div>

        <div className="summary-card">
          <h3>Humidity</h3>
          <div className="summary-value">
            {observation.rel_humidity?.toFixed(0) ?? 'N/A'}%
          </div>
        </div>

        <div className="summary-card">
          <h3>Wind</h3>
          <div className="summary-value">
            {observation.wind_speed?.toFixed(1) ?? 'N/A'} km/h
          </div>
          <div className="summary-details">
            Direction: {windDirectionToCompass(observation.wind_direction)}
          </div>
        </div>

        <div className="summary-card">
          <h3>Precipitation</h3>
          <div className="summary-value">
            {observation.precipitation?.toFixed(1) ?? '0.0'} mm
          </div>
        </div>

        <div className="summary-card">
          <h3>Pressure</h3>
          <div className="summary-value">
            {observation.station_pressure?.toFixed(1) ?? 'N/A'} kPa
          </div>
        </div>

        <div className="summary-card">
          <h3>Visibility</h3>
          <div className="summary-value">
            {observation.visibility?.toFixed(1) ?? 'N/A'} km
          </div>
        </div>
      </div>

      {observation.weather && (
        <div className="weather-condition">
          <strong>Conditions:</strong> {observation.weather}
        </div>
      )}

      <div className="observation-time">
        Last updated: {new Date(observation.observation_time).toLocaleString()}
      </div>
    </div>
  );
};
