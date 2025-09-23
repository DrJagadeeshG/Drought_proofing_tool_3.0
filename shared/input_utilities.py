"""
Input utility functions for drought proofing tool

This module contains functions for input data retrieval and processing:
- Climate and variable value retrieval
- Crop data processing
- Supply-side and demand-side intervention values
- Soil moisture intervention parameters

These functions were moved from shared/data_readers.py to break circular imports.

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Handles all input data retrieval and processing for variables, crops, and interventions from CSV files or manual sources
# ========================================

import pandas as pd
import os
import functools
from shared.utilities import to_float

# Cache for file paths
_file_paths_cache = {}


# input_utilities.py - Function 001: Returns cached file paths for datasets based on input source and master path
# Interactions: os
def get_file_paths(inp_source,master_path):
    # Create cache key from parameters
    cache_key = f"{inp_source}_{master_path}"

    # Return cached result if available
    if cache_key in _file_paths_cache:
        return _file_paths_cache[cache_key]

    fixed_subdir = r"Datasets"
    csv_subdir = os.path.join(fixed_subdir, "Inputs","csv_inputs")
    db_subdir = os.path.join(fixed_subdir, "Inputs","static_inputs")
    cli_subdir = os.path.join(fixed_subdir,"Inputs", "mandatory_inputs")
    # Define file paths directly
    paths = {
        "daily_data": os.path.join(master_path, cli_subdir, "pcp.csv"),
        "monthly_data": os.path.join(master_path, cli_subdir, "temp.csv"),
        "irrigation": os.path.join(master_path, cli_subdir, "irrigation.csv"),
        "crop_db": os.path.join(master_path, db_subdir, "crop_db.csv"),
        "radiation_db": os.path.join(master_path, db_subdir, "radiation_db.csv"),
    }
    # Set input_baseline and input_interventions based on the source
    if inp_source == "csv":
        paths["input_baseline"] = os.path.join(master_path, csv_subdir, "input.csv")
        paths["input_interventions"] = os.path.join(master_path, csv_subdir, "interventions.csv")
    else:
        paths["input_baseline"] = None
        paths["input_interventions"] = None
    # Cache the result before returning
    _file_paths_cache[cache_key] = paths

    return paths


# input_utilities.py - Function 002: Cached CSV reader to avoid repeated disk I/O operations
# Interactions: pandas, os, functools
@functools.lru_cache(maxsize=64)
def _read_cached_csv(file_path):
    """Cache CSV reading to avoid repeated disk I/O"""
    if file_path and os.path.exists(file_path):
        return pd.read_csv(file_path, header=None)
    return pd.DataFrame()


# input_utilities.py - Function 003: Handles value retrieval from CSV or manual sources for variables
# Interactions: get_file_paths, _read_cached_csv, pandas
def handle_value_retrieval(inp_data_source, variables, master_path, var_name, index, is_crops=False, is_area=False):

    file_paths = get_file_paths(inp_data_source, master_path)
    inp_df = _read_cached_csv(file_paths["input_baseline"]) if file_paths["input_baseline"] else pd.DataFrame()
    interv_inp_df = _read_cached_csv(file_paths["input_interventions"]) if file_paths["input_interventions"] else pd.DataFrame()
    inp_data_source = inp_data_source.strip().lower()
    if inp_data_source == "csv":
        if inp_df is not None and index is not None:
            # Initialize variable_value to collect the values
            variable_value = []
            # Retrieve from inp_df
            if is_area or is_crops:
                # Iterate over all rows of inp_df to find var_name
                for row in range(inp_df.shape[0]):  # Iterate over rows
                    if inp_df.iloc[row, 0] == var_name:  # Check if first column matches var_name
                        for col in range(1, inp_df.shape[1]):  # Iterate over columns starting from 1
                            value = inp_df.iloc[row, col]
                            if pd.isna(value):
                                variable_value.append("")  # Append empty string if column is NaN
                            else:
                                variable_value.append(value)  # Append the actual value, including 0
                        break  # Exit the loop once found
                # If variable_value is empty, try to get values from interv_inp_df
                if not variable_value:
                    for row in range(interv_inp_df.shape[0]):  # Same logic for interv_inp_df
                        if interv_inp_df.iloc[row, 0] == var_name:
                            for col in range(1, interv_inp_df.shape[1]):
                                value = interv_inp_df.iloc[row, col]
                                if pd.isna(value):
                                    variable_value.append("")  # Append empty string if column is NaN
                                else:
                                    variable_value.append(value)  # Append the actual value, including 0
                            break  # Exit the loop once found
            else:
                # Retrieve a single value from inp_df based on var_name
                for row in range(inp_df.shape[0]):
                    if inp_df.iloc[row, 0] == var_name:
                        variable_value = inp_df.iloc[row, 1]  # Get value from the next column
                        break
                # Check if value is still empty, then check interv_inp_df
                if not variable_value:
                    for row in range(interv_inp_df.shape[0]):
                        if interv_inp_df.iloc[row, 0] == var_name:
                            variable_value = interv_inp_df.iloc[row, 1]  # Get value from interv_inp_df
                            break
                # Raise an error only if variable_value is None, not 0 or empty string
                if variable_value is None:
                    raise KeyError(f"Variable {var_name} not found in both inp_df and interv_inp_df.")
            # Convert to list if it contains multiple values
            if isinstance(variable_value, list):
                variable_value = [v for v in variable_value if v != ""]  # Filter out only empty strings
            return variable_value
        else:
            raise ValueError("DataFrame and index must be provided for CSV input.")
    elif inp_data_source == "manual":
        variable_value = variables.get(var_name, None)
        if variable_value is None:
            raise ValueError(f"Variable {var_name} not found in the dictionary.")
        return variable_value
    else:
        raise ValueError("Invalid source specified. Must be 'manual' or 'csv'.")


# Default values for manual variables (these need to be defined)
latitude = None
climate = None
Soil_type1 = None
Soil_type2 = None
HSC1 = None
HSC2 = None
dist1 = None
dist2 = None
Soil_type1_dep = None
Soil_type2_dep = None
Net_Crop_Sown_Area = None
Fallow = None
Builtup = None
Water_bodies = None
Pasture = None
Forest = None
SW_Area = None
SW_Area_Irr_Eff = None
GW_Area = None
GW_Area_Irr_Eff = None
Aquifer_Depth = None
Starting_Level = None
Specific_Yield = None
Population = None
Domestic_Water_Use = None
Groundwater_Dependent = None
Surface_Water_Dependent = None
Other = None
Other_Water_Use = None

# Crop variables
Kharif_Crops = None
Kharif_Sowing_Month = None
Kharif_Sowing_Week = None
Kharif_Crops_Irr_Area = None
Kharif_Crops_Rainfed_Area = None
Kharif_Crops_Area = None
Kharif_Crops_Type = None
Kharif_Crop_Sown_Type = None
Rabi_Crops = None
Rabi_Sowing_Month = None
Rabi_Sowing_Week = None
Rabi_Crops_Irr_Area = None
Rabi_Crops_Rainfed_Area = None
Rabi_Crops_Area = None
Rabi_Crops_Type = None
Rabi_Crop_Sown_Type = None
Summer_Crops = None
Summer_Sowing_Month = None
Summer_Sowing_Week = None
Summer_Crops_Irr_Area = None
Summer_Crops_Rainfed_Area = None
Summer_Crops_Area = None
Summer_Crops_Type = None
Summer_Crop_Sown_Type = None

# Supply side intervention variables
Time_Period = None
Interest_Rate = None
Farm_Pond_Vol = None
Farm_Pond_Depth = None
Farm_Pond_Inf_Rate = None
Farm_Pond_Cost = None
Farm_Pond_Life_Span = None
Farm_Pond_Maintenance = None
Farm_Pond_Lined_Vol = None
Farm_Pond_Lined_Depth = None
Farm_Pond_Lined_Inf_Rate = None
Farm_Pond_Lined_Cost = None
Farm_Pond_Lined_Life_Span = None
Farm_Pond_Lined_Maintenance = None
Check_Dam_Vol = None
Check_Dam_Depth = None
Check_Dam_Inf_Rate = None
Check_Dam_Cost = None
Check_Dam_Life_Span = None
Check_Dam_Maintenance = None
Infiltration_Pond_Vol = None
Infiltration_Pond_Depth = None
Infiltration_Pond_Inf_Rate = None
Infiltration_Pond_Cost = None
Infiltration_Pond_Life_Span = None
Infiltration_Pond_Maintenance = None
Injection_Wells_Vol = None
Injection_Wells_Nos = None
Injection_Wells_Cost = None
Injection_Wells_Life_Span = None
Injection_Wells_Maintenance = None

# Demand side intervention variables
Kharif_Crop_Drip_Area = None
Rabi_Crop_Drip_Area = None
Summer_Crop_Drip_Area = None
Eff_Drip_irrigation = None
Kharif_Crop_Sprinkler_Area = None
Rabi_Crop_Sprinkler_Area = None
Summer_Crop_Sprinkler_Area = None
Eff_Sprinkler_irrigation = None
Kharif_Crop_Land_Levelling_Area = None
Rabi_Crop_Land_Levelling_Area = None
Summer_Crop_Land_Levelling_Area = None
Eff_Land_Levelling = None
Kharif_Crop_DSR_Area = None
Rabi_Crop_DSR_Area = None
Summer_Crop_DSR_Area = None
Eff_Direct_Seeded_Rice = None
Kharif_Crop_AWD_Area = None
Rabi_Crop_AWD_Area = None
Summer_Crop_AWD_Area = None
Eff_Alternate_Wetting_And_Dry = None
Kharif_Crop_SRI_Area = None
Rabi_Crop_SRI_Area = None
Summer_Crop_SRI_Area = None
Eff_SRI = None
Kharif_Crop_Ridge_Furrow_Area = None
Rabi_Crop_Ridge_Furrow_Area = None
Summer_Crop_Ridge_Furrow_Area = None
Eff_Ridge_Furrow_Irrigation = None
Kharif_Crop_Deficit_Area = None
Rabi_Crop_Deficit_Area = None
Summer_Crop_Deficit_Area = None
Eff_Deficit_Irrigation = None
Drip_Irr_Cost = None
Drip_Irr_Life_Span = None
Drip_Irr_Maintenance = None
Sprinkler_Irr_Cost = None
Sprinkler_Irr_Life_Span = None
Sprinkler_Irr_Maintenance = None
Land_Levelling_Cost = None
Land_Levelling_Life_Span = None
Land_Levelling_Maintenance = None
Direct_Seeded_Rice_Cost = None
Direct_Seeded_Rice_Life_Span = None
Alternate_Wetting_And_Dry_Cost = None
Alternate_Wetting_And_Dry_Life_Span = None
SRI_Cost = None
SRI_Life_Span = None
Ridge_Furrow_Irrigation_Cost = None
Ridge_Furrow_Irrigation_Life_Span = None
Deficit_Irrigation_Cost = None
Deficit_Irrigation_Life_Span = None

# Soil moisture intervention variables
Kharif_Crop_Cover_Crops_Area = None
Rabi_Crop_Cover_Crops_Area = None
Summer_Crop_Cover_Crops_Area = None
Kharif_Crop_Mulching_Area = None
Rabi_Crop_Mulching_Area = None
Summer_Crop_Mulching_Area = None
Kharif_Crop_BBF_Area = None
Rabi_Crop_BBF_Area = None
Summer_Crop_BBF_Area = None
Kharif_Crop_Bunds_Area = None
Rabi_Crop_Bunds_Area = None
Summer_Crop_Bunds_Area = None
Kharif_Crop_Tillage_Area = None
Rabi_Crop_Tillage_Area = None
Summer_Crop_Tillage_Area = None
Kharif_Crop_Tank_Area = None
Rabi_Crop_Tank_Area = None
Summer_Crop_Tank_Area = None
Red_CN_Cover_Crops = None
Cover_Crops_Cost = None
Cover_Crops_Life_Span = None
Cover_Crops_Eva_Red = None
Red_CN_Mulching = None
Mulching_Cost = None
Mulching_Life_Span = None
Mulching_Eva_Red = None
Red_CN_BBF = None
BBF_Cost = None
BBF_Life_Span = None
BBF_Maintenance = None
Eff_BBF = None
Red_CN_Bund = None
Bund_Cost = None
Bund_Life_Span = None
Bund_Maintenance = None
Red_CN_Tillage = None
Tillage_Cost = None
Tillage_Life_Span = None
Tillage_Eva_Red = None
Red_CN_Tank = None
Tank_Desilting_Life_Span = None
Tank_Eva_Red = None
Tank_Desilting_Vol = None
Tank_Desilting_Depth = None
Tank_Desilting_Cost = None


# input_utilities.py - Function 004: Returns kei coefficient value based on climate type
# Interactions: None
def get_kei_value(inp_climate):
    # Define kei values for different climates
    kei_values = {
        "semi arid": 1.05,
        "temperate": 1.10
    }

    # Check if climate is a list or a string
    if isinstance(inp_climate, list) and inp_climate:
        inp_climate = inp_climate[0]

    return kei_values.get(inp_climate, None)


# input_utilities.py - Function 005: Retrieves general input variables using handle_value_retrieval
# Interactions: handle_value_retrieval
def get_variable_value(inp_source,master_path,var_name, index):
    # Define a dictionary to map variable names to actual variables
    variables = {
        "latitude": latitude,
        "climate": climate,
        "Soil_type1": Soil_type1,
        "Soil_type2": Soil_type2,
        "HSC1": HSC1,
        "HSC2": HSC2,
        "dist1": dist1,
        "dist2": dist2,
        "Soil_type1_dep": Soil_type1_dep,
        "Soil_type2_dep": Soil_type2_dep,
        "Net_Crop_Sown_Area": Net_Crop_Sown_Area,
        "Fallow": Fallow,
        "Builtup": Builtup,
        "Water_bodies": Water_bodies,
        "Pasture": Pasture,
        "Forest": Forest,
        "SW_Area": SW_Area,
        "SW_Area_Irr_Eff": SW_Area_Irr_Eff,
        "GW_Area": GW_Area,
        "GW_Area_Irr_Eff": GW_Area_Irr_Eff,
        "Aquifer_Depth": Aquifer_Depth,
        "Starting_Level": Starting_Level,
        "Specific_Yield": Specific_Yield,
        "Population": Population,
        "Domestic_Water_Use": Domestic_Water_Use,
        "Groundwater_Dependent": Groundwater_Dependent,
        "Surface_Water_Dependent": Surface_Water_Dependent,
        "Other": Other,
        "Other_Water_Use": Other_Water_Use

    }

    return handle_value_retrieval(inp_source, variables,master_path, var_name, index)


# input_utilities.py - Function 006: Retrieves crop-related variables for Kharif, Rabi, and Summer seasons
# Interactions: handle_value_retrieval
def get_crops_variable_values(inp_source,master_path,var_name, index):
    # Define a dictionary to map variable names to actual variables
    variables = {
        "Kharif_Crops": Kharif_Crops,
        "Kharif_Sowing_Month": Kharif_Sowing_Month,
        "Kharif_Sowing_Week": Kharif_Sowing_Week,
        "Kharif_Crops_Irr_Area": Kharif_Crops_Irr_Area,
        "Kharif_Crops_Rainfed_Area": Kharif_Crops_Rainfed_Area,
        "Kharif_Crops_Area": Kharif_Crops_Area,
        "Kharif_Crops_Type": Kharif_Crops_Type,
        "Kharif_Crop_Sown_Type": Kharif_Crop_Sown_Type,

        "Rabi_Crops": Rabi_Crops,
        "Rabi_Sowing_Month": Rabi_Sowing_Month,
        "Rabi_Sowing_Week": Rabi_Sowing_Week,
        "Rabi_Crops_Irr_Area": Rabi_Crops_Irr_Area,
        "Rabi_Crops_Rainfed_Area": Rabi_Crops_Rainfed_Area,
        "Rabi_Crops_Area": Rabi_Crops_Area,
        "Rabi_Crops_Type": Rabi_Crops_Type,
        "Rabi_Crop_Sown_Type": Rabi_Crop_Sown_Type,

        "Summer_Crops": Summer_Crops,
        "Summer_Sowing_Month": Summer_Sowing_Month,
        "Summer_Sowing_Week": Summer_Sowing_Week,
        "Summer_Crops_Irr_Area": Summer_Crops_Irr_Area,
        "Summer_Crops_Rainfed_Area": Summer_Crops_Rainfed_Area,
        "Summer_Crops_Area": Summer_Crops_Area,
        "Summer_Crops_Type": Summer_Crops_Type,
        "Summer_Crop_Sown_Type": Summer_Crop_Sown_Type
    }

    return handle_value_retrieval(inp_source, variables,master_path, var_name, index, is_crops=True)


# input_utilities.py - Function 007: Retrieves supply-side intervention parameters and converts to float
# Interactions: shared.utilities.to_float, handle_value_retrieval
def get_supply_side_int_values(inp_source,master_path,var_name, index):
    # Define a dictionary to map variable names to actual supply-side intervention variables
    variables = {
        "Time_Period": Time_Period,
        "Interest_Rate": Interest_Rate,
        "Farm_Pond_Vol": Farm_Pond_Vol,
        "Farm_Pond_Depth": Farm_Pond_Depth,
        "Farm_Pond_Inf_Rate": Farm_Pond_Inf_Rate,
        "Farm_Pond_Cost": Farm_Pond_Cost,
        "Farm_Pond_Life_Span": Farm_Pond_Life_Span,
        "Farm_Pond_Maintenance": Farm_Pond_Maintenance,
        "Farm_Pond_Lined_Vol": Farm_Pond_Lined_Vol,
        "Farm_Pond_Lined_Depth": Farm_Pond_Lined_Depth,
        "Farm_Pond_Lined_Inf_Rate": Farm_Pond_Lined_Inf_Rate,
        "Farm_Pond_Lined_Cost": Farm_Pond_Lined_Cost,
        "Farm_Pond_Lined_Life_Span": Farm_Pond_Lined_Life_Span,
        "Farm_Pond_Lined_Maintenance": Farm_Pond_Lined_Maintenance,
        "Check_Dam_Vol": Check_Dam_Vol,
        "Check_Dam_Depth": Check_Dam_Depth,
        "Check_Dam_Inf_Rate": Check_Dam_Inf_Rate,
        "Check_Dam_Cost": Check_Dam_Cost,
        "Check_Dam_Life_Span": Check_Dam_Life_Span,
        "Check_Dam_Maintenance": Check_Dam_Maintenance,
        "Infiltration_Pond_Vol": Infiltration_Pond_Vol,
        "Infiltration_Pond_Depth": Infiltration_Pond_Depth,
        "Infiltration_Pond_Inf_Rate": Infiltration_Pond_Inf_Rate,
        "Infiltration_Pond_Cost": Infiltration_Pond_Cost,
        "Infiltration_Pond_Life_Span": Infiltration_Pond_Life_Span,
        "Infiltration_Pond_Maintenance": Infiltration_Pond_Maintenance,
        "Injection_Wells_Vol": Injection_Wells_Vol,
        "Injection_Wells_Nos": Injection_Wells_Nos,
        "Injection_Wells_Cost": Injection_Wells_Cost,
        "Injection_Wells_Life_Span": Injection_Wells_Life_Span,
        "Injection_Wells_Maintenance": Injection_Wells_Maintenance
    }

    return to_float(handle_value_retrieval(inp_source, variables, master_path, var_name, index), 0)


# input_utilities.py - Function 008: Retrieves demand-side intervention area values from crop calendar
# Interactions: handle_value_retrieval
def get_demand_side_interv_area_values(inp_source,master_path,var_name, index):
    # Dictionary containing the area variables
    variables = {
        "Kharif_Crop_Drip_Area": Kharif_Crop_Drip_Area,
        "Rabi_Crop_Drip_Area": Rabi_Crop_Drip_Area,
        "Summer_Crop_Drip_Area": Summer_Crop_Drip_Area,
        "Eff_Drip_irrigation": Eff_Drip_irrigation,
        "Kharif_Crop_Sprinkler_Area": Kharif_Crop_Sprinkler_Area,
        "Rabi_Crop_Sprinkler_Area": Rabi_Crop_Sprinkler_Area,
        "Summer_Crop_Sprinkler_Area": Summer_Crop_Sprinkler_Area,
        "Eff_Sprinkler_irrigation": Eff_Sprinkler_irrigation,
        "Kharif_Crop_Land_Levelling_Area": Kharif_Crop_Land_Levelling_Area,
        "Rabi_Crop_Land_Levelling_Area": Rabi_Crop_Land_Levelling_Area,
        "Summer_Crop_Land_Levelling_Area": Summer_Crop_Land_Levelling_Area,
        "Eff_Land_Levelling": Eff_Land_Levelling,
        "Kharif_Crop_DSR_Area": Kharif_Crop_DSR_Area,
        "Rabi_Crop_DSR_Area": Rabi_Crop_DSR_Area,
        "Summer_Crop_DSR_Area": Summer_Crop_DSR_Area,
        "Eff_Direct_Seeded_Rice": Eff_Direct_Seeded_Rice,
        "Kharif_Crop_AWD_Area": Kharif_Crop_AWD_Area,
        "Rabi_Crop_AWD_Area": Rabi_Crop_AWD_Area,
        "Summer_Crop_AWD_Area": Summer_Crop_AWD_Area,
        "Eff_Alternate_Wetting_And_Dry": Eff_Alternate_Wetting_And_Dry,
        "Kharif_Crop_SRI_Area": Kharif_Crop_SRI_Area,
        "Rabi_Crop_SRI_Area": Rabi_Crop_SRI_Area,
        "Summer_Crop_SRI_Area": Summer_Crop_SRI_Area,
        "Eff_SRI": Eff_SRI,
        "Kharif_Crop_Ridge_Furrow_Area": Kharif_Crop_Ridge_Furrow_Area,
        "Rabi_Crop_Ridge_Furrow_Area": Rabi_Crop_Ridge_Furrow_Area,
        "Summer_Crop_Ridge_Furrow_Area": Summer_Crop_Ridge_Furrow_Area,
        "Eff_Ridge_Furrow_Irrigation": Eff_Ridge_Furrow_Irrigation,
        "Kharif_Crop_Deficit_Area": Kharif_Crop_Deficit_Area,
        "Rabi_Crop_Deficit_Area": Rabi_Crop_Deficit_Area,
        "Summer_Crop_Deficit_Area": Summer_Crop_Deficit_Area,
        "Eff_Deficit_Irrigation": Eff_Deficit_Irrigation
    }

    return handle_value_retrieval(inp_source, variables, master_path, var_name, index, is_area=True)


# input_utilities.py - Function 009: Retrieves demand-side intervention cost and lifespan parameters
# Interactions: shared.utilities.to_float, handle_value_retrieval
def get_demand_side_interv_values(inp_source,master_path,var_name, index):
    # Define a dictionary to map variable names to actual variables
    variables = {
        "Drip_Irr_Cost": Drip_Irr_Cost,
        "Drip_Irr_Life_Span": Drip_Irr_Life_Span,
        "Drip_Irr_Maintenance": Drip_Irr_Maintenance,
        "Sprinkler_Irr_Cost": Sprinkler_Irr_Cost,
        "Sprinkler_Irr_Life_Span": Sprinkler_Irr_Life_Span,
        "Sprinkler_Irr_Maintenance": Sprinkler_Irr_Maintenance,
        "Land_Levelling_Cost": Land_Levelling_Cost,
        "Land_Levelling_Life_Span": Land_Levelling_Life_Span,
        "Land_Levelling_Maintenance": Land_Levelling_Maintenance,
        "Direct_Seeded_Rice_Cost": Direct_Seeded_Rice_Cost,
        "Direct_Seeded_Rice_Life_Span": Direct_Seeded_Rice_Life_Span,
        "Alternate_Wetting_And_Dry_Cost": Alternate_Wetting_And_Dry_Cost,
        "Alternate_Wetting_And_Dry_Life_Span": Alternate_Wetting_And_Dry_Life_Span,
        "SRI_Cost": SRI_Cost,
        "SRI_Life_Span": SRI_Life_Span,
        "Ridge_Furrow_Irrigation_Cost": Ridge_Furrow_Irrigation_Cost,
        "Ridge_Furrow_Irrigation_Life_Span": Ridge_Furrow_Irrigation_Life_Span,
        "Deficit_Irrigation_Cost": Deficit_Irrigation_Cost,
        "Deficit_Irrigation_Life_Span": Deficit_Irrigation_Life_Span

    }

    return to_float(handle_value_retrieval(inp_source, variables, master_path, var_name, index), 0)


# input_utilities.py - Function 010: Retrieves soil moisture intervention area values from crop calendar
# Interactions: handle_value_retrieval
def get_soil_moisture_interv_area_values(inp_source,master_path,var_name, index):
    variables = {
        "Kharif_Crop_Cover_Crops_Area": Kharif_Crop_Cover_Crops_Area,
        "Rabi_Crop_Cover_Crops_Area": Rabi_Crop_Cover_Crops_Area,
        "Summer_Crop_Cover_Crops_Area": Summer_Crop_Cover_Crops_Area,
        "Kharif_Crop_Mulching_Area": Kharif_Crop_Mulching_Area,
        "Rabi_Crop_Mulching_Area": Rabi_Crop_Mulching_Area,
        "Summer_Crop_Mulching_Area": Summer_Crop_Mulching_Area,
        "Kharif_Crop_BBF_Area": Kharif_Crop_BBF_Area,
        "Rabi_Crop_BBF_Area": Rabi_Crop_BBF_Area,
        "Summer_Crop_BBF_Area": Summer_Crop_BBF_Area,
        "Kharif_Crop_Bunds_Area": Kharif_Crop_Bunds_Area,
        "Rabi_Crop_Bunds_Area": Rabi_Crop_Bunds_Area,
        "Summer_Crop_Bunds_Area": Summer_Crop_Bunds_Area,
        "Kharif_Crop_Tillage_Area": Kharif_Crop_Tillage_Area,
        "Rabi_Crop_Tillage_Area": Rabi_Crop_Tillage_Area,
        "Summer_Crop_Tillage_Area": Summer_Crop_Tillage_Area,
        "Kharif_Crop_Tank_Area": Kharif_Crop_Tank_Area,
        "Rabi_Crop_Tank_Area": Rabi_Crop_Tank_Area,
        "Summer_Crop_Tank_Area": Summer_Crop_Tank_Area,
    }

    return handle_value_retrieval(inp_source, variables, master_path, var_name, index, is_area=True)


# input_utilities.py - Function 011: Retrieves soil moisture intervention parameters including CN reduction values
# Interactions: shared.utilities.to_float, handle_value_retrieval
def get_soil_moisture_interv_values(inp_source,master_path,var_name, index):
    # Dictionary containing the soil moisture intervention values
    variables = {
        "Red_CN_Cover_Crops": Red_CN_Cover_Crops,
        "Cover_Crops_Cost": Cover_Crops_Cost,
        "Cover_Crops_Life_Span": Cover_Crops_Life_Span,
        "Cover_Crops_Eva_Red": Cover_Crops_Eva_Red,

        "Red_CN_Mulching": Red_CN_Mulching,
        "Mulching_Cost": Mulching_Cost,
        "Mulching_Life_Span": Mulching_Life_Span,
        "Mulching_Eva_Red": Mulching_Eva_Red,

        "Red_CN_BBF": Red_CN_BBF,
        "BBF_Cost": BBF_Cost,
        "BBF_Life_Span": BBF_Life_Span,
        "BBF_Maintenance": BBF_Maintenance,
        "Eff_BBF": Eff_BBF,

        "Red_CN_Bund": Red_CN_Bund,
        "Bund_Cost": Bund_Cost,
        "Bund_Life_Span": Bund_Life_Span,
        "Bund_Maintenance": Bund_Maintenance,

        "Red_CN_Tillage": Red_CN_Tillage,
        "Tillage_Cost": Tillage_Cost,
        "Tillage_Life_Span": Tillage_Life_Span,
        "Tillage_Eva_Red": Tillage_Eva_Red,

        "Red_CN_Tank": Red_CN_Tank,
        "Tank_Desilting_Life_Span": Tank_Desilting_Life_Span,
        "Tank_Eva_Red": Tank_Eva_Red,
        "Tank_Desilting_Vol": Tank_Desilting_Vol,
        "Tank_Desilting_Depth": Tank_Desilting_Depth,
        "Tank_Desilting_Cost": Tank_Desilting_Cost,
    }

    return to_float(handle_value_retrieval(inp_source, variables,master_path, var_name, index), 0)