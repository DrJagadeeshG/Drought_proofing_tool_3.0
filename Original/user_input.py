"""
Created on Wed Sep 11 11:00:38 2024

@author: Dr. Jagadeesh, Consultant, IWMI
"""
import os
import pandas as pd
import functools
from manual_input import *
# import manual_input


# Cache for file paths to avoid repeated calls
_file_paths_cache = {}

# user_input.py - Function 1: Clears the file paths cache for testing or configuration changes
def clear_file_paths_cache():
    """Clear the file paths cache - useful for testing or changing configurations"""
    global _file_paths_cache
    _file_paths_cache.clear()
    print("File paths cache cleared")

# user_input.py - Function 2: Returns cached file paths for datasets based on input source and master path
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


# Convert list or single value to float
# user_input.py - Function 3: Converts various input types to float with fallback to default value
def to_float(value, default_value=float("nan")):
    if isinstance(value, list):
        # If the value is a list, take the first element and convert to float
        return float(value[0]) if value else default_value
    elif isinstance(value, (int, float)):
        # If it's already a number, return it as float
        return float(value)
    elif isinstance(value, str):
        # Return NaN for empty string
        if value.strip() == "":
            return float("nan")
        # Try to convert a non-empty string to float
        try:
            return float(value)
        except ValueError:
            # If conversion fails, return the default value
            return default_value
    else:
        # If it's neither list nor number, return the default value
        return default_value


# user_input.py - Function 4: Cached CSV reader to avoid repeated disk I/O operations
@functools.lru_cache(maxsize=64)
def _read_cached_csv(file_path):
    """Cache CSV reading to avoid repeated disk I/O"""
    if file_path and os.path.exists(file_path):
        return pd.read_csv(file_path, header=None)
    return pd.DataFrame()

# user_input.py - Function 5: Handles value retrieval from CSV or manual sources for variables
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


# user_input.py - Function 6: Returns kei coefficient value based on climate type
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


# user_input.py - Function 7: Retrieves general input variables using handle_value_retrieval
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


# user_input.py - Function 8: Retrieves crop-related variables for Kharif, Rabi, and Summer seasons
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


# user_input.py - Function 9: Retrieves supply-side intervention parameters and converts to float
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


# user_input.py - Function 10: Retrieves demand-side intervention area values from crop calendar
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


# user_input.py - Function 11: Retrieves demand-side intervention cost and lifespan parameters
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


# user_input.py - Function 12: Retrieves soil moisture intervention area values from crop calendar
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


# user_input.py - Function 13: Retrieves soil moisture intervention parameters including CN reduction values
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


# user_input.py - Function 14: Collects and organizes all input variables into ordered dictionary
def collect_inp_variables(inp_source,master_path):
    variables_list = [
        # (index, "variable_name", function_call)
        (1, "kei", lambda: get_kei_value(get_variable_value(inp_source,master_path,"climate", 1))),
        
        # Kharif Crops
        (16, "Kharif_Crops", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Crops", 16)),
        (17, "Kharif_Sowing_Month", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Sowing_Month", 17)),
        (18, "Kharif_Sowing_Week", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Sowing_Week", 18)),
        (19, "Kharif_Crops_Irr_Area", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Crops_Irr_Area", 19)),
        (20, "Kharif_Crops_Rainfed_Area", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Crops_Rainfed_Area", 20)),
        (21, "Kharif_Crops_Area", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Crops_Area", 21)),
        (22, "Kharif_Crops_Type", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Crops_Type", 22)),
        (23, "Kharif_Crop_Sown_Type", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Crop_Sown_Type", 23)),
        
        # Rabi Crops
        (24, "Rabi_Crops", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Crops", 24)),
        (25, "Rabi_Sowing_Month", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Sowing_Month", 25)),
        (26, "Rabi_Sowing_Week", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Sowing_Week", 26)),
        (27, "Rabi_Crops_Irr_Area", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Crops_Irr_Area", 27)),
        (28, "Rabi_Crops_Rainfed_Area", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Crops_Rainfed_Area", 28)),
        (29, "Rabi_Crops_Area", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Crops_Area", 29)),
        (30, "Rabi_Crops_Type", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Crops_Type", 30)),
        (31, "Rabi_Crop_Sown_Type", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Crop_Sown_Type", 31)),
        
        # Summer Crops
        (32, "Summer_Crops", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Crops", 32)),
        (33, "Summer_Sowing_Month", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Sowing_Month", 33)),
        (34, "Summer_Sowing_Week", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Sowing_Week", 34)),
        (35, "Summer_Crops_Irr_Area", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Crops_Irr_Area", 35)),
        (36, "Summer_Crops_Rainfed_Area", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Crops_Rainfed_Area", 36)),
        (37, "Summer_Crops_Area", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Crops_Area", 37)),
        (38, "Summer_Crops_Type", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Crops_Type", 38)),
        (39, "Summer_Crop_Sown_Type", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Crop_Sown_Type", 39)),
        
        # General Variables
        (0, "latitude", lambda: get_variable_value(inp_source,master_path,"latitude", 0)),
        # (1, "climate", lambda: get_variable_value("climate", 1)),
        (2, "Soil_type1", lambda: get_variable_value(inp_source,master_path,"Soil_type1", 2)),
        (3, "Soil_type2", lambda: get_variable_value(inp_source,master_path,"Soil_type2", 3)),
        (4, "HSC1", lambda: get_variable_value(inp_source,master_path,"HSC1", 4)),
        (5, "HSC2", lambda: get_variable_value(inp_source,master_path,"HSC2", 5)),
        (6, "dist1", lambda: get_variable_value(inp_source,master_path,"dist1", 6)),
        (7, "dist2", lambda: get_variable_value(inp_source,master_path,"dist2", 7)),
        (8, "Soil_type1_dep", lambda: get_variable_value(inp_source,master_path,"Soil_type1_dep", 8)),
        (9, "Soil_type2_dep", lambda: get_variable_value(inp_source,master_path,"Soil_type2_dep", 9)),
        (10, "Net_Crop_Sown_Area", lambda: get_variable_value(inp_source,master_path,"Net_Crop_Sown_Area", 10)),
        (11, "Fallow", lambda: get_variable_value(inp_source,master_path,"Fallow", 11)),
        (12, "Builtup", lambda: get_variable_value(inp_source,master_path,"Builtup", 12)),
        (13, "Water_bodies", lambda: get_variable_value(inp_source,master_path,"Water_bodies", 13)),
        (14, "Pasture", lambda: get_variable_value(inp_source,master_path,"Pasture", 14)),
        (15, "Forest", lambda: get_variable_value(inp_source,master_path,"Forest", 15)),
        (40, "SW_Area", lambda: get_variable_value(inp_source,master_path,"SW_Area", 40)),
        (41, "SW_Area_Irr_Eff", lambda: get_variable_value(inp_source,master_path,"SW_Area_Irr_Eff", 41)),
        (42, "GW_Area", lambda: get_variable_value(inp_source,master_path,"GW_Area", 42)),
        (43, "GW_Area_Irr_Eff", lambda: get_variable_value(inp_source,master_path,"GW_Area_Irr_Eff", 43)),
        (44, "Aquifer_Depth", lambda: get_variable_value(inp_source,master_path,"Aquifer_Depth", 44)),
        (45, "Starting_Level", lambda: get_variable_value(inp_source,master_path,"Starting_Level", 45)),
        (46, "Specific_Yield", lambda: get_variable_value(inp_source,master_path,"Specific_Yield", 46)),
        (47, "Population", lambda: get_variable_value(inp_source,master_path,"Population", 47)),
        (48, "Domestic_Water_Use", lambda: get_variable_value(inp_source,master_path,"Domestic_Water_Use", 48)),
        (49, "Groundwater_Dependent", lambda: get_variable_value(inp_source,master_path,"Groundwater_Dependent", 49)),
        (50, "Surface_Water_Dependent", lambda: get_variable_value(inp_source,master_path,"Surface_Water_Dependent", 50)),
        (51, "Other", lambda: get_variable_value(inp_source,master_path,"Other", 51)),
        (52, "Other_Water_Use", lambda: get_variable_value(inp_source,master_path,"Other_Water_Use", 52)),
        
    ]

    # Sort the list based on indices
    variables_list.sort(key=lambda x: x[0])

    # Create the ordered dictionary
    variables_dict = {}
    for index, var_name, func in variables_list:
        variables_dict[var_name] = func()

    return variables_dict


# user_input.py - Function 15: Collects and organizes all intervention variables into ordered dictionary
def collect_int_variables(inp_source,master_path):
    variables_list = [
        (0, "Time_Period", lambda: get_supply_side_int_values(inp_source,master_path,"Time_Period", 0)),
        (1, "Interest_Rate", lambda: get_supply_side_int_values(inp_source,master_path,"Interest_Rate", 1)),
        
        (2, "Farm_Pond_Vol", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Vol", 2)),
        (3, "Farm_Pond_Depth", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Depth", 3)),
        (4, "Farm_Pond_Inf_Rate", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Inf_Rate", 4)),
        (5, "Farm_Pond_Cost", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Cost", 5)),
        (6, "Farm_Pond_Life_Span", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Life_Span", 6)),
        (7, "Farm_Pond_Maintenance", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Maintenance", 7)),
        
        (8, "Farm_Pond_Lined_Vol", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Lined_Vol", 8)),
        (9, "Farm_Pond_Lined_Depth", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Lined_Depth", 9)),
        (10, "Farm_Pond_Lined_Inf_Rate", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Lined_Inf_Rate", 10)),
        (11, "Farm_Pond_Lined_Cost", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Lined_Cost", 11)),
        (12, "Farm_Pond_Lined_Life_Span", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Lined_Life_Span", 12)),
        (13, "Farm_Pond_Lined_Maintenance", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Lined_Maintenance", 13)),
        
        (14, "Check_Dam_Vol", lambda: get_supply_side_int_values(inp_source,master_path,"Check_Dam_Vol", 14)),
        (15, "Check_Dam_Depth", lambda: get_supply_side_int_values(inp_source,master_path,"Check_Dam_Depth", 15)),
        (16, "Check_Dam_Inf_Rate", lambda: get_supply_side_int_values(inp_source,master_path,"Check_Dam_Inf_Rate", 16)),
        (17, "Check_Dam_Cost", lambda: get_supply_side_int_values(inp_source,master_path,"Check_Dam_Cost", 17)),
        (18, "Check_Dam_Life_Span", lambda: get_supply_side_int_values(inp_source,master_path,"Check_Dam_Life_Span", 18)),
        (19, "Check_Dam_Maintenance", lambda: get_supply_side_int_values(inp_source,master_path,"Check_Dam_Maintenance", 19)),
        
        (20, "Infiltration_Pond_Vol", lambda: get_supply_side_int_values(inp_source,master_path,"Infiltration_Pond_Vol", 20)),
        (21, "Infiltration_Pond_Depth", lambda: get_supply_side_int_values(inp_source,master_path,"Infiltration_Pond_Depth", 21)),
        (22, "Infiltration_Pond_Inf_Rate", lambda: get_supply_side_int_values(inp_source,master_path,"Infiltration_Pond_Inf_Rate", 22)),
        (23, "Infiltration_Pond_Cost", lambda: get_supply_side_int_values(inp_source,master_path,"Infiltration_Pond_Cost", 23)),
        (24, "Infiltration_Pond_Life_Span", lambda: get_supply_side_int_values(inp_source,master_path,"Infiltration_Pond_Life_Span", 24)),
        (25, "Infiltration_Pond_Maintenance", lambda: get_supply_side_int_values(inp_source,master_path,"Infiltration_Pond_Maintenance", 25)),
        
        (26, "Injection_Wells_Vol", lambda: get_supply_side_int_values(inp_source,master_path,"Injection_Wells_Vol", 26)),
        (27, "Injection_Wells_Nos", lambda: get_supply_side_int_values(inp_source,master_path,"Injection_Wells_Nos", 27)),
        (28, "Injection_Wells_Cost", lambda: get_supply_side_int_values(inp_source,master_path,"Injection_Wells_Cost", 28)),
        (29, "Injection_Wells_Life_Span", lambda: get_supply_side_int_values(inp_source,master_path,"Injection_Wells_Life_Span", 29)),
        (30, "Injection_Wells_Maintenance", lambda: get_supply_side_int_values(inp_source,master_path,"Injection_Wells_Maintenance", 30)),
        
        (31, "Kharif_Crop_Drip_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Kharif_Crop_Drip_Area", 31)),
        (32, "Rabi_Crop_Drip_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Rabi_Crop_Drip_Area", 32)),
        (33, "Summer_Crop_Drip_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Summer_Crop_Drip_Area", 33)),
        (34, "Eff_Drip_irrigation", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Drip_irrigation", 34)),
        
        (38, "Kharif_Crop_Sprinkler_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Kharif_Crop_Sprinkler_Area", 38)),
        (39, "Rabi_Crop_Sprinkler_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Rabi_Crop_Sprinkler_Area", 39)),
        (40, "Summer_Crop_Sprinkler_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Summer_Crop_Sprinkler_Area", 40)),
        (41, "Eff_Sprinkler_irrigation", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Sprinkler_irrigation", 41)),
        
        (45, "Kharif_Crop_Land_Levelling_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Kharif_Crop_Land_Levelling_Area", 45)),
        (46, "Rabi_Crop_Land_Levelling_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Rabi_Crop_Land_Levelling_Area", 46)),
        (47, "Summer_Crop_Land_Levelling_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Summer_Crop_Land_Levelling_Area", 47)),
        (48, "Eff_Land_Levelling", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Land_Levelling", 48)),

        (52, "Kharif_Crop_DSR_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Kharif_Crop_DSR_Area", 52)),
        (53, "Rabi_Crop_DSR_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Rabi_Crop_DSR_Area", 53)),
        (54, "Summer_Crop_DSR_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Summer_Crop_DSR_Area", 54)),
        (55, "Eff_Direct_Seeded_Rice", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Direct_Seeded_Rice", 55)),

        (58, "Kharif_Crop_AWD_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Kharif_Crop_AWD_Area", 58)),
        (59, "Rabi_Crop_AWD_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Rabi_Crop_AWD_Area", 59)),
        (60, "Summer_Crop_AWD_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Summer_Crop_AWD_Area", 60)),
        (61, "Eff_Alternate_Wetting_And_Dry", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Alternate_Wetting_And_Dry", 61)),

        (64, "Kharif_Crop_SRI_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Kharif_Crop_SRI_Area", 64)),
        (65, "Rabi_Crop_SRI_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Rabi_Crop_SRI_Area", 65)),
        (66, "Summer_Crop_SRI_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Summer_Crop_SRI_Area", 66)),
        (67, "Eff_SRI", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_SRI", 67)),

        (70, "Kharif_Crop_Ridge_Furrow_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Kharif_Crop_Ridge_Furrow_Area", 70)),
        (71, "Rabi_Crop_Ridge_Furrow_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Rabi_Crop_Ridge_Furrow_Area", 71)),
        (72, "Summer_Crop_Ridge_Furrow_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Summer_Crop_Ridge_Furrow_Area", 72)),
        (73, "Eff_Ridge_Furrow_Irrigation", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Ridge_Furrow_Irrigation", 73)),

        (76, "Kharif_Crop_Deficit_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Kharif_Crop_Deficit_Area", 76)),
        (77, "Rabi_Crop_Deficit_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Rabi_Crop_Deficit_Area", 77)),
        (78, "Summer_Crop_Deficit_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Summer_Crop_Deficit_Area", 78)),
        (79, "Eff_Deficit_Irrigation", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Deficit_Irrigation", 79)),

        # Costs and Lifespan variables
        (35, "Drip_Irr_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Drip_Irr_Cost", 35)),
        (36, "Drip_Irr_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Drip_Irr_Life_Span", 36)),
        (37, "Drip_Irr_Maintenance", lambda: get_demand_side_interv_values(inp_source,master_path,"Drip_Irr_Maintenance", 37)),

        (42, "Sprinkler_Irr_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Sprinkler_Irr_Cost", 42)),
        (43, "Sprinkler_Irr_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Sprinkler_Irr_Life_Span", 43)),
        (44, "Sprinkler_Irr_Maintenance", lambda: get_demand_side_interv_values(inp_source,master_path,"Sprinkler_Irr_Maintenance", 44)),

        (49, "Land_Levelling_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Land_Levelling_Cost", 49)),
        (50, "Land_Levelling_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Land_Levelling_Life_Span", 50)),
        (51, "Land_Levelling_Maintenance", lambda: get_demand_side_interv_values(inp_source,master_path,"Land_Levelling_Maintenance", 51)),

        (56, "Direct_Seeded_Rice_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Direct_Seeded_Rice_Cost", 56)),
        (57, "Direct_Seeded_Rice_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Direct_Seeded_Rice_Life_Span", 57)),

        (62, "Alternate_Wetting_And_Dry_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Alternate_Wetting_And_Dry_Cost", 62)),
        (63, "Alternate_Wetting_And_Dry_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Alternate_Wetting_And_Dry_Life_Span", 63)),

        (68, "SRI_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"SRI_Cost", 68)),
        (69, "SRI_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"SRI_Life_Span", 69)),

        (74, "Ridge_Furrow_Irrigation_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Ridge_Furrow_Irrigation_Cost", 74)),
        (75, "Ridge_Furrow_Irrigation_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Ridge_Furrow_Irrigation_Life_Span", 75)),

        (80, "Deficit_Irrigation_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Deficit_Irrigation_Cost", 80)),
        (81, "Deficit_Irrigation_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Deficit_Irrigation_Life_Span", 81)),

        # Soil moisture intervention variables
        (82, "Kharif_Crop_Cover_Crops_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Kharif_Crop_Cover_Crops_Area", 82)),
        (83, "Rabi_Crop_Cover_Crops_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Rabi_Crop_Cover_Crops_Area", 83)),
        (84, "Summer_Crop_Cover_Crops_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Summer_Crop_Cover_Crops_Area", 84)),

        (89, "Kharif_Crop_Mulching_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Kharif_Crop_Mulching_Area", 89)),
        (90, "Rabi_Crop_Mulching_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Rabi_Crop_Mulching_Area", 90)),
        (91, "Summer_Crop_Mulching_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Summer_Crop_Mulching_Area", 91)),

        (96, "Kharif_Crop_BBF_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Kharif_Crop_BBF_Area", 96)),
        (97, "Rabi_Crop_BBF_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Rabi_Crop_BBF_Area", 97)),
        (98, "Summer_Crop_BBF_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Summer_Crop_BBF_Area", 98)),
        
        (104, "Kharif_Crop_Bunds_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Kharif_Crop_Bunds_Area", 104)),
        (105, "Rabi_Crop_Bunds_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Rabi_Crop_Bunds_Area", 105)),
        (106, "Summer_Crop_Bunds_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Summer_Crop_Bunds_Area", 106)),
        
        (111, "Kharif_Crop_Tillage_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Kharif_Crop_Tillage_Area", 111)),
        (112, "Rabi_Crop_Tillage_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Rabi_Crop_Tillage_Area", 112)),
        (113, "Summer_Crop_Tillage_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Summer_Crop_Tillage_Area", 113)),
        
        (118, "Kharif_Crop_Tank_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Kharif_Crop_Tank_Area", 118)),
        (119, "Rabi_Crop_Tank_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Rabi_Crop_Tank_Area", 119)),
        (120, "Summer_Crop_Tank_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Summer_Crop_Tank_Area", 120)),
        
        (85, "Red_CN_Cover_Crops", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Red_CN_Cover_Crops", 85)),
        (86, "Cover_Crops_Cost", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Cover_Crops_Cost", 86)),
        (87, "Cover_Crops_Life_Span", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Cover_Crops_Life_Span", 87)),
        (88, "Cover_Crops_Eva_Red", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Cover_Crops_Eva_Red", 88)),
        
        (92, "Red_CN_Mulching", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Red_CN_Mulching", 92)),
        (93, "Mulching_Cost", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Mulching_Cost", 93)),
        (94, "Mulching_Life_Span", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Mulching_Life_Span", 94)),
        (95, "Mulching_Eva_Red", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Mulching_Eva_Red", 95)),
        
        (99, "Red_CN_BBF", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Red_CN_BBF", 99)),
        (100, "BBF_Cost", lambda: get_soil_moisture_interv_values(inp_source,master_path,"BBF_Cost", 100)),
        (101, "BBF_Life_Span", lambda: get_soil_moisture_interv_values(inp_source,master_path,"BBF_Life_Span", 101)),
        (102, "BBF_Maintenance", lambda: get_soil_moisture_interv_values(inp_source,master_path,"BBF_Maintenance", 102)),
        (103, "Eff_BBF", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Eff_BBF", 103)),
        
        (107, "Red_CN_Bund", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Red_CN_Bund", 107)),
        (108, "Bund_Cost", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Bund_Cost", 108)),
        (109, "Bund_Life_Span", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Bund_Life_Span", 109)),
        (110, "Bund_Maintenance", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Bund_Maintenance", 110)),
        (114, "Red_CN_Tillage", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Red_CN_Tillage", 114)),
        (115, "Tillage_Cost", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tillage_Cost", 115)),
        (116, "Tillage_Life_Span", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tillage_Life_Span", 116)),
        (117, "Tillage_Eva_Red", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tillage_Eva_Red", 117)),
        (121, "Red_CN_Tank", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Red_CN_Tank", 121)),
        (122, "Tank_Desilting_Life_Span", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tank_Desilting_Life_Span", 122)),
        (123, "Tank_Eva_Red", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tank_Eva_Red", 123)),
        (124, "Tank_Desilting_Vol", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tank_Desilting_Vol", 124)),
        (125, "Tank_Desilting_Depth", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tank_Desilting_Depth", 125)),
        (126, "Tank_Desilting_Cost", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tank_Desilting_Cost", 126)),
        ]
        
    # Sort the list based on indices
    variables_list.sort(key=lambda x: x[0])

    # Create the ordered dictionary
    variables_dict = {}
    for index, var_name, func in variables_list:
        variables_dict[var_name] = func()

    return variables_dict




