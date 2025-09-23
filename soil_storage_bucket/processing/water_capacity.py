"""
Water capacity calculations for soil storage bucket

This module contains functions for calculating various water capacities in soil:
- Total available water (TAW)
- Readily available water (RAW)
- Total evaporable water (TEW)
- Readily evaporable water (REW)

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates soil water capacities including total and readily available water for crops and evaporation
# ========================================


# water_capacity.py - Function 001: Calculates total available water (TAW) for each plot based on root depth
# Interactions: None
def calc_taw(df_crop, capacity, all_plots):
    for plot in all_plots:
        df_crop[f"TAWi_{plot}"] = capacity * df_crop[f"crop_rd_{plot}"]
    return df_crop


# water_capacity.py - Function 002: Calculates readily available water (RAW) based on depletion factors
# Interactions: None
def calc_raw(df_crop, all_plots):
    for plot in all_plots:
        df_crop[f"RAWi_{plot}"] = df_crop[f"final_depletion_{plot}"] * df_crop[f"TAWi_{plot}"]
    return df_crop


# water_capacity.py - Function 003: Calculates total evaporable water (TEW) from soil surface layer
# Interactions: None
def calc_tew(df_crop, theta_fc, theta_wp, all_plots):
    for plot in all_plots:
        df_crop[f"TEWi_{plot}"] = (theta_fc - 0.5 * theta_wp) * df_crop["Ze"]
    return df_crop


# water_capacity.py - Function 004: Calculates readily evaporable water (REW) from soil surface
# Interactions: None
def calc_rew(df_crop, all_plots):
    for plot in all_plots:
        df_crop[f"REWi_{plot}"] = 0.4 * df_crop[f"TEWi_{plot}"]
    return df_crop