// API service utilities
import axios from 'axios';
import type {
  WeatherStation,
  HourlyObservation,
  StationWithObservations,
  WeatherStatistics,
  LatestObservationsMap,
} from '../types/weather';

const API_BASE_URL = '/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to format dates for API
export const formatDateForAPI = (date: Date): string => {
  return date.toISOString().split('T')[0];
};

// Weather Stations API
export const weatherStationsAPI = {
  getAll: async (params?: {
    active?: boolean;
    has_data?: boolean;
    search?: string;
  }): Promise<WeatherStation[]> => {
    const response = await api.get<WeatherStation[]>('/stations/', { params });
    return response.data;
  },

  getById: async (id: number): Promise<WeatherStation> => {
    const response = await api.get<WeatherStation>(`/stations/${id}/`);
    return response.data;
  },

  getWithObservations: async (
    id: number,
    hours: number = 168
  ): Promise<StationWithObservations> => {
    const response = await api.get<StationWithObservations>(
      `/stations/${id}/with_observations/`,
      { params: { hours } }
    );
    return response.data;
  },

  getStatistics: async (
    id: number,
    startDate?: string,
    endDate?: string
  ): Promise<WeatherStatistics> => {
    const response = await api.get<WeatherStatistics>(
      `/stations/${id}/statistics/`,
      { params: { start_date: startDate, end_date: endDate } }
    );
    return response.data;
  },
};

// Observations API
export const observationsAPI = {
  getAll: async (params?: {
    station?: number;
    start_date?: string;
    end_date?: string;
    limit?: number;
  }): Promise<HourlyObservation[]> => {
    const response = await api.get<HourlyObservation[]>('/observations/', { params });
    return response.data;
  },

  getById: async (id: number): Promise<HourlyObservation> => {
    const response = await api.get<HourlyObservation>(`/observations/${id}/`);
    return response.data;
  },

  getRecent: async (hours: number = 24): Promise<HourlyObservation[]> => {
    const response = await api.get<HourlyObservation[]>('/observations/recent/', {
      params: { hours },
    });
    return response.data;
  },

  getLatest: async (): Promise<LatestObservationsMap> => {
    const response = await api.get<LatestObservationsMap>('/observations/latest/');
    return response.data;
  },
};

// Helper functions for wind direction
export const windDirectionToCompass = (degrees: number | null): string => {
  if (degrees === null) return 'N/A';
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  const index = Math.round(degrees / 45) % 8;
  return directions[index];
};

export const windDirectionToDegrees = (direction: string | null): number | null => {
  if (!direction) return null;
  const directions: { [key: string]: number } = {
    N: 0,
    NE: 45,
    E: 90,
    SE: 135,
    S: 180,
    SW: 225,
    W: 270,
    NW: 315,
  };
  return directions[direction.toUpperCase()] || null;
};
