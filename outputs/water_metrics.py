"""
Water requirement metrics for drought proofing tool outputs

This module contains functions for calculating water requirement metrics:
- Irrigation water requirement fulfillment
- Crop water requirement metrics
- Water requirement calculations for calendar and crop years

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates water requirement metrics including irrigation fulfillment and crop water requirement percentages
# ========================================
import numpy as np
import pandas as pd
from shared.utilities import safe_divide


# water_metrics.py - Function 001: Calculates percentage of irrigation water requirement fulfilled
# Interactions: shared.utilities.safe_divide, numpy
def calc_per_irr_water_req_fulfilled(df_mm):
    df_mm["Percent_Irr_Water_Req_Fulfilled"] = np.where(
        df_mm["Total Irrigated Area"] == 0,
        0,
        np.where(
            df_mm["Irr_water_need"] == 0,
            1,
            safe_divide(df_mm["Actual_IWR"] + df_mm["GW_extracted"], df_mm["Irr_water_need"])
        )
    )
    return df_mm


# water_metrics.py - Function 002: Calculates crop water requirement met for each crop
# Interactions: shared.utilities.safe_divide
def calc_cwr_met(df_mm, crops):
    for crop in crops:
        etci_col = f"ETci_{crop}"
        iwr_col = f"IWR_{crop}"
        percent_irrigation_col = "Percent_Irr_Water_Req_Fulfilled"
        irr_cwr_col = f"Irr_CWR_met_{crop}"
        rainfed_cwr_col = f"Rainfed_CWR_met_{crop}"
        irr_cwr_col_per = f"%Irr_CWR_met_{crop}"
        rainfed_cwr_col_per = f"%Rainfed_CWR_met_{crop}"
        if etci_col in df_mm.columns and iwr_col in df_mm.columns and percent_irrigation_col in df_mm.columns:
            df_mm[irr_cwr_col] = (df_mm[etci_col] - df_mm[iwr_col]) + df_mm[iwr_col] * df_mm[percent_irrigation_col]
            df_mm[rainfed_cwr_col] = df_mm[etci_col] - df_mm[iwr_col]
            df_mm[irr_cwr_col_per] = safe_divide(df_mm[irr_cwr_col], df_mm[etci_col])
            df_mm[rainfed_cwr_col_per] = safe_divide(df_mm[rainfed_cwr_col], df_mm[etci_col])
        else:
            print(f"Error: Required columns for {crop} not found in dataframe")
    return df_mm


# water_metrics.py - Function 003: Gets crop water requirement in mm for all crops
# Interactions: pandas
def get_cwr_mm(df_yr, all_crops):
    df_cwr = pd.DataFrame({"Date": df_yr["Date"]})  # Create DataFrame with Date column
    for crop in all_crops:
        df_cwr[f"CWR_{crop}(mm)"] = df_yr[f"ETci_{crop}"]
        df_cwr[f"IWR_{crop}(mm)"] = df_yr[f"IWR_{crop}"]
    return df_cwr


# water_metrics.py - Function 004: Gets percentage of crop water requirement met
# Interactions: pandas
def get_cwr_met(df_yr, all_crops):
    df_cwr_met = pd.DataFrame({"Date": df_yr["Date"]})
    for crop in all_crops:
        df_cwr_met[f"%Irr_CWR_met_{crop}"] = df_yr[f"%Irr_CWR_met_{crop}"]
        df_cwr_met[f"%Rf_CWR_met_{crop}"] = df_yr[f"%Rainfed_CWR_met_{crop}"]
    return df_cwr_met


# water_metrics.py - Function 005: Gets crop water requirement for crop year
# Interactions: pandas
def get_cwr_mm_cyr(df_crop_yr,all_crops):
    df_cwr =  pd.DataFrame({"Date": df_crop_yr["water_year"]})
    for crop in all_crops:
        df_cwr[f"CWR_{crop}(mm)"] = df_crop_yr[f"ETci_{crop}"]
        df_cwr[f"IWR_{crop}(mm)"] = df_crop_yr[f"IWR_{crop}"]
    return df_cwr


# water_metrics.py - Function 006: Gets crop water requirement met for crop year
# Interactions: pandas
def get_cwr_met_cyr(df_crop_yr, all_crops):
    df_cwr_met = pd.DataFrame({"Date": df_crop_yr["water_year"]})
    for crop in all_crops:
        df_cwr_met[f"%Irr_CWR_met_{crop}"] = df_crop_yr[f"%Irr_CWR_met_{crop}"]
        df_cwr_met[f"%Rf_CWR_met_{crop}"] = df_crop_yr[f"%Rainfed_CWR_met_{crop}"]
    return df_cwr_met