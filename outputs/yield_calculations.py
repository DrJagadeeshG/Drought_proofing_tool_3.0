"""
Yield calculations for drought proofing tool outputs

This module contains functions for calculating crop yields:
- Yield calculations for irrigated and rainfed areas
- Yield processing for all crops
- Yield calculations for calendar and crop years

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates crop yields under different water stress scenarios including irrigated and rainfed conditions
# ========================================
import numpy as np
import pandas as pd


# yield_calculations.py - Function 001: Calculates crop yields for irrigated and rainfed areas
# Interactions: numpy, pandas
def calculate_yields(df_yr, df_cc, crop, irr_area, rainfed_area, ky_value, total_area, final_eff):
    etci_col = f"ETci_{crop}"
    irr_cwr_col = f"Irr_CWR_met_{crop}"
    rainfed_cwr_col = f"Rainfed_CWR_met_{crop}"

    new_cols = {}

    # Calculate the "%Irr_CWR_met_{crop}" column
    if irr_area == 0:
        new_cols[f"%Irr_CWR_met_{crop}"] = 0
    else:
        new_cols[f"%Irr_CWR_met_{crop}"] = df_yr[irr_cwr_col] / df_yr[etci_col]
    # Calculate the "%Rainfed_CWR_met_{crop}" column
    if rainfed_area == 0:
        new_cols[f"%Rainfed_CWR_met_{crop}"] = 0
    else:
        new_cols[f"%Rainfed_CWR_met_{crop}"] = df_yr[rainfed_cwr_col] / df_yr[etci_col]
    # Calculate Combined CWR
    new_cols[f"%Combined_CWR_met_{crop}"] = ((new_cols[f"%Irr_CWR_met_{crop}"] * irr_area) +
                                             (new_cols[f"%Rainfed_CWR_met_{crop}"] * rainfed_area)) / total_area
    # Calculate yields
    new_cols[f"Irr_yield_{crop}"] = np.where(
        irr_area == 0,
        0,
        np.maximum(1 - ky_value * (1 - (df_yr[irr_cwr_col] / df_yr[etci_col])), 0)
    )
    new_cols[f"Rainfed_yield_{crop}"] = np.where(
        rainfed_area == 0,
        0,
        np.maximum(1 - ky_value * (1 - (df_yr[rainfed_cwr_col] / df_yr[etci_col])), 0)
    )
    # Calculate Average Yield
    new_cols[f"Avg_yield_{crop}"] = np.where(
        total_area == 0,
        0,
        ((new_cols[f"Irr_yield_{crop}"] * irr_area) + (new_cols[f"Rainfed_yield_{crop}"] * rainfed_area)) / total_area
    )
    # Calculate water metrics
    new_cols[f"IWR_met_{crop}"] = np.where(irr_area == 0, 0, df_yr[irr_cwr_col] / df_yr[etci_col])
    new_cols[f"Irr_CWR_{crop}(cu.m/ha)"] = df_yr[etci_col] * 10
    new_cols[f"Irr_CWR_{crop}(cu.m)"] = df_yr[etci_col] * irr_area * 10
    new_cols[f"Irr_CWA_{crop}(cu.m/ha)"] = df_yr[irr_cwr_col] * 10
    new_cols[f"Irr_CWA_{crop}(cu.m)"] = df_yr[irr_cwr_col] * irr_area * 10

    new_cols[f"Rainfed_CWR_{crop}(cu.m/ha)"] = df_yr[etci_col] * 10
    new_cols[f"Rainfed_CWR_{crop}(cu.m)"] = df_yr[etci_col] * 10 * rainfed_area
    new_cols[f"Rainfed_CWA_{crop}(cu.m/ha)"] = df_yr[rainfed_cwr_col] * 10
    new_cols[f"Rainfed_CWA_{crop}(cu.m)"] = df_yr[rainfed_cwr_col] * 10 * rainfed_area

    new_cols[f"Combined CWR_{crop}(cu.m/ha)"] = (new_cols[f"Irr_CWR_{crop}(cu.m/ha)"] * irr_area +
                                                 new_cols[f"Rainfed_CWR_{crop}(cu.m/ha)"] * rainfed_area) / total_area

    new_cols[f"Combined CWR_{crop}(cu.m)"] = (new_cols[f"Irr_CWR_{crop}(cu.m)"] * irr_area +
                                              new_cols[f"Rainfed_CWR_{crop}(cu.m)"] * rainfed_area) / total_area

    new_cols[f"Combined CWA_{crop}(cu.m/ha)"] = (new_cols[f"Irr_CWA_{crop}(cu.m/ha)"] * irr_area +
                                                 new_cols[f"Rainfed_CWA_{crop}(cu.m/ha)"] * rainfed_area) / total_area

    new_cols[f"Combined CWA_{crop}(cu.m)"] = (new_cols[f"Irr_CWA_{crop}(cu.m)"] * irr_area +
                                              new_cols[f"Rainfed_CWA_{crop}(cu.m)"] * rainfed_area) / total_area
    new_cols[f"Potential_Yield_{crop} (Kg/ha)"] = df_cc.at[crop, "Yield (tonne/ha)"] * 1000
    new_cols[f"Potential_Irr_Production_{crop}(tonnes)"] = (new_cols[
                                                                f"Potential_Yield_{crop} (Kg/ha)"] * irr_area) / 1000
    new_cols[f"Total_Irr_Production_{crop}"] = new_cols[f"Potential_Irr_Production_{crop}(tonnes)"] * new_cols[
        f"Irr_yield_{crop}"]
    new_cols[f"Potential_Rf_Production_{crop}(tonnes)"] = (new_cols[
                                                               f"Potential_Yield_{crop} (Kg/ha)"] * rainfed_area) / 1000
    new_cols[f"Total_Rf_Production_{crop}"] = new_cols[f"Potential_Rf_Production_{crop}(tonnes)"] * new_cols[
        f"Rainfed_yield_{crop}"]
    new_cols[f"Potential_combined_Production_{crop}(tonnes)"] = (
            (new_cols[f"Potential_Yield_{crop} (Kg/ha)"] * total_area) / 1000
    )
    new_cols[f"Total_combined_Production_{crop}"] = (
            new_cols[f"Potential_combined_Production_{crop}(tonnes)"] *
            new_cols[f"Avg_yield_{crop}"]
    )
    new_cols[f"Potential_WP_{crop} (kg/cu.m)"] = new_cols[f"Potential_Yield_{crop} (Kg/ha)"] / new_cols[
        f"Combined CWR_{crop}(cu.m/ha)"]
    new_cols[f"Combined_WP_{crop} (kg/cu.m)"] = (new_cols[f"Avg_yield_{crop}"] * new_cols[
        f"Potential_Yield_{crop} (Kg/ha)"]) / new_cols[f"Combined CWA_{crop}(cu.m/ha)"]
    new_cols[f"AE_crop_soil_{crop}(mm)"] = df_yr[f"AE_crop_{crop}"] + df_yr[f"AE_soil_{crop}"]
    new_cols[f"Yield_Irr_{crop} (kg/ha)"] = new_cols[f"Irr_yield_{crop}"] * new_cols[f"Potential_Yield_{crop} (Kg/ha)"]
    new_cols[f"Yield_rf_{crop} (kg/ha)"] = new_cols[f"Rainfed_yield_{crop}"] * new_cols[
        f"Potential_Yield_{crop} (Kg/ha)"]
    new_cols[f"Actual_Rainfed_WP_{crop} (kg/cu.m)"] = new_cols[f"Yield_rf_{crop} (kg/ha)"] / (
            df_yr[rainfed_cwr_col] * 10)
    new_cols[f"Water_use_total_{crop} [ETA + IWR/eff]"] = new_cols[f"AE_crop_soil_{crop}(mm)"] + (
            (df_yr[f"IWR_{crop}"] * new_cols[f"IWR_met_{crop}"]) / final_eff)
    new_cols[f"Actual Irrigated WP (kg/ha)_{crop}"] = new_cols[f"Yield_Irr_{crop} (kg/ha)"] / (
            new_cols[f"Water_use_total_{crop} [ETA + IWR/eff]"] * 10)
    # Add all new columns at once
    df_yr = pd.concat([df_yr, pd.DataFrame(new_cols)], axis=1)
    return df_yr


# yield_calculations.py - Function 002: Calculates yields for all crops
# Interactions: calculate_yields
def calc_yield(df_cc, df_yr, all_crops):
    print("FUNCTION 53: calc_yield() - Calculating crop yields")
    for crop in all_crops:
        irr_area = df_cc.at[crop, "Irr_Area"]
        rainfed_area = df_cc.at[crop, "Rainfed_Area"]
        ky_value = df_cc.at[crop, "Ky"]
        total_area = df_cc.at[crop, "Area"]
        final_eff = df_cc.at[crop, "Final_eff"]
        df_yr = calculate_yields(df_yr, df_cc, crop, irr_area, rainfed_area, ky_value, total_area, final_eff)
    return df_yr


# yield_calculations.py - Function 003: Gets yield percentages for all crops
# Interactions: pandas
def get_yield_per(df_yr, all_crops):
    df_yield = pd.DataFrame({"Date": df_yr["Date"]})
    for crop in all_crops:
        df_yield[f"%Irr_yield_{crop}"] = df_yr[f"Irr_yield_{crop}"]
        df_yield[f"%Rf_yield_{crop}"] = df_yr[f"Rainfed_yield_{crop}"]
        df_yield[f"%yield_{crop}"] = df_yr[f"Avg_yield_{crop}"]
    return df_yield


# yield_calculations.py - Function 004: Gets yield percentages for crop year
# Interactions: pandas
def get_yield_per_cyr(df_crop_yr, all_crops):
    df_yield = pd.DataFrame({"Date": df_crop_yr["water_year"]})
    for crop in all_crops:
        df_yield[f"%Irr_yield_{crop}"] = df_crop_yr[f"Irr_yield_{crop}"]
        df_yield[f"%Rf_yield_{crop}"] = df_crop_yr[f"Rainfed_yield_{crop}"]
        df_yield[f"%yield_{crop}"] = df_crop_yr[f"Avg_yield_{crop}"]
    return df_yield


# yield_calculations.py - Function 005: Calculates yields for water year analysis
# Interactions: numpy, pandas
def calc_yields(df_crop_yr, crop, irr_area, rainfed_area, ky_value, total_area):
    etci_col = f"ETci_{crop}"
    irr_cwr_col = f"Irr_CWR_met_{crop}"
    rainfed_cwr_col = f"Rainfed_CWR_met_{crop}"
    # Initialize a dictionary to store new columns
    new_cols = {}
    # Calculate the "%Irr_CWR_met_{crop}" column
    irr_met = df_crop_yr[irr_cwr_col] / df_crop_yr[etci_col]
    new_cols[f"%Irr_CWR_met_{crop}"] = np.where(irr_area == 0, 0, irr_met.clip(upper=1))
    # Calculate the "%Rainfed_CWR_met_{crop}" column
    rainfed_met = df_crop_yr[rainfed_cwr_col] / df_crop_yr[etci_col]
    new_cols[f"%Rainfed_CWR_met_{crop}"] = np.where(rainfed_area == 0, 0, rainfed_met.clip(upper=1))
    # Calculate Combined CWR
    combined_cwr = (new_cols[f"%Irr_CWR_met_{crop}"] * irr_area +
                    new_cols[f"%Rainfed_CWR_met_{crop}"] * rainfed_area) / total_area
    new_cols[f"%Combined_CWR_met_{crop}"] = combined_cwr
    # Calculate yields
    new_cols[f"Irr_yield_{crop}"] = np.where(
        irr_area == 0,
        0,
        (1 - ky_value * (1 - new_cols[f"%Irr_CWR_met_{crop}"])).clip(0, 1)
    )
    new_cols[f"Rainfed_yield_{crop}"] = np.where(
        rainfed_area == 0,
        0,
        (1 - ky_value * (1 - new_cols[f"%Rainfed_CWR_met_{crop}"])).clip(0, 1)
    )
    # Calculate Average Yield
    avg_yield = np.where(
        total_area == 0,
        0,
        (new_cols[f"Irr_yield_{crop}"] * irr_area +
         new_cols[f"Rainfed_yield_{crop}"] * rainfed_area) / total_area
    )
    new_cols[f"Avg_yield_{crop}"] = avg_yield
    # Concatenate new columns to the original DataFrame
    df_crop_yr = pd.concat([df_crop_yr, pd.DataFrame(new_cols)], axis=1)
    return df_crop_yr


# yield_calculations.py - Function 006: Calculates yields for water year for all crops
# Interactions: calc_yields
def calculate_yield_wyr(df_cc, df_crop_yr, all_crops):

    for crop in all_crops:
        irr_area = df_cc.at[crop, "Irr_Area"]
        rainfed_area = df_cc.at[crop, "Rainfed_Area"]
        ky_value = df_cc.at[crop, "Ky"]
        total_area = df_cc.at[crop, "Area"]
        df_crop_yr = calc_yields(df_crop_yr, crop, irr_area, rainfed_area, ky_value, total_area)

    return df_crop_yr