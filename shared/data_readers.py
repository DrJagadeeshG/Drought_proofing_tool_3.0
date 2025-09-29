"""
Data reading and caching functions for drought proofing tool

This module contains functions for data reading and caching:
- CSV file reading and processing
- Data caching and retrieval
- Input variable processing

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Handles data reading, caching, and processing from CSV files and databases for crops, climate, and interventions
# ========================================

import pandas as pd
import numpy as np
import os
import functools
from shared.utilities import to_float, resample, calc_days_in_month
# Removed circular import: from orchestrator.input_collector import collect_inp_variables
# Functions that need collect_inp_variables will have it passed as parameter
# Removed circular import - calc_etom will be imported locally where needed

# Cache for file paths
_file_paths_cache = {}


# data_readers.py - Function 001: Reads and formats crop database from CSV file
# Interactions: pandas
def get_crop_data(crop_db):
    crop_df = pd.read_csv(crop_db, header=None)
    crop_df = crop_df.drop(index=0)
    crop_df.columns = crop_df.iloc[0]
    crop_df = crop_df.drop(index=1).reset_index(drop=True)
    return crop_df


# data_readers.py - Function 002: Retrieves solar radiation data for specific latitude
# Interactions: pandas
def get_radiation_db(radiation_db, latitude):
    # Check if latitude is a list and convert it to a string
    if isinstance(latitude, list) and len(latitude) > 0:
        latitude = latitude[0]
    # Read the radiation database CSV file
    df_rd_db = pd.read_csv(radiation_db)
    df_rd_db.set_index("Lat", inplace=True)
    # Filter the data for the desired latitude
    filtered_data = df_rd_db.loc[latitude]
    # Create a new DataFrame to store the monthly values
    df_rd = filtered_data.reset_index()
    df_rd.columns = ["Month", "Radiation"]
    return df_rd


# data_readers.py - Function 003: Reads precipitation data and calculates 5-day rolling rainfall
# Interactions: pandas
def get_pcp_value(daily_data):
    df_dd = pd.read_csv(daily_data)
    df_dd.columns = ["Date", "Pi"]
    df_dd["Date"] = pd.to_datetime(df_dd["Date"], format="%m/%d/%Y")
    df_dd["last_5_days_Rain"] = df_dd["Pi"].rolling(window=5, min_periods=1).sum()
    return df_dd


# data_readers.py - Function 004: Retrieves and caches season-wise crop data including areas and sowing details
# Interactions: get_crops_variable_values
def get_season_crop_data(inp_source,master_path):
    print("FUNCTION 1: get_season_crop_data() - Getting season crop data")
    var_season_data = {}
    for season_key in ["kharif", "rabi", "summer"]:
        season_data = get_crops_variable_values(inp_source,master_path,season_key, 0)
        var_season_data[season_key] = season_data
    return var_season_data


# data_readers.py - Function 005: Retrieves land use type areas including crop, fallow, built-up areas
# Interactions: orchestrator.input_collector.collect_inp_variables
def get_land_use_types(inp_source,master_path):
    # Import here to avoid circular import
    from orchestrator.input_collector import collect_inp_variables
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


# data_readers.py - Function 006: Retrieves season values with crop types and sowing details
# Interactions: orchestrator.input_collector.collect_inp_variables
def get_seasons_val(inp_source,master_path):
    # Import here to avoid circular import
    from orchestrator.input_collector import collect_inp_variables
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


# data_readers.py - Function 007: Retrieves season data for crop type processing
# Interactions: orchestrator.input_collector.collect_inp_variables
def get_seasons_data(inp_source,master_path):
    # Import here to avoid circular import
    from orchestrator.input_collector import collect_inp_variables
    inp_vars = collect_inp_variables(inp_source,master_path)
    seasons = [
        ("Kharif", inp_vars["Kharif_Crops"], inp_vars["Kharif_Crops_Type"], inp_vars["Kharif_Crop_Sown_Type"]),
        ("Rabi", inp_vars["Rabi_Crops"], inp_vars["Rabi_Crops_Type"], inp_vars["Rabi_Crop_Sown_Type"]),
        ("Summer", inp_vars["Summer_Crops"], inp_vars["Summer_Crops_Type"], inp_vars["Summer_Crop_Sown_Type"])
    ]
    return seasons


# data_readers.py - Function 008: Processes monthly climate and precipitation data
# Interactions: soil_storage_bucket.outflux.evapotranspiration.calc_etom, shared.utilities.resample, shared.utilities.calc_days_in_month
def process_monthly_data(df_dd, file_paths,inp_source,master_path):
    print("FUNCTION 29: process_monthly_data() - Processing monthly climate data")
    # Import calc_etom locally to avoid circular import
    from soil_storage_bucket.outflux.evapotranspiration import calc_etom
    monthly_data = file_paths["monthly_data"]
    df_mm = resample(df_dd, monthly_data, "Date", "Pi").rename(columns={"Pi": "Rain"})
    df_mm["Days"] = df_mm["Date"].map(lambda x: calc_days_in_month(x.year, x.month))
    df_mm = calc_etom(df_mm,file_paths,inp_source,master_path)
    return df_mm


# data_readers.py - Function 009: Retrieves cover type and treatment type for crops from database
# Interactions: pandas
def get_cover_type(df_cc, crop_df):
    for crop in df_cc.index:
        row = crop_df[crop_df["Crops"] == crop]
        if not row.empty:
            # Extract the relevant data from the found row in crop_df
            df_cc.loc[crop, "Cover Type"] = row["Cover Type"].values[0]
            df_cc.loc[crop, "Treatment Type"] = row["Treatment Type"].values[0]
        else:
            # Handle case where crop is not found in crop_df (optional)
            df_cc.loc[crop, "Cover Type"] = None
            df_cc.loc[crop, "Treatment Type"] = None
    return df_cc


# data_readers.py - Function 010: Clears the file paths cache for testing or configuration changes
# Interactions: None
def clear_file_paths_cache():
    """Clear the file paths cache - useful for testing or changing configurations"""
    global _file_paths_cache
    _file_paths_cache.clear()
    print("File paths cache cleared")


# data_readers.py - Function 011: Returns cached file paths for datasets based on input source and master path
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
        # Add new intervention CSV files
        paths["supply_interventions"] = os.path.join(master_path, csv_subdir, "supply_interventions_correct.csv")
        paths["demand_interventions"] = os.path.join(master_path, csv_subdir, "demand_interventions_correct.csv")
        paths["soil_interventions"] = os.path.join(master_path, csv_subdir, "soil_interventions_correct.csv")
    else:
        paths["input_baseline"] = None
        paths["input_interventions"] = None
        paths["supply_interventions"] = None
        paths["demand_interventions"] = None
        paths["soil_interventions"] = None
    # Cache the result before returning
    _file_paths_cache[cache_key] = paths
    
    return paths


# data_readers.py - Function 012: Cached CSV reader to avoid repeated disk I/O operations
# Interactions: pandas, os, functools
@functools.lru_cache(maxsize=64)
def _read_cached_csv(file_path):
    """Cache CSV reading to avoid repeated disk I/O"""
    if file_path and os.path.exists(file_path):
        return pd.read_csv(file_path, header=None)
    return pd.DataFrame()


# data_readers.py - Function 012A: Reads supply intervention data from new tabular CSV format
# Interactions: pandas, os, shared.utilities.to_float
def read_supply_interventions_csv(file_path, scenario_num=1):
    """
    Reads supply interventions from new tabular CSV format
    Returns: dict with intervention data for specified scenario
    """
    if not os.path.exists(file_path):
        return {}
    
    # Read CSV with headers
    df = pd.read_csv(file_path)
    
    # Find the data section (starts after "SUPPLY SIDE INTERVENTIONS")
    data_start_row = None
    for idx, row in df.iterrows():
        if 'S.no' in str(row.iloc[0]):
            data_start_row = idx
            break
    
    if data_start_row is None:
        return {}
    
    # Get the header row and data rows
    header_row = df.iloc[data_start_row]
    data_rows = df.iloc[data_start_row + 1:]
    
    # Find scenario columns based on scenario number
    scenario_col_start = None
    if scenario_num == 1:
        scenario_col_start = 2  # Scenario 1 starts at column 2
    elif scenario_num == 2:
        scenario_col_start = 11  # Scenario 2 starts at column 11  
    elif scenario_num == 3:
        scenario_col_start = 20  # Scenario 3 starts at column 20
    
    if scenario_col_start is None:
        return {}
    
    interventions_data = {}
    
    # Process each intervention row
    for idx, row in data_rows.iterrows():
        if pd.isna(row.iloc[0]) or row.iloc[0] == '':
            continue
            
        intervention_name = str(row.iloc[1]).replace('1_', '').replace('2_', '').replace('3_', '')
        
        # Extract parameters for the specified scenario
        interventions_data[intervention_name] = {
            'Volume': to_float(row.iloc[scenario_col_start], 0),
            'Depth': to_float(row.iloc[scenario_col_start + 1], 0),
            'Infiltration_Rate': to_float(row.iloc[scenario_col_start + 2], 0),
            'Cost': to_float(row.iloc[scenario_col_start + 3], 0),
            'Life_Span': to_float(row.iloc[scenario_col_start + 4], 0),
            'Maintenance': to_float(row.iloc[scenario_col_start + 5], 0),
            'Numbers': to_float(row.iloc[scenario_col_start + 6], 0) if scenario_col_start + 6 < len(row) else 0
        }
    
    return interventions_data


# data_readers.py - Function 012B: Gets specific supply intervention parameter value
# Interactions: read_supply_interventions_csv, get_file_paths, shared.utilities.to_float
def get_supply_intervention_value(intervention_name, parameter, scenario_num, master_path):
    """
    Gets specific parameter value for a supply intervention from CSV
    """
    file_paths = get_file_paths("csv", master_path)
    if not file_paths.get("supply_interventions"):
        return 0
    
    interventions_data = read_supply_interventions_csv(file_paths["supply_interventions"], scenario_num)
    
    if intervention_name in interventions_data:
        return interventions_data[intervention_name].get(parameter, 0)
    
    return 0


# data_readers.py - Function 012C: Reads demand intervention data from new tabular CSV format
# Interactions: pandas, os, shared.utilities.to_float
def read_demand_interventions_csv(file_path, scenario_num=1):
    """
    Reads demand interventions from new tabular CSV format
    Returns: dict with intervention data for specified scenario
    """
    if not os.path.exists(file_path):
        return {}
    
    # Read CSV with headers
    df = pd.read_csv(file_path)
    
    # Find the data section (starts after "DEMAND SIDE INTERVENTIONS")
    data_start_row = None
    for idx, row in df.iterrows():
        if 'S.no' in str(row.iloc[0]):
            data_start_row = idx
            break
    
    if data_start_row is None:
        return {}
    
    # Get the header row and data rows
    header_row = df.iloc[data_start_row]
    data_rows = df.iloc[data_start_row + 1:]
    
    # Find scenario columns based on scenario number
    scenario_col_start = None
    if scenario_num == 1:
        scenario_col_start = 2  # Scenario 1 starts at column 2
    elif scenario_num == 2:
        scenario_col_start = 11  # Scenario 2 starts at column 11  
    elif scenario_num == 3:
        scenario_col_start = 20  # Scenario 3 starts at column 20
    
    if scenario_col_start is None:
        return {}
    
    interventions_data = {}
    
    # Process each intervention row
    for idx, row in data_rows.iterrows():
        if pd.isna(row.iloc[0]) or row.iloc[0] == '':
            continue
            
        intervention_name = str(row.iloc[1]).replace('1_', '').replace('2_', '').replace('3_', '')
        
        # Extract parameters for the specified scenario - handle empty/nan values
        interventions_data[intervention_name] = {
            'Crop_Name': str(row.iloc[scenario_col_start]) if not pd.isna(row.iloc[scenario_col_start]) else '',
            'Area': to_float(row.iloc[scenario_col_start + 1], 0) if not pd.isna(row.iloc[scenario_col_start + 1]) else 0,
            'Efficiency': to_float(row.iloc[scenario_col_start + 2], 0) if not pd.isna(row.iloc[scenario_col_start + 2]) else 0,
            'Water_Saved': to_float(row.iloc[scenario_col_start + 3], 0) if not pd.isna(row.iloc[scenario_col_start + 3]) else 0,
            'Cost': to_float(row.iloc[scenario_col_start + 4], 0) if not pd.isna(row.iloc[scenario_col_start + 4]) else 0,
            'Life_Span': to_float(row.iloc[scenario_col_start + 5], 0) if not pd.isna(row.iloc[scenario_col_start + 5]) else 0,
            'Maintenance': to_float(row.iloc[scenario_col_start + 6], 0) if not pd.isna(row.iloc[scenario_col_start + 6]) else 0
        }
    
    return interventions_data


# data_readers.py - Function 012D: Gets specific demand intervention parameter value
# Interactions: read_demand_interventions_csv, get_file_paths, shared.utilities.to_float
def get_demand_intervention_value(intervention_name, parameter, scenario_num, master_path):
    """
    Gets specific parameter value for a demand intervention from CSV
    """
    file_paths = get_file_paths("csv", master_path)
    if not file_paths.get("demand_interventions"):
        return 0
    
    interventions_data = read_demand_interventions_csv(file_paths["demand_interventions"], scenario_num)
    
    if intervention_name in interventions_data:
        return interventions_data[intervention_name].get(parameter, 0)
    
    return 0


# data_readers.py - Function 012E: Reads soil intervention data from new tabular CSV format
# Interactions: pandas, os, shared.utilities.to_float
def read_soil_interventions_csv(file_path, scenario_num=1):
    """
    Reads soil interventions from new tabular CSV format
    Returns: dict with intervention data for specified scenario
    """
    if not os.path.exists(file_path):
        return {}
    
    # Read CSV with headers
    df = pd.read_csv(file_path)
    
    # Find the data section (starts after "SOIL MANAGEMENT INTERVENTIONS")
    data_start_row = None
    for idx, row in df.iterrows():
        if 'S.no' in str(row.iloc[0]):
            data_start_row = idx
            break
    
    if data_start_row is None:
        return {}
    
    # Get the header row and data rows
    header_row = df.iloc[data_start_row]
    data_rows = df.iloc[data_start_row + 1:]
    
    # Find scenario columns based on scenario number
    scenario_col_start = None
    if scenario_num == 1:
        scenario_col_start = 2  # Scenario 1 starts at column 2
    elif scenario_num == 2:
        scenario_col_start = 11  # Scenario 2 starts at column 11  
    elif scenario_num == 3:
        scenario_col_start = 20  # Scenario 3 starts at column 20
    
    if scenario_col_start is None:
        return {}
    
    interventions_data = {}
    
    # Process each intervention row
    for idx, row in data_rows.iterrows():
        if pd.isna(row.iloc[0]) or row.iloc[0] == '':
            continue
            
        intervention_name = str(row.iloc[1]).replace('1_', '').replace('2_', '').replace('3_', '')
        
        # Extract parameters for the specified scenario - handle empty/nan values
        interventions_data[intervention_name] = {
            'Crop_Name': str(row.iloc[scenario_col_start]) if not pd.isna(row.iloc[scenario_col_start]) else '',
            'Area': to_float(row.iloc[scenario_col_start + 1], 0) if not pd.isna(row.iloc[scenario_col_start + 1]) else 0,
            'CN_Reduction': to_float(row.iloc[scenario_col_start + 2], 0) if not pd.isna(row.iloc[scenario_col_start + 2]) else 0,
            'Evaporation_Reduction': to_float(row.iloc[scenario_col_start + 3], 0) if not pd.isna(row.iloc[scenario_col_start + 3]) else 0,
            'Cost': to_float(row.iloc[scenario_col_start + 4], 0) if not pd.isna(row.iloc[scenario_col_start + 4]) else 0,
            'Life_Span': to_float(row.iloc[scenario_col_start + 5], 0) if not pd.isna(row.iloc[scenario_col_start + 5]) else 0,
            'Maintenance': to_float(row.iloc[scenario_col_start + 6], 0) if not pd.isna(row.iloc[scenario_col_start + 6]) else 0
        }
    
    return interventions_data


# data_readers.py - Function 012F: Gets specific soil intervention parameter value
# Interactions: read_soil_interventions_csv, get_file_paths, shared.utilities.to_float
def get_soil_intervention_value(intervention_name, parameter, scenario_num, master_path):
    """
    Gets specific parameter value for a soil intervention from CSV
    """
    file_paths = get_file_paths("csv", master_path)
    if not file_paths.get("soil_interventions"):
        return 0
    
    interventions_data = read_soil_interventions_csv(file_paths["soil_interventions"], scenario_num)
    
    if intervention_name in interventions_data:
        return interventions_data[intervention_name].get(parameter, 0)
    
    return 0


# data_readers.py - Function 013: Handles value retrieval from CSV or manual sources for variables
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


# data_readers.py - Function 014: Returns kei coefficient value based on climate type
# Interactions: None
def get_kei_value(inp_climate):
    # Define kei values for different climates
    kei_values = {
        "semi arid": 1.05,
        "temperate": 1.10,
        "arid": 1.10,
        "tropical": 1.05,
        "sub tropical": 1.10
    }
    # Default to 1.05 if climate type is not found
    return kei_values.get(inp_climate.lower(), 1.05)


# data_readers.py - Function 015: Retrieves general input variables using handle_value_retrieval
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


# data_readers.py - Function 016: Retrieves crop-related variables for Kharif, Rabi, and Summer seasons
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


# data_readers.py - Function 017: Retrieves supply-side intervention parameters and converts to float
# Interactions: shared.utilities.to_float, handle_value_retrieval
def get_supply_side_int_values(inp_source,master_path,var_name, index):
    # Define a dictionary to map variable names to actual supply-side intervention variables
    variables = {
        "Time_Period": None, "Interest_Rate": None, "Farm_Pond_Vol": None, "Farm_Pond_Depth": None,
        "Farm_Pond_Inf_Rate": None, "Farm_Pond_Cost": None, "Farm_Pond_Life_Span": None, "Farm_Pond_Maintenance": None,
        "Farm_Pond_Lined_Vol": None, "Farm_Pond_Lined_Depth": None, "Farm_Pond_Lined_Inf_Rate": None,
        "Farm_Pond_Lined_Cost": None, "Farm_Pond_Lined_Life_Span": None, "Farm_Pond_Lined_Maintenance": None,
        "Check_Dam_Vol": None, "Check_Dam_Depth": None, "Check_Dam_Inf_Rate": None, "Check_Dam_Cost": None,
        "Check_Dam_Life_Span": None, "Check_Dam_Maintenance": None, "Infiltration_Pond_Vol": None,
        "Infiltration_Pond_Depth": None, "Infiltration_Pond_Inf_Rate": None, "Infiltration_Pond_Cost": None,
        "Infiltration_Pond_Life_Span": None, "Infiltration_Pond_Maintenance": None, "Injection_Wells_Vol": None,
        "Injection_Wells_Nos": None, "Injection_Wells_Cost": None, "Injection_Wells_Life_Span": None, "Injection_Wells_Maintenance": None
    }
    return to_float(handle_value_retrieval(inp_source, variables, master_path, var_name, index), 0)


# data_readers.py - Function 018: Retrieves demand-side intervention area values from crop calendar
# Interactions: handle_value_retrieval
def get_demand_side_interv_area_values(inp_source,master_path,var_name, index):
    # Dictionary containing the area variables
    variables = {
        "Kharif_Crop_Drip_Area": None, "Rabi_Crop_Drip_Area": None, "Summer_Crop_Drip_Area": None,
        "Eff_Drip_irrigation": None, "Kharif_Crop_Sprinkler_Area": None, "Rabi_Crop_Sprinkler_Area": None,
        "Summer_Crop_Sprinkler_Area": None, "Eff_Sprinkler_irrigation": None
    }
    return handle_value_retrieval(inp_source, variables, master_path, var_name, index, is_area=True)


# data_readers.py - Function 019: Retrieves demand-side intervention cost and lifespan parameters
# Interactions: shared.utilities.to_float, handle_value_retrieval
def get_demand_side_interv_values(inp_source,master_path,var_name, index):
    # Dictionary containing the cost and lifespan variables
    variables = {
        "Drip_irrigation_cost": None, "Drip_irrigation_lifespan": None, "Drip_irrigation_maintenance": None,
        "Sprinkler_irrigation_cost": None, "Sprinkler_irrigation_lifespan": None, "Sprinkler_irrigation_maintenance": None
    }
    return to_float(handle_value_retrieval(inp_source, variables, master_path, var_name, index), 0)


# data_readers.py - Function 020: Retrieves soil moisture intervention area values from crop calendar
# Interactions: handle_value_retrieval
def get_soil_moisture_interv_area_values(inp_source,master_path,var_name, index):
    # Dictionary containing the soil moisture intervention area variables
    variables = {
        "Kharif_Crop_Cover_Area": None, "Rabi_Crop_Cover_Area": None, "Summer_Crop_Cover_Area": None,
        "Kharif_Crop_Mulching_Area": None, "Rabi_Crop_Mulching_Area": None, "Summer_Crop_Mulching_Area": None,
        "Kharif_Crop_Bunds_Area": None, "Rabi_Crop_Bunds_Area": None, "Summer_Crop_Bunds_Area": None,
        "Kharif_Crop_Tillage_Area": None, "Rabi_Crop_Tillage_Area": None, "Summer_Crop_Tillage_Area": None,
        "Kharif_Crop_BBF_Area": None, "Rabi_Crop_BBF_Area": None, "Summer_Crop_BBF_Area": None,
        "Kharif_Crop_Tank_Area": None, "Rabi_Crop_Tank_Area": None, "Summer_Crop_Tank_Area": None
    }
    return handle_value_retrieval(inp_source, variables, master_path, var_name, index, is_area=True)


# data_readers.py - Function 021: Retrieves soil moisture intervention parameters including CN reduction values
# Interactions: shared.utilities.to_float, handle_value_retrieval
def get_soil_moisture_interv_values(inp_source,master_path,var_name, index):
    # Dictionary containing the soil moisture intervention variables
    variables = {
        "Red_CN_Cover_Crops": None, "Red_CN_Mulching": None, "Red_CN_Bund": None, "Red_CN_Tillage": None, "Red_CN_BBF": None,
        "Cover_Crops_cost": None, "Cover_Crops_lifespan": None, "Cover_Crops_maintenance": None,
        "Mulching_cost": None, "Mulching_lifespan": None, "Mulching_maintenance": None,
        "Bund_cost": None, "Bund_lifespan": None, "Bund_maintenance": None,
        "Tillage_cost": None, "Tillage_lifespan": None, "Tillage_maintenance": None,
        "BBF_cost": None, "BBF_lifespan": None, "BBF_maintenance": None,
        "Farm_Pond_Tank_cost": None, "Farm_Pond_Tank_lifespan": None, "Farm_Pond_Tank_maintenance": None
    }
    return to_float(handle_value_retrieval(inp_source, variables, master_path, var_name, index), 0)


# data_readers.py - Function 022: Retrieves and caches season-wise crop data including areas and sowing details
# Interactions: orchestrator.input_collector.collect_inp_variables
def get_season_data(inp_source,master_path):
    print("FUNCTION 8: get_season_data() - Getting season data for crops [CACHED]")
    # Import here to avoid circular import
    from orchestrator.input_collector import collect_inp_variables
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


# data_readers.py - Function 023: Reads irrigation data and merges with monthly dataframe
# Interactions: pandas
def irrigation_data_input(df_ir_path, df_mm):
    df_ir = pd.read_csv(df_ir_path)
    df_ir["Date"] = df_mm["Date"]
    columns = ["Date"] + [col for col in df_ir.columns if col != "Date"]
    df_ir = df_ir[columns]
    return df_ir

