"""
Data aggregation and yearly processing for drought proofing tool outputs

This module contains functions for data aggregation and yearly processing:
- Data resampling and aggregation
- Weighted average calculations
- Year data processing for calendar and crop years

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Aggregates and processes output data including yearly resampling, weighted averages, and crop/calendar year calculations
# ========================================

import pandas as pd
import numpy as np
from . import water_metrics
from . import yield_calculations
from . import drought_metrics


# output_aggregator.py - Function 001: Resamples monthly data to yearly aggregates
# Interactions: pandas
def get_resample_yr_optimized(df_mm, crops):
    print("FUNCTION 51: get_resample_yr_optimized() - Resampling yearly data")
    # List of columns to resample
    cols_to_resample = [f"ETci_{crop}" for crop in crops] + \
                       [f"Irr_CWR_met_{crop}" for crop in crops] + \
                       [f"Rainfed_CWR_met_{crop}" for crop in crops] + \
                       [f"AE_crop_{crop}" for crop in crops] + \
                       [f"AE_soil_{crop}" for crop in crops] + \
                       [f"IWR_{crop}" for crop in crops] + \
                       ["ET_Biological"]
    # Resample the specified columns
    df_yr = df_mm[["Date"] + cols_to_resample].set_index("Date").resample("Y").sum().reset_index()
    return df_yr


# output_aggregator.py - Function 002: Calculates weighted averages for yield and water metrics
# Interactions: pandas
def calculate_weighted_averages(df_cc, df_yr, all_crops, yield_columns, other_columns):
    print("FUNCTION 54: calculate_weighted_averages() - Calculating weighted averages")
    # Initialize drought proofing components
    total_weighted_rainfed_yield = pd.Series(0, index=df_yr.index)
    total_weighted_irrigated_yield = pd.Series(0, index=df_yr.index)
    total_rainfed_area = df_cc["Rainfed_Area"].sum()
    total_irrigated_area = df_cc["Irr_Area"].sum()

    # Calculate weighted averages for yield-related metrics
    for output_column, (yield_template, area_column) in yield_columns.items():
        total_weighted_yield = pd.Series(0, index=df_yr.index)
        total_area = df_cc[area_column].sum()

        for crop in all_crops:
            yield_col = yield_template.format(crop=crop)
            if yield_col in df_yr.columns:
                area = df_cc.at[crop, area_column]
                total_weighted_yield += df_yr[yield_col] * area
                if area_column == "Rainfed_Area":
                    total_weighted_rainfed_yield += df_yr[yield_col] * area
                elif area_column == "Irr_Area":
                    total_weighted_irrigated_yield += df_yr[yield_col] * area

        df_yr[output_column] = ((total_weighted_yield / total_area) * 100) if total_area > 0 else 0

    # Calculate weighted averages for other metrics (e.g., CWR, CWA)
    for output_column, col_template in other_columns.items():
        df_yr[output_column] = pd.Series(0, index=df_yr.index)
        for crop in all_crops:
            metric_col = col_template.format(crop=crop)
            if metric_col in df_yr.columns:
                area = df_cc.at[crop, "Area"]
                df_yr[output_column] += df_yr[metric_col] * area

        total_area = df_cc["Area"].sum()
        df_yr[output_column] /= total_area if total_area > 0 else 1

    # # Calculate the "Drought Proofing" metric
    df_yr["Drought Proofing"] = (total_weighted_rainfed_yield + total_weighted_irrigated_yield) / (
                total_rainfed_area + total_irrigated_area)
    return df_yr


# output_aggregator.py - Function 003: Processes year data based on calendar or crop year
# Interactions: outputs.water_metrics, outputs.yield_calculations, outputs.drought_metrics
def process_year_data(df_yr, df_crop_yr, all_crops, year_type):
    print("FUNCTION 69: process_year_data() - Processing year data")
    year_type = year_type.strip().lower()

    if year_type == "calendar":
        # Run the functions if it's a calendar year
        df_cwr = water_metrics.get_cwr_mm(df_yr, all_crops)
        df_cwr_met = water_metrics.get_cwr_met(df_yr, all_crops)
        df_yield = yield_calculations.get_yield_per(df_yr, all_crops)
        df_drought = drought_metrics.get_drought_proofness(df_yr)

    elif year_type == "crop":
        # Run the crop year functions
        df_cwr = water_metrics.get_cwr_mm_cyr(df_crop_yr, all_crops)
        df_cwr_met = water_metrics.get_cwr_met_cyr(df_crop_yr, all_crops)
        df_yield = yield_calculations.get_yield_per_cyr(df_crop_yr, all_crops)
        df_drought = drought_metrics.get_drought_proofness_cyr(df_crop_yr)

    else:
        raise ValueError("Invalid year_type. Please choose either 'calendar' or 'crop'.")
    return df_cwr, df_cwr_met, df_yield, df_drought


# output_aggregator.py - Function 004: Processes water year data for crop or calendar year
# Interactions: get_sowing_month, pandas
def process_water_year_data(df_mm, df_cp, crops, year_type="crop"):
    # Prepare df_wb_mm with renamed columns - keep both water balance ET and biological ET
    df_wb_mm = df_mm[["Date", "Rain", "Final_Runoff", "Final_Recharge", "Final_ET", "ET_Biological"]].copy()
    df_wb_mm.columns = ["Date", "Rain(mm)", "Runoff(mm)", "Recharge(mm)", "ET_WaterBalance(mm)", "ET_Biological(mm)"]
    # Get the result month from the provided function
    result_month = get_sowing_month(df_cp)
    if result_month is None or result_month == "":
        result_month = "Jun"  # Default to June if no month found
    result_month_num = pd.to_datetime(f"{result_month} 1, 2000").month

    if year_type.strip().lower() == "calendar":
        water_year = df_mm["Date"].dt.year
    else:
        water_year = df_mm["Date"].dt.year.where(df_mm["Date"].dt.month >= result_month_num,
                                                 df_mm["Date"].dt.year - 1)

    df_mm = df_mm.assign(water_year=water_year)
    df_wb_mm = df_wb_mm.assign(water_year=water_year)

    # Create the column list to resample
    col_to_resample = [f"ETci_{crop}" for crop in crops] + \
                      [f"IWR_{crop}" for crop in crops] + \
                      [f"Irr_CWR_met_{crop}" for crop in crops] + \
                      [f"Rainfed_CWR_met_{crop}" for crop in crops]
    # Group by water year and sum for crops
    df_crop_yr = df_mm.groupby("water_year")[col_to_resample].sum().reset_index()
    # Group by water year and sum for water balance data
    df_wb_yr = df_wb_mm.groupby("water_year", as_index=False).agg({
        "Rain(mm)": "sum",
        "Runoff(mm)": "sum",
        "Recharge(mm)": "sum",
        "ET_WaterBalance(mm)": "sum",
        "ET_Biological(mm)": "sum"
    })
    return df_crop_yr, df_wb_yr, df_wb_mm


# output_aggregator.py - Function 005: Calculates weighted averages for water year metrics
# Interactions: pandas
def calc_weighted_avg(df_cc, df_crop_yr, all_crops, yield_columns, other_columns):
    # Initialize drought proofing components
    total_weighted_rainfed_yield = pd.Series(0, index=df_crop_yr.index)
    total_weighted_irrigated_yield = pd.Series(0, index=df_crop_yr.index)
    total_rainfed_area = df_cc["Rainfed_Area"].sum()
    total_irrigated_area = df_cc["Irr_Area"].sum()
    # Calculate weighted averages for yield-related metrics
    for output_column, (yield_template, area_column) in yield_columns.items():
        total_weighted_yield = pd.Series(0, index=df_crop_yr.index)
        total_area = df_cc[area_column].sum()

        for crop in all_crops:
            yield_col = yield_template.format(crop=crop)
            if yield_col in df_crop_yr.columns:
                area = df_cc.at[crop, area_column]
                total_weighted_yield += df_crop_yr[yield_col] * area
                if area_column == "Rainfed_Area":
                    total_weighted_rainfed_yield += df_crop_yr[yield_col] * area
                elif area_column == "Irr_Area":
                    total_weighted_irrigated_yield += df_crop_yr[yield_col] * area

        df_crop_yr[output_column] = (total_weighted_yield / total_area) if total_area > 0 else 0

    # Calculate weighted averages for other metrics (e.g., CWR, CWA)
    for output_column, col_template in other_columns.items():
        df_crop_yr[output_column] = pd.Series(0, index=df_crop_yr.index)
        for crop in all_crops:
            metric_col = col_template.format(crop=crop)
            if metric_col in df_crop_yr.columns:
                area = df_cc.at[crop, "Area"]
                df_crop_yr[output_column] += df_crop_yr[metric_col] * area

        total_area = df_cc["Area"].sum()
        df_crop_yr[output_column] /= total_area if total_area > 0 else 1

    # # Calculate the "Drought Proofing" metric
    df_crop_yr["Drought Proofing"] = (total_weighted_rainfed_yield + total_weighted_irrigated_yield) / (
                total_rainfed_area + total_irrigated_area)
    return df_crop_yr


# output_aggregator.py - Function 006: Gets earliest sowing month from crop plan
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
    return None