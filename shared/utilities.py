"""
Utility functions for drought proofing tool

This module contains common utility functions:
- Safe mathematical operations
- Data conversion utilities

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Provides common utility functions for safe mathematical operations, data conversions, and data processing
# ========================================

import numpy as np
import pandas as pd
import calendar


# utilities.py - Function 001: Resamples time series data from one dataframe and merges with another from CSV
# Interactions: pandas
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
        print(f"Error in resample function: {e}")
        return None


# utilities.py - Function 002: Converts water depth in millimeters to volume in cubic meters
# Interactions: pandas, numpy
def mm_to_m3(x, y):
    x = pd.to_numeric(x, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")
    z = x * 10000 * (y / 1000)
    z = np.where(np.isnan(z), 0, z)
    return z


# utilities.py - Function 003: Converts water volume in cubic meters to depth in millimeters
# Interactions: pandas, numpy
def m3_to_mm(x, y):
    x = pd.to_numeric(x, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")
    z = (y * 1000) / (x * 10000)
    z = np.where(np.isnan(z), 0, z)
    return z


# utilities.py - Function 004: Calculates percentage value from fraction and total
# Interactions: pandas
def get_percentage(x, y):
    x = pd.to_numeric(x, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")
    z = (x * y) / 100
    return z


# utilities.py - Function 005: Performs subtraction with error handling for invalid inputs
# Interactions: pandas
def safe_subtract(x, y):
    x = pd.to_numeric(x, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")
    try:
        return x - y
    except (TypeError, ValueError):
        return 0


# utilities.py - Function 006: Optimizes dataframe memory by converting to smaller data types
# Interactions: pandas
def convert_dtypes(df):
    # Convert float64 to float32
    float_cols = df.select_dtypes(include=["float64"]).columns
    df[float_cols] = df[float_cols].astype("float32")
    # Convert int64 to int32
    int_cols = df.select_dtypes(include=["int64"]).columns
    df[int_cols] = df[int_cols].astype("int32")
    return df


# utilities.py - Function 007: Safely converts area list values to float with zero fallback
# Interactions: None
def safe_float_conversion(area_list):
    return [float(area) if area else 0.0 for area in area_list]


# utilities.py - Function 008: Safely converts crop list preserving None values
# Interactions: None
def safe_crop_conversion(crop_list):
    return [crop if crop else None for crop in crop_list]


# utilities.py - Function 009: Calculates number of days in a specific month and year
# Interactions: calendar
def calc_days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


# utilities.py - Function 010: Calculates total area from land use and land cover components
# Interactions: None
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


# utilities.py - Function 011: Converts seasonal data dictionary to list of dataframes with error handling
# Interactions: process_season_data, pandas
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


# utilities.py - Function 012: Converts specified dataframe columns to numeric with error handling
# Interactions: pandas
def convert_columns_to_numeric(df, columns):
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# utilities.py - Function 013: Converts various input types to float with fallback to default value
# Interactions: None
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


# utilities.py - Function 014: Calculates land use fraction from area and total area
# Interactions: to_float
def calc_lulc(x, total_area):
    # Convert x and total_area to float if they are lists
    x = to_float(x, 0)
    total_area = to_float(total_area, 0)
    # Calculate the value
    y = x / total_area if total_area != 0 else 0  # Avoid division by zero
    return y


# utilities.py - Function 015: Processes seasonal crop data into structured dictionary format
# Interactions: safe_crop_conversion, safe_float_conversion
def process_season_data(season, crops, sowing_months, sowing_weeks, irrigated_areas, rainfed_areas):
    # Get the maximum length among all lists
    max_length = max(len(crops), len(sowing_months), len(sowing_weeks), len(irrigated_areas), len(rainfed_areas))
    # Pad lists to the maximum length
    crops = safe_crop_conversion(crops + [None] * (max_length - len(crops)))
    sowing_months = sowing_months + [None] * (max_length - len(sowing_months))  # Keep as-is (no float conversion)
    sowing_weeks = sowing_weeks + [None] * (max_length - len(sowing_weeks))      # Keep as-is (no float conversion)
    irrigated_areas = safe_float_conversion(irrigated_areas + [0] * (max_length - len(irrigated_areas)))
    rainfed_areas = safe_float_conversion(rainfed_areas + [0] * (max_length - len(rainfed_areas)))
    # Create the season data dictionary
    season_data = {
        "Season": [season] * max_length,
        "Crop": crops,
        "Sowing_Month": sowing_months,
        "Sowing_Week": sowing_weeks,
        "Irrigated_Area": irrigated_areas,
        "Rainfed_Area": rainfed_areas
    }
    return season_data


# utilities.py - Function 016: Performs safe division with zero handling
# Interactions: numpy
def safe_divide(numerator, denominator):
    return np.where(denominator != 0, numerator / denominator, 0)


# utilities.py - Function 017: Calculates monthly remaining growth days and updates monthly dataframe
# Interactions: pandas
def calc_monthly_remaining_growth_days(df, crops, df_mm, df_cc):
    print("FUNCTION 20: calc_monthly_remaining_growth_days() - Calculating monthly remaining growth days")
    rg_days_cols = [col for col in df.columns if col.startswith("RG_days_")]
    df_filtered = df[rg_days_cols + ["Date"]]

    # Resample and count positive values for RG_days_ columns
    monthly_counts = df_filtered.set_index("Date").resample("M").apply(lambda x: (x > 0).sum())

    # Reset index of monthly_counts to align with df_mm
    monthly_counts_reset = monthly_counts.reset_index(drop=True)

    # Update df_mm directly with the new monthly counts
    df_mm_updated = df_mm.join(monthly_counts_reset, how="left")

    for crop in crops:
        crop_col = f"RG_days_{crop}"
        irr_col = f"Irr_Area_{crop}"
        rainfed_col = f"Rainfed_Area_{crop}"

        if crop_col in df_mm_updated.columns:
            df_mm_updated[irr_col] = df_mm_updated.apply(
                lambda row: df_cc.loc[crop, "Irr_Area"] if row[crop_col] > 0 else 0,
                axis=1
            ).astype(float)

            df_mm_updated[rainfed_col] = df_mm_updated.apply(
                lambda row: df_cc.loc[crop, "Rainfed_Area"] if row[crop_col] > 0 else 0,
                axis=1
            ).astype(float)
    return df_mm_updated