"""
Water stress calculations for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates water stress coefficients and depletion factors for crops and soil evaporation
# ========================================
import numpy as np


# water_stress.py - Function 001: Calculates depletion factor for water stress threshold of specific crop
# Interactions: numpy
def calculate_depletion_factor(df_crop, crop_df, selected_crop):
    crop_row = crop_df[crop_df["Crops"] == selected_crop]

    if not crop_row.empty:
        depletion_factor_str = crop_row["Depletion fraction - p"].values[0]

        try:
            temp_p = float(depletion_factor_str)
            # Apply the depletion factor only where crop_rd is greater than 0
            p = np.where(df_crop[f"{selected_crop}_crop_rd"] > 0, temp_p, 0)
        except ValueError:
            raise ValueError(f"Invalid depletion factor value: {depletion_factor_str}")
    else:
        print(f"No '{selected_crop}' crop found in the crop database.")
        p = np.zeros(df_crop.shape[0])  # Default to zeros if crop not found
    return p


# water_stress.py - Function 002: Calculates final aggregated depletion factor by plot for all crops
# Interactions: calculate_depletion_factor
def calc_final_depletion_factor(df_crop, crop_df, all_crops, valid_crops_df):
    # Step 1: Calculate depletion factor for each crop
    for selected_crop in all_crops:
        df_crop[f"{selected_crop}_depletion"] = calculate_depletion_factor(df_crop, crop_df, selected_crop)

    # Step 2: Initialize columns for each plot
    plot_numbers = valid_crops_df["Plot"].unique()
    for plot in plot_numbers:
        df_crop[f"final_depletion_{plot}"] = 0

    # Step 3: Sum depletion factors by plot
    for plot in plot_numbers:
        # Get the list of crops for this plot
        crops_in_plot = valid_crops_df[valid_crops_df["Plot"] == plot]["Crop"].tolist()

        # Calculate sum of depletion factors for crops in this plot
        if crops_in_plot:
            df_crop[f"final_depletion_{plot}"] = df_crop.apply(
                lambda row: sum(row[f"{crop}_depletion"] for crop in crops_in_plot if f"{crop}_depletion" in row.index),
                axis=1
            )
    return df_crop


# water_stress.py - Function 003: Determines soil evaporation stress condition based on water deficits
# Interactions: None
def calc_ks_soil_cond(kei, smdi, rewi, tewi):
    if kei == 0:
        return 0
    elif smdi < rewi:
        return 1
    elif rewi < smdi < tewi:
        return 2
    else:
        return 3


# water_stress.py - Function 004: Calculates soil evaporation stress coefficient based on moisture conditions
# Interactions: None
def calc_ks_soil(ks_soil_cond, tewi, smdi, rewi):
    if ks_soil_cond == 1:
        return 1
    elif ks_soil_cond == 2:
        return (tewi - smdi) / (tewi - rewi)
    else:
        return 0


# water_stress.py - Function 005: Determines crop transpiration stress condition based on water availability
# Interactions: None
def calc_ks_crop_cond(kci, smdi, rawi, tawi):
    if kci == 0:
        return 0
    elif smdi < rawi:
        return 1
    elif rawi < smdi < tawi:
        return 2
    else:
        return 3


# water_stress.py - Function 006: Calculates crop transpiration stress coefficient based on soil moisture
# Interactions: None
def calc_ks_crop(ks_crop_cond, tawi, smdi, rawi):
    if ks_crop_cond == 1:
        return 1
    elif ks_crop_cond == 2:
        return (tawi - smdi) / (tawi - rawi)
    else:
        return 0