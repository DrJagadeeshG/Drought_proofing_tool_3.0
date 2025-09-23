"""
Soil water storage calculations for soil storage bucket

This module contains functions for calculating soil water storage:
- Crop water storage and evaporation parameters

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Orchestrates soil water storage calculations including water capacities and evaporation parameters
# ========================================
from shared.crop_processing import process_sown_area, calculate_net_sown_area_by_plot
from soil_storage_bucket.processing.conservation_practices import calc_soil_ke, calc_final_evap_red, calc_final_evap_red_plot_wise
from soil_storage_bucket.processing.water_capacity import calc_taw, calc_raw, calc_tew, calc_rew


# water_storage.py - Function 001: Calculates crop water storage and evaporation parameters
# Interactions: shared.crop_processing.process_sown_area, shared.crop_processing.calculate_net_sown_area_by_plot, soil_storage_bucket.processing.conservation_practices.calc_soil_ke, soil_storage_bucket.processing.conservation_practices.calc_final_evap_red, soil_storage_bucket.processing.conservation_practices.calc_final_evap_red_plot_wise, soil_storage_bucket.processing.water_capacity.calc_taw, soil_storage_bucket.processing.water_capacity.calc_raw, soil_storage_bucket.processing.water_capacity.calc_tew, soil_storage_bucket.processing.water_capacity.calc_rew
def calc_crop_int(df_crop, df_cc, df_cp, valid_crops_df, all_plots, all_crops, soil_prop_list):
    df_crop = process_sown_area(df_crop, df_cp)
    df_crop["Ze"] = soil_prop_list[3]
    df_crop = calc_taw(df_crop, soil_prop_list[0], all_plots)
    df_crop = calc_raw(df_crop, all_plots)
    df_crop = calc_tew(df_crop, soil_prop_list[1], soil_prop_list[2], all_plots)
    df_crop = calc_rew(df_crop, all_plots)
    # Calculate row-by-row mean for TEWi and REWi across all plots
    df_crop["TEWi"] = df_crop.filter(like="TEWi_").mean(axis=1)
    df_crop["REWi"] = df_crop.filter(like="REWi_").mean(axis=1)
    # Process the sown area using the updated function
    df_crop = calculate_net_sown_area_by_plot(df_crop, valid_crops_df, df_cc)
    df_crop = calc_soil_ke(df_crop, df_cc, all_crops)
    df_crop = calc_final_evap_red(df_crop, all_crops)
    df_crop = calc_final_evap_red_plot_wise(df_crop, all_crops, all_plots)
    return df_crop