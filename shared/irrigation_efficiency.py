"""
Irrigation efficiency calculations for drought proofing tool

This module contains functions for calculating irrigation efficiency:
- Weighted irrigation efficiency from surface and groundwater sources
- Overall irrigation efficiency considering all intervention types

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates irrigation efficiency from different sources and intervention types for drought proofing analysis
# ========================================
import pandas as pd
import numpy as np
from shared.utilities import to_float, get_percentage, safe_divide


# irrigation_efficiency.py - Function 001: Calculates weighted irrigation efficiency from surface and groundwater sources
# Interactions: shared.utilities.to_float, shared.utilities.get_percentage
def calc_irr_eff(area_eff_list,inp_lulc_val_list):
    sw_area = to_float(area_eff_list[0],0)
    gw_area = to_float(area_eff_list[1], 0)
    net_crop_sown_area = to_float(inp_lulc_val_list[0], 0)
    sw_area_irr_eff = (to_float(area_eff_list[2], 0))/100
    gw_area_irr_eff = (to_float(area_eff_list[3], 0))/100
    # Calculate the percentages
    gw_area = round(get_percentage(gw_area, net_crop_sown_area), 3)
    sw_area = round(get_percentage(sw_area, net_crop_sown_area), 3)
    # Extract the irrigation efficiency or use the default
    sw_eff = sw_area_irr_eff if sw_area_irr_eff else (area_eff_list[4])/100
    gw_eff = gw_area_irr_eff if gw_area_irr_eff else (area_eff_list[4])/100
    # Calculate the irrigation efficiency
    irr_eff = round(((gw_area * gw_eff) + (sw_area * sw_eff)) / net_crop_sown_area, 3)
    return irr_eff


# irrigation_efficiency.py - Function 002: Calculates overall irrigation efficiency considering all intervention types
# Interactions: shared.utilities.safe_divide, shared.utilities.to_float, shared.utilities.convert_dtypes, pandas, numpy
def calc_overall_eff(df_mm, df_cc, crops, irr_eff):
    print("FUNCTION 40: calc_overall_eff() - Calculating overall irrigation efficiency")
    # Calculate Area_with_Intervention
    area_with_intervention = (df_cc["Drip_Area"] +
                              df_cc["Sprinkler_Area"] +
                              df_cc["BBF_Area"])
    
    # Calculate Intervention_area_eff
    intervention_area_eff = safe_divide(
        (df_cc["Drip_Area"] * df_cc["Eff_Drip"] +
         df_cc["Sprinkler_Area"] * df_cc["Eff_Sprinkler"] +
         df_cc["BBF_Area"] * df_cc["Eff_BBF"]),
        area_with_intervention
    )

    # Calculate Water_saved_area
    water_saved_area = (df_cc["Land_Levelling_Area"] +
                        df_cc["DSR_Area"] +
                        df_cc["AWD_Area"] +
                        df_cc["SRI_Area"] +
                        df_cc["Ridge_Furrow_Area"] +
                        df_cc["Deficit_Area"])

    # Calculate Water_saved_eff
    water_saved_eff = safe_divide(
        (df_cc["Land_Levelling_Area"] * df_cc["Eff_Land_Levelling"] +
         df_cc["DSR_Area"] * df_cc["Eff_DSR"] +
         df_cc["AWD_Area"] * df_cc["Eff_AWD"] +
         df_cc["SRI_Area"] * df_cc["Eff_SRI"] +
         df_cc["Ridge_Furrow_Area"] * df_cc["Eff_Ridge_Furrow"] +
         df_cc["Deficit_Area"] * df_cc["Eff_Deficit"]),
        water_saved_area
    )

    # Calculate Area_without_Intervention
    area_without_intervention = np.where(
        df_cc["Irr_Area"] >= area_with_intervention,
        df_cc["Irr_Area"] - area_with_intervention,
        np.nan  # Set to NaN if the condition is not met
    )

    # Calculate Overall_eff
    overall_eff = safe_divide(
        (area_with_intervention * intervention_area_eff +
         area_without_intervention * irr_eff),
        df_cc["Irr_Area"]
    )

    # Calculate Area_without_Water_saving_Intervention
    area_without_water_saving_intervention = np.where(
        df_cc["Irr_Area"] >= water_saved_area,
        df_cc["Irr_Area"] - water_saved_area,
        np.nan  # Set to NaN if the condition is not met
    )

    # Calculate Overall_water_saved_eff
    overall_water_saved_eff = safe_divide(
        (water_saved_area * water_saved_eff +
         area_without_water_saving_intervention * (to_float(0, 0)/100)),  # Using default value instead of manual_input
        df_cc["Irr_Area"]
    )

    # Calculate Eff_after_WS and Eff_after_rf
    eff_after_ws = ((1 - overall_eff) * overall_water_saved_eff) + overall_eff
    eff_after_rf = ((1 - eff_after_ws) * df_cc["Over_all_rf"]) + eff_after_ws

    # Calculate Final_eff
    final_eff = eff_after_rf.fillna(0)

    # Concatenate the new columns back into df_cc
    df_cc = pd.concat([
        df_cc,
        pd.DataFrame({
            "Area_with_Intervention": area_with_intervention,
            "Intervention_area_eff": intervention_area_eff,
            "Water_saved_area": water_saved_area,
            "Water_saved_eff": water_saved_eff,
            "Area_without_Intervention": area_without_intervention,
            "Overall_eff": overall_eff,
            "Area_without_Water_saving_Intervention": area_without_water_saving_intervention,
            "Overall_water_saved_eff": overall_water_saved_eff,
            "Eff_after_WS": eff_after_ws,
            "Eff_after_rf": eff_after_rf,
            "Final_eff": final_eff
        }, index=df_cc.index)
    ], axis=1)

    # Iterate over each crop and calculate respective irrigation efficiency
    for crop in crops:
        irr_area_col = f"Irr_Area_{crop}"
        eff_col = f"Irrigation_eff_{crop}"
        iwr_col = f"IWR_{crop}"
        water_need_col = f"Irr_water_need_{crop}"
        final_eff_col = "Final_eff"  # Assuming "Final_eff" is present in df_cc

        # Ensure "Final_eff" is available in df_cc
        if final_eff_col in df_cc.columns:
            # Calculate irrigation efficiency for the crop
            df_mm[eff_col] = df_mm.apply(
                lambda row: df_cc.loc[crop, final_eff_col] if row[irr_area_col] > 0 else 0,
                axis=1
            ).astype(float)

        # Ensure columns exist in DataFrames
        if iwr_col in df_mm.columns and irr_area_col in df_mm.columns and eff_col in df_mm.columns:
            # Calculate irrigation water need for the crop
            df_mm[water_need_col] = safe_divide(
                (df_mm[iwr_col] / 1000) * df_mm[irr_area_col] * 10000, df_mm[eff_col]
            )

    # Sum all crop irrigation water needs across the dataset
    df_mm["Irr_water_need"] = df_mm.filter(like="Irr_water_need_").sum(axis=1)
    df_mm["Total Irrigated Area"] = df_mm.filter(like="Irr_Area_").sum(axis=1)
    df_mm["Total Rainfed Area"] = df_mm.filter(like="Rainfed_Area_").sum(axis=1)

    # Print error message if Water_saved_area exceeds Irr_Area
    error_rows = df_cc[df_cc["Irr_Area"] < df_cc["Water_saved_area"]]
    if not error_rows.empty:
        print("Error: The following rows have Irr_Area <= Area_with_Intervention:")
        print(error_rows)

    # Convert data types for df_cc
    from shared.utilities import convert_dtypes
    df_cc = convert_dtypes(df_cc)

    return df_cc, df_mm