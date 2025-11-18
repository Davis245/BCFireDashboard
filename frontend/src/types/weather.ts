// Type definitions for weather data and stations
export interface WeatherStation {
  id: number;
  station_id: string;
  name: string;
  province: string;
  latitude: number;
  longitude: number;
  elevation: number | null;
  is_active: boolean;
}

export interface HourlyObservation {
  id: number;
  station: number;
  observation_time: string;
  temperature: number | null;
  dew_point: number | null;
  rel_humidity: number | null;
  wind_direction: string | null;
  wind_speed: number | null;
  visibility: number | null;
  station_pressure: number | null;
  humidex: number | null;
  wind_chill: number | null;
  weather: string | null;
  precipitation: number | null;
}

export interface StationWithObservations extends WeatherStation {
  recent_observations: HourlyObservation[];
}

export interface WeatherStatistics {
  avg_temperature: number | null;
  min_temperature: number | null;
  max_temperature: number | null;
  avg_humidity: number | null;
  total_precipitation: number | null;
  observation_count: number;
}

export interface DateRange {
  start_date: string;
  end_date: string;
}

export interface LatestObservationsMap {
  [stationId: number]: HourlyObservation;
}
