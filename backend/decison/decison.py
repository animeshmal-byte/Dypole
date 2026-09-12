def dispatch_energy(consumption, solar, wind, diesel_capacity=None):
    """
    Decide how to meet energy consumption from solar, wind, and diesel.

    Parameters:
        consumption (float): required energy (x)
        solar (float): energy produced by solar (y)
        wind (float): energy produced by wind (z)
        diesel_capacity (float, optional): max diesel can supply.
            If None, assumed unlimited.

    Returns:
        dict with:
            solar_used, wind_used, diesel_used,
            battery_charge (excess renewable sent to battery),
            unmet_demand (if diesel_capacity can't cover the gap)
    """
    renewable_total = solar + wind

    result = {
        "solar_used": 0.0,
        "wind_used": 0.0,
        "diesel_used": 0.0,
        "battery_charge": 0.0,
        "unmet_demand": 0.0,
    }

    if renewable_total >= consumption:
        # Case 1: renewable excess (or exact match) — no diesel needed
        # Use solar first, then wind, to meet consumption
        if solar >= consumption:
            result["solar_used"] = consumption
            result["wind_used"] = 0.0
        else:
            result["solar_used"] = solar
            result["wind_used"] = consumption - solar

        result["battery_charge"] = renewable_total - consumption

    else:
        # Case 2: renewable deficit — diesel fills the gap
        result["solar_used"] = solar
        result["wind_used"] = wind
        deficit = consumption - renewable_total

        if diesel_capacity is None or diesel_capacity >= deficit:
            result["diesel_used"] = deficit
        else:
            result["diesel_used"] = diesel_capacity
            result["unmet_demand"] = deficit - diesel_capacity

    return result