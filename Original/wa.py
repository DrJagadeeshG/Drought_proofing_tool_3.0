
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:52:52 2024

@author: Dr. Jagadeesh, Consultant, IWMI
"""
import pandas as pd
import numpy as np
import crop_pattern
from user_input import to_float
import manual_input


# wa.py - Function 1: Reads irrigation data and merges with monthly dataframe
def irrigation_data_input(df_ir_path, df_mm):
    df_ir = pd.read_csv(df_ir_path)
    df_ir["Date"] = df_mm["Date"]
    columns = ["Date"] + [col for col in df_ir.columns if col != "Date"]
    df_ir = df_ir[columns]

    return df_ir

# wa.py - Function 2: Calculates aquifer storage limit based on parameters
def calculate_storage_limit(aquifer_para_list):
    aquifer_depth = to_float(aquifer_para_list[0], 0)
    specific_yield = to_float(aquifer_para_list[2], 0)
    total_area = to_float(aquifer_para_list[3], 0)
    storage_limit = aquifer_depth * (specific_yield / 100) * total_area * 10000
    return storage_limit


# wa.py - Function 3: Calculates residual groundwater storage
def calc_storage_residualgw(df_mm,aquifer_para_list):
    
    df_mm.loc[0, "Residual_storage"] = to_float(aquifer_para_list[2], 0) * (
        to_float(aquifer_para_list[1], 0) / 100) * to_float(
            aquifer_para_list[3], 0) * 10000

    return df_mm

# wa.py - Function 4: Calculates surface area from volume and depth
def calc_surface_area(vol, depth):
    vol = to_float(vol, 0)
    depth = to_float(depth, 0)
    # Check if both vol and depth are 0
    if vol == 0 and depth == 0:
        return 0
    # Prevent division by zero
    if depth == 0:
        raise ValueError("Depth cannot be zero unless volume is also zero.")
    return vol / depth


# wa.py - Function 5: Calculates added monthly recharge from infiltration
def calc_added_monthly_recharge(surface_area, inf_rate):
    inf_rate = to_float(inf_rate, 0)
    return surface_area * inf_rate * 30 / 1000


# wa.py - Function 6: Calculates recharge capacity for water harvesting structures
def calc_recharge_capacity(farm_pond_vol, farm_pond_depth,
                           farm_pond_inf_rate, farm_pond_lined_vol,
                           farm_pond_lined_depth, farm_pond_lined_inf_rate,
                           check_dam_vol, check_dam_depth,
                           check_dam_inf_rate, inf_pond_vol,
                           inf_pond_depth, inf_pond_inf_rate,
                           injection_wells_vol, injection_wells_nos):
    # Surface areas
    surface_areas = {
        "farm": calc_surface_area(farm_pond_vol, farm_pond_depth),
        "farm_lined": calc_surface_area(farm_pond_lined_vol, farm_pond_lined_depth),
        "check_dam": calc_surface_area(check_dam_vol, check_dam_depth),
        "inf_pond": calc_surface_area(inf_pond_vol, inf_pond_depth)
    }

    # Added monthly recharge
    added_recharges = {
        "farm": calc_added_monthly_recharge(surface_areas["farm"], farm_pond_inf_rate),
        "farm_lined": calc_added_monthly_recharge(surface_areas["farm_lined"], farm_pond_lined_inf_rate),
        "check_dam": calc_added_monthly_recharge(surface_areas["check_dam"], check_dam_inf_rate),
        "inf_pond": calc_added_monthly_recharge(surface_areas["inf_pond"], inf_pond_inf_rate)
    }

    # Additional recharge
    added_monthly_recharge_inj_well = to_float(injection_wells_vol, 0) * to_float(injection_wells_nos , 0)* 30

    # Total added recharge
    added_recharge_capacity = added_monthly_recharge_inj_well + added_recharges["inf_pond"]

    # SW storage capacity created
    sw_storage_capacity_created = (to_float(farm_pond_vol, 0) + to_float(farm_pond_lined_vol, 0) + to_float(check_dam_vol, 0)) - (
            added_recharges["farm"] + added_recharges["farm_lined"] + added_recharges["check_dam"])

    return surface_areas, added_recharges, added_recharge_capacity, sw_storage_capacity_created


# wa.py - Function 7: Calculates potential evapotranspiration from surface water
def calc_potential_et(total_surface_area_farm, df_mm):
    
    df_mm["Potential_ET"] = total_surface_area_farm * (df_mm["ETom"] / 1000)

    return df_mm

# wa.py - Function 8: Calculates canal water supply availability
def calc_canal_supply(df_ir, df_mm):
    def get_canal_supply(row):
        month_index = row.name % 12
        value = df_ir.loc[month_index, "Canal_WA"]
        return 0 if np.isnan(value) else value

    df_mm["Canal_supply"] = df_mm.apply(get_canal_supply, axis=1)
    return df_mm

# wa.py - Function 9: Calculates irrigation water requirement after canal supply
def get_iwr_after_canal(df_mm):
    df_mm["IWR_after_canal"] = df_mm["Irr_water_need"] - df_mm["Canal_supply"]
    return df_mm


# wa.py - Function 10: Calculates potential groundwater recharge from structures
def calc_potential_recharge(farm, farm_lined, check_dam, df_mm):
    added_surface_recharge_capacity = farm + farm_lined + check_dam
    df_mm["Potential_recharge"] = added_surface_recharge_capacity
    return df_mm

# wa.py - Function 11: Calculates domestic water requirements
def calc_domestic_need(population, domestic_water_use, df_mm):
    population = to_float(population, 0)
    domestic_water_use = to_float(domestic_water_use, 0)
    
    df_mm["Domestic_need"]= (population * domestic_water_use * df_mm["Days"]) / 1000
    return df_mm

# wa.py - Function 12: Calculates non-domestic water requirements
def calc_other_need(other, other_water_use, df_mm):
    other = to_float(other, 0)
    other_water_use = to_float(other_water_use, 0)
    
    df_mm["Other_need"] = (other * other_water_use * df_mm["Days"]) / 1000
    return df_mm

# wa.py - Function 13: Calculates groundwater needs for domestic use
def calc_gw_need(df_mm, groundwater_dependent):
    df_mm["GW_need"] = (to_float(groundwater_dependent, 0) / 100) * (df_mm["Domestic_need"] + df_mm["Other_need"])
    return df_mm

# wa.py - Function 14: Calculates surface water needs
def calc_sw_need(df_mm):
    df_mm["SW_need"] = df_mm["Domestic_need"] + df_mm["Other_need"] - df_mm["GW_need"]
    return df_mm

# wa.py - Function 15: Calculates abstracted surface water
def calc_sw_abstracted(df_mm):
    conditions = [
        df_mm["Qom(m^3)"] - df_mm["SW_need"] < 0,
        df_mm["Qom(m^3)"] - df_mm["SW_need"] >= df_mm["SW_need"]
    ]

    choices = [df_mm["Qom(m^3)"], df_mm["SW_need"]]

    df_mm["SW_abstracted"] = np.select(conditions, choices, default=df_mm["Qom(m^3)"] - df_mm["SW_need"])
    return df_mm

# wa.py - Function 16: Calculates remaining water after domestic surface water use
def calc_value_after_subtracting_domestic_sw_use(df_mm):
    df_mm["value_after_subtracting_domestic_SW_use"] = df_mm["Qom(m^3)"] - df_mm["SW_abstracted"]

    return df_mm


# wa.py - Function 17: Calculates complex water storage dynamics and abstractions
def calc_storage(df_mm, sw_storage_capacity_created, added_recharge_capacity, storage_limit):
    denominator = df_mm["Potential_recharge"] + df_mm["Potential_ET"] + df_mm["IWR_after_canal"]
    denominator[denominator == 0] = np.inf
    df_mm.loc[0, "Value after Rejected Recharge"] = to_float(manual_input.Previous_Month_Rejected_Recharge, 0) + df_mm.loc[
        0, "Qom(m^3)"]
    df_mm.loc[0, "Storage"] = min(sw_storage_capacity_created,
                                  df_mm.loc[0, "Value after Rejected Recharge"] +
                                  to_float(manual_input.Previous_Month_storage, 0) -
                                  df_mm.loc[0, "SW_abstracted"])
    df_mm.loc[0, "all_req_met"] = np.where(
        df_mm.loc[0, "Potential_recharge"] + df_mm.loc[0, "Potential_ET"] +
        df_mm.loc[0, "IWR_after_canal"] > df_mm.loc[0, "Storage"], 0, 1
    )
    conditions = df_mm.loc[0, "all_req_met"] == 0
    if conditions:
        # Apply calculations when all_req_met is 0
        df_mm.loc[0, "Actual_Recharge"] = (
                (df_mm.loc[0, "Storage"] / denominator[0]) * df_mm.loc[0, "Potential_recharge"]
        )
        df_mm.loc[0, "Actual_ET"] = (
                (df_mm.loc[0, "Storage"] / denominator[0]) * df_mm.loc[0, "Potential_ET"]
        )
        df_mm.loc[0, "Actual_IWR"] = (
                (df_mm.loc[0, "Storage"] / denominator[0]) * df_mm.loc[0, "IWR_after_canal"]
        )
    else:
        # Apply calculations when all_req_met is not 0
        df_mm.loc[0, "Actual_Recharge"] = df_mm.loc[0, "Potential_recharge"]
        df_mm.loc[0, "Actual_ET"] = df_mm.loc[0, "Potential_ET"]
        df_mm.loc[0, "Actual_IWR"] = df_mm.loc[0, "IWR_after_canal"]

    df_mm.loc[0, "Runoff_captured"] = df_mm.loc[0, "Storage"] - to_float(manual_input.Previous_Month_storage, 0)
    df_mm.loc[0, "Runoff_left_after_storage"] = df_mm.loc[0, "value_after_subtracting_domestic_SW_use"] - df_mm.loc[
        0, "Runoff_captured"]
    df_mm.loc[0, "Runoff in GW recharge str"] = added_recharge_capacity if (df_mm.loc[
                                                                                0, "Runoff_left_after_storage"] >
                                                                            added_recharge_capacity) else \
        df_mm.loc[0, "Runoff_left_after_storage"]
    df_mm.loc[0, "added_monthly_recharge"] = df_mm.loc[0, "Actual_Recharge"] + df_mm.loc[0, "Runoff in GW recharge str"]
    df_mm.loc[0, "Cumulative_storage_monthly"] = (
            df_mm.loc[0, "Residual_storage"] +
            df_mm.loc[0, "added_monthly_recharge"] +
            df_mm.loc[0, "Accumulated_natural_recharge"]
    )
    df_mm.loc[0, "GW_abstracted"] = np.minimum(df_mm.loc[0, "Cumulative_storage_monthly"], df_mm.loc[0, "GW_need"])
    df_mm.loc[0, "Cumulative_left_after_domestic_abstraction"] = max(0, df_mm.loc[0, "Cumulative_storage_monthly"] -
                                                                     df_mm.loc[0, "GW_abstracted"])
    conditions = [
        df_mm.loc[0, "Irr_water_need"] == 0,
        df_mm.loc[0, "Actual_IWR"] >= df_mm.loc[0, "Irr_water_need"],
        df_mm.loc[0, "Irr_water_need"] - df_mm.loc[0, "Actual_IWR"] <= df_mm.loc[
            0, "Cumulative_left_after_domestic_abstraction"]
    ]
    choices = [0, 0, df_mm.loc[0, "Irr_water_need"] - df_mm.loc[0, "Actual_IWR"]]
    df_mm.loc[0, "GW_extracted"] = np.select(conditions, choices,
                                             default=df_mm.loc[0, "Cumulative_left_after_domestic_abstraction"])
    df_mm.loc[0, "Cumulative_left_after_crop_abstraction"] = crop_pattern.safe_subtract(
        df_mm.loc[0, "Cumulative_left_after_domestic_abstraction"], df_mm.loc[0, "GW_extracted"])
    df_mm.loc[0, "Rejected_recharge"] = df_mm.loc[0, "Cumulative_left_after_crop_abstraction"] - storage_limit if \
        df_mm.loc[0, "Cumulative_left_after_crop_abstraction"] > storage_limit else 0
    df_mm.loc[0, "GW_left_after_rejected_recharge"] = (
            df_mm.loc[0, "Cumulative_left_after_crop_abstraction"] -
            df_mm.loc[0, "Rejected_recharge"]
    )
    df_mm.loc[0, "Captured Runoff in m³"] = df_mm.loc[0, "Runoff_captured"] + df_mm.loc[0, "Runoff in GW recharge str"]
    # Loop through the rows to calculate the values
    for i in range(1, len(df_mm)):
        df_mm.loc[i, "Value after Rejected Recharge"] = df_mm.loc[i - 1, "Rejected_recharge"] + df_mm.loc[i, "Qom(m^3)"]
        df_mm.loc[i, "Residual_storage"] = df_mm.loc[i - 1, "GW_left_after_rejected_recharge"]
        df_mm.loc[i, "Storage"] = min(sw_storage_capacity_created,
                                      df_mm.loc[i - 1, "Storage"] -
                                      df_mm.loc[i - 1, "Actual_Recharge"] -
                                      df_mm.loc[i - 1, "Actual_ET"] -
                                      df_mm.loc[i - 1, "Actual_IWR"] +
                                      df_mm.loc[i, "Value after Rejected Recharge"] -
                                      df_mm.loc[i, "SW_abstracted"])
        df_mm.loc[i, "all_req_met"] = np.where(
            df_mm.loc[i, "Potential_recharge"] + df_mm.loc[i, "Potential_ET"] +
            df_mm.loc[i, "IWR_after_canal"] > df_mm.loc[i, "Storage"], 0, 1
        )
        conditions = df_mm.loc[i, "all_req_met"] == 0
        if conditions:
            # Apply calculations when all_req_met is i
            df_mm.loc[i, "Actual_Recharge"] = (
                    (df_mm.loc[i, "Storage"] / denominator[i]) * df_mm.loc[i, "Potential_recharge"]
            )
            df_mm.loc[i, "Actual_ET"] = (
                    (df_mm.loc[i, "Storage"] / denominator[i]) * df_mm.loc[i, "Potential_ET"]
            )
            df_mm.loc[i, "Actual_IWR"] = (
                    (df_mm.loc[i, "Storage"] / denominator[i]) * df_mm.loc[i, "IWR_after_canal"]
            )
        else:
            # Apply calculations when all_req_met is not i
            df_mm.loc[i, "Actual_Recharge"] = df_mm.loc[i, "Potential_recharge"]
            df_mm.loc[i, "Actual_ET"] = df_mm.loc[i, "Potential_ET"]
            df_mm.loc[i, "Actual_IWR"] = df_mm.loc[i, "IWR_after_canal"]
        df_mm.loc[i, "Runoff_captured"] = df_mm.loc[i, "Storage"] - (
                df_mm.loc[i - 1, "Storage"] - df_mm.loc[i - 1, "Actual_Recharge"] -
                df_mm.loc[i - 1, "Actual_ET"] - df_mm.loc[i - 1, "Actual_IWR"])
        df_mm.loc[i, "Runoff_left_after_storage"] = df_mm.loc[i, "value_after_subtracting_domestic_SW_use"] - df_mm.loc[
            i, "Runoff_captured"]
        df_mm.loc[i, "Runoff in GW recharge str"] = added_recharge_capacity if (df_mm.loc[
                                                                                    i, "Runoff_left_after_storage"] >
                                                                                added_recharge_capacity) else \
            df_mm.loc[i, "Runoff_left_after_storage"]
        df_mm.loc[i, "added_monthly_recharge"] = df_mm.loc[i, "Actual_Recharge"] + df_mm.loc[
            i, "Runoff in GW recharge str"]
        df_mm.loc[i, "Cumulative_storage_monthly"] = (
                df_mm.loc[i, "Residual_storage"] +
                df_mm.loc[i, "added_monthly_recharge"] +
                df_mm.loc[i, "Accumulated_natural_recharge"]
        )
        df_mm.loc[i, "GW_abstracted"] = np.minimum(df_mm.loc[i, "Cumulative_storage_monthly"], df_mm.loc[i, "GW_need"])
        df_mm.loc[i, "Cumulative_left_after_domestic_abstraction"] = max(0, df_mm.loc[i, "Cumulative_storage_monthly"] -
                                                                         df_mm.loc[i, "GW_abstracted"])
        conditions1 = [
            df_mm.loc[i, "Irr_water_need"] == 0,
            df_mm.loc[i, "Actual_IWR"] >= df_mm.loc[i, "Irr_water_need"],
            df_mm.loc[i, "Irr_water_need"] - df_mm.loc[i, "Actual_IWR"] <= df_mm.loc[
                i, "Cumulative_left_after_domestic_abstraction"]
        ]
        choices1 = [0, 0, df_mm.loc[i, "Irr_water_need"] - df_mm.loc[i, "Actual_IWR"]]
        df_mm.loc[i, "GW_extracted"] = np.select(conditions1, choices1,
                                                 default=df_mm.loc[i, "Cumulative_left_after_domestic_abstraction"])
        df_mm.loc[i, "Cumulative_left_after_crop_abstraction"] = crop_pattern.safe_subtract(
            df_mm.loc[i, "Cumulative_left_after_domestic_abstraction"], df_mm.loc[i, "GW_extracted"])
        df_mm.loc[i, "Rejected_recharge"] = df_mm.loc[i, "Cumulative_left_after_crop_abstraction"] - storage_limit if \
            df_mm.loc[i, "Cumulative_left_after_crop_abstraction"] > storage_limit else 0
        df_mm.loc[i, "GW_left_after_rejected_recharge"] = (
                df_mm.loc[i, "Cumulative_left_after_crop_abstraction"] -
                df_mm.loc[i, "Rejected_recharge"]
        )
        df_mm.loc[i, "Captured Runoff in m³"] = df_mm.loc[i, "Runoff_captured"] + df_mm.loc[
            i, "Runoff in GW recharge str"]
    return df_mm


# wa.py - Function 18: Calculates percentage of irrigation water requirement fulfilled
def calc_per_irr_water_req_fulfilled(df_mm):
    df_mm["Percent_Irr_Water_Req_Fulfilled"] = np.where(
        df_mm["Total Irrigated Area"] == 0,
        0,
        np.where(
            df_mm["Irr_water_need"] == 0,
            1,
            crop_pattern.safe_divide(df_mm["Actual_IWR"] + df_mm["GW_extracted"], df_mm["Irr_water_need"])
        )
    )
    return df_mm


# wa.py - Function 19: Calculates crop water requirement met for each crop
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
            df_mm[rainfed_cwr_col] = (df_mm[etci_col] - df_mm[iwr_col])
            df_mm[irr_cwr_col_per] = np.where(df_mm[etci_col] == 0, 0, (df_mm[irr_cwr_col] / df_mm[etci_col]))
            df_mm[rainfed_cwr_col_per] = np.where(df_mm[etci_col] == 0, 0, (df_mm[rainfed_cwr_col] / df_mm[etci_col]))
    return df_mm


# wa.py - Function 20: Resamples monthly data to yearly aggregates
def get_resample_yr_optimized(df_mm, crops):
    print("FUNCTION 51: get_resample_yr_optimized() - Resampling yearly data")
    # List of columns to resample
    cols_to_resample = [f"ETci_{crop}" for crop in crops] + \
                       [f"Irr_CWR_met_{crop}" for crop in crops] + \
                       [f"Rainfed_CWR_met_{crop}" for crop in crops] + \
                       [f"AE_crop_{crop}" for crop in crops] + \
                       [f"AE_soil_{crop}" for crop in crops] + \
                       [f"IWR_{crop}" for crop in crops]
    # Resample the specified columns
    df_yr = df_mm[["Date"] + cols_to_resample].set_index("Date").resample("Y").sum().reset_index()
    return df_yr


# wa.py - Function 21: Calculates crop yields for irrigated and rainfed areas
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


# wa.py - Function 22: Calculates yields for all crops
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


# wa.py - Function 23: Calculates weighted averages for yield and water metrics
def calculate_weighted_averages(df_cc, df_yr, all_crops, yield_columns, other_columns):
    print("FUNCTION 54: calculate_weighted_averages() - Calculating weighted averages")
    # Initialize drought proofing components
    total_weighted_rainfed_yield = pd.Series(0, index=df_yr.index)
    total_weighted_irrigated_yield = pd.Series(0, index=df_yr.index)
    total_rainfed_area = df_cc["Rainfed_Area"].sum()
    total_irrigated_area = df_cc["Irr_Area"].sum()

    # Calculate weighted averages for yield-related metrics
    for output_column, (yield_template, area_column) in yield_columns.items():
        total_weighted_yield = pd.Series(0, index=df_yr.index)
        total_area = df_cc[area_column].sum()

        for crop in all_crops:
            yield_col = yield_template.format(crop=crop)
            if yield_col in df_yr.columns:
                area = df_cc.at[crop, area_column]
                total_weighted_yield += df_yr[yield_col] * area
                if area_column == "Rainfed_Area":
                    total_weighted_rainfed_yield += df_yr[yield_col] * area
                elif area_column == "Irr_Area":
                    total_weighted_irrigated_yield += df_yr[yield_col] * area

        df_yr[output_column] = ((total_weighted_yield / total_area) * 100) if total_area > 0 else 0

    # Calculate weighted averages for other metrics (e.g., CWR, CWA)
    for output_column, col_template in other_columns.items():
        df_yr[output_column] = pd.Series(0, index=df_yr.index)
        for crop in all_crops:
            metric_col = col_template.format(crop=crop)
            if metric_col in df_yr.columns:
                area = df_cc.at[crop, "Area"]
                df_yr[output_column] += df_yr[metric_col] * area

        total_area = df_cc["Area"].sum()
        df_yr[output_column] /= total_area if total_area > 0 else 1

    # # Calculate the "Drought Proofing" metric
    df_yr["Drought Proofing"] = (total_weighted_rainfed_yield + total_weighted_irrigated_yield) / (
                total_rainfed_area + total_irrigated_area)
    return df_yr


# wa.py - Function 24: Adds runoff to recharge calculations
def add_runoff_to_recharge(df_mm):
    new_columns = pd.DataFrame({
        "runoff to recharge": df_mm["Actual_Recharge_mm"] + df_mm["Runoff in GW recharge str_mm"]})
    df_mm = pd.concat([df_mm, new_columns], axis=1)
    return df_mm

# wa.py - Function 25: Calculates final runoff after storage
def calc_final_ro(df_mm):
    df_mm["final_ro"] = (df_mm["Qom"] - df_mm["Captured Runoff in m³_mm"]).clip(lower=0)
    return df_mm


# wa.py - Function 26: Calculates final runoff including rejected recharge
def calc_final_runoff(df_mm):
    df_mm["Final_Runoff"] = df_mm["final_ro"] + df_mm["Rejected_recharge_mm"]
    return df_mm


# wa.py - Function 27: Calculates final groundwater recharge
def calc_final_recharge(df_mm):
    df_mm["Final_Recharge"] = (df_mm["Recharge"] - df_mm["Rejected_recharge_mm"] + df_mm["runoff to recharge"]).clip(
        lower=0)
    return df_mm


# wa.py - Function 28: Calculates final evapotranspiration from water balance
def calc_final_et(df_mm):
    df_mm["Final_ET"] = (df_mm["Rain"] - df_mm["Final_Runoff"] - df_mm["Final_Recharge"]).clip(lower=0)
    return df_mm


# wa.py - Function 29: Calculates biological evapotranspiration from crop and soil
def calc_final_et_biological(df_mm, crops):
    """
    Calculate Final_ET from actual biological evapotranspiration instead of water balance residual.
    Sums AE_crop and AE_soil for all crops plus fallow evaporation.
    """
    # Initialize Final_ET with zeros
    df_mm["Final_ET_Bio"] = 0.0
    
    # Sum actual evapotranspiration from all crops
    for crop in crops:
        ae_crop_col = f"AE_crop_{crop}"
        ae_soil_col = f"AE_soil_{crop}"
        
        if ae_crop_col in df_mm.columns and ae_soil_col in df_mm.columns:
            df_mm["Final_ET_Bio"] += df_mm[ae_crop_col] + df_mm[ae_soil_col]
    
    # Add fallow area evapotranspiration if available
    if "AE_soil_Fallow" in df_mm.columns:
        df_mm["Final_ET_Bio"] += df_mm["AE_soil_Fallow"]
    
    # Keep biological ET for analysis, but use water balance ET for final results
    df_mm["Final_ET"] = (df_mm["Rain"] - df_mm["Final_Runoff"] - df_mm["Final_Recharge"]).clip(lower=0)
    
    return df_mm


# wa.py - Function 30: Gets crop water requirement in mm for all crops
def get_cwr_mm(df_yr, all_crops):
    df_cwr = pd.DataFrame({"Date": df_yr["Date"]})  # Create DataFrame with Date column
    for crop in all_crops:
        df_cwr[f"CWR_{crop}(mm)"] = df_yr[f"ETci_{crop}"]
        df_cwr[f"IWR_{crop}(mm)"] = df_yr[f"IWR_{crop}"]
    return df_cwr


# wa.py - Function 31: Gets percentage of crop water requirement met
def get_cwr_met(df_yr, all_crops):
    df_cwr_met = pd.DataFrame({"Date": df_yr["Date"]})
    for crop in all_crops:
        df_cwr_met[f"%Irr_CWR_met_{crop}"] = df_yr[f"%Irr_CWR_met_{crop}"]
        df_cwr_met[f"%Rf_CWR_met_{crop}"] = df_yr[f"%Rainfed_CWR_met_{crop}"]
    return df_cwr_met


# wa.py - Function 32: Gets yield percentages for all crops
def get_yield_per(df_yr, all_crops):
    df_yield = pd.DataFrame({"Date": df_yr["Date"]})
    for crop in all_crops:
        df_yield[f"%Irr_yield_{crop}"] = df_yr[f"Irr_yield_{crop}"]
        df_yield[f"%Rf_yield_{crop}"] = df_yr[f"Rainfed_yield_{crop}"]
        df_yield[f"%yield_{crop}"] = df_yr[f"Avg_yield_{crop}"]
    return df_yield


# wa.py - Function 33: Gets drought proofing index
def get_drought_proofness(df_yr):
    df_drought = pd.DataFrame({"Date": df_yr["Date"]})
    df_drought["Drought Proofing"] = df_yr["Drought Proofing"]
    return df_drought

# wa.py - Function 34: Gets crop water requirement for crop year
def get_cwr_mm_cyr(df_crop_yr,all_crops):
    df_cwr =  pd.DataFrame({"Date": df_crop_yr["water_year"]})
    for crop in all_crops:
        df_cwr[f"CWR_{crop}(mm)"] = df_crop_yr[f"ETci_{crop}"]
        df_cwr[f"IWR_{crop}(mm)"] = df_crop_yr[f"IWR_{crop}"]
    return df_cwr

# wa.py - Function 35: Gets crop water requirement met for crop year
def get_cwr_met_cyr(df_crop_yr, all_crops):
    df_cwr_met = pd.DataFrame({"Date": df_crop_yr["water_year"]})
    for crop in all_crops:
        df_cwr_met[f"%Irr_CWR_met_{crop}"] = df_crop_yr[f"%Irr_CWR_met_{crop}"]
        df_cwr_met[f"%Rf_CWR_met_{crop}"] = df_crop_yr[f"%Rainfed_CWR_met_{crop}"]
    return df_cwr_met

# wa.py - Function 36: Gets yield percentages for crop year
def get_yield_per_cyr(df_crop_yr, all_crops):
    df_yield = pd.DataFrame({"Date": df_crop_yr["water_year"]})
    for crop in all_crops:
        df_yield[f"%Irr_yield_{crop}"] = df_crop_yr[f"Irr_yield_{crop}"]
        df_yield[f"%Rf_yield_{crop}"] = df_crop_yr[f"Rainfed_yield_{crop}"]
        df_yield[f"%yield_{crop}"] = df_crop_yr[f"Avg_yield_{crop}"]
    return df_yield

# wa.py - Function 37: Gets drought proofing index for crop year
def get_drought_proofness_cyr(df_crop_yr):
    df_drought = pd.DataFrame({"Date": df_crop_yr["water_year"]})
    df_drought["Drought Proofing"] = df_crop_yr["Drought Proofing"]
    return df_drought
    

# wa.py - Function 38: Processes year data based on calendar or crop year
def process_year_data(df_yr, df_crop_yr, all_crops, year_type):
    print("FUNCTION 69: process_year_data() - Processing year data")
    year_type = year_type.strip().lower()

    if year_type == "calendar":
        # Run the functions if it's a calendar year
        df_cwr = get_cwr_mm(df_yr, all_crops)
        df_cwr_met = get_cwr_met(df_yr, all_crops)
        df_yield = get_yield_per(df_yr, all_crops)
        df_drought = get_drought_proofness(df_yr)
        
    elif year_type == "crop":
        # Run the crop year functions
        df_cwr = get_cwr_mm_cyr(df_crop_yr, all_crops)
        df_cwr_met = get_cwr_met_cyr(df_crop_yr, all_crops)
        df_yield = get_yield_per_cyr(df_crop_yr, all_crops)
        df_drought = get_drought_proofness_cyr(df_crop_yr)
        
    else:
        raise ValueError("Invalid year_type. Please choose either 'calendar' or 'crop'.")
    return df_cwr, df_cwr_met, df_yield, df_drought


# wa.py - Function 39: Gets earliest sowing month from crop plan
def get_sowing_month(df_cp):
    # Define the order of preference for seasons
    season_priority = ["Kharif", "Rabi", "Summer"]
    # Loop through the priority list
    for season in season_priority:
        # Filter rows where Season matches the current season
        season_df = df_cp[df_cp["Season"] == season].copy()  # Use .copy() to avoid the warning
        if not season_df.empty:
            # Extract the "Sowing_Month" column and convert it to datetime for comparison
            season_df.loc[:, "Sowing_Month"] = pd.to_datetime(season_df["Sowing_Month"], format="%b")
            # Get the earliest month
            smallest_month = season_df["Sowing_Month"].min()
            # Convert back to month name (e.g., "Jun")
            return smallest_month.strftime("%b")
    return None


# wa.py - Function 40: Processes water year data for crop or calendar year
def process_water_year_data(df_mm, df_cp, crops, year_type="crop"):
    # Prepare df_wb_mm with renamed columns
    df_wb_mm = df_mm[["Date", "Rain", "Final_Runoff", "Final_Recharge", "Final_ET", "Final_ET_Bio"]].copy()
    df_wb_mm.columns = ["Date", "Rain(mm)", "Runoff(mm)", "Recharge(mm)", "ET(mm)", "ET_Bio(mm)"]
    # Get the result month from the provided function
    result_month = get_sowing_month(df_cp)
    if result_month is None or result_month == "":
        result_month = "Jun"  # Default to June if no month found
    result_month_num = pd.to_datetime(f"{result_month} 1, 2000").month
    
    if year_type.strip().lower() == "calendar":
        water_year = df_mm["Date"].dt.year
    else:
        water_year = df_mm["Date"].dt.year.where(df_mm["Date"].dt.month >= result_month_num,
                                                 df_mm["Date"].dt.year - 1)
    
    df_mm = df_mm.assign(water_year=water_year)
    df_wb_mm = df_wb_mm.assign(water_year=water_year)

    # Create the column list to resample
    col_to_resample = [f"ETci_{crop}" for crop in crops] + \
                      [f"IWR_{crop}" for crop in crops] + \
                      [f"Irr_CWR_met_{crop}" for crop in crops] + \
                      [f"Rainfed_CWR_met_{crop}" for crop in crops]
    # Group by water year and sum for crops
    df_crop_yr = df_mm.groupby("water_year")[col_to_resample].sum().reset_index()
    # Group by water year and sum for water balance data
    df_wb_yr = df_wb_mm.groupby("water_year", as_index=False).agg({
        "Rain(mm)": "sum",
        "Runoff(mm)": "sum",
        "Recharge(mm)": "sum",
        "ET(mm)": "sum",
        "ET_Bio(mm)": "sum"
    })
    return df_crop_yr, df_wb_yr, df_wb_mm


# wa.py - Function 41: Calculates yields for water year analysis
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


# wa.py - Function 42: Calculates yields for water year for all crops
def calculate_yield_wyr(df_cc, df_crop_yr, all_crops):
    
    for crop in all_crops:
        irr_area = df_cc.at[crop, "Irr_Area"]
        rainfed_area = df_cc.at[crop, "Rainfed_Area"]
        ky_value = df_cc.at[crop, "Ky"]
        total_area = df_cc.at[crop, "Area"]
        df_crop_yr = calc_yields(df_crop_yr, crop, irr_area, rainfed_area, ky_value, total_area)
        
    return df_crop_yr


# wa.py - Function 43: Calculates weighted averages for water year metrics
def calc_weighted_avg(df_cc, df_crop_yr, all_crops, yield_columns, other_columns):
    # Initialize drought proofing components
    total_weighted_rainfed_yield = pd.Series(0, index=df_crop_yr.index)
    total_weighted_irrigated_yield = pd.Series(0, index=df_crop_yr.index)
    total_rainfed_area = df_cc["Rainfed_Area"].sum()
    total_irrigated_area = df_cc["Irr_Area"].sum()
    # Calculate weighted averages for yield-related metrics
    for output_column, (yield_template, area_column) in yield_columns.items():
        total_weighted_yield = pd.Series(0, index=df_crop_yr.index)
        total_area = df_cc[area_column].sum()

        for crop in all_crops:
            yield_col = yield_template.format(crop=crop)
            if yield_col in df_crop_yr.columns:
                area = df_cc.at[crop, area_column]
                total_weighted_yield += df_crop_yr[yield_col] * area
                if area_column == "Rainfed_Area":
                    total_weighted_rainfed_yield += df_crop_yr[yield_col] * area
                elif area_column == "Irr_Area":
                    total_weighted_irrigated_yield += df_crop_yr[yield_col] * area

        df_crop_yr[output_column] = (total_weighted_yield / total_area) if total_area > 0 else 0

    # Calculate weighted averages for other metrics (e.g., CWR, CWA)
    for output_column, col_template in other_columns.items():
        df_crop_yr[output_column] = pd.Series(0, index=df_crop_yr.index)
        for crop in all_crops:
            metric_col = col_template.format(crop=crop)
            if metric_col in df_crop_yr.columns:
                area = df_cc.at[crop, "Area"]
                df_crop_yr[output_column] += df_crop_yr[metric_col] * area

        total_area = df_cc["Area"].sum()
        df_crop_yr[output_column] /= total_area if total_area > 0 else 1

    # # Calculate the "Drought Proofing" metric
    df_crop_yr["Drought Proofing"] = (total_weighted_rainfed_yield + total_weighted_irrigated_yield) / (
                total_rainfed_area + total_irrigated_area)
    return df_crop_yr
