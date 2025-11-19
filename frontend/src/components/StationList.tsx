import { useState, useMemo } from 'react';
import type { WeatherStation, LatestObservationsMap } from '../types/weather';

interface StationListProps {
  stations: WeatherStation[];
  latestObservations: LatestObservationsMap;
  selectedStation: WeatherStation | null;
  onStationSelect: (station: WeatherStation) => void;
}

export const StationList = ({
  stations,
  latestObservations,
  selectedStation,
  onStationSelect,
}: StationListProps) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'temperature'>('name');

  const filteredStations = useMemo(() => {
    let filtered = stations.filter((station) =>
      station.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    filtered.sort((a, b) => {
      if (sortBy === 'name') {
        return a.name.localeCompare(b.name);
      } else {
        const tempA = parseFloat(latestObservations[a.id]?.temperature ?? '-999');
        const tempB = parseFloat(latestObservations[b.id]?.temperature ?? '-999');
        return tempB - tempA;
      }
    });

    return filtered;
  }, [stations, searchTerm, sortBy, latestObservations]);

  return (
    <div className="station-list">
      <div className="station-list-header">
        <h3>Weather Stations ({filteredStations.length})</h3>
        <input
          type="text"
          placeholder="Search stations..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as 'name' | 'temperature')}
          className="sort-select"
        >
          <option value="name">Sort by Name</option>
          <option value="temperature">Sort by Temperature</option>
        </select>
      </div>
      <div className="stations-container">
        {filteredStations.map((station) => {
          const observation = latestObservations[station.id];
          const isSelected = selectedStation?.id === station.id;

          return (
            <div
              key={station.id}
              className={`station-item ${isSelected ? 'selected' : ''}`}
              onClick={() => onStationSelect(station)}
            >
              <h4>{station.name}</h4>
              {observation ? (
                <div className="station-data">
                  <div className="data-row">
                    <span className="data-label">Temp:</span>
                    <span className="data-value">
                      {observation.temperature ? parseFloat(observation.temperature).toFixed(1) : 'N/A'}°C
                    </span>
                  </div>
                  <div className="data-row">
                    <span className="data-label">Humidity:</span>
                    <span className="data-value">
                      {observation.relative_humidity ?? 'N/A'}%
                    </span>
                  </div>
                  <div className="data-row">
                    <span className="data-label">Wind:</span>
                    <span className="data-value">
                      {observation.wind_speed ? parseFloat(observation.wind_speed).toFixed(1) : 'N/A'} km/h{' '}
                      {observation.wind_direction || ''}
                    </span>
                  </div>
                </div>
              ) : (
                <p className="no-data">No recent data</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
