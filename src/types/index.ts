export interface Driver {
  id: string;
  name: string;
  team: string;
  color: string;
  number: number;
}

export interface LapData {
  lapNumber: number;
  lapTime: number;
  sector1: number;
  sector2: number;
  sector3: number;
  speed: number;
  position: number;
  compound: string;
  tyreLife: number;
}

export interface TelemetryData {
  distance: number;
  speed: number;
  throttle: number;
  brake: number;
  gear: number;
  rpm: number;
  drs: boolean;
}

export interface SessionInfo {
  year: number;
  grandPrix: string;
  sessionType: string;
  date: string;
  trackName: string;
  lapRecord?: string;
  weather?: string;
}

export interface RacePosition {
  lap: number;
  position: number;
  driver: string;
  team: string;
}

export interface TireStrategy {
  driver: string;
  stints: Array<{
    compound: string;
    startLap: number;
    endLap: number;
    lapCount: number;
  }>;
}

export interface WeatherData {
  time: string;
  airTemp: number;
  humidity: number;
  pressure: number;
  rainfall: boolean;
  trackTemp: number;
  windDirection: number;
  windSpeed: number;
}