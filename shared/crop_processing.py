"""
Crop data processing functions for drought proofing tool

This module contains functions for processing crop-related data:
- Crop dormancy calculations
- Crop data management utilities

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Processes crop data including plot assignments, seasonal crops, growth calculations, and yield parameters
# ========================================

import pandas as pd
import numpy as np
from shared.utilities import safe_crop_conversion, safe_float_conversion, convert_season_data_to_df, convert_columns_to_numeric, to_float
from orchestrator.input_collector import collect_inp_variables, collect_int_variables
from soil_storage_bucket.outflux.evapotranspiration import apply_eva_red, calc_red_soil_evap
from soil_storage_bucket.processing.crop_coefficients import process_crops

# Constants from crop_pattern.py
attribute_names = [
    "Crops", "Sowing_Month", "Sowing_Week", "Crops_Irr_Area", "Crops_Rainfed_Area", "Crops_Area",
    "Crops_Type", "Crop_Sown_Type", "Crop_Drip_Area", "Crop_Sprinkler_Area", "Crop_Land_Levelling_Area",
    "Crop_DSR_Area", "Crop_AWD_Area", "Crop_SRI_Area", "Crop_Ridge_Furrow_Area", "Crop_Deficit_Area",
    "Crop_BBF_Area", "Crop_Cover_Crops_Area", "Crop_Mulching_Area", "Crop_Bunds_Area", "Crop_Tillage_Area",
    "Crop_Tank_Area", "Cover_Crops_Eva_Red", "Mulching_Eva_Red", "Tank_Eva_Red", "Tillage_Eva_Red"
]

# Define default efficiency values
default_efficiency_values = {
    "Eff_Drip": 90,
    "Eff_Sprinkler": 70,
    "Eff_Land_Levelling": 25,
    "Eff_DSR": 25,
    "Eff_AWD": 25,
    "Eff_SRI": 25,
    "Eff_Ridge_Furrow": 25,
    "Eff_Deficit": 50,
    "Eff_BBF": 65
}

default_eva_red_values = {
    "Cover_Crops_Eva_Red": 50,
    "Mulching_Eva_Red": 25,
    "Tank_Eva_Red": 50,
    "Tillage_Eva_Red": 0
}

# List of columns to convert
numeric_columns = [
    "Drip_Area", "Sprinkler_Area", "BBF_Area",
    "Eff_Drip", "Eff_Sprinkler", "Eff_BBF",
    "Land_Levelling_Area", "DSR_Area", "AWD_Area",
    "SRI_Area", "Ridge_Furrow_Area", "Deficit_Area",
    "Eff_Land_Levelling", "Eff_DSR", "Eff_AWD",
    "Eff_SRI", "Eff_Ridge_Furrow", "Eff_Deficit", "Yield (tonne/ha)",
    "Irr_Area", "Rainfed_Area", "Area", "Price (Rs/tonne)",
    "Cover_Area", "Mulching_Area", "Bunds_Area", "Tillage_Area",
    "Tank_Area", "Ky"
]

# Define yield columns to be averaged
yield_columns = {
    "Rainfed_Yield_Avg": ("Rainfed_yield_{crop}", "Rainfed_Area"),
    "Irrigated_Yield_Avg": ("Irr_yield_{crop}", "Irr_Area")
}

# Define other metrics to be averaged (e.g., CWR, CWA)
other_columns = {
    "Rainfed_CWR_Avg": "Rainfed_CWR_{crop}(cu.m/ha)",
    "Rainfed_CWA_Avg": "Rainfed_CWA_{crop}(cu.m/ha)",
    "Irrigated_CWR_Avg": "Irr_CWR_{crop}(cu.m/ha)",
    "Irrigated_CWA_Avg": "Irr_CWA_{crop}(cu.m/ha)",
    "Combined_CWR_Avg": "Combined CWR_{crop}(cu.m/ha)",
    "Combined_CWA_Avg": "Combined CWA_{crop}(cu.m/ha)",
    "ET_Biological_Avg": "ET_Biological"
}




# crop_processing.py - Function 001: Assigns plot numbers to crops and calculates plot statistics
# Interactions: shared.utilities.convert_season_data_to_df, pandas
def assign_plots_to_crops(var_season_data):
    print("FUNCTION 29: assign_plots_to_crops() - Assigning plots to crops")
    all_data = convert_season_data_to_df(var_season_data)
    df_cp = pd.concat(all_data, ignore_index=True)
    # Calculate the total area
    df_cp["Total_Area"] = df_cp["Irrigated_Area"] + df_cp["Rainfed_Area"]
    # Initialize lists for plot assignments and max area limits
    plot_assignments = []
    
    # Loop through each season's data to assign plots
    plot_counter = 0
    for season, details in var_season_data.items():
        num_crops = len(details["Crops"])
        for i in range(num_crops):
            plot_assignments.append(f"plot {plot_counter + 1}")
            plot_counter += 1

    # Assign plots to DataFrame
    df_cp["Plot"] = plot_assignments
    # Calculate the number of unique plots
    num_plots = len(df_cp["Plot"].unique())
    return df_cp, num_plots


# crop_processing.py - Function 002: Filters crop pattern data to include only valid non-empty crops
# Interactions: pandas
def select_valid_crops(df_cp):
    # Filter out rows with empty or null crops
    valid_crops_df = df_cp[df_cp["Crop"].notna() & (df_cp["Crop"] != "")]
    # Select relevant columns
    valid_crops_df = valid_crops_df[["Season", "Crop", "Plot"]].drop_duplicates()
    return valid_crops_df


# crop_processing.py - Function 003: Combines seasonal attributes from input and intervention variables
# Interactions: orchestrator.input_collector.collect_inp_variables, orchestrator.input_collector.collect_int_variables
def get_dynamic_crop_plot_mapping(inp_source, master_path):
    """
    Dynamically creates a mapping between plot numbers and crop names
    based on the actual crop pattern data.
    Returns: {1: 'Chilli', 2: 'Tobacco', 3: 'Pulses'} (example)
    """
    from orchestrator.input_collector import collect_inp_variables
    
    inp_var = collect_inp_variables(inp_source, master_path)
    
    plot_to_crop = {}
    
    # Process each plot directly (Plot 1, 2, 3) instead of using seasons
    for plot_num in [1, 2, 3]:
        # Try multiple possible naming conventions for backward compatibility
        possible_keys = [
            f"Plot_{plot_num}_Crop",  # Future: Direct plot-based naming
            f"Plot{plot_num}_Crop",   # Alternative format
        ]
        
        # Fallback: Map to seasonal data for backward compatibility
        season_mapping = {1: 'Kharif', 2: 'Rabi', 3: 'Summer'}
        if plot_num in season_mapping:
            possible_keys.append(f"{season_mapping[plot_num]}_Crops")
        
        crop_name = None
        for key in possible_keys:
            crop_name = inp_var.get(key, None)
            if crop_name:
                break
        
        # Handle single crop (string) or multiple crops (list)
        if isinstance(crop_name, str) and crop_name.strip():
            plot_to_crop[plot_num] = crop_name.strip()
        elif isinstance(crop_name, list) and len(crop_name) > 0 and crop_name[0]:
            plot_to_crop[plot_num] = crop_name[0].strip()
    
    return plot_to_crop

def map_plot_interventions_to_crops(attribute_name, int_var, plot_to_crop_mapping, inp_source, master_path, scenario_num):
    """
    Maps plot-based intervention areas to specific crops dynamically.
    
    Args:
        attribute_name: e.g., "Crop_Drip_Area"
        int_var: intervention variables dictionary
        plot_to_crop_mapping: {1: 'Chilli', 2: 'Tobacco', 3: 'Pulses'}
        inp_source: input source
        master_path: master path
        scenario_num: scenario number
    
    Returns:
        List of intervention areas for each crop in order
    """
    # Map attribute names to intervention types
    intervention_mapping = {
        # Demand-side interventions
        "Crop_Drip_Area": "Drip_Area",
        "Crop_Sprinkler_Area": "Sprinkler_Area", 
        "Crop_Land_Levelling_Area": "Land_Levelling_Area",
        "Crop_DSR_Area": "DSR_Area",
        "Crop_AWD_Area": "AWD_Area",
        "Crop_SRI_Area": "SRI_Area",
        "Crop_Ridge_Furrow_Area": "Ridge_Furrow_Area",
        "Crop_Deficit_Area": "Deficit_Area",
        # Soil moisture interventions
        "Crop_BBF_Area": "BBF_Area",
        "Crop_Cover_Crops_Area": "Cover_Crops_Area",
        "Crop_Mulching_Area": "Mulching_Area", 
        "Crop_Bunds_Area": "Bunds_Area",
        "Crop_Tillage_Area": "Tillage_Area",
        "Crop_Tank_Area": "Tank_Area"
    }
    
    intervention_type = intervention_mapping.get(attribute_name)
    if not intervention_type:
        return []
    
    # Determine which utility function to use based on intervention type
    if intervention_type in ["Drip_Area", "Sprinkler_Area", "Land_Levelling_Area", "DSR_Area", "AWD_Area", "SRI_Area", "Ridge_Furrow_Area", "Deficit_Area"]:
        from shared.input_utilities import get_demand_side_interv_area_values
        utility_function = get_demand_side_interv_area_values
    else:  # Soil moisture interventions
        from shared.input_utilities import get_soil_moisture_interv_area_values
        utility_function = get_soil_moisture_interv_area_values
    
    crop_interventions = []
    
    # Process each crop in the order they appear in the system
    for plot_num in sorted(plot_to_crop_mapping.keys()):
        crop_name = plot_to_crop_mapping[plot_num]
        plot_key = f"Crop_Area_{plot_num}_{intervention_type}"
        
        # Read the plot-based value directly from the intervention system
        # Use the appropriate utility function based on intervention type
        intervention_area = utility_function(inp_source, master_path, plot_key, 0, scenario_num)
        
        # Flatten the result if it's a list
        if isinstance(intervention_area, list) and len(intervention_area) > 0:
            intervention_area = intervention_area[0]
        elif isinstance(intervention_area, list):
            intervention_area = 0
            
        crop_interventions.append(intervention_area)
    
    return crop_interventions

def combine_attributes(attribute_name,inp_source,master_path, scenario_num=0):
    inp_var = collect_inp_variables(inp_source,master_path)  # Dictionary from your collect_inp_variables function
    int_var = collect_int_variables(inp_source,master_path, scenario_num)   # Dictionary from your collect_int_variables function
    
    # NEW: Dynamic plot-based intervention mapping for ALL intervention types
    intervention_types = [
        # Demand-side interventions
        "Crop_Drip_Area", "Crop_Sprinkler_Area", "Crop_Land_Levelling_Area",
        "Crop_DSR_Area", "Crop_AWD_Area", "Crop_SRI_Area", 
        "Crop_Ridge_Furrow_Area", "Crop_Deficit_Area",
        # Soil moisture interventions
        "Crop_BBF_Area", "Crop_Cover_Crops_Area", "Crop_Mulching_Area",
        "Crop_Bunds_Area", "Crop_Tillage_Area", "Crop_Tank_Area"
    ]
    
    if attribute_name in intervention_types:
        # Get dynamic crop-plot mapping
        plot_to_crop = get_dynamic_crop_plot_mapping(inp_source, master_path)
        # Map plot-based interventions to crops
        crop_interventions = map_plot_interventions_to_crops(attribute_name, int_var, plot_to_crop, inp_source, master_path, scenario_num)
        
        # Return the interventions in the correct order for each crop
        return crop_interventions
    
    # Try plot-based format first (Plot_1_, Plot_2_, Plot_3_)
    plot_values = []
    found_plot_data = False
    
    for plot_num in [1, 2, 3]:
        plot_key = f"Plot_{plot_num}_{attribute_name}"
        
        plot_inp = inp_var.get(plot_key, [])
        plot_int = int_var.get(plot_key, [])
        
        if plot_inp or plot_int:
            found_plot_data = True
            
        # Convert single values to lists if necessary
        if not isinstance(plot_inp, list):
            plot_inp = [plot_inp] if plot_inp is not None else []
        if not isinstance(plot_int, list):
            plot_int = [plot_int] if plot_int is not None else []
            
        plot_combined = plot_inp + plot_int
        plot_values.extend(plot_combined)
    
    # If plot-based data found, return it
    if found_plot_data:
        return plot_values
    
    # Fallback to seasonal format for backward compatibility
    kharif_key = f"Kharif_{attribute_name}"
    rabi_key = f"Rabi_{attribute_name}"
    summer_key = f"Summer_{attribute_name}"
    
    # Get values, ensuring they are lists
    kharif_inp = inp_var.get(kharif_key, [])
    rabi_inp = inp_var.get(rabi_key, [])
    summer_inp = inp_var.get(summer_key, [])
    
    kharif_int = int_var.get(kharif_key, [])
    rabi_int = int_var.get(rabi_key, [])
    summer_int = int_var.get(summer_key, [])
    
    # Convert single values to lists if necessary
    if not isinstance(kharif_inp, list):
        kharif_inp = [kharif_inp] if kharif_inp is not None else []
    if not isinstance(rabi_inp, list):
        rabi_inp = [rabi_inp] if rabi_inp is not None else []
    if not isinstance(summer_inp, list):
        summer_inp = [summer_inp] if summer_inp is not None else []
        
    if not isinstance(kharif_int, list):
        kharif_int = [kharif_int] if kharif_int is not None else []
    if not isinstance(rabi_int, list):
        rabi_int = [rabi_int] if rabi_int is not None else []
    if not isinstance(summer_int, list):
        summer_int = [summer_int] if summer_int is not None else []
    
    # Combine the lists
    kharif = kharif_inp + kharif_int
    rabi = rabi_inp + rabi_int
    summer = summer_inp + summer_int
    
    return kharif + rabi + summer


# crop_processing.py - Function 004: Combines and normalizes all crop attributes to consistent lengths
# Interactions: combine_attributes
def combine_and_normalize_attributes(var_attribute_names,inp_source,master_path, scenario_num=0):
    print("FUNCTION 31: combine_and_normalize_attributes() - Combining and normalizing attributes")
    all_attributes = {
        name.replace("Crops_", "").replace("Crop_", "").replace("Crops", "All Crops"):
            combine_attributes(name,inp_source,master_path, scenario_num)
        for name in var_attribute_names
    }
        
    for key, value in all_attributes.items():
        all_attributes[key] = [0 if item == "" else item for item in value]

    # Find the maximum length of the lists
    max_length = max(len(v) for v in all_attributes.values())

    # Normalize the lengths of all lists, filling with 0 instead of None
    for key, value in all_attributes.items():
        if len(value) < max_length:
            # Pad with 0 instead of None
            all_attributes[key] = value + [0] * (max_length - len(value))
        elif len(value) > max_length:
            # Truncate the list to max_length
            all_attributes[key] = value[:max_length]

    return all_attributes


# crop_processing.py - Function 005: Applies irrigation efficiency values based on intervention areas
# Interactions: orchestrator.input_collector.collect_int_variables, shared.utilities.to_float
def apply_efficiency(row, default_eff_val,inp_source,master_path):
    int_var = collect_int_variables(inp_source,master_path)
    # Apply efficiency values with defaults if area is greater than 0
    row["Eff_Drip"] = (to_float(int_var["Eff_Drip_irrigation"], default_eff_val["Eff_Drip"]) if to_float(
        row["Drip_Area"]) > 0 else default_eff_val["Eff_Drip"])/100
    
    row["Eff_Sprinkler"] = (to_float(int_var["Eff_Sprinkler_irrigation"],default_eff_val["Eff_Sprinkler"]
                                    ) if to_float(row["Sprinkler_Area"]) > 0 else default_eff_val["Eff_Sprinkler"])/100
        
    row["Eff_Land_Levelling"] = (to_float(int_var["Eff_Land_Levelling"],
                                                    default_eff_val["Eff_Land_Levelling"]) if to_float(
        row["Land_Levelling_Area"]) > 0 else default_eff_val["Eff_Land_Levelling"])/100
                                                        
    row["Eff_DSR"] = (to_float(int_var["Eff_Direct_Seeded_Rice"], default_eff_val["Eff_DSR"]) if to_float(
        row["DSR_Area"]) > 0 else default_eff_val["Eff_DSR"])/100
    
    row["Eff_AWD"] = (to_float(int_var["Eff_Alternate_Wetting_And_Dry"],
                                         default_eff_val["Eff_AWD"]) if to_float(
        row["AWD_Area"]) > 0 else default_eff_val["Eff_AWD"])/100
                                             
    row["Eff_SRI"] = (to_float(int_var["Eff_SRI"], default_eff_val["Eff_SRI"]) if to_float(
        row["SRI_Area"]) > 0 else default_eff_val["Eff_SRI"])/100
    
    row["Eff_Ridge_Furrow"] = (to_float(int_var["Eff_Ridge_Furrow_Irrigation"],
                                                  default_eff_val["Eff_Ridge_Furrow"]) if to_float(
        row["Ridge_Furrow_Area"]) > 0 else default_eff_val["Eff_Ridge_Furrow"])/100
                                                      
    row["Eff_Deficit"] = (to_float(int_var["Eff_Deficit_Irrigation"],
                                             default_eff_val["Eff_Deficit"]) if to_float(
        row["Deficit_Area"]) > 0 else default_eff_val["Eff_Deficit"])/100
                                                 
    row["Eff_BBF"] = (to_float(int_var["Eff_BBF"], default_eff_val["Eff_BBF"]) if to_float(
        row["BBF_Area"]) > 0 else default_eff_val["Eff_BBF"])/100
    return row


# crop_processing.py - Function 006: Retrieves yield response factor and economic data for crops
# Interactions: numpy, pandas
def get_ky_value(all_crops, crop_df, df_cc):
    print("FUNCTION 32: get_ky_value() - Getting Ky values for yield calculation")
    df_cc["Ky"] = np.float32(0)  # Set Ky column to float32
    df_cc["Yield (tonne/ha)"] = np.float32(0)
    df_cc["Price (Rs/tonne)"] = np.int32(0)

    for crop in all_crops:
        crop_row = crop_df[crop_df["Crops"] == crop]
        if crop_row.empty:
            raise ValueError(f"Selected crop {crop} not found in crop_df")

        ky_value = crop_row["Ky Values"].values[0]
        pt_yield = crop_row["Yield (tonne/ha)"].values[0]
        price = crop_row["Price (Rs/tonne)"].values[0]

        # Store the Ky value in df_cc corresponding to the crop
        if crop in df_cc.index:
            df_cc.at[crop, "Ky"] = np.float32(ky_value)
            df_cc.at[crop, "Yield (tonne/ha)"] = np.float32(pt_yield)
            df_cc.at[crop, "Price (Rs/tonne)"] = np.int32(price)
        else:
            raise ValueError(f"Selected crop {crop} not found in df_cc index")
    return df_cc


# crop_processing.py - Function 007: Returns irrigation return flow coefficients based on crop type
# Interactions: None
def get_return_flow(crop):
    #From GEC Report 2015 Return Flow for Paddy and Non paddy field
    if crop == "Rice":
        gw_rf = 0.325
        sw_rf = 0.375
    else:
        gw_rf = 0.15
        sw_rf = 0.20
    return gw_rf, sw_rf


# crop_processing.py - Function 008: Calculates weighted return flow based on water source dependencies
# Interactions: get_return_flow, orchestrator.input_collector.collect_inp_variables, shared.utilities.to_float
def apply_return_flow(row,inp_source,master_path):
    crop = row.name
    gw_rf, sw_rf = get_return_flow(crop)
    row["GW_rf"] = gw_rf
    row["SW_rf"] = sw_rf
    inp_vars = collect_inp_variables(inp_source,master_path)

    try:
        row["Over_all_rf"] = ((gw_rf * to_float(inp_vars["Groundwater_Dependent"], 0)) + (
                sw_rf * to_float(inp_vars["Surface_Water_Dependent"], 0))) / 100

    except Exception as e:
        print(f"Error calculating overall return flow for crop {crop}: {e}")
        row["Over_all_rf"] = 0  # Default value in case of error
    return row


# crop_processing.py - Function 009: Processes crop details including efficiency and return flow values
# Interactions: combine_and_normalize_attributes, soil_storage_bucket.outflux.evapotranspiration.apply_eva_red, apply_efficiency, soil_storage_bucket.outflux.evapotranspiration.calc_red_soil_evap, get_ky_value, apply_return_flow, shared.utilities.convert_columns_to_numeric, pandas
def crop_details(attribute_names, all_crops, crop_df,inp_source,master_path, scenario_num=0):
    all_attributes = combine_and_normalize_attributes(attribute_names,inp_source,master_path, scenario_num)
    df_cc = pd.DataFrame(all_attributes)

    if "All Crops" in df_cc.columns:
        df_cc.set_index("All Crops", inplace=True)
        # Drop rows where the "All Crops" index value is empty
        df_cc = df_cc[df_cc.index != ""]  # Remove rows where the index is an empty string
        df_cc = df_cc[~df_cc.index.isna()]  # Remove rows where the index is NaN
    df_cc["Area"] = pd.to_numeric(df_cc["Irr_Area"]) + pd.to_numeric(df_cc["Rainfed_Area"])

    # Initialize efficiency columns with default values before applying functions
    for eff_key, eff_value in default_efficiency_values.items():
        df_cc[eff_key] = eff_value / 100  # Convert percentage to decimal
    
    # Initialize eva reduction columns with default values
    for eva_key, eva_value in default_eva_red_values.items():
        df_cc[eva_key] = eva_value
    
    # Initialize return flow columns with default values
    df_cc["GW_rf"] = 0.15  # Default non-paddy groundwater return flow
    df_cc["SW_rf"] = 0.20  # Default non-paddy surface water return flow
    df_cc["Over_all_rf"] = 0.17  # Default overall return flow

    df_cc = df_cc.apply(apply_eva_red, axis=1, 
                        args=(default_eva_red_values,inp_source, master_path))
    df_cc = df_cc.apply(apply_efficiency, axis=1, 
                    args=(default_efficiency_values, inp_source, master_path))
    df_cc = df_cc.apply(calc_red_soil_evap, axis=1)
    df_cc = get_ky_value(all_crops, crop_df, df_cc)
    df_cc = df_cc.apply(lambda row: apply_return_flow(row, inp_source, master_path), axis=1)
    df_cc = convert_columns_to_numeric(df_cc, numeric_columns)
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


# crop_processing.py - Function 010: Processes seasonal crop data and growth parameters
# Interactions: soil_storage_bucket.processing.crop_coefficients.process_crops, process_yearly_rg_days
def process_seasonal_crops(df_crop, crop_df, df_cp, season):
    for season_name, crops, sowing_month, sowing_week, crop_type, crop_sown_type in season:
        df_crop = process_crops(df_crop, crop_df, crops, sowing_month, sowing_week, df_cp)
        df_crop = process_yearly_rg_days(df_crop, crop_df, crops, sowing_month, sowing_week)
    return df_crop


# crop_processing.py - Function 011: Retrieves total growth days for a specific crop from crop database
# Interactions: pandas
def get_total_growth_days(crop_df, selected_crop):
    crop_row = crop_df[crop_df["Crops"] == selected_crop]
    if crop_row.empty:
        raise ValueError(f"Selected crop {selected_crop} not found in crop_df")
    try:
        return float(crop_row["Total Growth Days"].values[0])
    except ValueError:
        raise ValueError(f"Invalid total growth days value for crop {selected_crop}")


# crop_processing.py - Function 012: Calculates crop sowing start date based on year, month, and week
# Interactions: pandas
def find_start_date(year, sowing_month_num, sowing_week):
    start_date = pd.to_datetime(f"{year}-{sowing_month_num}-01") + pd.Timedelta(days=(int(sowing_week) - 1) * 7)
    return start_date


# crop_processing.py - Function 013: Calculates remaining growth days for initial year of crop cycle
# Interactions: get_total_growth_days, find_start_date, pandas, numpy
def calc_rg_days_ini(df, crop_df, selected_crop, sowing_month, sowing_week):
    sowing_month_num = pd.to_datetime(f"{sowing_month} 1, 2000").month
    total_growth_days = get_total_growth_days(crop_df, selected_crop)
    rg_days_col_name = f"RG_days_{selected_crop}"

    # Calculate start dates for all entries in the DataFrame
    df["start_date"] = df["Date"].dt.year.apply(find_start_date, args=(sowing_month_num, sowing_week))
    
    # Calculate end dates for crop growth period
    df["end_date"] = df["start_date"] + pd.Timedelta(days=total_growth_days)

    # Calculate remaining growth days for the initial year - FIXED: Added end_date condition
    df[rg_days_col_name] = np.where(
        (df["Date"] >= df["start_date"]) & (df["Date"] < df["end_date"]),
        np.maximum(0, total_growth_days - (df["Date"] - df["start_date"]).dt.days - 1),
        0
    )

    # Drop the temporary columns
    df.drop(["start_date", "end_date"], axis=1, inplace=True)
    return df


# crop_processing.py - Function 014: Calculates remaining growth days for subsequent years of crop cycle
# Interactions: get_total_growth_days, find_start_date, pandas
def calc_remaining_days(df, crop_df, selected_crop, sowing_month, sowing_week):
    sowing_month_num = pd.to_datetime(f"{sowing_month} 1, 2000").month
    total_growth_days = get_total_growth_days(crop_df, selected_crop)
    rg_days_col_name = f"RG_days_{selected_crop}"

    # Use the exact same logic as original - row by row calculation
    def find_start_date_row(row):
        start_date = pd.to_datetime(f"{row['Date'].year}-{sowing_month_num}-01") + pd.Timedelta(
            days=(int(sowing_week) - 1) * 7)
        return start_date if start_date <= row["Date"] else start_date - pd.DateOffset(years=1)

    df["start_date"] = df.apply(find_start_date_row, axis=1)
    df[rg_days_col_name] = (df["start_date"] + pd.Timedelta(days=total_growth_days) - df["Date"] - pd.Timedelta(
        days=1)).dt.days.clip(lower=0)
    df.drop("start_date", axis=1, inplace=True)

    return df


# crop_processing.py - Function 015: Processes remaining growth days for all years in dataset
# Interactions: calc_rg_days_ini, calc_remaining_days, pandas
def process_yearly_rg_days(df, crop_df, crops, months, weeks):
    print("FUNCTION 19: process_yearly_rg_days() - Processing yearly remaining growth days")
    first_year = df["Date"].dt.year.min()
    first_year_df = df[df["Date"].dt.year == first_year].copy()
    remaining_years_df = df[df["Date"].dt.year != first_year].copy()

    # Initialize RG_days columns to 0 for all crops in remaining years
    for crop in crops:
        if crop:
            rg_days_col_name = f"RG_days_{crop}"
            if rg_days_col_name not in remaining_years_df.columns:
                remaining_years_df[rg_days_col_name] = 0
            else:
                remaining_years_df[rg_days_col_name] = 0  # Reset to 0

    # Process first year crops
    for crop, month, week in zip(crops, months, weeks):
        if crop and month and week:
            first_year_df = calc_rg_days_ini(first_year_df, crop_df, crop, month, week)

    # Process remaining years crops
    for crop, month, week in zip(crops, months, weeks):
        if crop and month and week:
            remaining_years_df = calc_remaining_days(remaining_years_df, crop_df, crop, month, week)

    # Combine the dataframes
    df_combined = pd.concat([first_year_df, remaining_years_df]).sort_values("Date").reset_index(drop=True)
    return df_combined




# crop_processing.py - Function 016: Determines sown area based on remaining growth days
# Interactions: None
def calc_sown_area(remaining_growth_day, area):
    return area if remaining_growth_day > 0 else 0


# crop_processing.py - Function 017: Processes sown area calculations for all crops in crop pattern
# Interactions: calc_sown_area
def process_sown_area(df, df_cp):
    # Iterate over the crops in the "Crop" column of df_cp
    for selected_crop in df_cp["Crop"].unique():
        # Skip if the crop is empty or None
        if not selected_crop:
            continue
        # Retrieve the total area corresponding to the crop from df_cp
        area = df_cp.loc[df_cp["Crop"] == selected_crop, "Total_Area"].values
        if len(area) == 0:
            raise ValueError(f"No area found for crop '{selected_crop}' in df_cp.")
        area = float(area[0])  # Convert area to float for consistency
        df[f"{selected_crop}_Sown_Area"] = df[f"RG_days_{selected_crop}"].apply(lambda x: calc_sown_area(x, area))
    return df


# crop_processing.py - Function 018: Calculates net sown area aggregated by plot from crop calendar
# Interactions: pandas
def calculate_net_sown_area_by_plot(df_crop, valid_crops_df, df_cc):
    for plot in valid_crops_df["Plot"].unique():
        # Get the crops associated with the current plot
        crops_in_plot = valid_crops_df.loc[valid_crops_df["Plot"] == plot, "Crop"].tolist()
        
        # Calculate the constant total area for this plot from df_cc
        total_plot_area = 0
        for crop in crops_in_plot:
            if crop in df_cc.index:
                total_plot_area += df_cc.loc[crop, "Area"]
        
        # Set constant NSA for the plot (doesn't change with growing season)
        df_crop[f"{plot}_NSA"] = total_plot_area
    
    return df_crop


# crop_processing.py - Function 019: Calculates total sown area across all crops with area limit enforcement
# Interactions: shared.utilities.to_float, numpy
def calculate_total_sown_area(df, crops, net_crop_sown_area):
    # Initialize the new column with zero
    df["Actual Crop Sown Area"] = np.float32(0)
    net_crop_sown_area = to_float(net_crop_sown_area, 0)

    # Sum the sown areas for each crop and store the total in the new column
    for crop in crops:
        sown_area_col = f"{crop}_Sown_Area"
        if sown_area_col in df.columns:
            df["Actual Crop Sown Area"] += df[sown_area_col]

    # Ensure each row's total sown area does not exceed the Net Crop Sown Area
    exceeded_rows = df["Actual Crop Sown Area"] > net_crop_sown_area
    if exceeded_rows.any():
        print(
            f"Warning: Some rows have an Actual Crop Sown Area that exceeds \
            the Net Crop Sown Area of {net_crop_sown_area} ha.")

    # Clip the values to ensure they don't exceed the user-defined limit
    df["Actual Crop Sown Area"] = df["Actual Crop Sown Area"].clip(upper=net_crop_sown_area)
    return df


# crop_processing.py - Function 020: Calculates fallow area from net sown area and actual crop areas
# Interactions: shared.utilities.to_float
def calc_fallow_area(net_crop_sown_area, sown_area, fallow):
    net_crop_sown_area = to_float(net_crop_sown_area, 0.0)
    fallow = to_float(fallow, 0)
    fallow_area = net_crop_sown_area - sown_area + fallow
    return fallow_area


# crop_processing.py - Function 021: Gets earliest sowing month from crop plan
# Interactions: pandas
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
    # If no valid season data is found, return None
    return None


# crop_processing.py - Function 022: Determines crop dormancy status based on sown area
# Interactions: None
def calc_dormant(sown_area):
    return "N" if sown_area > 0 else "Y"


# Helper function: Calculates start date for crop cycle based on sowing parameters
def find_start_date_row(row, sowing_month_num, sowing_week):
    start_date = pd.to_datetime(f"{row['Date'].year}-{sowing_month_num}-01") + pd.Timedelta(
        days=(int(sowing_week) - 1) * 7)
    return start_date if start_date <= row["Date"] else start_date - pd.DateOffset(years=1)