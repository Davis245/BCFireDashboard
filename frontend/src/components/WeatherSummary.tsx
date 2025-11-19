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
            {observation.temperature ? parseFloat(observation.temperature).toFixed(1) : 'N/A'}°C
          </div>
          <div className="summary-details">
            {observation.hourly_ffmc && (
              <div>FFMC: {parseFloat(observation.hourly_ffmc).toFixed(1)}</div>
            )}
            {observation.danger_rating && (
              <div>Danger: {observation.danger_rating}</div>
            )}
          </div>
        </div>

        <div className="summary-card">
          <h3>Humidity</h3>
          <div className="summary-value">
            {observation.relative_humidity ?? 'N/A'}%
          </div>
        </div>

        <div className="summary-card">
          <h3>Wind</h3>
          <div className="summary-value">
            {observation.wind_speed ? parseFloat(observation.wind_speed).toFixed(1) : 'N/A'} km/h
          </div>
          <div className="summary-details">
            Direction: {observation.wind_direction ? `${observation.wind_direction}°` : 'N/A'}
            {observation.wind_gust && (
              <div>Gust: {parseFloat(observation.wind_gust).toFixed(1)} km/h</div>
            )}
          </div>
        </div>

        <div className="summary-card">
          <h3>Precipitation</h3>
          <div className="summary-value">
            {observation.precipitation ? parseFloat(observation.precipitation).toFixed(1) : '0.0'} mm
          </div>
        </div>

        {observation.hourly_fwi && (
          <div className="summary-card">
            <h3>Fire Weather Index</h3>
            <div className="summary-value">
              {parseFloat(observation.hourly_fwi).toFixed(1)}
            </div>
            {observation.danger_rating && (
              <div className="summary-details">
                Rating: {observation.danger_rating}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="observation-time">
        Last updated: {new Date(observation.observation_time).toLocaleString()}
      </div>
    </div>
  );
};
