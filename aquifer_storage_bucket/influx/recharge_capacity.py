"""
Recharge capacity calculations for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates recharge capacity from water harvesting structures including surface areas and infiltration rates
# ========================================
from shared.utilities import to_float


# recharge_capacity.py - Function 001: Calculates recharge capacity for water harvesting structures
# Interactions: calc_surface_area, calc_added_monthly_recharge, shared.utilities.to_float
def calc_recharge_capacity(farm_pond_vol, farm_pond_depth,
                           farm_pond_inf_rate, farm_pond_lined_vol,
                           farm_pond_lined_depth, farm_pond_lined_inf_rate,
                           check_dam_vol, check_dam_depth,
                           check_dam_inf_rate, inf_pond_vol,
                           inf_pond_depth, inf_pond_inf_rate,
                           injection_wells_vol, injection_wells_nos):
    # Surface areas
    surface_areas = {
        "farm": calc_surface_area(farm_pond_vol, farm_pond_depth),
        "farm_lined": calc_surface_area(farm_pond_lined_vol, farm_pond_lined_depth),
        "check_dam": calc_surface_area(check_dam_vol, check_dam_depth),
        "inf_pond": calc_surface_area(inf_pond_vol, inf_pond_depth)
    }
    # Added monthly recharge
    added_recharges = {
        "farm": calc_added_monthly_recharge(surface_areas["farm"], farm_pond_inf_rate),
        "farm_lined": calc_added_monthly_recharge(surface_areas["farm_lined"], farm_pond_lined_inf_rate),
        "check_dam": calc_added_monthly_recharge(surface_areas["check_dam"], check_dam_inf_rate),
        "inf_pond": calc_added_monthly_recharge(surface_areas["inf_pond"], inf_pond_inf_rate)
    }
    # Additional recharge
    added_monthly_recharge_inj_well = to_float(injection_wells_vol, 0) * to_float(injection_wells_nos , 0)* 30
    # Total added recharge
    added_recharge_capacity = added_monthly_recharge_inj_well + added_recharges["inf_pond"]
    # SW storage capacity created
    sw_storage_capacity_created = (to_float(farm_pond_vol, 0) + to_float(farm_pond_lined_vol, 0) + to_float(check_dam_vol, 0)) - (
            added_recharges["farm"] + added_recharges["farm_lined"] + added_recharges["check_dam"])
    return surface_areas, added_recharges, added_recharge_capacity, sw_storage_capacity_created


# recharge_capacity.py - Function 002: Calculates surface area from volume and depth
# Interactions: shared.utilities.to_float
def calc_surface_area(vol, depth):
    vol = to_float(vol, 0)
    depth = to_float(depth, 0)
    # Check if both vol and depth are 0
    if vol == 0 and depth == 0:
        return 0
    # Prevent division by zero
    if depth == 0:
        raise ValueError("Depth cannot be zero unless volume is also zero.")
    return vol / depth


# recharge_capacity.py - Function 003: Calculates added monthly recharge from surface area and infiltration rate
# Interactions: shared.utilities.to_float
def calc_added_monthly_recharge(surface_area, inf_rate):
    inf_rate = to_float(inf_rate, 0)
    return surface_area * inf_rate * 30 / 1000