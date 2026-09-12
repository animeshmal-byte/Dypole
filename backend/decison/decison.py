def dispatch_energy(consumption, solar, wind, battery_charge, battery_capacity, is_calamity=False):
    """
    Dispatch decision for a microgrid with solar, wind, diesel, and battery.

    Normal mode priority: solar+wind -> battery -> diesel (diesel assumed always sufficient)
    Calamity mode priority: solar+wind -> battery charging is the goal; diesel covers
                             consumption; any renewable left after battery is full
                             still offsets consumption before diesel does.

    Parameters:
        consumption (float): required load (x)
        solar (float): solar production
        wind (float): wind production
        battery_charge (float): current battery charge level
        battery_capacity (float): max battery capacity
        is_calamity (bool): True if in storm-prep mode

    Returns:
        dict with renewable_used, battery_used, battery_charged,
        diesel_used, curtailed, new_battery_charge
    """
    renewable_total = solar + wind

    result = {
        "renewable_used": 0.0,
        "battery_used": 0.0,
        "battery_charged": 0.0,
        "diesel_used": 0.0,
        "curtailed": 0.0,
        "new_battery_charge": battery_charge,
    }

    if not is_calamity:
        if renewable_total >= consumption:
            # Renewables cover it fully; excess goes to battery (capped), rest curtailed
            result["renewable_used"] = consumption
            excess = renewable_total - consumption
            room = battery_capacity - battery_charge
            charged = min(excess, room)
            result["battery_charged"] = charged
            result["curtailed"] = excess - charged
            result["new_battery_charge"] = battery_charge + charged
        else:
            # Renewables fall short; battery covers the gap; diesel covers the rest
            result["renewable_used"] = renewable_total
            deficit = consumption - renewable_total
            drawn = min(deficit, battery_charge)
            result["battery_used"] = drawn
            result["diesel_used"] = deficit - drawn
            result["new_battery_charge"] = battery_charge - drawn

    else:
        # Calamity: renewables prioritize charging the battery
        room = battery_capacity - battery_charge
        charged = min(renewable_total, room)
        result["battery_charged"] = charged
        result["new_battery_charge"] = battery_charge + charged

        leftover_renewable = renewable_total - charged
        renewable_to_consumption = min(leftover_renewable, consumption)
        result["renewable_used"] = renewable_to_consumption
        result["diesel_used"] = consumption - renewable_to_consumption
        result["curtailed"] = leftover_renewable - renewable_to_consumption

    return result