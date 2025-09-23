"""
Domestic and non-domestic water demand calculations for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates domestic and non-domestic water demands including groundwater dependency
# ========================================
from shared.utilities import to_float


# domestic_demand.py - Function 001: Calculates domestic water requirements
# Interactions: shared.utilities.to_float
def calc_domestic_need(population, domestic_water_use, df_mm):
    population = to_float(population, 0)
    domestic_water_use = to_float(domestic_water_use, 0)
    
    df_mm["Domestic_need"]= (population * domestic_water_use * df_mm["Days"]) / 1000
    return df_mm


# domestic_demand.py - Function 002: Calculates non-domestic water requirements
# Interactions: shared.utilities.to_float
def calc_other_need(other, other_water_use, df_mm):
    other = to_float(other, 0)
    other_water_use = to_float(other_water_use, 0)
    
    df_mm["Other_need"] = (other * other_water_use * df_mm["Days"]) / 1000
    return df_mm


# domestic_demand.py - Function 003: Calculates groundwater needs for domestic use
# Interactions: shared.utilities.to_float
def calc_gw_need(df_mm, groundwater_dependent):
    df_mm["GW_need"] = (to_float(groundwater_dependent, 0) / 100) * (df_mm["Domestic_need"] + df_mm["Other_need"])
    return df_mm