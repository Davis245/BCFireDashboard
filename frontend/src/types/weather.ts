// Type definitions for weather data and stations
export interface WeatherStation {
  id: number
  name: string
  latitude: number
  longitude: number
}

export interface WeatherData {
  id: number
  station: number
  timestamp: string
  temperature: number
  humidity: number
  windSpeed: number
  precipitation: number
}

// Additional types will be defined here
