"""
Conservation practice effects calculations for soil storage bucket

This module contains functions for calculating the effects of conservation practices:
- Area calculations under conservation practices
- Soil water content adjustments
- Field capacity calculations
- Evaporation reduction factors

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates effects of conservation practices on soil moisture, field capacity, and evaporation reduction
# ========================================
import numpy as np
import pandas as pd
from shared.utilities import to_float


# conservation_practices.py - Function 001: Calculates total area under soil moisture conservation practices
# Interactions: None
def calculate_soil_moisture_sums(df):
    soil_moisture_columns = ["BBF_Area", "Cover_Area", "Mulching_Area", "Bunds_Area", "Tillage_Area"]
    overall_sum = df[soil_moisture_columns].sum().sum()
    return df, overall_sum


# conservation_practices.py - Function 002: Calculates soil water content with conservation practice adjustments
# Interactions: calculate_soil_moisture_sums
def calculate_awc_soil(df, cover_crops_practice, mulching_practice, bbf_practice, bund_practice, tillage_practice,
                       awc_capacity):
    practices = {
        "Cover_Crops_SM_with_practice": cover_crops_practice,
        "Mulching_SM_with_practice": mulching_practice,
        "BBF_SM_with_practice": bbf_practice,
        "Bund_SM_with_practice": bund_practice,
        "Tillage_SM_with_practice": tillage_practice
    }

    area_columns = {
        "Cover_Crops_SM_with_practice": "Cover_Area",
        "Mulching_SM_with_practice": "Mulching_Area",
        "BBF_SM_with_practice": "BBF_Area",
        "Bund_SM_with_practice": "Bunds_Area",
        "Tillage_SM_with_practice": "Tillage_Area"
    }

    df, overall_sum = calculate_soil_moisture_sums(df)

    if overall_sum == 0:
        awc_soil_con = 0
    else:
        x = 0  # Initialize x
        for practice_column, practice_percentage in practices.items():
            area_column = area_columns.get(practice_column)
            if area_column in df.columns:
                x += df[area_column].sum() * (practice_percentage / 100)
        awc_soil = (x * awc_capacity) / overall_sum
        awc_soil_con = awc_soil
    return awc_soil_con


# conservation_practices.py - Function 003: Calculates final field capacity considering conservation and non-conservation areas
# Interactions: shared.utilities.to_float
def calculate_capacity(awc_capacity, with_out_soil_con, total_area, overall_sum, awc_soil_con):
    awc_capacity = to_float(awc_capacity, 0)
    with_out_soil_con = to_float(with_out_soil_con, 0)
    total_area = to_float(total_area, 0)
    overall_sum = to_float(overall_sum, 0)
    awc_soil_con = to_float(awc_soil_con, 0)

    capacity = ((awc_capacity * (with_out_soil_con / 100) * (total_area - overall_sum)) + (
            overall_sum * awc_soil_con)) / total_area
    return capacity


# conservation_practices.py - Function 004: Calculates soil evaporation reduction factors for conservation practices
# Interactions: pandas, numpy
def calc_soil_ke(df_crop, df_cc, all_crops):
    new_columns = {}

    for crop in all_crops:
        eva_red_area = []
        eva_red = []

        # Vectorized calculation - much faster than iterrows
        mask = df_crop[f"{crop}_Sown_Area"] > 0
        area_calc = (
            df_cc.at[crop, "Tillage_Area"] +
            df_cc.at[crop, "Mulching_Area"] +
            df_cc.at[crop, "Cover_Area"] +
            df_cc.at[crop, "Tank_Area"]
        )
        
        eva_red_area = np.where(mask, area_calc, 0)
        eva_red = np.where(mask & (area_calc > 0), df_cc.at[crop, "red_soil_evap"], 0)

        new_columns[f"eva_red_area_{crop}"] = eva_red_area
        new_columns[f"eva_red_{crop}"] = eva_red

    # Add all new columns at once to avoid fragmentation
    df_crop = pd.concat([df_crop, pd.DataFrame(new_columns)], axis=1)

    return df_crop


# conservation_practices.py - Function 005: Calculates final evaporation reduction factors for each crop
# Interactions: pandas, numpy
def calc_final_evap_red(df_crop, all_crops):
    new_columns = {}
    for crop in all_crops:
        final_evap_red = []

        # Vectorized calculation - much faster than iterrows
        sown_area = df_crop.get(f"{crop}_Sown_Area", pd.Series([0] * len(df_crop)))
        eva_red_area = df_crop.get(f"eva_red_area_{crop}", pd.Series([0] * len(df_crop)))
        eva_red = df_crop.get(f"eva_red_{crop}", pd.Series([0] * len(df_crop)))
        
        # Calculate final_evap_red vectorized
        mask_valid = ~pd.isna(sown_area) & (sown_area > 0)
        final_evap_red = np.where(
            mask_valid,
            1 - ((eva_red_area * eva_red) / sown_area),
            1
        )

        new_columns[f"Final_Evap_Red_{crop}"] = final_evap_red
    df_crop = pd.concat([df_crop, pd.DataFrame(new_columns)], axis=1)
    return df_crop


# conservation_practices.py - Function 006: Calculates weighted evaporation reduction factors aggregated by plot
# Interactions: pandas
def calc_final_evap_red_plot_wise(df_crop, all_crops, all_plots):
    # Initialize the new column with zeros
    plot_columns = {f"Final_Evap_Red_{plot}": [0.0] * len(df_crop) for plot in all_plots}
    df_crop = pd.concat([df_crop, pd.DataFrame(plot_columns)], axis=1)

    for plot in all_plots:
        for crop in all_crops:
            # Filter rows where plot is present
            plot_df = df_crop[df_crop.apply(lambda row: any(
                row[f"Plot_{crop_name}"] == plot for crop_name in all_crops), axis=1)]

            if plot_df.empty:
                continue

            if f"Final_Evap_Red_{crop}" in df_crop.columns:
                sown_area_col = f"{crop}_Sown_Area"
                if sown_area_col in plot_df.columns:
                    weighted_evap_red = (plot_df[sown_area_col] *
                                         plot_df[f"Final_Evap_Red_{crop}"]
                                         ).sum() / plot_df[sown_area_col].sum()
                    df_crop.loc[plot_df.index, f"Final_Evap_Red_{plot}"] = weighted_evap_red

    return df_crop