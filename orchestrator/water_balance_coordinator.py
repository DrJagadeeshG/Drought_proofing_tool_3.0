"""
Water balance coordination functions for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Coordinates complex water balance calculations including storage dynamics, irrigation demands, and groundwater abstractions
# ========================================

import numpy as np
from shared.utilities import to_float, mm_to_m3, m3_to_mm, safe_subtract, convert_dtypes
from shared.data_readers import irrigation_data_input
from aquifer_storage_bucket.processing.storage_tracking import calc_storage_residualgw
from surface_water_bucket.outflux.evaporation import calc_potential_et
from surface_water_bucket.influx.water_supply import calc_canal_supply
from soil_storage_bucket.outflux.irrigation_demand import get_iwr_after_canal
from aquifer_storage_bucket.influx.recharge_calculations import calc_potential_recharge
from aquifer_storage_bucket.outflux.domestic_demand import calc_domestic_need, calc_other_need, calc_gw_need
from surface_water_bucket.outflux.water_demand import calc_sw_need
from surface_water_bucket.outflux.water_abstraction import calc_sw_abstracted
from surface_water_bucket.processing.water_balance import calc_value_after_subtracting_domestic_sw_use, calc_final_runoff
from outputs.water_metrics import calc_per_irr_water_req_fulfilled, calc_cwr_met
from aquifer_storage_bucket.influx.recharge_calculations import add_runoff_to_recharge, calc_final_recharge
from surface_water_bucket.outflux.runoff_disposal import calc_final_ro
from soil_storage_bucket.outflux.evapotranspiration import calc_final_et, calc_final_et_biological


# water_balance_coordinator.py - Function 001: Processes water management including storage and irrigation
# Interactions: shared.data_readers.irrigation_data_input, aquifer_storage_bucket.processing.storage_tracking.calc_storage_residualgw, shared.utilities.mm_to_m3, shared.utilities.to_float, surface_water_bucket.outflux.evaporation.calc_potential_et, surface_water_bucket.influx.water_supply.calc_canal_supply, soil_storage_bucket.outflux.irrigation_demand.get_iwr_after_canal, aquifer_storage_bucket.influx.recharge_calculations.calc_potential_recharge, aquifer_storage_bucket.outflux.domestic_demand.calc_domestic_need, aquifer_storage_bucket.outflux.domestic_demand.calc_other_need, aquifer_storage_bucket.outflux.domestic_demand.calc_gw_need, surface_water_bucket.outflux.water_demand.calc_sw_need, surface_water_bucket.outflux.water_abstraction.calc_sw_abstracted, surface_water_bucket.processing.water_balance.calc_value_after_subtracting_domestic_sw_use, calc_storage, shared.utilities.m3_to_mm, outputs.water_metrics.calc_per_irr_water_req_fulfilled, outputs.water_metrics.calc_cwr_met
def process_water_management(df_mm, all_crops, surface_areas, added_recharges, water_resource_list, inp_aquifer_para, irrigation):
    (population, domestic_water_use, other, other_water_use,
     groundwater_dependent, sw_storage_capacity_created, added_recharge_capacity, storage_limit) = water_resource_list
    df_ir = irrigation_data_input(irrigation, df_mm)
    df_mm = calc_storage_residualgw(df_mm, inp_aquifer_para)
    df_mm["Accumulated_natural_recharge"] = mm_to_m3(to_float(inp_aquifer_para[3], 0), df_mm["Recharge"])
    # Calculate total surface area for farm
    total_surface_area_farm = surface_areas["farm"]
    # Perform calculations
    df_mm = calc_potential_et(total_surface_area_farm, df_mm)
    df_mm = calc_canal_supply(df_ir, df_mm)
    df_mm = get_iwr_after_canal(df_mm)
    df_mm = calc_potential_recharge(
        added_recharges["farm"],
        added_recharges["farm_lined"],
        added_recharges["check_dam"],
        df_mm
    )
    # Domestic and other water needs calculations
    df_mm = calc_domestic_need(population, domestic_water_use, df_mm)
    df_mm = calc_other_need(other, other_water_use, df_mm)
    # Groundwater and surface water needs calculations
    df_mm = calc_gw_need(df_mm, groundwater_dependent)
    df_mm = calc_sw_need(df_mm)
    df_mm = calc_sw_abstracted(df_mm)
    # Subtract domestic surface water use
    df_mm = calc_value_after_subtracting_domestic_sw_use(df_mm)
    # Storage calculations
    df_mm = calc_storage(df_mm, sw_storage_capacity_created, added_recharge_capacity, storage_limit)
    # Convert units from m³ to mm
    for col in ["Actual_Recharge", "Runoff in GW recharge str", "Captured Runoff in m³", "Rejected_recharge"]:
        df_mm[f"{col}_mm"] = m3_to_mm(to_float(inp_aquifer_para[3], 0), df_mm[col])
    # Final calculations for irrigation water requirement
    df_mm = calc_per_irr_water_req_fulfilled(df_mm)
    df_mm = calc_cwr_met(df_mm, all_crops)
    return df_mm


# water_balance_coordinator.py - Function 002: Processes final water balance calculations
# Interactions: aquifer_storage_bucket.influx.recharge_calculations.add_runoff_to_recharge, surface_water_bucket.outflux.runoff_disposal.calc_final_ro, surface_water_bucket.processing.water_balance.calc_final_runoff, aquifer_storage_bucket.influx.recharge_calculations.calc_final_recharge, soil_storage_bucket.outflux.evapotranspiration.calc_final_et_biological, soil_storage_bucket.outflux.evapotranspiration.calc_final_et, shared.utilities.convert_dtypes
def process_final_wb(df, all_crops=None):
    df = add_runoff_to_recharge(df)
    df = calc_final_ro(df)
    df = calc_final_runoff(df)
    df = calc_final_recharge(df)
    
    # Use biological ET calculation if crops are provided, otherwise use water balance
    if all_crops is not None:
        df = calc_final_et_biological(df, all_crops)
    else:
        df = calc_final_et(df)
    
    df = convert_dtypes(df)
    return df


# water_balance_coordinator.py - Function 003: Calculates complex water storage dynamics and abstractions
# Interactions: shared.utilities.to_float, shared.utilities.safe_subtract, numpy
def calc_storage(df_mm, sw_storage_capacity_created, added_recharge_capacity, storage_limit):
    denominator = df_mm["Potential_recharge"] + df_mm["Potential_ET"] + df_mm["IWR_after_canal"]
    denominator[denominator == 0] = np.inf
    df_mm.loc[0, "Value after Rejected Recharge"] = to_float(0, 0) + df_mm.loc[
        0, "Qom(m^3)"]
    df_mm.loc[0, "Storage"] = min(sw_storage_capacity_created,
                                  df_mm.loc[0, "Value after Rejected Recharge"] +
                                  to_float(0, 0) -
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
    df_mm.loc[0, "Runoff_captured"] = df_mm.loc[0, "Storage"] - to_float(0, 0)
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
    df_mm.loc[0, "Cumulative_left_after_crop_abstraction"] = safe_subtract(
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
        df_mm.loc[i, "Cumulative_left_after_crop_abstraction"] = safe_subtract(
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