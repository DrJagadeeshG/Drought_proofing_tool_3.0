"""
Surface water evaporation functions for surface water bucket

This module contains functions for calculating surface water evaporation:
- Potential evapotranspiration from surface water

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates potential evapotranspiration losses from surface water bodies
# ========================================


# evaporation.py - Function 001: Calculates potential evapotranspiration from surface water
# Interactions: None
def calc_potential_et(total_surface_area_farm, df_mm):
    
    df_mm["Potential_ET"] = total_surface_area_farm * (df_mm["ETom"] / 1000)

    return df_mm