# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:51:05 2024

@author: Dr. Jagadeesh, Consultant, IWMI
"""
import calendar

import numpy as np
import pandas as pd

from user_input import collect_inp_variables
from user_input import collect_int_variables
from user_input import to_float

# List of attribute names to be combined
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

# Define yield-related metrics and their corresponding area columns
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
    "Combined_CWA_Avg": "Combined CWA_{crop}(cu.m/ha)"
}


# crop_pattern.py - Function 1: Resamples time series data from one dataframe and merges with another from CSV
def resample(df1, df2_path, date_col, resample_col, freq="M", agg_func="sum"):
    try:
        # Read the CSV file into df2 with optimized settings
        df2 = pd.read_csv(df2_path, engine='c', low_memory=False)

        # Ensure the date_col is in datetime format
        df1[date_col] = pd.to_datetime(df1[date_col])

        # Perform the resampling
        if isinstance(agg_func, str):
            df_resamp = df1.resample(freq, on=date_col)[resample_col].agg(agg_func)
        else:
            df_resamp = df1.resample(freq, on=date_col)[resample_col].apply(agg_func)

        df2["Date"] = df_resamp.index

        # Merge the resampled data into df2
        df2 = df2.merge(df_resamp, left_on="Date", right_on=date_col, how="left")

        # Reorder the columns so that "Date" is the first column
        cols = ["Date"] + [col for col in df2.columns if col != "Date"]
        df2 = df2[cols]

        return df2

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# crop_pattern.py - Function 2: Converts water depth in millimeters to volume in cubic meters
def mm_to_m3(x, y):
    x = pd.to_numeric(x, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")
    z = x * 10000 * (y / 1000)
    z = np.where(np.isnan(z), 0, z)
    return z


# crop_pattern.py - Function 3: Converts water volume in cubic meters to depth in millimeters
def m3_to_mm(x, y):
    x = pd.to_numeric(x, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")
    z = (y * 1000) / (x * 10000)
    z = np.where(np.isnan(z), 0, z)
    return z


# crop_pattern.py - Function 4: Calculates percentage value from fraction and total
def get_percentage(x, y):
    x = pd.to_numeric(x, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")
    z = (x * y) / 100
    return z

# crop_pattern.py - Function 5: Performs division with zero-denominator protection
def safe_divide(numerator, denominator):
    return np.where(denominator != 0, numerator / denominator, 0)


# crop_pattern.py - Function 6: Performs subtraction with error handling for invalid inputs
def safe_subtract(x, y):
    x = pd.to_numeric(x, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")
    try:
        return x - y
    except (TypeError, ValueError):
        return 0


# crop_pattern.py - Function 7: Optimizes dataframe memory by converting to smaller data types
def convert_dtypes(df):
    # Convert float64 to float32
    float_cols = df.select_dtypes(include=["float64"]).columns
    df[float_cols] = df[float_cols].astype("float32")
    # Convert int64 to int32
    int_cols = df.select_dtypes(include=["int64"]).columns
    df[int_cols] = df[int_cols].astype("int32")
    return df


# crop_pattern.py - Function 8: Reads and formats crop database from CSV file
def get_crop_data(crop_db):
    crop_df = pd.read_csv(crop_db, header=None)
    crop_df = crop_df.drop(index=0)
    crop_df.columns = crop_df.iloc[0]
    crop_df = crop_df.drop(index=1).reset_index(drop=True)
    return crop_df


# crop_pattern.py - Function 9: Retrieves solar radiation data for specific latitude
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


# Define functions
# crop_pattern.py - Function 10: Safely converts area list values to float with zero fallback
def safe_float_conversion(area_list):
    return [float(area) if area else 0.0 for area in area_list]


# crop_pattern.py - Function 11: Safely converts crop list preserving None values
def safe_crop_conversion(crop_list):
    return [crop if crop else None for crop in crop_list]


# crop_pattern.py - Function 12: Processes seasonal crop data into structured dictionary format
def process_season_data(season_name, crops, sowing_month, sowing_week, irr_area, rainfed_area):
    return {
        "Season": season_name,
        "Crop": safe_crop_conversion(crops),
        "Sowing_Month": sowing_month,
        "Sowing_Week": sowing_week,
        "Irrigated_Area": safe_float_conversion(irr_area),
        "Rainfed_Area": safe_float_conversion(rainfed_area),
    }


# crop_pattern.py - Function 13: Assigns plot numbers to crops and calculates plot statistics
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


# crop_pattern.py - Function 14: Reads precipitation data and calculates 5-day rolling rainfall
def get_pcp_value(daily_data):
    df_dd = pd.read_csv(daily_data)
    df_dd.columns = ["Date", "Pi"]
    df_dd["Date"] = pd.to_datetime(df_dd["Date"], format="%m/%d/%Y")
    df_dd["last_5_days_Rain"] = df_dd["Pi"].rolling(window=5, min_periods=1).sum()
    return df_dd


# crop_pattern.py - Function 15: Calculates number of days in a specific month and year
def calc_days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


# crop_pattern.py - Function 16: Calculates monthly reference evapotranspiration using Hargreaves method
def calc_etom(df_mm,file_paths,inp_source,master_path):
    print("FUNCTION 27: calc_etom() - Calculating reference evapotranspiration")
    # df_rd = get_radiation_db(drought_proofing_tool.radiation_db, user_input.latitude)
    
    radiation_db = file_paths["radiation_db"]
    df_rd = get_radiation_db(radiation_db, collect_inp_variables(inp_source,master_path)["latitude"])
    # Initialize the ETom column with zeros
    df_mm["ETom"] = 0.0

    # Vectorized ETom calculation - much faster than iterrows
    df_mm["month_index"] = df_mm.index % 12
    df_mm["radiation"] = df_mm["month_index"].map(df_rd["Radiation"])
    df_mm["ETom"] = (0.0023 * df_mm["radiation"] * np.sqrt(df_mm["Tmax"] - df_mm["Tmin"]) *
                     (df_mm["Tmean"] + 17.8) * df_mm["Days"])
    df_mm.drop(["month_index", "radiation"], axis=1, inplace=True)
    return df_mm


# crop_pattern.py - Function 17: Distributes monthly reference ET to daily values
def calculate_daily_etoi(df_mm, df_dd):
    print("FUNCTION 28: calculate_daily_etoi() - Calculating daily ET reference")
    # Vectorized approach - much faster than nested loops
    daily_etoi = df_mm["ETom"] / df_mm["Days"]
    df_dd["EToi"] = daily_etoi.repeat(df_mm["Days"]).values
    return df_dd


# crop_pattern.py - Function 18: Filters crop pattern data to include only valid non-empty crops
def select_valid_crops(df_cp):
    # Filter out rows with empty or null crops
    valid_crops_df = df_cp[df_cp["Crop"].notna() & (df_cp["Crop"] != "")]
    # Select relevant columns
    valid_crops_df = valid_crops_df[["Season", "Crop", "Plot"]].drop_duplicates()
    return valid_crops_df


# crop_pattern.py - Function 19: Combines seasonal attributes from input and intervention variables
def combine_attributes(attribute_name,inp_source,master_path):
    inp_var = collect_inp_variables(inp_source,master_path)  # Dictionary from your collect_inp_variables function
    int_var = collect_int_variables(inp_source,master_path)   # Dictionary from your collect_int_variables function
    # Access the lists from inp_var and int_var dictionaries
    kharif = inp_var.get(f"Kharif_{attribute_name}", []) + int_var.get(f"Kharif_{attribute_name}", [])
    rabi = inp_var.get(f"Rabi_{attribute_name}", []) + int_var.get(f"Rabi_{attribute_name}", [])
    summer = inp_var.get(f"Summer_{attribute_name}", []) + int_var.get(f"Summer_{attribute_name}", [])
    
    return kharif + rabi + summer


# crop_pattern.py - Function 20: Calculates total area from land use and land cover components
def calculate_total_area(inp_lulc_val_list):
    # Initialize the total area variable
    total_area_val = 0
    # List of areas for debugging
    areas = {
        "net_crop_sown_area": inp_lulc_val_list[0],
        "fallow": inp_lulc_val_list[1],
        "builtup": inp_lulc_val_list[2],
        "water_bodies": inp_lulc_val_list[3],
        "pasture": inp_lulc_val_list[4],
        "forest": inp_lulc_val_list[5]
    }

    # Validate input and calculate total area
    for area_name, area_value in areas.items():
        try:
            # Check if area_value is a list and take the first element if so
            if isinstance(area_value, list):
                area_value = area_value[0]  # Take the first element

            # Convert to float if it's a string or number
            area_value = float(area_value)
            total_area_val += area_value
        except (ValueError, TypeError):
            print(f"Warning: {area_name} should be a number, but got: {area_value}")
    return total_area_val


# def convert_season_data_to_df(var_season_data):
#     all_data = []
#     for season, details in var_season_data.items():
#         processed_data = process_season_data(
#             season,
#             details["Crops"],
#             details["Sowing_Month"],
#             details["Sowing_Week"],
#             details["Irrigated_Area"],
#             details["Rainfed_Area"]
#         )
#         all_data.append(pd.DataFrame(processed_data))
#     return all_data

# crop_pattern.py - Function 21: Converts seasonal data dictionary to list of dataframes with error handling
def convert_season_data_to_df(var_season_data):
    print("FUNCTION 30: convert_season_data_to_df() - Converting season data to dataframe")
    all_data = []
    for season, details in var_season_data.items():
        try:
            processed_data = process_season_data(
                season,
                details["Crops"],
                details["Sowing_Month"],
                details["Sowing_Week"],
                details["Irrigated_Area"],
                details["Rainfed_Area"]
            )
            all_data.append(pd.DataFrame(processed_data))
        except ValueError as ve:
            print(f"ValueError: All arrays must be of the same length for season '{season}'. Error: {ve}")
            continue  # Skip this iteration and move on to the next season
        
        except Exception as e:
            print(f"Unexpected error for season '{season}': {e}")
            continue
    return all_data

# crop_pattern.py - Function 22: Combines and normalizes all crop attributes to consistent lengths
def combine_and_normalize_attributes(var_attribute_names,inp_source,master_path):
    print("FUNCTION 31: combine_and_normalize_attributes() - Combining and normalizing attributes")
    all_attributes = {
        name.replace("Crops_", "").replace("Crop_", "").replace("Crops", "All Crops"):
            combine_attributes(name,inp_source,master_path)
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


# crop_pattern.py - Function 23: Applies evaporation reduction factors based on conservation practices
def apply_eva_red(row, default_val_eva_red,inp_source,master_path):
    int_var = collect_int_variables(inp_source,master_path)
    # Convert "Cover_Crops_Eva_Red" based on "Cover_Area"
    row["Cover_Eva_Red"] = ((
        to_float(int_var["Cover_Crops_Eva_Red"], default_val_eva_red["Cover_Crops_Eva_Red"])
        if to_float(row["Cover_Area"]) > 0
        else default_val_eva_red["Cover_Crops_Eva_Red"]
    ))/100
    row["Mulching_Eva_Red"] = ((
        to_float(int_var["Mulching_Eva_Red"], default_val_eva_red["Mulching_Eva_Red"])
        if to_float(row["Mulching_Area"]) > 0
        else default_val_eva_red["Mulching_Eva_Red"]
    ))/100
    row["Tank_Eva_Red"] = ((
        to_float(int_var["Tank_Eva_Red"], default_val_eva_red["Tank_Eva_Red"])
        if to_float(row["Tank_Area"]) > 0
        else default_val_eva_red["Tank_Eva_Red"]
    ))/100
    row["Tillage_Eva_Red"] = ((
        to_float(int_var["Tillage_Eva_Red"], default_val_eva_red["Tillage_Eva_Red"])
        if to_float(row["Tillage_Area"]) > 0
        else default_val_eva_red["Tillage_Eva_Red"]
    ))/100
    return row


# crop_pattern.py - Function 24: Applies irrigation efficiency values based on intervention areas
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


# Function to calculate the average evaporation reduction
# crop_pattern.py - Function 25: Calculates average soil evaporation reduction from conservation practices
def calc_red_soil_evap(row):
    # Calculate the mean of the specified evaporation reduction columns
    row["red_soil_evap"] = row[["Tillage_Eva_Red", "Tank_Eva_Red", "Mulching_Eva_Red", "Cover_Eva_Red"]].mean()
    return row


# crop_pattern.py - Function 26: Retrieves yield response factor and economic data for crops
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


# crop_pattern.py - Function 27: Returns irrigation return flow coefficients based on crop type
def get_return_flow(crop):
    #From GEC Report 2015 Return Flow for Paddy and Non paddy field
    if crop == "Rice":
        gw_rf = 0.325
        sw_rf = 0.375
    else:
        gw_rf = 0.15
        sw_rf = 0.20
    return gw_rf, sw_rf


# crop_pattern.py - Function 28: Calculates weighted return flow based on water source dependencies
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


# crop_pattern.py - Function 29: Converts specified dataframe columns to numeric with error handling
def convert_columns_to_numeric(df, columns):
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df
