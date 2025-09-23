"""
Curve number calculations for surface water bucket

This module contains functions for calculating curve numbers:
- Consolidated curve numbers for crops and land use
- Curve number calculations and adjustments

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates curve numbers for runoff estimation including crop CN values, land use consolidation, and moisture condition adjustments
# ========================================

import numpy as np
from shared.utilities import to_float, safe_divide, calc_lulc
from shared.land_use import calculate_total_area
from shared.crop_processing import calculate_total_sown_area, calc_fallow_area, calc_dormant
from orchestrator.input_collector import collect_inp_variables, collect_int_variables
from surface_water_bucket.processing.moisture_conditions import calc_amc_cond
from surface_water_bucket.input_data.curve_number_data import get_cn, get_fallow_cn_soil_type


# curve_numbers.py - Function 001: Calculates consolidated curve numbers for crops and land use
# Interactions: shared.land_use.calculate_total_area, update_cn2, shared.crop_processing.calculate_total_sown_area, calculate_consolidated_crop_cn2, shared.crop_processing.calc_fallow_area, shared.utilities.calc_lulc, calc_fallowcn2, calc_final_cn2, calc_cn2_adjusted, calc_cn1, calc_cn3, shared.crop_processing.calc_dormant, surface_water_bucket.processing.moisture_conditions.calc_amc_cond
def calc_crop_consolidated_cn(df_dd, df_crop, actual_cn2, df_cc, all_crops, inp_lulc_val_list, cn_values_list):
    print("FUNCTION 14: calc_crop_consolidated_cn() - Calculating crop consolidated CN values")
    area = calculate_total_area(inp_lulc_val_list)
    df_crop = update_cn2(df_crop, actual_cn2, df_cc, all_crops)
    df_crop = calculate_total_sown_area(df_crop, all_crops, inp_lulc_val_list[0])
    df_crop = calculate_consolidated_crop_cn2(df_crop, all_crops)
    df_crop["Fallow_area"] = df_crop.apply(
        lambda row: calc_fallow_area(inp_lulc_val_list[0], row["Actual Crop Sown Area"], inp_lulc_val_list[1]), axis=1)
    df_crop["Builtup_area"] = df_crop.apply(lambda row: calc_lulc(inp_lulc_val_list[2], area), axis=1)
    df_crop["Waterbodies_area"] = df_crop.apply(lambda row: calc_lulc(inp_lulc_val_list[3], area),
                                                axis=1)
    df_crop["Pasture"] = df_crop.apply(lambda row: calc_lulc(inp_lulc_val_list[4], area), axis=1)
    df_crop["Forest"] = df_crop.apply(lambda row: calc_lulc(inp_lulc_val_list[5], area), axis=1)
    df_crop["Crop_Area"] = df_crop.apply(lambda row: calc_lulc(row["Actual Crop Sown Area"], area),
                                         axis=1)
    df_crop["Fallow_Area"] = df_crop.apply(lambda row: calc_lulc(row["Fallow_area"], area), axis=1)
    df_crop["Fallowcn2"] = df_crop["Fallow_area"].apply(lambda x: calc_fallowcn2(x, cn_values_list[1]))
    df_crop["Final_cn2"] = df_crop.apply(lambda row: calc_final_cn2(row["Builtup_area"], cn_values_list[2],
                                                                    row["Waterbodies_area"], cn_values_list[3],
                                                                    row["Pasture"], cn_values_list[4],
                                                                    row["Forest"], cn_values_list[5],
                                                                    row["Crop_Area"], row["consolidated_crop_cn2"],
                                                                    row["Fallow_Area"], row["Fallowcn2"]), axis=1)

    df_crop["Final_CN2"] = calc_cn2_adjusted(df_crop["Final_cn2"], cn_values_list[0])
    df_crop["Final_CN1"] = df_crop["Final_cn2"].apply(calc_cn1)
    df_crop["Final_CN3"] = df_crop["Final_cn2"].apply(calc_cn3)
    df_crop["Dormant"] = df_crop["Actual Crop Sown Area"].apply(calc_dormant)
    df_crop["AMC"] = calc_amc_cond(df_dd, df_crop)
    
    # CRITICAL FIX: Recalculate Final CN values after consolidated_crop_cn2 is updated
    df_crop["Final_cn2"] = df_crop.apply(lambda row: calc_final_cn2(row["Builtup_area"], cn_values_list[2],
                                                                    row["Waterbodies_area"], cn_values_list[3],
                                                                    row["Pasture"], cn_values_list[4],
                                                                    row["Forest"], cn_values_list[5],
                                                                    row["Crop_Area"], row["consolidated_crop_cn2"],
                                                                    row["Fallow_Area"], row["Fallowcn2"]), axis=1)
    df_crop["Final_CN2"] = calc_cn2_adjusted(df_crop["Final_cn2"], cn_values_list[0])
    df_crop["Final_CN1"] = df_crop["Final_cn2"].apply(calc_cn1)
    df_crop["Final_CN3"] = df_crop["Final_cn2"].apply(calc_cn3)
    
    return df_crop


# curve_numbers.py - Function 002: Retrieves all curve number values for seasons
# Interactions: calculate_cn_values
def get_all_cn_values(seasons, df_cc, crop_df, soil_output_list):
    all_cn_values = {}

    for season_name, crops, crops_type, crop_sown_type in seasons:
        cn_values = calculate_cn_values(
            crops, crops_type, crop_sown_type, df_cc, crop_df,
            soil_output_list[4], soil_output_list[5],
            soil_output_list[2], soil_output_list[3]
        )
        all_cn_values.update(cn_values)
    return all_cn_values


# curve_numbers.py - Function 003: Processes and calculates actual curve number values
# Interactions: get_all_cn_values, calculate_actual_cn, calc_red_cn_area, surface_water_bucket.input_data.curve_number_data.get_fallow_cn_soil_type, calc_act_fallow_cn2
def process_cn_values(seasons, df_cc, crop_df, soil_output_list, all_crops,inp_source,master_path):
    # Get all CN values
    all_cn_values = get_all_cn_values(seasons, df_cc, crop_df, soil_output_list)
    # Calculate Actual CN2 values and update all_cn_values
    actual_cn2 = calculate_actual_cn(all_cn_values,inp_source,master_path)
    df_cc = calc_red_cn_area(df_cc, all_crops, actual_cn2,inp_source, master_path)
    # Safely attempt to get the CN values, defaulting to 0 if an error occurs
    cn_f1 = float(get_fallow_cn_soil_type(crop_df, soil_output_list[4]) or 0)
    cn_f2 = float(get_fallow_cn_soil_type(crop_df, soil_output_list[5]) or 0)
    # Calculate the actual Fallow CN2
    actual_fallow_cn2 = calc_act_fallow_cn2(cn_f1, cn_f2,inp_source,master_path)
    return df_cc, actual_fallow_cn2, actual_cn2


# curve_numbers.py - Function 004: Calculates curve number values for all crops considering two soil layers
# Interactions: surface_water_bucket.input_data.curve_number_data.get_cn
def calculate_cn_values(crop_list, crop_type_list, crop_sown_type_list, df_cc, crop_df, soil_type1, soil_type2, hsc1,
                        hsc2):
    cn_values = {}

    for i, crop in enumerate(crop_list):

        if not crop:
            continue
        # Initialize crop_type and crop_sown_type with None
        crop_type = None
        crop_sown_type = None

        # Check if the index exists in crop_type_list and crop_sown_type_list
        if i < len(crop_type_list) and crop_type_list[i]:
            crop_type = crop_type_list[i]
        if i < len(crop_sown_type_list) and crop_sown_type_list[i]:
            crop_sown_type = crop_sown_type_list[i]

        # If crop_type or crop_sown_type is still None, get values from df_cc
        if crop_type is None or crop_sown_type is None:
            if crop in df_cc.index:
                crop_type = crop_type or df_cc.loc[crop, "Cover Type"]
                crop_sown_type = crop_sown_type or df_cc.loc[crop, "Treatment Type"]
            else:
                print(f"Crop {crop} not found in df_cc")
                continue

        # Get CN values based on the crop type and soil type
        cn1 = get_cn(crop_df, crop_type, crop_sown_type, hsc1, soil_type1)
        cn2 = get_cn(crop_df, crop_type, crop_sown_type, hsc2, soil_type2)
        # Add the CN values to the dictionary
        cn_values[crop] = {
            "CN1": cn1,
            "CN2": cn2
        }
    return cn_values


# curve_numbers.py - Function 005: Calculates weighted actual CN2 value from two soil layer contributions
# Interactions: None
def calc_act_cn2(cn1, cn2, dist1, dist2):
    if cn1 is not None and cn2 is not None:
        try:
            cn = ((dist1 * float(cn1)) + (dist2 * float(cn2))) / 100
            return cn
        except ValueError:
            print("Error converting CN values to float.")
            return None
    else:
        print("Cannot calculate Actual CN2 due to missing CN values.")
        return None


# curve_numbers.py - Function 006: Calculates actual curve numbers for all crops using input distributions
# Interactions: orchestrator.input_collector.collect_inp_variables, calc_act_cn2, shared.utilities.to_float
def calculate_actual_cn(all_cn_values,inp_source,master_path):
    print("FUNCTION 22: calculate_actual_cn() - Calculating actual CN values")
    inp_var = collect_inp_variables(inp_source,master_path)
    updated_cn_values = {}

    for crop, cn_data in all_cn_values.items():
        cn1 = cn_data.get("CN1")
        cn2 = cn_data.get("CN2")

        loc_actual_cn2 = calc_act_cn2(cn1, cn2, to_float(inp_var["dist1"], 0), to_float(inp_var["dist2"], 0))

        updated_cn_values[crop] = {
            "CN1": cn1,
            "CN2": cn2,
            "Actual_CN2": loc_actual_cn2
        }

    return updated_cn_values


# curve_numbers.py - Function 007: Calculates reduced curve numbers considering conservation interventions
# Interactions: orchestrator.input_collector.collect_int_variables, shared.utilities.to_float, shared.utilities.safe_divide
def calc_red_cn_area(df_cc, all_crops, dict_actual_cn2, inp_source, master_path):
    print("FUNCTION 23: calc_red_cn_area() - Calculating reduced CN area")
    inp_var = collect_int_variables(inp_source, master_path)
    
    for crop in all_crops:
        if crop in dict_actual_cn2:
            # Total_Int_Area calculation
            df_cc.at[crop, "Total_Int_Area"] = (
                df_cc.at[crop, "Cover_Area"] + df_cc.at[crop, "Mulching_Area"] +
                df_cc.at[crop, "Bunds_Area"] + df_cc.at[crop, "Tillage_Area"] +
                df_cc.at[crop, "BBF_Area"] + df_cc.at[crop, "Tank_Area"]
            )
            if df_cc.at[crop, "Total_Int_Area"] != 0:
                df_cc.at[crop, "Red_CN2"] = safe_divide(
                    (
                        df_cc.at[crop, "Cover_Area"] * to_float(inp_var.get("Red_CN_Cover_Crops", 0)) +
                        df_cc.at[crop, "Mulching_Area"] * to_float(inp_var.get("Red_CN_Mulching", 0)) +
                        df_cc.at[crop, "Bunds_Area"] * to_float(inp_var.get("Red_CN_Bund", 0)) +
                        df_cc.at[crop, "Tillage_Area"] * to_float(inp_var["Red_CN_Tillage"], 0) +
                        df_cc.at[crop, "BBF_Area"] * to_float(inp_var["Red_CN_BBF"], 0) +
                        df_cc.at[crop, "Tank_Area"] * to_float(inp_var.get("Red_CN_Tillage", 0))
                    ),
                    df_cc.at[crop, "Total_Int_Area"]
                )
            else:
                df_cc.at[crop, "Red_CN2"] = 0
            # CN2 calculation
            df_cc.at[crop, "CN2"] = dict_actual_cn2[crop]["Actual_CN2"] - df_cc.at[crop, "Red_CN2"]
            # No_Int_Area calculation
            df_cc.at[crop, "No_Int_Area"] = df_cc.at[crop, "Area"] - df_cc.at[crop, "Total_Int_Area"]
            # New_CN2 calculation
            df_cc.at[crop, "New_CN2"] = (
                (df_cc.at[crop, "Total_Int_Area"] * df_cc.at[crop, "CN2"]) +
                (df_cc.at[crop, "No_Int_Area"] * dict_actual_cn2[crop]["Actual_CN2"])
            ) / df_cc.at[crop, "Area"]

    return df_cc


# curve_numbers.py - Function 008: Calculates actual fallow curve number from two soil layer contributions
# Interactions: orchestrator.input_collector.collect_inp_variables
def calc_act_fallow_cn2(cn_f1, cn_f2, inp_source, master_path):
    inp_var = collect_inp_variables(inp_source, master_path)
    
    # Access dist1 and dist2 from the input variables
    dist1_raw = inp_var.get("dist1", 0)
    dist2_raw = inp_var.get("dist2", 0)
    
    dist1 = float(dist1_raw[0]) if isinstance(dist1_raw, (list, tuple)) else float(dist1_raw)
    dist2 = float(dist2_raw[0]) if isinstance(dist2_raw, (list, tuple)) else float(dist2_raw)
    
    try:
        cn = ((dist1 * cn_f1) + (dist2 * cn_f2)) / 100
    except Exception as e:
        print(f"Error during CN calculation: {e}")
        cn = None

    return cn


# curve_numbers.py - Function 009: Returns curve number for crop based on sown area status
# Interactions: None
def calc_crop_cn2(sown_area, actual_cn2):
    return actual_cn2 if sown_area > 0 else 0


# curve_numbers.py - Function 010: Updates crop curve numbers in dataframe for all crops
# Interactions: calc_crop_cn2
def update_cn2(df_crop, actual_cn2, df_cc, all_crops):
    for crop in all_crops:
        if crop in actual_cn2:
            # Get the actual CN2 value from the dictionary or fallback to df_cc
            if isinstance(actual_cn2[crop], dict):
                actual_cn2_value = actual_cn2[crop].get("Actual_CN2", 0)
            else:
                actual_cn2_value = actual_cn2[crop]
            
            # If still 0 or None, try to get from df_cc
            if not actual_cn2_value and crop in df_cc.index:
                actual_cn2_value = df_cc.at[crop, "New_CN2"]
                
            df_crop[f"{crop}_CN2"] = df_crop.apply(
                lambda row: calc_crop_cn2(row.get(f"{crop}_Sown_Area", 0), actual_cn2_value), axis=1
            )
        else:
            print(f"Warning: No Actual_CN2 value found for {crop}")
    return df_crop


# curve_numbers.py - Function 011: Calculates area-weighted consolidated curve number for all crops
# Interactions: None
def calculate_consolidated_crop_cn2(df_crop, all_crops):
    print("FUNCTION 24: calculate_consolidated_crop_cn2() - Calculating consolidated crop CN2")
    def consolidated_crop_cn2(sown_area, actual_crop_sown_area, crop_cn2):
        if actual_crop_sown_area > 0:
            return (sown_area / actual_crop_sown_area) * crop_cn2
        else:
            return 0
    # Initialize the new column with zeros
    df_crop["consolidated_crop_cn2"] = 0

    # Iterate over each crop and update the consolidated CN2 value
    for selected_crop in all_crops:
        sown_area_col = f"{selected_crop}_Sown_Area"
        crop_cn2_col = f"{selected_crop}_CN2"

        if sown_area_col in df_crop.columns and crop_cn2_col in df_crop.columns:
            df_crop["consolidated_crop_cn2"] += df_crop.apply(
                lambda row: consolidated_crop_cn2(row[sown_area_col],
                                                  row["Actual Crop Sown Area"],
                                                  row[crop_cn2_col]), axis=1)

    # Clip the values to a maximum of 100
    df_crop["consolidated_crop_cn2"] = df_crop["consolidated_crop_cn2"].clip(upper=100)
    return df_crop


# curve_numbers.py - Function 012: Returns fallow curve number based on fallow area presence
# Interactions: None
def calc_fallowcn2(fallow_area, actual_fallow_cn2):
    return actual_fallow_cn2 if fallow_area > 0 else 0


_calc_final_cn2_printed = False

# curve_numbers.py - Function 013: Calculates area-weighted final curve number from all land uses
# Interactions: None
def calc_final_cn2(x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6):
    global _calc_final_cn2_printed
    if not _calc_final_cn2_printed:
        print("FUNCTION 25: calc_final_cn2() - Calculating final CN2 values")
        _calc_final_cn2_printed = True
    y = x1 * y1 + x2 * y2 + x3 * y3 + x4 * y4 + x5 * y5 + x6 * y6
    return y


# curve_numbers.py - Function 014: Adjusts curve number based on slope using Williams formula
# Interactions: numpy
def calc_cn2_adjusted(final_cn2, inp_slope):
    inp_slope = inp_slope/100
    cn2_adjusted = final_cn2 * ((1.9274 * inp_slope + 2.1327) / (inp_slope + 2.1791))
    return np.minimum(cn2_adjusted, 100)


# curve_numbers.py - Function 015: Calculates CN1 (dry conditions) from CN2 using standard formula
# Interactions: None
def calc_cn1(final_cn2):
    cn1 = final_cn2 / (2.281 - 0.01281 * final_cn2)
    return cn1


# curve_numbers.py - Function 016: Calculates CN3 (wet conditions) from CN2 using standard formula
# Interactions: None
def calc_cn3(final_cn2):
    cn3 = final_cn2 / (0.427 + 0.00573 * final_cn2)
    return cn3


# curve_numbers.py - Function 017: Selects appropriate curve number based on antecedent moisture condition
# Interactions: numpy
def calc_cn(df_crop):
    conditions = [
        df_crop["AMC"] == 1,
        df_crop["AMC"] == 2
    ]
    choices = [df_crop["Final_CN1"], df_crop["Final_CN2"]]
    cn = np.select(conditions, choices, default=df_crop["Final_CN3"])
    return cn