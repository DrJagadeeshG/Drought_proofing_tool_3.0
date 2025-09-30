
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:52:52 2024

@author: Dr. Jagadeesh, Consultant, IWMI
"""
import pandas as pd
import numpy as np
import manual_input
import kc_et
import smd
import wa
import crop_pattern
import Economic
from user_input import collect_int_variables
from user_input import collect_inp_variables
from user_input import to_float
from user_input import get_file_paths
import functools
import pickle
import hashlib


# drpf_functions.py - Function 1: Retrieves and caches season-wise crop data including areas and sowing details
@functools.lru_cache(maxsize=128)
def get_season_data(inp_source,master_path):
    print("FUNCTION 8: get_season_data() - Getting season data for crops [CACHED]")
    # Collect input variables using your `collect_inp_variables()` function
    inp_variables = collect_inp_variables(inp_source,master_path)

    # Construct the season_data dictionary
    season_data = {
        "Kharif": {
            "Crops": inp_variables["Kharif_Crops"],
            "Sowing_Month": inp_variables["Kharif_Sowing_Month"],
            "Sowing_Week": inp_variables["Kharif_Sowing_Week"],
            "Irrigated_Area": inp_variables["Kharif_Crops_Irr_Area"],
            "Rainfed_Area": inp_variables["Kharif_Crops_Rainfed_Area"]
        },
        "Rabi": {
            "Crops": inp_variables["Rabi_Crops"],
            "Sowing_Month": inp_variables["Rabi_Sowing_Month"],
            "Sowing_Week": inp_variables["Rabi_Sowing_Week"],
            "Irrigated_Area": inp_variables["Rabi_Crops_Irr_Area"],
            "Rainfed_Area": inp_variables["Rabi_Crops_Rainfed_Area"]
        },
        "Summer": {
            "Crops": inp_variables["Summer_Crops"],
            "Sowing_Month": inp_variables["Summer_Sowing_Month"],
            "Sowing_Week": inp_variables["Summer_Sowing_Week"],
            "Irrigated_Area": inp_variables["Summer_Crops_Irr_Area"],
            "Rainfed_Area": inp_variables["Summer_Crops_Rainfed_Area"]
        }
    }

    return season_data

# drpf_functions.py - Function 2: Retrieves land use type areas including crop, fallow, built-up areas
def get_land_use_types(inp_source,master_path):
    # Collect input variables using your `collect_inp_variables()` function
    inp_variables = collect_inp_variables(inp_source,master_path)

    # Construct the land_use_types dictionary
    land_use_types = {
        "Net_Crop_Sown_Area": inp_variables["Net_Crop_Sown_Area"],
        "Fallow": inp_variables["Fallow"],
        "Builtup": inp_variables["Builtup"],
        "Water_bodies": inp_variables["Water_bodies"],
        "Pasture": inp_variables["Pasture"],
        "Forest": inp_variables["Forest"]
    }

    return land_use_types

fixed_values = {
    "Ia_AMC1": manual_input.Ia_AMC1,
    "Ia_AMC2": manual_input.Ia_AMC2,
    "Ia_AMC3": manual_input.Ia_AMC3,
    "Soil_GWrecharge_coefficient": manual_input.Soil_GWrecharge_coefficient
}



# drpf_functions.py - Function 3: Processes monthly runoff and converts to cubic meters
def process_monthly_qi(df_dd, df_mm, inp_aquifer_para):
    # Calculate monthly Qi
    df_mm = kc_et.calculate_monthly_qi(df_dd, df_mm)
    # Convert Qom from mm to m^3
    df_mm["Qom(m^3)"] = crop_pattern.mm_to_m3(to_float(inp_aquifer_para[3], 0), df_mm["Qom"])
    return df_mm

# drpf_functions.py - Function 4: Calculates soil properties including AWC and depths
def soil_calculation(inp_source,master_path):
    inp_vars = collect_inp_variables(inp_source,master_path)

    soil_type1 = kc_et.get_soil_type(inp_vars["Soil_type1"])
    soil_type2 = kc_et.get_soil_type(inp_vars["Soil_type2"])
    hsc1 = kc_et.get_soil_type(inp_vars["HSC1"])
    hsc2 = kc_et.get_soil_type(inp_vars["HSC2"])
    awc_1 = kc_et.calculate_awc(soil_type1)
    awc_2 = kc_et.calculate_awc(soil_type2) if soil_type2 else None
    dist1 = inp_vars["dist1"]
    dist2 = inp_vars["dist2"]
    soil_type1_dep = inp_vars["Soil_type1_dep"]
    soil_type2_dep = inp_vars["Soil_type2_dep"]
    
    loc_soil_list = [awc_1, awc_2, hsc1, hsc2, soil_type1, soil_type2, dist1, dist2, soil_type1_dep, soil_type2_dep]
    return loc_soil_list

# drpf_functions.py - Function 5: Retrieves season values with crop types and sowing details
def get_seasons_val(inp_source,master_path):
    inp_vars = collect_inp_variables(inp_source,master_path)
    seasons = [
        ("Kharif", inp_vars["Kharif_Crops"], inp_vars["Kharif_Sowing_Month"], inp_vars["Kharif_Sowing_Week"], 
         inp_vars["Kharif_Crops_Type"], inp_vars["Kharif_Crop_Sown_Type"]),
        ("Rabi", inp_vars["Rabi_Crops"], inp_vars["Rabi_Sowing_Month"], inp_vars["Rabi_Sowing_Week"], 
         inp_vars["Rabi_Crops_Type"], inp_vars["Rabi_Crop_Sown_Type"]),
        ("Summer", inp_vars["Summer_Crops"], inp_vars["Summer_Sowing_Month"], inp_vars["Summer_Sowing_Week"], 
         inp_vars["Summer_Crops_Type"], inp_vars["Summer_Crop_Sown_Type"])
    ]
    
    return seasons
# drpf_functions.py - Function 6: Retrieves season data for crop type processing
def get_seasons_data(inp_source,master_path):
    inp_vars = collect_inp_variables(inp_source,master_path)
    seasons = [
        ("Kharif", inp_vars["Kharif_Crops"], inp_vars["Kharif_Crops_Type"], inp_vars["Kharif_Crop_Sown_Type"]),
        ("Rabi", inp_vars["Rabi_Crops"], inp_vars["Rabi_Crops_Type"], inp_vars["Rabi_Crop_Sown_Type"]),
        ("Summer", inp_vars["Summer_Crops"], inp_vars["Summer_Crops_Type"], inp_vars["Summer_Crop_Sown_Type"])
    ]
    return seasons

# drpf_functions.py - Function 7: Calculates consolidated curve numbers for crops and land use
def calc_crop_consolidated_cn(df_dd, df_crop, actual_cn2, df_cc, all_crops, inp_lulc_val_list, cn_values_list):
    print("FUNCTION 14: calc_crop_consolidated_cn() - Calculating crop consolidated CN values")
    area = crop_pattern.calculate_total_area(inp_lulc_val_list)
    df_crop = kc_et.update_cn2(df_crop, actual_cn2, df_cc, all_crops)
    df_crop = kc_et.calculate_total_sown_area(df_crop, all_crops, inp_lulc_val_list[0])
    df_crop = kc_et.calculate_consolidated_crop_cn2(df_crop, all_crops)
    df_crop["Fallow_area"] = df_crop.apply(
        lambda row: kc_et.calc_fallow_area(inp_lulc_val_list[0], row["Actual Crop Sown Area"], inp_lulc_val_list[1]), axis=1)
    df_crop["Builtup_area"] = df_crop.apply(lambda row: kc_et.calc_lulc(inp_lulc_val_list[2], area), axis=1)
    df_crop["Waterbodies_area"] = df_crop.apply(lambda row: kc_et.calc_lulc(inp_lulc_val_list[3], area),
                                                axis=1)
    df_crop["Pasture"] = df_crop.apply(lambda row: kc_et.calc_lulc(inp_lulc_val_list[4], area), axis=1)
    df_crop["Forest"] = df_crop.apply(lambda row: kc_et.calc_lulc(inp_lulc_val_list[5], area), axis=1)
    df_crop["Crop_Area"] = df_crop.apply(lambda row: kc_et.calc_lulc(row["Actual Crop Sown Area"], area),
                                         axis=1)
    df_crop["Fallow_Area"] = df_crop.apply(lambda row: kc_et.calc_lulc(row["Fallow_area"], area), axis=1)
    df_crop["Fallowcn2"] = df_crop["Fallow_area"].apply(lambda x: kc_et.calc_fallowcn2(x, cn_values_list[1]))
    df_crop["Final_cn2"] = df_crop.apply(lambda row: kc_et.calc_final_cn2(row["Builtup_area"], cn_values_list[2],
                                                                    row["Waterbodies_area"], cn_values_list[3],
                                                                    row["Pasture"], cn_values_list[4],
                                                                    row["Forest"], cn_values_list[5],
                                                                    row["Crop_Area"], row["consolidated_crop_cn2"],
                                                                    row["Fallow_Area"], row["Fallowcn2"]), axis=1)

    df_crop["Final_CN2"] = kc_et.calc_cn2_adjusted(df_crop["Final_cn2"], cn_values_list[0])
    df_crop["Final_CN1"] = df_crop["Final_cn2"].apply(kc_et.calc_cn1)
    df_crop["Final_CN3"] = df_crop["Final_cn2"].apply(kc_et.calc_cn3)
    df_crop["Dormant"] = df_crop["Actual Crop Sown Area"].apply(kc_et.calc_dormant)
    df_crop["AMC"] = kc_et.calc_amc_cond(df_dd, df_crop)
    
    # CRITICAL FIX: Recalculate Final CN values after consolidated_crop_cn2 is updated
    df_crop["Final_cn2"] = df_crop.apply(lambda row: kc_et.calc_final_cn2(row["Builtup_area"], cn_values_list[2],
                                                                    row["Waterbodies_area"], cn_values_list[3],
                                                                    row["Pasture"], cn_values_list[4],
                                                                    row["Forest"], cn_values_list[5],
                                                                    row["Crop_Area"], row["consolidated_crop_cn2"],
                                                                    row["Fallow_Area"], row["Fallowcn2"]), axis=1)
    df_crop["Final_CN2"] = kc_et.calc_cn2_adjusted(df_crop["Final_cn2"], cn_values_list[0])
    df_crop["Final_CN1"] = df_crop["Final_cn2"].apply(kc_et.calc_cn1)
    df_crop["Final_CN3"] = df_crop["Final_cn2"].apply(kc_et.calc_cn3)
    
    return df_crop


# drpf_functions.py - Function 8: Processes crop details including efficiency and return flow values
def crop_details(attribute_names, all_crops, crop_df,inp_source,master_path):
    all_attributes = crop_pattern.combine_and_normalize_attributes(attribute_names,inp_source,master_path)
    df_cc = pd.DataFrame(all_attributes)

    if "All Crops" in df_cc.columns:
        df_cc.set_index("All Crops", inplace=True)
        # Drop rows where the "All Crops" index value is empty
        df_cc = df_cc[df_cc.index != ""]  # Remove rows where the index is an empty string
        df_cc = df_cc[~df_cc.index.isna()]  # Remove rows where the index is NaN
    df_cc["Area"] = pd.to_numeric(df_cc["Irr_Area"]) + pd.to_numeric(df_cc["Rainfed_Area"])

    df_cc = df_cc.apply(crop_pattern.apply_eva_red, axis=1, 
                        args=(crop_pattern.default_eva_red_values,inp_source, master_path))
    df_cc = df_cc.apply(crop_pattern.apply_efficiency, axis=1, 
                    args=(crop_pattern.default_efficiency_values, inp_source, master_path))
    df_cc = df_cc.apply(crop_pattern.calc_red_soil_evap, axis=1)
    df_cc = crop_pattern.get_ky_value(all_crops, crop_df, df_cc)
    df_cc = df_cc.apply(lambda row: crop_pattern.apply_return_flow(row, inp_source, master_path), axis=1)
    df_cc = crop_pattern.convert_columns_to_numeric(df_cc, crop_pattern.numeric_columns)
    columns_to_check = [
        "Drip_Area", "Sprinkler_Area", "Land_Levelling_Area", "DSR_Area",
        "AWD_Area", "SRI_Area", "Ridge_Furrow_Area", "Deficit_Area",
        "BBF_Area", "Cover_Area", "Mulching_Area", "Bunds_Area",
        "Tillage_Area", "Tank_Area"
    ]
    for column in columns_to_check:
        df_cc[column] = pd.to_numeric(df_cc[column], errors='coerce')
    for index, row in df_cc.iterrows():
        for column in columns_to_check:
            if row["Area"] < row[column]:
                error_message = f"Error: Crop {index}'s Total Area is less than {column}"
                print(error_message)
                raise ValueError(error_message)  # Raise an exception to stop the code

    return df_cc


# drpf_functions.py - Function 9: Calculates runoff discharge using curve number method
def calc_discharge(df_dd, df_crop, fixed_values_list):
    df_dd["CNi"] = kc_et.calc_cn(df_crop)
    df_dd["Si"], df_dd["Iai"] = kc_et.calc_abstraction(df_dd, df_crop, fixed_values_list[0], fixed_values_list[1],
                                                 fixed_values_list[2])
    df_dd["Recharge_src"] = df_dd.apply(lambda x: kc_et.get_recharge(x["Pi"], fixed_values_list[3]), axis=1)
    df_dd["Rain_src"] = df_dd.apply(lambda row: kc_et.get_rain_src_model(row["Pi"], row["Recharge_src"]), axis=1)
    df_dd["runoff"] = df_dd.apply(lambda row: kc_et.runoff_cn(row["Pi"], row["Iai"], row["Si"]), axis=1)
    df_dd["Qi"] = df_dd.apply(lambda row: kc_et.calc_runoff_cn(row["Rain_src"], row["Iai"], row["runoff"]), axis=1)
    df_dd["Eff_Rain"] = df_dd.apply(lambda row: kc_et.get_eff_rain(row["Rain_src"], row["Qi"]), axis=1)
    df_dd["Pei"] = df_dd.apply(lambda row: kc_et.get_eff_rain(row["Pi"], row["Qi"]), axis=1)
    return df_dd


# drpf_functions.py - Function 10: Calculates crop water storage and evaporation parameters
def calc_crop_int(df_crop, df_cc, df_cp, valid_crops_df, all_plots, all_crops, soil_prop_list):
    df_crop = kc_et.process_sown_area(df_crop, df_cp)
    df_crop["Ze"] = soil_prop_list[3]
    df_crop = kc_et.calc_taw(df_crop, soil_prop_list[0], all_plots)
    df_crop = kc_et.calc_raw(df_crop, all_plots)
    df_crop = kc_et.calc_tew(df_crop, soil_prop_list[1], soil_prop_list[2], all_plots)
    df_crop = kc_et.calc_rew(df_crop, all_plots)
    # Calculate row-by-row mean for TEWi and REWi across all plots
    df_crop["TEWi"] = df_crop.filter(like="TEWi_").mean(axis=1)
    df_crop["REWi"] = df_crop.filter(like="REWi_").mean(axis=1)
    # Process the sown area using the updated function
    df_crop = kc_et.calculate_net_sown_area_by_plot(df_crop, valid_crops_df, df_cc)
    df_crop = kc_et.calc_soil_ke(df_crop, df_cc, all_crops)
    df_crop = kc_et.calc_final_evap_red(df_crop, all_crops)
    df_crop = kc_et.calc_final_evap_red_plot_wise(df_crop, all_crops, all_plots)
    return df_crop


# drpf_functions.py - Function 11: Calculates soil moisture deficit index for each plot
def calc_smdi_plot(df_crop, df_dd, valid_crops_df, all_plots, smdi_1):
    print("FUNCTION 18: calc_smdi_plot() - Calculating soil moisture deficit for each plot")
    smdi_shifted_dict = {}
    smdi_dict = {}

    for plot in all_plots:
        # Initialize the first value and store it in the dictionary
        smdi_shifted_dict[f"SMDi_shifted_{plot}"] = [smdi_1] + [0] * (len(df_crop) - 1)
        # Create an array of zeros for SMDi_{plot}
        smdi_dict[f"SMDi_{plot}"] = np.zeros(len(df_crop), dtype=np.float32)

    # Convert dictionaries to DataFrames
    smdi_shifted_df = pd.DataFrame(smdi_shifted_dict, dtype=np.float32)
    smdi_df = pd.DataFrame(smdi_dict)

    # Assign the new columns to df_crop at once
    df_crop = pd.concat([df_crop, smdi_shifted_df, smdi_df], axis=1)
    for plot in all_plots:
        for i in range(len(df_crop)):
            if i > 0:
                df_crop.loc[i, f"SMDi_shifted_{plot}"] = df_crop.loc[i - 1, f"SMDi_{plot}"]

            df_crop.loc[i, f"Ks_soil_cond_{plot}"] = smd.calc_ks_soil_cond(df_crop.loc[i, f"Kei_{plot}"],
                                                                       df_crop.loc[i, f"SMDi_shifted_{plot}"],
                                                                       df_crop.loc[i, f"REWi_{plot}"],
                                                                       df_crop.loc[i, f"TEWi_{plot}"])

            df_crop.loc[i, f"Ks_soil_{plot}"] = smd.calc_ks_soil(df_crop.loc[i, f"Ks_soil_cond_{plot}"],
                                                             df_crop.loc[i, f"TEWi_{plot}"],
                                                             df_crop.loc[i, f"SMDi_shifted_{plot}"],
                                                             df_crop.loc[i, f"REWi_{plot}"])

            df_crop.loc[i, f"AE_soil_{plot}"] = smd.calc_ae_soil(df_dd.loc[i, f"ESi_{plot}"],
                                                             df_dd.loc[i, "Pei"],
                                                             df_crop.loc[i, f"Ks_soil_cond_{plot}"],
                                                             df_crop.loc[i, f"Ks_soil_{plot}"],
                                                             df_crop.loc[i, f"Final_Evap_Red_{plot}"])

            df_crop.loc[i, f"Ks_crop_cond_{plot}"] = smd.calc_ks_crop_cond(df_crop.loc[i, f"Kci_{plot}"],
                                                                       df_crop.loc[i, f"SMDi_shifted_{plot}"],
                                                                       df_crop.loc[i, f"RAWi_{plot}"],
                                                                       df_crop.loc[i, f"TAWi_{plot}"])

            df_crop.loc[i, f"Ks_crop_{plot}"] = smd.calc_ks_crop(df_crop.loc[i, f"Ks_crop_cond_{plot}"],
                                                             df_crop.loc[i, f"TAWi_{plot}"],
                                                             df_crop.loc[i, f"SMDi_shifted_{plot}"],
                                                             df_crop.loc[i, f"RAWi_{plot}"])

            df_crop.loc[i, f"AE_crop_{plot}"] = smd.calc_ae_crop(df_dd.loc[i, f"ETci_{plot}"],
                                                             df_dd.loc[i, "Pei"],
                                                             df_crop.loc[i, f"Ks_crop_cond_{plot}"],
                                                             df_crop.loc[i, f"Ks_crop_{plot}"])

            smdi_value = smd.calc_smd(df_crop.loc[i, f"SMDi_shifted_{plot}"],
                                  df_crop.loc[i, f"AE_soil_{plot}"],
                                  df_crop.loc[i, f"AE_crop_{plot}"],
                                  df_dd.loc[i, "Pei"])

            df_crop.loc[i, f"SMDi_{plot}"] = np.float32(smdi_value)

    for plot in all_plots:
        columns_to_convert = [
            f"SMDi_shifted_{plot}", f"Ks_soil_cond_{plot}", f"Ks_soil_{plot}",
            f"AE_soil_{plot}", f"Ks_crop_cond_{plot}", f"Ks_crop_{plot}",
            f"AE_crop_{plot}", f"SMDi_{plot}"
        ]

        df_crop[columns_to_convert] = df_crop[columns_to_convert].astype("float32")

    df_crop = smd.calc_ae_per_crop(df_crop, valid_crops_df, ae_type="crop")
    df_crop = smd.calc_ae_per_crop(df_crop, valid_crops_df, ae_type="soil")
    df_crop = smd.update_gwnr(df_crop, df_dd, all_plots)
    return df_crop


# drpf_functions.py - Function 12: Calculates groundwater recharge for fallow and crop plots
def calc_gwnr_fallow_plot(df_crop, df_mm, df_dd, all_plots, all_crops, inp_lulc_val_list, df_cc):
    print("FUNCTION 19: calc_gwnr_fallow_plot() - Calculating groundwater recharge for fallow plots")
    df_mm = smd.calc_monthly_gwnrm_crop(df_crop, df_mm, all_plots)

    df_dd["Kc_Fallow"] = np.float32(0)
    df_dd["Ke_Fallow"] = df_dd["Kc_Fallow"].apply(smd.calc_ke)
    df_dd["ESi_Fallow"] = df_dd.apply(lambda row: smd.calc_esi_fallow(row), axis=1)
    df_dd.loc[0, "SMDi_shifted_Fallow"] = manual_input.SMDi_1
    
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

        df_dd.loc[i, "Ks_soil_cond_Fallow"] = smd.calc_ks_soil_cond(df_dd.loc[i, "Ke_Fallow"],
                                                                df_dd.loc[i, "SMDi_shifted_Fallow"],
                                                                df_crop.loc[i, "REWi"],
                                                                df_crop.loc[i, "TEWi"])

        df_dd.loc[i, "Ks_soil_Fallow"] = smd.calc_ks_soil(df_dd.loc[i, "Ks_soil_cond_Fallow"],
                                                      df_crop.loc[i, "TEWi"],
                                                      df_dd.loc[i, "SMDi_shifted_Fallow"],
                                                      df_crop.loc[i, "REWi"])

        df_dd.loc[i, "AE_soil_Fallow"] = smd.calc_ae_soil_fallow(df_dd.loc[i, "ESi_Fallow"],
                                                             df_dd.loc[i, "Pei"],
                                                             df_dd.loc[i, "Ks_soil_cond_Fallow"],
                                                             df_dd.loc[i, "Ks_soil_Fallow"])

        df_dd.loc[i, "SMDi_Fallow"] = smd.calc_smd_fallow(df_dd.loc[i, "SMDi_shifted_Fallow"],
                                                      df_dd.loc[i, "AE_soil_Fallow"],
                                                      df_dd.loc[i, "Pei"])

    df_crop["GWnr_Fallow"] = df_dd.apply(lambda row: smd.calc_gwnr_fallow(row["SMDi_Fallow"],
                                                                      row["SMDi_shifted_Fallow"],
                                                                      row["AE_soil_Fallow"],
                                                                      row["Pei"]), axis=1)

    df_mm = smd.calc_monthly_gwnrm_fallow(df_crop, df_mm)
    df_crop = smd.calc_fallow_area1(df_crop, inp_lulc_val_list[1], inp_lulc_val_list[2], inp_lulc_val_list[3], inp_lulc_val_list[4], inp_lulc_val_list[5])
    # Calculate sum of all crop areas for recharge calculation
    # This will be the sum of all crop areas (Chilli: 712 + Tobacco: 1880 + Pulses: 1150 = 3742)
    total_crop_areas = sum(df_cc["Area"].values)  # Sum of all crop areas from crop characteristics
    df_crop["Recharge"] = df_crop.apply(lambda row: smd.calc_recharge(row, all_plots, total_crop_areas), axis=1)
    df_mm = smd.calc_monthly_recharge(df_crop, df_mm)
    df_crop = smd.calculate_iwr(df_dd, df_crop, all_crops)
    df_mm = smd.calculate_monthly_iwr(df_dd, df_mm.copy(), df_crop.copy(), all_crops)
    df_dd = crop_pattern.convert_dtypes(df_dd)
    df_crop = crop_pattern.convert_dtypes(df_crop)
    
    # Update AE_soil_crop with fallow values when crop is not sown
    for crop in all_crops:
        sown_area_col = f"{crop}_Sown_Area"
        ae_soil_crop_col = f"AE_soil_{crop}"
        if sown_area_col in df_crop.columns and ae_soil_crop_col in df_crop.columns:
            # Where crop is not sown, use fallow evaporation value
            not_sown_mask = df_crop[sown_area_col] == 0
            df_crop.loc[not_sown_mask, ae_soil_crop_col] = df_dd.loc[not_sown_mask, "AE_soil_Fallow"]
    
    # Recalculate monthly aggregation after AE_soil changes
    df_mm = smd.calculate_monthly_iwr(df_dd, df_mm.copy(), df_crop.copy(), all_crops)
    
    return df_crop, df_mm, df_dd


# drpf_functions.py - Function 13: Calculates economic parameters for interventions
def calc_int_economics(combined_intervention_data, economic_list):
    df_int = pd.DataFrame(combined_intervention_data)

    # Replace empty lists with NaN for cleaner data using map instead of applymap
    df_int = df_int.map(lambda x: np.nan if isinstance(x, list) and len(x) == 0 else x)

    df_int["Capital Cost"] = df_int.apply(
        lambda row: Economic.calc_cost(row["Volume (Cu.m)/Area"], row["Cost (Rs/Cu.m)"]),
        axis=1
    )
    df_int["Total Capital Cost"] = df_int.apply(
        lambda row: Economic.calc_cost(row["Capital Cost"], row["Number of Units"]),
        axis=1)

    df_int["Equalized Annual Cost"] = df_int.apply(
        lambda row: Economic.calculate_eac(row["Total Capital Cost"], economic_list[0], economic_list[1]),
        axis=1
    )

    df_int = Economic.calculate_maintenance_cost(df_int, economic_list[1])

    df_int["NPV"] = df_int.apply(
        lambda row: Economic.calc_npv(row["Maintenance Cost"], row["Equalized Annual Cost"], economic_list[0], economic_list[1]),
        axis=1
    )
    return df_int


# drpf_functions.py - Function 14: Calculates comprehensive intervention economics
def calculate_intervention_economics(economic_list, df_cc,inp_source,master_path):
    print("FUNCTION 21: calculate_intervention_economics() - Calculating intervention economics")
    supply_side_int = Economic.get_supplyside_int_data(economic_list,inp_source,master_path)
    demand_side_int = Economic.get_demandside_int_data(df_cc, economic_list,inp_source,master_path)
    soil_moisture_int = Economic.get_soil_moistureside_int_data(df_cc, economic_list,inp_source,master_path)
    combined_intervention_data = Economic.create_intervention_data(supply_side_int, demand_side_int, soil_moisture_int)
    df_int = calc_int_economics(combined_intervention_data, economic_list)
    return df_int


# drpf_functions.py - Function 15: Retrieves all curve number values for seasons
def get_all_cn_values(seasons, df_cc, crop_df, soil_output_list):
    all_cn_values = {}

    for season_name, crops, crops_type, crop_sown_type in seasons:
        cn_values = kc_et.calculate_cn_values(
            crops, crops_type, crop_sown_type, df_cc, crop_df,
            soil_output_list[4], soil_output_list[5],
            soil_output_list[2], soil_output_list[3]
        )
        all_cn_values.update(cn_values)
    return all_cn_values


# drpf_functions.py - Function 16: Calculates crop evapotranspiration for each plot
def calc_etci_plot(df_crop, df_cc, df_cp, df_dd, df_mm, all_plots, all_crops, num_plots, counter, kei, valid_crops_df,
                   crop_df):
    print("FUNCTION 23: calc_etci_plot() - Calculating ETc for each plot")
    # Calculate Kci for each crop
    for crop in all_crops:
        df_crop[f"Kci_{crop}"] = df_crop.apply(lambda row: kc_et.calc_crop_kc(row, crop), axis=1)

    df_crop = kc_et.calc_kci_by_plot(df_crop, df_cp, all_crops, num_plots)

    for crop in all_crops:
        # Call the combined function for each crop
        monthly_etci = df_dd.apply(
            lambda row: kc_et.calc_etci(df_cc, row["EToi"], df_crop.loc[row.name, f"Kci_{crop}"], crop, counter), axis=1)
        # Create a new column in df_dd for the ETci values of the current crop
        df_dd[f"ETci_{crop}"] = monthly_etci
        # Resample and sum the monthly ETci values for the current crop
        monthly_etci_sum = df_dd.resample("M", on="Date")[f"ETci_{crop}"].sum().reset_index()
        # Merge the monthly ETci with df_mm
        df_mm = df_mm.merge(monthly_etci_sum, on="Date", how="left")

    for plot in all_plots:
        # Ensure the column name is formatted correctly
        kci_column = f"Kci_{plot}"

        # Check if the Kci column exists in df_crop
        if kci_column in df_crop.columns:
            # Calculate ETci for each plot
            df_dd[f"ETci_{plot}"] = df_dd.apply(
                lambda row: kc_et.calc_etci(
                    df_cc,
                    row["EToi"],
                    df_crop.loc[row.name, kci_column]
                    , crop, counter),
                axis=1
            )
        else:
            print(f"Column {kci_column} not found in df_crop")

        monthly_etci = df_dd.resample("M", on="Date")[f"ETci_{plot}"].sum().reset_index()
        df_mm = df_mm.merge(monthly_etci, on="Date", how="left")

    total_etci_columns = [f"ETci_{plot}" for plot in all_plots]
    df_dd["ETci"] = df_dd[total_etci_columns].sum(axis=1)
    df_crop = kc_et.calculate_stage_1(df_crop, all_crops, df_cp)
    df_crop = kc_et.calc_kei(df_crop, kei, all_plots)
    df_dd = kc_et.calculate_daily_esi(df_dd, df_crop, all_plots)
    df_mm = kc_et.calc_monthly_remaining_growth_days(df_crop, all_crops, df_mm, df_cc)
    df_crop = kc_et.calc_final_crop_rd(df_crop, crop_df, all_crops, valid_crops_df)
    df_crop = kc_et.calc_final_depletion_factor(df_crop, crop_df, all_crops, valid_crops_df)
    return df_dd, df_crop, df_mm


# drpf_functions.py - Function 17: Processes water management including storage and irrigation
def process_water_management(df_mm, all_crops, surface_areas, added_recharges, water_resource_list, inp_aquifer_para, irrigation):
    (population, domestic_water_use, other, other_water_use,
     groundwater_dependent, sw_storage_capacity_created, added_recharge_capacity, storage_limit) = water_resource_list

    df_ir = wa.irrigation_data_input(irrigation, df_mm)

    df_mm = wa.calc_storage_residualgw(df_mm, inp_aquifer_para)
    df_mm["Accumulated_natural_recharge"] = crop_pattern.mm_to_m3(to_float(inp_aquifer_para[3], 0), df_mm["Recharge"])

    # Calculate total surface area for farm
    total_surface_area_farm = surface_areas["farm"]

    # Perform calculations
    df_mm = wa.calc_potential_et(total_surface_area_farm, df_mm)
    df_mm = wa.calc_canal_supply(df_ir, df_mm)
    df_mm = wa.get_iwr_after_canal(df_mm)
    df_mm = wa.calc_potential_recharge(
        added_recharges["farm"],
        added_recharges["farm_lined"],
        added_recharges["check_dam"],
        df_mm
    )

    # Domestic and other water needs calculations
    df_mm = wa.calc_domestic_need(population, domestic_water_use, df_mm)
    df_mm = wa.calc_other_need(other, other_water_use, df_mm)

    # Groundwater and surface water needs calculations
    df_mm = wa.calc_gw_need(df_mm, groundwater_dependent)
    df_mm = wa.calc_sw_need(df_mm)
    df_mm = wa.calc_sw_abstracted(df_mm)

    # Subtract domestic surface water use
    df_mm = wa.calc_value_after_subtracting_domestic_sw_use(df_mm)

    # Storage calculations
    df_mm = wa.calc_storage(df_mm, sw_storage_capacity_created, added_recharge_capacity, storage_limit)

    # Convert units from m³ to mm
    for col in ["Actual_Recharge", "Runoff in GW recharge str", "Captured Runoff in m³", "Rejected_recharge"]:
        df_mm[f"{col}_mm"] = crop_pattern.m3_to_mm(to_float(inp_aquifer_para[3], 0), df_mm[col])

    # Final calculations for irrigation water requirement
    df_mm = wa.calc_per_irr_water_req_fulfilled(df_mm)
    df_mm = wa.calc_cwr_met(df_mm, all_crops)
    return df_mm


# drpf_functions.py - Function 18: Processes seasonal crop data and growth parameters
def process_seasonal_crops(df_crop, crop_df, df_cp, season):
    for season_name, crops, sowing_month, sowing_week, crop_type, crop_sown_type in season:
        df_crop = kc_et.process_crops(df_crop, crop_df, crops, sowing_month, sowing_week, df_cp)
        df_crop = kc_et.process_yearly_rg_days(df_crop, crop_df, crops, sowing_month, sowing_week)
    return df_crop


# drpf_functions.py - Function 19: Processes and calculates actual curve number values
def process_cn_values(seasons, df_cc, crop_df, soil_output_list, all_crops,inp_source,master_path):
    # Get all CN values
    all_cn_values = get_all_cn_values(seasons, df_cc, crop_df, soil_output_list)
    # Calculate Actual CN2 values and update all_cn_values
    actual_cn2 = kc_et.calculate_actual_cn(all_cn_values,inp_source,master_path)
    df_cc = kc_et.calc_red_cn_area(df_cc, all_crops, actual_cn2,inp_source, master_path)
    # Safely attempt to get the CN values, defaulting to 0 if an error occurs
    cn_f1 = float(kc_et.get_fallow_cn_soil_type(crop_df, soil_output_list[4]) or 0)
    cn_f2 = float(kc_et.get_fallow_cn_soil_type(crop_df, soil_output_list[5]) or 0)
    # Calculate the actual Fallow CN2
    actual_fallow_cn2 = kc_et.calc_act_fallow_cn2(cn_f1, cn_f2,inp_source,master_path)
    return df_cc, actual_fallow_cn2, actual_cn2


# drpf_functions.py - Function 20: Processes final water balance calculations
def process_final_wb(df, all_crops=None):
    df = wa.add_runoff_to_recharge(df)
    df = wa.calc_final_ro(df)
    df = wa.calc_final_runoff(df)
    df = wa.calc_final_recharge(df)
    
    # Use biological ET calculation if crops are provided, otherwise use water balance
    if all_crops is not None:
        df = wa.calc_final_et_biological(df, all_crops)
    else:
        df = wa.calc_final_et(df)
    
    df = crop_pattern.convert_dtypes(df)
    return df


# drpf_functions.py - Function 21: Processes yearly data and calculates weighted averages
def process_yearly_df(df_mm, df_cc, all_crops, yield_columns, other_columns):
    print("FUNCTION 28: process_yearly_df() - Processing yearly data aggregations")
    df_yr = wa.get_resample_yr_optimized(df_mm, all_crops)
    df_yr = wa.calc_yield(df_cc, df_yr, all_crops)
    df_yr = wa.calculate_weighted_averages(df_cc, df_yr, all_crops, yield_columns, other_columns)
    df_yr = crop_pattern.convert_dtypes(df_yr)
    return df_yr


# drpf_functions.py - Function 22: Processes monthly climate and precipitation data
def process_monthly_data(df_dd, file_paths,inp_source,master_path):
    print("FUNCTION 29: process_monthly_data() - Processing monthly climate data")
    monthly_data = file_paths["monthly_data"]
    df_mm = crop_pattern.resample(df_dd, monthly_data, "Date", "Pi").rename(columns={"Pi": "Rain"})
    df_mm["Days"] = df_mm["Date"].map(lambda x: crop_pattern.calc_days_in_month(x.year, x.month))
    df_mm = crop_pattern.calc_etom(df_mm,file_paths,inp_source,master_path)

    return df_mm


# drpf_functions.py - Function 23: Main orchestrator running all drought proofing processes
def dr_prf_all_processes(inp_source,master_path,file_paths,year_type, counter):
    print("FUNCTION 30: dr_prf_all_processes() - Running all drought proofing processes")
    inp_var = collect_inp_variables(inp_source,master_path)
    int_var = collect_int_variables(inp_source,master_path)
    crop_df = crop_pattern.get_crop_data(file_paths["crop_db"])
    season_data = get_season_data(inp_source,master_path)
    df_cp, num_plots = crop_pattern.assign_plots_to_crops(season_data)
    df_dd = crop_pattern.get_pcp_value(file_paths["daily_data"])
    df_mm = process_monthly_data(df_dd, file_paths,inp_source,master_path)
    df_dd = crop_pattern.calculate_daily_etoi(df_mm, df_dd)
    df_crop = pd.DataFrame(df_dd["Date"])
    valid_crops_df = crop_pattern.select_valid_crops(df_cp)
    all_crops = valid_crops_df["Crop"].tolist()
    all_plots = valid_crops_df["Plot"].unique().tolist()
    df_cc = crop_details(crop_pattern.attribute_names, all_crops, crop_df,inp_source,master_path)
    season = get_seasons_val(inp_source,master_path)
    df_crop = process_seasonal_crops(df_crop, crop_df, df_cp, season)
    df_dd, df_crop, df_mm = calc_etci_plot(df_crop, df_cc, df_cp, df_dd, df_mm, all_plots, all_crops,
                                           num_plots, counter, inp_var["kei"], valid_crops_df, crop_df)

    soil_output_list = soil_calculation(inp_source,master_path)
    # Calculate AWC capacity
    depth, awc, awc_capacity = kc_et.calculate_awc_capacity(soil_output_list[6], soil_output_list[7], soil_output_list[8],
                                                            soil_output_list[9], soil_output_list[0],soil_output_list[1])
    # Assuming df_cc is your DataFrame
    df_cc, overall_sum = kc_et.calculate_soil_moisture_sums(df_cc)
    # Calculate AWC for soil
    awc_soil_con = kc_et.calculate_awc_soil(df_cc, manual_input.Cover_Crops_SM_with_practice,
                                            manual_input.Mulching_SM_with_practice,
                                            manual_input.BBF_SM_with_practice, manual_input.Bund_SM_with_practice,
                                            manual_input.Tillage_SM_with_practice,
                                            awc_capacity)
    df_cc = kc_et.get_cover_type(df_cc, crop_df)
    seasons = get_seasons_data(inp_source,master_path)
    df_cc, actual_fallow_cn2, actual_cn2 = process_cn_values(seasons, df_cc, crop_df, soil_output_list,
                                                                            all_crops,inp_source,master_path)
    
    # land_use_types = get_land_use_types()
    crop_area_inp_list = list(get_land_use_types(inp_source,master_path).values())
    cn_lulc_values_list = [manual_input.slope, actual_fallow_cn2] + [getattr(manual_input, attr) for attr in
                                                                     ["Builtup_cn2", "WB_cn2", "Pasture_cn2",
                                                                      "Forest_cn2"]]
    total_area = crop_pattern.calculate_total_area(crop_area_inp_list)
    capacity = kc_et.calculate_capacity(awc_capacity, manual_input.with_out_soil_con, total_area, overall_sum, awc_soil_con)
    soil_prop_list = [capacity, manual_input.theta_FC, manual_input.theta_WP, manual_input.Ze]
    
    
    df_crop = calc_crop_int(df_crop, df_cc, df_cp, valid_crops_df, all_plots, all_crops, soil_prop_list)
    
    df_crop = calc_crop_consolidated_cn(df_dd, df_crop, actual_cn2, df_cc, all_crops, crop_area_inp_list,
                                                       cn_lulc_values_list)
    fixed_values_list = list(fixed_values.values())
    df_dd = calc_discharge(df_dd, df_crop, fixed_values_list)
    aquifer_para_list = [inp_var["Aquifer_Depth"], inp_var["Starting_Level"], inp_var["Specific_Yield"], total_area]
    df_mm = process_monthly_qi(df_dd, df_mm, aquifer_para_list)

    df_crop = calc_smdi_plot(df_crop, df_dd, valid_crops_df, all_plots, manual_input.SMDi_1)
    df_crop, df_mm, df_dd = calc_gwnr_fallow_plot(df_crop, df_mm, df_dd, all_plots, all_crops, crop_area_inp_list, df_cc)
    area_eff_list = [
        inp_var.get(attr) for attr in ["SW_Area", "GW_Area", "SW_Area_Irr_Eff", "GW_Area_Irr_Eff"]
    ] + [manual_input.Eff_Default_Irrigation]
    
    irr_eff = smd.calc_irr_eff(area_eff_list, crop_area_inp_list)
    df_cc, df_mm = smd.calc_overall_eff(df_mm, df_cc, all_crops, irr_eff)
    storage_limit = wa.calculate_storage_limit(aquifer_para_list)
    surface_areas, added_recharges, added_recharge_capacity, sw_storage_capacity_created = wa.calc_recharge_capacity(
        int_var["Farm_Pond_Vol"], int_var["Farm_Pond_Depth"], int_var["Farm_Pond_Inf_Rate"],
        int_var["Farm_Pond_Lined_Vol"], int_var["Farm_Pond_Lined_Depth"], int_var["Farm_Pond_Lined_Inf_Rate"],
        int_var["Check_Dam_Vol"], int_var["Check_Dam_Depth"], int_var["Check_Dam_Inf_Rate"],
        int_var["Infiltration_Pond_Vol"], int_var["Infiltration_Pond_Depth"], int_var["Infiltration_Pond_Inf_Rate"],
        int_var["Injection_Wells_Vol"], int_var["Injection_Wells_Nos"]
    )
    
    water_resource_list = [
        inp_var.get(attr) for attr in [
            "Population", "Domestic_Water_Use", "Other", "Other_Water_Use", "Groundwater_Dependent"
        ]] + [sw_storage_capacity_created, added_recharge_capacity, storage_limit]

    df_mm = process_water_management(df_mm, all_crops, surface_areas, added_recharges, water_resource_list,
                                                    aquifer_para_list, file_paths["irrigation"])
    df_mm = process_final_wb(df_mm, all_crops)
    df_yr = process_yearly_df(df_mm, df_cc, all_crops, crop_pattern.yield_columns,
                                             crop_pattern.other_columns)
    economic_list = [float(int_var["Interest_Rate"]), float(int_var["Time_Period"])]
    df_int = calculate_intervention_economics(economic_list, df_cc,inp_source,master_path)
    df_crop_yr, df_wb_yr, df_wb_mm = wa.process_water_year_data(df_mm, df_cp, all_crops, year_type)
    df_crop_yr = wa.calculate_yield_wyr(df_cc, df_crop_yr, all_crops)
    df_crop_yr = wa.calc_weighted_avg(df_cc, df_crop_yr, all_crops, crop_pattern.yield_columns,
                                      crop_pattern.other_columns)
    df_cwr, df_cwr_met, df_yield, df_drought = wa.process_year_data(df_yr, df_crop_yr, all_crops, year_type)

# Removed from here - moved to proper location in calc_gwnr_fallow_plot

    output_dictionary = {
        "df_dd.csv": df_dd,
        "df_mm.csv": df_mm,
        "df_crop.csv": df_crop,
        "df_yr.csv": df_yr,
        "df_wb_mm_output.csv": df_wb_mm,
        "df_cwr_output.csv": df_cwr,
        "df_cwr_met_output.csv": df_cwr_met,
        "df_yield_output.csv": df_yield,
        "df_drought_output.csv": df_drought,
        "df_cc.csv": df_cc,  # Ensure df_cc is saved with its index,
        "df_int.csv": df_int,
        "df_wb_yr_output.csv": df_wb_yr
    }
    
    return output_dictionary


# drpf_functions.py - Function 24: Entry point for drought proofing routines
def run_dr_pf_routines(inp_source, master_path, year_type, counter):
    print("FUNCTION 31: run_dr_pf_routines() - Starting main drought proofing routines")
    file_paths = get_file_paths(inp_source, master_path)
    consolidated_dataframes = dr_prf_all_processes(inp_source, master_path, file_paths, year_type, counter)
    return consolidated_dataframes

