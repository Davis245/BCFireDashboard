// Type definitions for weather data and stations
export interface WeatherStation {
  id: number;
  station_code: string;
  name: string;
  province: string;
  latitude: string | null;
  longitude: string | null;
  elevation: string | null;
  is_active: boolean;
  last_updated?: string | null;
}

export interface HourlyObservation {
  id: number;
  station: number;
  station_code?: string;
  station_name?: string;
  observation_time: string;
  temperature: string | null;
  relative_humidity: number | null;
  precipitation: string | null;
  wind_direction: number | null;
  wind_speed: string | null;
  wind_gust: string | null;
  hourly_ffmc: string | null;
  hourly_isi: string | null;
  hourly_fwi: string | null;
  ffmc: string | null;
  dmc: string | null;
  dc: string | null;
  isi: string | null;
  bui: string | null;
  fwi: string | null;
  danger_rating: string | null;
  snow_depth: string | null;
  solar_radiation: string | null;
}

export interface StationWithObservations extends WeatherStation {
  recent_observations: HourlyObservation[];
}

export interface WeatherStatistics {
  station_code: string;
  station_name: string;
  start_date: string;
  end_date: string;
  avg_temperature: string | null;
  min_temperature: string | null;
  max_temperature: string | null;
  total_precipitation: string | null;
  avg_precipitation: string | null;
  avg_humidity: string | null;
  min_humidity: number | null;
  max_humidity: number | null;
  avg_wind_speed: string | null;
  max_wind_speed: string | null;
  total_observations: number;
}

export interface DateRange {
  start_date: string;
  end_date: string;
}

export interface LatestObservationsMap {
  [stationCode: string]: HourlyObservation;
}
