import { useState, useEffect } from 'react';
import { WeatherMap } from '../components/WeatherMap';
import { StationList } from '../components/StationList';
import { WeatherSummary } from '../components/WeatherSummary';
import { weatherStationsAPI, observationsAPI } from '../services/api';
import type { WeatherStation, LatestObservationsMap } from '../types/weather';

export const Dashboard = () => {
  const [stations, setStations] = useState<WeatherStation[]>([]);
  const [latestObservations, setLatestObservations] = useState<LatestObservationsMap>({});
  const [selectedStation, setSelectedStation] = useState<WeatherStation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch stations with data
      const stationsData = await weatherStationsAPI.getAll({
        has_data: true,
        active: true,
      });
      setStations(stationsData);

      // Fetch latest observations for all stations
      const latestData = await observationsAPI.getLatest();
      setLatestObservations(latestData);

      // Select first station by default
      if (stationsData.length > 0) {
        setSelectedStation(stationsData[0]);
      }
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleStationSelect = (station: WeatherStation) => {
    setSelectedStation(station);
  };

  if (loading) {
    return <div className="loading">Loading weather data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (stations.length === 0) {
    return <div className="no-data">No weather stations found with data.</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-main">
        <WeatherMap
          stations={stations}
          latestObservations={latestObservations}
          selectedStation={selectedStation}
          onStationSelect={handleStationSelect}
        />
        <WeatherSummary
          station={selectedStation}
          observation={selectedStation ? latestObservations[selectedStation.id] : null}
        />
      </div>
      <StationList
        stations={stations}
        latestObservations={latestObservations}
        selectedStation={selectedStation}
        onStationSelect={handleStationSelect}
      />
    </div>
  );
};
