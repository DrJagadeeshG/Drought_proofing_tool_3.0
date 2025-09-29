"""
Groundwater recharge calculations for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates groundwater recharge from various sources including natural recharge, fallow areas, and surface infiltration structures
# ========================================

import numpy as np
import pandas as pd
from shared.utilities import to_float, convert_dtypes
from soil_storage_bucket.processing.water_stress import calc_ks_soil_cond, calc_ks_soil
from soil_storage_bucket.outflux.evapotranspiration import calc_ke, calc_esi_fallow, calc_ae_soil_fallow
from shared import config_constants
# Removed circular import - moved calc_smd_fallow function to this file
from soil_storage_bucket.outflux.irrigation_demand import calculate_iwr, calculate_monthly_iwr
from orchestrator.input_collector import collect_inp_variables


# recharge_calculations.py - Function 001: Calculates groundwater recharge for fallow and crop plots
# Interactions: calc_monthly_gwnrm_crop, soil_storage_bucket.outflux.evapotranspiration.calc_ke, soil_storage_bucket.outflux.evapotranspiration.calc_esi_fallow, soil_storage_bucket.processing.water_stress.calc_ks_soil_cond, soil_storage_bucket.processing.water_stress.calc_ks_soil, soil_storage_bucket.outflux.evapotranspiration.calc_ae_soil_fallow, calc_smd_fallow, calc_gwnr_fallow, calc_monthly_gwnrm_fallow, calc_fallow_area1, calc_recharge, calc_monthly_recharge, soil_storage_bucket.outflux.irrigation_demand.calculate_iwr, soil_storage_bucket.outflux.irrigation_demand.calculate_monthly_iwr, shared.utilities.convert_dtypes, numpy, pandas
def calc_gwnr_fallow_plot(df_crop, df_mm, df_dd, all_plots, all_crops, inp_lulc_val_list, df_cc):
    print("FUNCTION 19: calc_gwnr_fallow_plot() - Calculating groundwater recharge for fallow plots")
    df_mm = calc_monthly_gwnrm_crop(df_crop, df_mm, all_plots)
    df_dd["Kc_Fallow"] = np.float32(0)
    df_dd["Ke_Fallow"] = df_dd["Kc_Fallow"].apply(calc_ke)
    df_dd["ESi_Fallow"] = df_dd.apply(lambda row: calc_esi_fallow(row), axis=1)
    df_dd.loc[0, "SMDi_shifted_Fallow"] = config_constants.SMDi_1
    
    # TEMPORARILY DISABLED: September 1st fallow reset (for testing)
    # fallow_reset_indices = []
    # for i in range(len(df_dd)):
    #     # Check if date is September 1st of any year
    #     date = pd.to_datetime(df_dd.loc[i, "Date"])
    #     if date.month == 9 and date.day == 1:
    #         fallow_reset_indices.append(i)
    for i in range(len(df_dd)):
        if i > 0:
            # ALWAYS use previous day's SMDi_Fallow (no reset)
            df_dd.loc[i, "SMDi_shifted_Fallow"] = df_dd.loc[i - 1, "SMDi_Fallow"]
            # ORIGINAL RESET LOGIC (commented out):
            # if i in fallow_reset_indices:
            #     df_dd.loc[i, "SMDi_shifted_Fallow"] = 0
            # else:
            #     df_dd.loc[i, "SMDi_shifted_Fallow"] = df_dd.loc[i - 1, "SMDi_Fallow"]
        df_dd.loc[i, "Ks_soil_cond_Fallow"] = calc_ks_soil_cond(df_dd.loc[i, "Ke_Fallow"],
                                                                df_dd.loc[i, "SMDi_shifted_Fallow"],
                                                                df_crop.loc[i, "REWi"],
                                                                df_crop.loc[i, "TEWi"])
        df_dd.loc[i, "Ks_soil_Fallow"] = calc_ks_soil(df_dd.loc[i, "Ks_soil_cond_Fallow"],
                                                      df_crop.loc[i, "TEWi"],
                                                      df_dd.loc[i, "SMDi_shifted_Fallow"],
                                                      df_crop.loc[i, "REWi"])
        df_dd.loc[i, "AE_soil_Fallow"] = calc_ae_soil_fallow(df_dd.loc[i, "ESi_Fallow"],
                                                             df_dd.loc[i, "Pei"],
                                                             df_dd.loc[i, "Ks_soil_cond_Fallow"],
                                                             df_dd.loc[i, "Ks_soil_Fallow"])
        df_dd.loc[i, "SMDi_Fallow"] = calc_smd_fallow(df_dd.loc[i, "SMDi_shifted_Fallow"],
                                                      df_dd.loc[i, "AE_soil_Fallow"],
                                                      df_dd.loc[i, "Pei"])
    df_crop["GWnr_Fallow"] = df_dd.apply(lambda row: calc_gwnr_fallow(row["SMDi_Fallow"],
                                                                      row["SMDi_shifted_Fallow"],
                                                                      row["AE_soil_Fallow"],
                                                                      row["Pei"]), axis=1)
    df_mm = calc_monthly_gwnrm_fallow(df_crop, df_mm)
    df_crop = calc_fallow_area1(df_crop, inp_lulc_val_list[1], inp_lulc_val_list[2], inp_lulc_val_list[3], inp_lulc_val_list[4], inp_lulc_val_list[5])
    # Calculate sum of all crop areas for recharge calculation
    # This will be the sum of all crop areas (Chilli: 712 + Tobacco: 1880 + Pulses: 1150 = 3742)
    total_crop_areas = sum(df_cc["Area"].values)  # Sum of all crop areas from crop characteristics
    df_crop["Recharge"] = df_crop.apply(lambda row: calc_recharge(row, all_plots, total_crop_areas), axis=1)
    df_mm = calc_monthly_recharge(df_crop, df_mm)
    df_crop = calculate_iwr(df_dd, df_crop, all_crops)
    df_mm = calculate_monthly_iwr(df_dd, df_mm.copy(), df_crop.copy(), all_crops)
    df_dd = convert_dtypes(df_dd)
    df_crop = convert_dtypes(df_crop)
    
    # DISABLED: Update AE_soil_crop with fallow values when crop is not sown
    # This redistribution is disabled to ensure crop AE values exactly match plot AE values
    # for crop in all_crops:
    #     sown_area_col = f"{crop}_Sown_Area"
    #     ae_soil_crop_col = f"AE_soil_{crop}"
    #     if sown_area_col in df_crop.columns and ae_soil_crop_col in df_crop.columns:
    #         # Where crop is not sown, use fallow evaporation value
    #         not_sown_mask = df_crop[sown_area_col] == 0
    #         df_crop.loc[not_sown_mask, ae_soil_crop_col] = df_dd.loc[not_sown_mask, "AE_soil_Fallow"]
    
    # Recalculate monthly aggregation after AE_soil changes
    df_mm = calculate_monthly_iwr(df_dd, df_mm.copy(), df_crop.copy(), all_crops)
    
    return df_crop, df_mm, df_dd


# recharge_calculations.py - Function 002: Calculates groundwater natural recharge when soil is at field capacity
# Interactions: None
def calc_gwnr(smdi, smdi_shifted, ae_crop, ae_soil, pei):
    return abs(smdi_shifted + ae_crop + ae_soil - pei) if smdi == 0 else 0


# recharge_calculations.py - Function 003: Updates groundwater natural recharge for all plots in dataset
# Interactions: calc_gwnr, numpy, pandas
def update_gwnr(df_crop, df_dd, all_plots):
    # Initialize a column for total GWnr
    df_crop["GWnr"] = np.float32(0)
    # Loop over each plot and calculate GWnr
    for plot in all_plots:
        smdi_col = f"SMDi_{plot}"
        smdi_shifted_col = f"SMDi_shifted_{plot}"
        ae_crop_col = f"AE_crop_{plot}"
        ae_soil_col = f"AE_soil_{plot}"
        # Calculate GWnr for each plot and store in a new column
        df_crop[f"GWnr_{plot}"] = df_crop.apply(
            lambda row: calc_gwnr(
                row[smdi_col],
                row[smdi_shifted_col],
                row[ae_crop_col],
                row[ae_soil_col],
                df_dd.loc[row.name, "Pei"]
            ),
            axis=1
        )
        # # Add to the total GWnr
        # df_crop["GWnr"] += df_crop[f"GWnr_{plot}"]

    # Ensure the total GWnr is of the correct type
    df_crop["GWnr"] = df_crop["GWnr"].astype("float32")

    return df_crop


# recharge_calculations.py - Function 004: Aggregates daily groundwater recharge to monthly values for crops
# Interactions: pandas
def calc_monthly_gwnrm_crop(df_crop, df_mm, all_plots):
    print("FUNCTION 38: calc_monthly_gwnrm_crop() - Calculating monthly groundwater recharge")
    for plot in all_plots:
        # Resample the GWnr values for each crop to a monthly frequency and sum them
        gw_nrm = df_crop.resample("M", on="Date")[f"GWnr_{plot}"].sum().reset_index()
        # Merge the resampled monthly GWnr values into df_mm
        df_mm = df_mm.merge(gw_nrm, on="Date", how="left")
        # Rename the column appropriately
        df_mm.rename(columns={f"GWnr_{plot}": f"GWnrm_{plot}"}, inplace=True)
    return df_mm


# recharge_calculations.py - Function 005: Calculates groundwater natural recharge from fallow land areas
# Interactions: numpy
def calc_gwnr_fallow(smdi_fallow, smdi_shifted_fallow, ae_soil_fallow, pei):
    return abs(smdi_shifted_fallow + ae_soil_fallow - pei) if smdi_fallow == 0 else np.float32(0)


# recharge_calculations.py - Function 006: Aggregates daily groundwater recharge from fallow areas to monthly totals
# Interactions: pandas
def calc_monthly_gwnrm_fallow(df_crop, df_mm):
    # Resample the GWnr values to a monthly frequency and sum them
    gw_nrmf = df_crop.resample("M", on="Date")["GWnr_Fallow"].sum().reset_index()
    # Merge the resampled monthly GWnr values into df_mm
    df_mm = df_mm.merge(gw_nrmf, on="Date", how="left")
    # Rename the column appropriately
    df_mm.rename(columns={"GWnr_Fallow": "GWnrm_Fallow"}, inplace=True)
    return df_mm


# recharge_calculations.py - Function 007: Calculates total fallow area including non-crop land uses for recharge
# Interactions: shared.utilities.to_float
def calc_fallow_area1(df_crop, fallow, builtup, water_bodies, pasture, forest):
    fallow_var = to_float(fallow, 0)
    builtup_var = to_float(builtup, 0)
    water_bodies_var = to_float(water_bodies, 0)
    pasture_var = to_float(pasture, 0)
    forest_var = to_float(forest, 0)
    df_crop["Fallow Area Recharge"] = fallow_var + builtup_var + water_bodies_var + pasture_var + forest_var
    return df_crop


# recharge_calculations.py - Function 008: Calculates area-weighted average groundwater recharge across all land uses
# Interactions: None
def calc_recharge(row, all_plots, total_crop_areas):
    numerator = sum(row[f"{plot}_NSA"] * row[f"GWnr_{plot}"] for plot in all_plots)
    # Add the fallow area contribution to the numerator
    numerator += row["Fallow Area Recharge"] * row["GWnr_Fallow"]
    # Use sum of all crop areas + fallow area recharge as denominator
    denominator = total_crop_areas + row["Fallow Area Recharge"]
    return numerator / denominator if denominator != 0 else 0


# recharge_calculations.py - Function 009: Aggregates daily recharge values to monthly totals for water balance
# Interactions: pandas
def calc_monthly_recharge(df_crop, df_mm):
    recharge = df_crop.resample("M", on="Date")["Recharge"].sum().reset_index()
    # Merge the resampled monthly GWnr values into df_mm
    df_mm = df_mm.merge(recharge, on="Date", how="left")
    return df_mm


# recharge_calculations.py - Function 010: Calculates groundwater recharge from precipitation
# Interactions: None
def get_recharge(pi, soil_gwrecharge_coefficient):
    recharge = pi * soil_gwrecharge_coefficient
    return recharge



# recharge_calculations.py - Function 011: Calculates added monthly recharge from infiltration
# Interactions: shared.utilities.to_float
def calc_added_monthly_recharge(surface_area, inf_rate):
    inf_rate = to_float(inf_rate, 0)
    return surface_area * inf_rate * 30 / 1000


# recharge_calculations.py - Function 012: Calculates potential groundwater recharge from structures
# Interactions: pandas
def calc_potential_recharge(farm, farm_lined, check_dam, df_mm):
    added_surface_recharge_capacity = farm + farm_lined + check_dam
    df_mm["Potential_recharge"] = added_surface_recharge_capacity
    return df_mm


# recharge_calculations.py - Function 013: Adds runoff to recharge calculations
# Interactions: pandas
def add_runoff_to_recharge(df_mm):
    new_columns = pd.DataFrame({
        "runoff to recharge": df_mm["Actual_Recharge_mm"] + df_mm["Runoff in GW recharge str_mm"]})
    df_mm = pd.concat([df_mm, new_columns], axis=1)
    return df_mm


# recharge_calculations.py - Function 014: Calculates final groundwater recharge
# Interactions: pandas
def calc_final_recharge(df_mm):
    df_mm["Final_Recharge"] = (df_mm["Recharge"] - df_mm["Rejected_recharge_mm"] + df_mm["runoff to recharge"]).clip(
        lower=0)
    return df_mm


# recharge_calculations.py - Function 015: Calculates soil moisture deficit for fallow land areas
# Interactions: None
def calc_smd_fallow(smdi, ae_soil, pei):
    if smdi + ae_soil - pei < 0:
        return 0
    else:
        return smdi + ae_soil - pei