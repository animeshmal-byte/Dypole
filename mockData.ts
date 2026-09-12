import { StatusResponse, ScheduleResponse, TelemetryMetrics } from '../types';

export const mockNormalStatus: StatusResponse = {
  severity: "normal",
  battery: {
    capacity_kwh: 5.4,
    usable_kwh: 2.6,
    current_kwh: 3.3,
    discharge_kw: 1.1
  },
  diesel_health: 78,
  restock_days_remaining: 4
};

export const mockNormalSchedule: ScheduleResponse = [
  { hour: 0, diesel_kw: 0, solar_kw: 2.1, wind_kw: 1.4, battery_kw: 0, demand_kw: 3.0, battery_soc_after: 3.3, reason: "Solar and wind cover demand" },
  { hour: 1, diesel_kw: 0, solar_kw: 2.3, wind_kw: 1.5, battery_kw: 0, demand_kw: 3.2, battery_soc_after: 3.5, reason: "Surplus renewable generation routed to BESS storage charging" },
  { hour: 2, diesel_kw: 0, solar_kw: 2.6, wind_kw: 1.3, battery_kw: 0, demand_kw: 3.4, battery_soc_after: 3.8, reason: "Solar irradiance peak; zero-diesel baseline fully preserved" },
  { hour: 3, diesel_kw: 0, solar_kw: 2.8, wind_kw: 1.2, battery_kw: 0, demand_kw: 3.6, battery_soc_after: 4.0, reason: "High solar yield; station life-support and laboratories on 100% clean power" },
  { hour: 4, diesel_kw: 0, solar_kw: 2.5, wind_kw: 1.4, battery_kw: 0, demand_kw: 3.5, battery_soc_after: 4.2, reason: "Solar and wind balancing HVAC and deep-ice sensor arrays" },
  { hour: 5, diesel_kw: 0, solar_kw: 2.0, wind_kw: 1.6, battery_kw: 0, demand_kw: 3.4, battery_soc_after: 4.3, reason: "Wind pickup offsetting solar azimuth reduction; battery fully saturated" },
  { hour: 6, diesel_kw: 0, solar_kw: 1.4, wind_kw: 1.8, battery_kw: 0.2, demand_kw: 3.4, battery_soc_after: 4.2, reason: "BESS storage micro-discharge smoothing dusk transition" },
  { hour: 7, diesel_kw: 0, solar_kw: 0.8, wind_kw: 1.9, battery_kw: 0.6, demand_kw: 3.3, battery_soc_after: 4.0, reason: "Battery buffering wind variance during low-horizon sun elevation" },
  { hour: 8, diesel_kw: 0, solar_kw: 0.3, wind_kw: 2.0, battery_kw: 1.0, demand_kw: 3.3, battery_soc_after: 3.7, reason: "Wind turbine generation maintaining primary grid frequency (50.02 Hz)" },
  { hour: 9, diesel_kw: 0.4, solar_kw: 0.0, wind_kw: 1.8, battery_kw: 1.1, demand_kw: 3.3, battery_soc_after: 3.5, reason: "Diesel generator standby warm-up; minimal dispatch for voltage support" },
  { hour: 10, diesel_kw: 0.8, solar_kw: 0.0, wind_kw: 1.6, battery_kw: 0.9, demand_kw: 3.3, battery_soc_after: 3.3, reason: "Night cycle power balance maintained within optimal diesel efficiency envelope" },
  { hour: 11, diesel_kw: 0.5, solar_kw: 0.2, wind_kw: 1.7, battery_kw: 0.8, demand_kw: 3.2, battery_soc_after: 3.2, reason: "Dawn solar emergence; diesel throttle back sequence initiated" },
];

export const mockBlizzardStatus: StatusResponse = {
  severity: "emergency",
  battery: {
    capacity_kwh: 5.4,
    usable_kwh: 2.6,
    current_kwh: 1.8,
    discharge_kw: 3.2
  },
  diesel_health: 64,
  restock_days_remaining: 2
};

export const mockBlizzardSchedule: ScheduleResponse = [
  { hour: 0, diesel_kw: 3.2, solar_kw: 0.0, wind_kw: 0.8, battery_kw: 1.2, demand_kw: 5.2, battery_soc_after: 3.1, reason: "Katabatic blizzard: High wind shear, zero solar PV, diesel genset #1 primary" },
  { hour: 1, diesel_kw: 3.5, solar_kw: 0.0, wind_kw: 0.5, battery_kw: 1.4, demand_kw: 5.4, battery_soc_after: 2.9, reason: "Diesel ramp-up to support station life-support and heating circuits" },
  { hour: 2, diesel_kw: 3.5, solar_kw: 0.0, wind_kw: 0.4, battery_kw: 1.6, demand_kw: 5.5, battery_soc_after: 2.6, reason: "Peak blizzard load; battery buffer discharging near cutoff limit" },
  { hour: 3, diesel_kw: 3.8, solar_kw: 0.0, wind_kw: 0.6, battery_kw: 1.2, demand_kw: 5.6, battery_soc_after: 2.4, reason: "Full diesel generation dispatch; BESS discharge throttled to protect cell temp" },
  { hour: 4, diesel_kw: 3.6, solar_kw: 0.0, wind_kw: 0.9, battery_kw: 0.8, demand_kw: 5.3, battery_soc_after: 2.3, reason: "Wind speed fluctuating between 55-75 kt; turbine pitch feathering active" },
  { hour: 5, diesel_kw: 3.4, solar_kw: 0.0, wind_kw: 1.2, battery_kw: 0.6, demand_kw: 5.2, battery_soc_after: 2.2, reason: "Turbine generator #2 re-engaged on microgrid bus" },
  { hour: 6, diesel_kw: 3.0, solar_kw: 0.1, wind_kw: 1.5, battery_kw: 0.4, demand_kw: 5.0, battery_soc_after: 2.1, reason: "Diffuse twilight solar detection; diesel throttling down baseline" },
  { hour: 7, diesel_kw: 2.8, solar_kw: 0.3, wind_kw: 1.6, battery_kw: 0.2, demand_kw: 4.9, battery_soc_after: 2.1, reason: "Wind gust stability improving; BESS float charging initiated" },
  { hour: 8, diesel_kw: 2.4, solar_kw: 0.6, wind_kw: 1.8, battery_kw: 0.0, demand_kw: 4.8, battery_soc_after: 2.2, reason: "Wind-diesel hybrid balancing active; battery reserve preserved" },
  { hour: 9, diesel_kw: 2.0, solar_kw: 0.9, wind_kw: 1.8, battery_kw: 0.0, demand_kw: 4.7, battery_soc_after: 2.3, reason: "Renewable penetration increasing to 57%" },
  { hour: 10, diesel_kw: 1.5, solar_kw: 1.2, wind_kw: 1.9, battery_kw: 0.0, demand_kw: 4.6, battery_soc_after: 2.5, reason: "Diesel gen transitioned to low idle standby mode" },
  { hour: 11, diesel_kw: 0.8, solar_kw: 1.5, wind_kw: 2.1, battery_kw: 0.0, demand_kw: 4.4, battery_soc_after: 2.8, reason: "Microgrid stabilized; blizzard warning downgrade in progress" },
];

export const normalTelemetry: TelemetryMetrics = {
  ambientTemp: -38,
  windSpeed: 48,
  windDir: 'SSE',
  syncLatency: 42,
  busFrequency: 50.02,
  peakCapacity: 280.0,
  solarElevation: 12.4,
  katabaticWindProj: 50,
  internalCellTemp: 14.2,
  healthCycleIndex: 97.8,
  fuelReservePct: 52,
  fuelReserveLiters: 14200,
  runningHours: 4120.4,
  serviceRemainHours: 379.5,
  exhaustTemp: 342,
};

export const blizzardTelemetry: TelemetryMetrics = {
  ambientTemp: -47,
  windSpeed: 68,
  windDir: 'S',
  syncLatency: 88,
  busFrequency: 49.85,
  peakCapacity: 280.0,
  solarElevation: 0.0,
  katabaticWindProj: 75,
  internalCellTemp: 8.4,
  healthCycleIndex: 96.1,
  fuelReservePct: 41,
  fuelReserveLiters: 11200,
  runningHours: 4148.2,
  serviceRemainHours: 351.7,
  exhaustTemp: 418,
};

export interface HistoryPoint {
  time: string;
  offsetHours: number;
  wind: number;
  solar: number;
  bess: number;
  diesel: number;
  demand: number;
}

export const generate72HourHistory = (scenario: 'normal' | 'blizzard'): HistoryPoint[] => {
  const points: HistoryPoint[] = [];
  const hours = 72;
  for (let i = 0; i <= hours; i += 3) {
    const t = hours - i;
    const label = t === 0 ? 'CURRENT DISPATCH (T-0)' : `T -${t} HOURS`;
    
    if (scenario === 'blizzard') {
      const blizzardIntensity = Math.sin((i / 72) * Math.PI);
      points.push({
        time: label,
        offsetHours: -t,
        wind: parseFloat((18 + Math.random() * 8 + (1 - blizzardIntensity) * 15).toFixed(1)),
        solar: parseFloat((Math.max(0, Math.sin((i % 24) / 24 * Math.PI * 2) * 5 * (1 - blizzardIntensity * 0.9))).toFixed(1)),
        bess: parseFloat((12 + Math.random() * 6).toFixed(1)),
        diesel: parseFloat((25 + blizzardIntensity * 35 + Math.random() * 8).toFixed(1)),
        demand: parseFloat((65 + blizzardIntensity * 20).toFixed(1)),
      });
    } else {
      const cycle = Math.sin((i % 24) / 24 * Math.PI * 2);
      const solarVal = Math.max(0, cycle * 42 + 5);
      const windVal = 50 + Math.sin(i / 12) * 15 + Math.random() * 8;
      const bessVal = Math.max(8, 25 + Math.cos(i / 8) * 12);
      const dieselVal = solarVal + windVal + bessVal > 120 ? 8 + Math.random() * 4 : 18 + Math.random() * 6;
      points.push({
        time: label,
        offsetHours: -t,
        wind: parseFloat(windVal.toFixed(1)),
        solar: parseFloat(solarVal.toFixed(1)),
        bess: parseFloat(bessVal.toFixed(1)),
        diesel: parseFloat(dieselVal.toFixed(1)),
        demand: parseFloat((solarVal + windVal + bessVal + dieselVal - 8).toFixed(1)),
      });
    }
  }
  return points;
};

export interface ForecastPoint {
  time: string;
  actual: number | null;
  predicted: number | null;
  upperConfidence: number | null;
  lowerConfidence: number | null;
  threshold: number;
}

export const generate24HourForecast = (scenario: 'normal' | 'blizzard'): ForecastPoint[] => {
  const points: ForecastPoint[] = [];
  const labels = ['-6H', '-5H', '-4H', '-3H', '-2H', '-1H', 'NOW (T-0)', '+2H', '+4H', '+6H [SUNRISE]', '+8H', '+10H', '+12H', '+14H', '+16H', '+18H', '+20H', '+22H', '+24H'];
  
  labels.forEach((label, idx) => {
    const isPastOrNow = idx <= 6;
    
    let baseLoad = 135 + Math.sin(idx * 0.4) * 22 + Math.cos(idx * 0.2) * 10;
    if (scenario === 'blizzard') baseLoad += 35;

    const actual = isPastOrNow ? parseFloat(baseLoad.toFixed(1)) : null;
    const predicted = idx >= 6 ? parseFloat((baseLoad + (idx === 6 ? 0 : Math.sin(idx * 0.5) * 6)).toFixed(1)) : null;
    const upperConfidence = predicted !== null ? parseFloat((predicted * 1.046).toFixed(1)) : null;
    const lowerConfidence = predicted !== null ? parseFloat((predicted * 0.954).toFixed(1)) : null;

    points.push({
      time: label,
      actual,
      predicted,
      upperConfidence,
      lowerConfidence,
      threshold: 180,
    });
  });

  return points;
};
