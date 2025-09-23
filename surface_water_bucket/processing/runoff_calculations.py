"""
Runoff calculations for surface water bucket

This module contains functions for calculating runoff:
- Water abstraction parameters
- Runoff calculations using SCS curve number method

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates surface runoff using SCS curve number method and processes water abstraction parameters
# ========================================
import numpy as np
from shared.utilities import to_float, mm_to_m3, safe_divide
from surface_water_bucket.processing.curve_numbers import calc_cn
from outputs.output_aggregator import calc_weighted_avg
from aquifer_storage_bucket.influx.recharge_calculations import get_recharge
from surface_water_bucket.influx.precipitation_processing import get_rain_src_model


# runoff_calculations.py - Function 001: Processes monthly runoff and converts to cubic meters
# Interactions: calculate_monthly_qi, shared.utilities.to_float, shared.utilities.mm_to_m3
def process_monthly_qi(df_dd, df_mm, inp_aquifer_para):
    # Calculate monthly Qi
    df_mm = calculate_monthly_qi(df_dd, df_mm)
    # Convert Qom from mm to m^3
    df_mm["Qom(m^3)"] = mm_to_m3(to_float(inp_aquifer_para[3], 0), df_mm["Qom"])
    return df_mm


# runoff_calculations.py - Function 002: Calculates runoff discharge using curve number method
# Interactions: surface_water_bucket.processing.curve_numbers.calc_cn, calc_abstraction, aquifer_storage_bucket.influx.recharge_calculations.get_recharge, surface_water_bucket.influx.precipitation_processing.get_rain_src_model, runoff_cn, calc_runoff_cn, get_eff_rain
def calc_discharge(df_dd, df_crop, fixed_values_list):
    df_dd["CNi"] = calc_cn(df_crop)
    df_dd["Si"], df_dd["Iai"] = calc_abstraction(df_dd, df_crop, fixed_values_list[0], fixed_values_list[1],
                                                 fixed_values_list[2])
    df_dd["Recharge_src"] = df_dd.apply(lambda x: get_recharge(x["Pi"], fixed_values_list[3]), axis=1)
    df_dd["Rain_src"] = df_dd.apply(lambda row: get_rain_src_model(row["Pi"], row["Recharge_src"]), axis=1)
    df_dd["runoff"] = df_dd.apply(lambda row: runoff_cn(row["Pi"], row["Iai"], row["Si"]), axis=1)
    df_dd["Qi"] = df_dd.apply(lambda row: calc_runoff_cn(row["Rain_src"], row["Iai"], row["runoff"]), axis=1)
    df_dd["Eff_Rain"] = df_dd.apply(lambda row: get_eff_rain(row["Rain_src"], row["Qi"]), axis=1)
    df_dd["Pei"] = df_dd.apply(lambda row: get_eff_rain(row["Pi"], row["Qi"]), axis=1)
    return df_dd


# runoff_calculations.py - Function 003: Calculates water abstraction parameters for runoff calculation
# Interactions: numpy
def calc_abstraction(df_dd, df_crop, ia_amc1, ia_amc2, ia_amc3):
    print("FUNCTION 26: calc_abstraction() - Calculating water abstraction")
    si = (25400 / df_dd["CNi"]) - 254
    conditions = [
        df_crop["AMC"] == 1,
        df_crop["AMC"] == 2
    ]
    choices = [si * ia_amc1, si * ia_amc2]
    iai = np.select(conditions, choices, default=si * ia_amc3)
    return si, iai


# runoff_calculations.py - Function 004: Calculates surface runoff using SCS curve number method
# Interactions: shared.utilities.safe_divide
def runoff_cn(pi, iai, si):
    q = safe_divide((pi - iai) ** 2, (pi + si - iai))
    return q


# runoff_calculations.py - Function 005: Applies runoff calculation only when rainfall exceeds initial abstraction
# Interactions: None
def calc_runoff_cn(rain_src, iai, runoff):
    return 0 if rain_src < iai else runoff


# runoff_calculations.py - Function 006: Calculates effective rainfall by subtracting runoff from net rainfall
# Interactions: None
def get_eff_rain(rain_src, runoff):
    peff = rain_src - runoff
    return peff


# runoff_calculations.py - Function 007: Aggregates daily runoff to monthly totals and merges with monthly data
# Interactions: pandas
def calculate_monthly_qi(df_dd, df_mm):
    # Resample the Qi values to a monthly frequency and sum them
    qom = df_dd.resample("M", on="Date")["Qi"].sum().reset_index()

    # Merge the resampled monthly Qi values into df_mm
    df_mm = df_mm.merge(qom, on="Date", how="left")

    # Rename the column appropriately
    df_mm.rename(columns={"Qi": "Qom"}, inplace=True)

    return df_mm