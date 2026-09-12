import http from 'http';

const PORT = process.env.PORT || 8000;

// Scenario states for mock server
let currentScenario = 'normal'; // 'normal' | 'blizzard'

const getStatusData = (scenario) => {
  if (scenario === 'blizzard') {
    return {
      severity: 'emergency',
      battery: {
        capacity_kwh: 5.4,
        usable_kwh: 2.6,
        current_kwh: 1.8,
        discharge_kw: 3.2,
      },
      diesel_health: 64,
      restock_days_remaining: 2,
    };
  }
  return {
    severity: 'normal',
    battery: {
      capacity_kwh: 5.4,
      usable_kwh: 2.6,
      current_kwh: 3.3,
      discharge_kw: 1.1,
    },
    diesel_health: 78,
    restock_days_remaining: 4,
  };
};

const getScheduleData = (scenario) => {
  if (scenario === 'blizzard') {
    return [
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
  }

  return [
    { hour: 0, diesel_kw: 0, solar_kw: 2.1, wind_kw: 1.4, battery_kw: 0, demand_kw: 3.0, battery_soc_after: 3.3, reason: "Solar and wind cover demand" },
    { hour: 1, diesel_kw: 0, solar_kw: 2.3, wind_kw: 1.5, battery_kw: 0, demand_kw: 3.2, battery_soc_after: 3.5, reason: "Surplus renewable generation routed to BESS storage charging" },
    { hour: 2, diesel_kw: 0, solar_kw: 2.6, wind_kw: 1.3, battery_kw: 0, demand_kw: 3.4, battery_soc_after: 3.8, reason: "Solar irradiance peak; zero-emission baseline fully sustained" },
    { hour: 3, diesel_kw: 0, solar_kw: 2.8, wind_kw: 1.2, battery_kw: 0, demand_kw: 3.6, battery_soc_after: 4.0, reason: "High solar yield; station life-support and labs on 100% renewables" },
    { hour: 4, diesel_kw: 0, solar_kw: 2.5, wind_kw: 1.4, battery_kw: 0, demand_kw: 3.5, battery_soc_after: 4.2, reason: "Solar and wind generation balancing station HVAC and scientific sensors" },
    { hour: 5, diesel_kw: 0, solar_kw: 2.0, wind_kw: 1.6, battery_kw: 0, demand_kw: 3.4, battery_soc_after: 4.3, reason: "Wind pickup offsetting solar azimuth angle reduction" },
    { hour: 6, diesel_kw: 0, solar_kw: 1.4, wind_kw: 1.8, battery_kw: 0.2, demand_kw: 3.4, battery_soc_after: 4.2, reason: "BESS storage mild discharge smoothing dusk transition" },
    { hour: 7, diesel_kw: 0, solar_kw: 0.8, wind_kw: 1.9, battery_kw: 0.6, demand_kw: 3.3, battery_soc_after: 4.0, reason: "Battery buffering wind variance during low-angle solar phase" },
    { hour: 8, diesel_kw: 0, solar_kw: 0.3, wind_kw: 2.0, battery_kw: 1.0, demand_kw: 3.3, battery_soc_after: 3.7, reason: "Wind turbine generation maintaining primary grid frequency" },
    { hour: 9, diesel_kw: 0.4, solar_kw: 0.0, wind_kw: 1.8, battery_kw: 1.1, demand_kw: 3.3, battery_soc_after: 3.5, reason: "Diesel generator standby warm-up; minimal dispatch for voltage support" },
    { hour: 10, diesel_kw: 0.8, solar_kw: 0.0, wind_kw: 1.6, battery_kw: 0.9, demand_kw: 3.3, battery_soc_after: 3.3, reason: "Night cycle power balance maintained within optimal diesel efficiency" },
    { hour: 11, diesel_kw: 0.5, solar_kw: 0.2, wind_kw: 1.7, battery_kw: 0.8, demand_kw: 3.2, battery_soc_after: 3.2, reason: "Dawn solar emergence; diesel throttle back sequence initiated" },
  ];
};

const server = http.createServer((req, res) => {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  const url = new URL(req.url, `http://${req.headers.host}`);

  // Scenario toggle endpoint for convenience
  if (url.pathname === '/scenario' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const parsed = JSON.parse(body);
        if (parsed.scenario) {
          currentScenario = parsed.scenario;
        }
      } catch (e) {}
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ currentScenario }));
    });
    return;
  }

  if (url.pathname === '/status') {
    const data = getStatusData(currentScenario);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data, null, 2));
    return;
  }

  if (url.pathname === '/schedule') {
    const data = getScheduleData(currentScenario);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data, null, 2));
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Endpoint not found', available: ['/status', '/schedule'] }));
});

server.listen(PORT, () => {
  console.log(`📡 Polar Station Mock API Server listening on http://localhost:${PORT}`);
  console.log(`   GET http://localhost:${PORT}/status`);
  console.log(`   GET http://localhost:${PORT}/schedule`);
});
