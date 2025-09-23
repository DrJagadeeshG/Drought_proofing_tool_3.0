"""
Crop coefficient calculations for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates crop coefficients (Kc) for different growth stages including initial, development, mid-season, and late-season stages
# ========================================

import math
import pandas as pd
import numpy as np


# crop_coefficients.py - Function 001: Calculates initial crop coefficient (Kc) for initial growth stage
# Interactions: pandas, numpy, math
def calculate_kc_ini(df, crop_df, sowing_week, sowing_month, stage_column, kc_column, selected_crop):
    sowing_month_num = pd.to_datetime(f"{sowing_month} 1, 2000").month
    def local_find_start_date(year):
        local_start_date = pd.to_datetime(f"{year}-{sowing_month_num}-01")
        local_start_date += pd.Timedelta(days=(int(sowing_week) - 1) * 7)  # Convert sowing_week to int
        return local_start_date

    df["start_date"] = df["Date"].dt.year.apply(local_find_start_date)

    crop_row = crop_df[crop_df["Crops"] == selected_crop]
    if crop_row.empty:
        raise ValueError(f"Selected crop {selected_crop} not found in crop_df")

    l_days_str = crop_row[stage_column].values[0]
    kc_value = float(crop_row[kc_column].values[0])

    try:
        l_ini_days_float = float(l_days_str)
        # Round up if decimal part exceeds 0.5
        if (l_ini_days_float % 1) > 0.5:
            l_ini_days = math.ceil(l_ini_days_float)
        else:
            l_ini_days = int(l_ini_days_float)

    except ValueError:
        raise ValueError(f"Invalid {stage_column} value: {l_days_str}")

    kc_col_name = f"{kc_column}_{selected_crop}"
    df[kc_col_name] = np.float32(0)

    # Vectorized approach - much faster than iterrows
    for start_date in df["start_date"].unique():
        end_date = start_date + pd.Timedelta(days=l_ini_days)
        mask = (df["Date"] >= start_date) & (df["Date"] < end_date)
        df.loc[mask, kc_col_name] = np.float32(kc_value)
    return df, l_ini_days


# crop_coefficients.py - Function 002: Calculates crop coefficient (Kc) for development growth stage
# Interactions: pandas, numpy, math
def calculate_kc_dev(df, crop_df, stage_column, kc_column, selected_crop, l_ini_days):
    crop_row = crop_df[crop_df["Crops"] == selected_crop]
    if crop_row.empty:
        raise ValueError(f"Selected crop {selected_crop} not found in crop_df")

    l_days_str = crop_row[stage_column].values[0]
    kc_value = float(crop_row[kc_column].values[0])

    try:
        l_dev_days_float = float(l_days_str)
        # Round up if decimal part exceeds 0.5
        if (l_dev_days_float % 1) > 0.5:
            l_dev_days = math.ceil(l_dev_days_float)
        else:
            l_dev_days = int(l_dev_days_float)
    except ValueError:
        raise ValueError(f"Invalid {stage_column} value: {l_days_str}")

    kc_col_name = f"{kc_column}_{selected_crop}"
    df[kc_col_name] = np.float32(0)

    # Vectorized approach
    for start_date in df["start_date"].unique():
        dev_start_date = start_date + pd.Timedelta(days=l_ini_days)
        dev_end_date = dev_start_date + pd.Timedelta(days=l_dev_days)
        mask = (df["Date"] >= dev_start_date) & (df["Date"] < dev_end_date)
        df.loc[mask, kc_col_name] = np.float32(kc_value)
    return df, l_dev_days


# crop_coefficients.py - Function 003: Calculates crop coefficient (Kc) for mid-season growth stage
# Interactions: pandas, numpy, math
def calculate_kc_mid(df, crop_df, stage_column, kc_column, selected_crop, l_ini_days, l_dev_days):
    crop_row = crop_df[crop_df["Crops"] == selected_crop]
    if crop_row.empty:
        raise ValueError(f"Selected crop {selected_crop} not found in crop_df")

    l_days_str = crop_row[stage_column].values[0]
    kc_value = float(crop_row[kc_column].values[0])

    try:
        l_mid_days_float = float(l_days_str)
        # Round up if decimal part exceeds 0.5
        if (l_mid_days_float % 1) > 0.5:
            l_mid_days = math.ceil(l_mid_days_float)
        else:
            l_mid_days = int(l_mid_days_float)

    except ValueError:
        raise ValueError(f"Invalid {stage_column} value: {l_days_str}")

    kc_col_name = f"{kc_column}_{selected_crop}"
    df[kc_col_name] = np.float32(0)

    # Vectorized approach - much faster than iterrows
    for start_date in df["start_date"].unique():
        adj_start_date = start_date + pd.Timedelta(days=l_ini_days + l_dev_days)
        end_date = adj_start_date + pd.Timedelta(days=l_mid_days)
        mask = (df["Date"] >= adj_start_date) & (df["Date"] < end_date)
        df.loc[mask, kc_col_name] = np.float32(kc_value)
    return df, l_mid_days


# crop_coefficients.py - Function 004: Calculates crop coefficient (Kc) for late season growth stage
# Interactions: pandas, numpy, math
def calculate_kc_late(df, crop_df, stage_column, kc_column, selected_crop, l_ini_days, l_dev_days, l_mid_days):
    crop_row = crop_df[crop_df["Crops"] == selected_crop]
    if crop_row.empty:
        raise ValueError(f"Selected crop {selected_crop} not found in crop_df")

    l_days_str = crop_row[stage_column].values[0]
    kc_value = float(crop_row[kc_column].values[0])

    try:
        l_late_days_float = float(l_days_str)
        # Round up if decimal part exceeds 0.5
        if (l_late_days_float % 1) > 0.5:
            l_late_days = math.ceil(l_late_days_float)
        else:
            l_late_days = int(l_late_days_float)

    except ValueError:
        raise ValueError(f"Invalid {stage_column} value: {l_days_str}")

    kc_col_name = f"{kc_column}_{selected_crop}"
    df[kc_col_name] = np.float32(0)

    # Vectorized approach - much faster than iterrows
    for start_date in df["start_date"].unique():
        adj_start_date = start_date + pd.Timedelta(days=l_ini_days + l_dev_days + l_mid_days)
        end_date = adj_start_date + pd.Timedelta(days=l_late_days)
        mask = (df["Date"] >= adj_start_date) & (df["Date"] < end_date)
        df.loc[mask, kc_col_name] = np.float32(kc_value)
    df.drop("start_date", axis=1, inplace=True)
    return df, l_late_days


# crop_coefficients.py - Function 005: Processes all crop coefficients through all growth stages for multiple crops
# Interactions: calculate_kc_ini, calculate_kc_dev, calculate_kc_mid, calculate_kc_late
def process_crops(df, crop_df, crops, sowing_months, sowing_weeks, df_cp):
    print("FUNCTION 17: process_crops() - Processing crop coefficients")
    for i, selected_crop in enumerate(crops):
        if selected_crop:
            sowing_month = sowing_months[i]
            sowing_week = sowing_weeks[i]

            # Add the plot information based on the selected crop from df_cp
            plot_info = df_cp[df_cp["Crop"] == selected_crop]["Plot"].values[0]
            df[f"Plot_{selected_crop}"] = plot_info

            df, l_ini_days = calculate_kc_ini(df, crop_df, sowing_week, sowing_month, "L_ini_days", "kc_ini",
                                              selected_crop)
            df, l_dev_days = calculate_kc_dev(df, crop_df, "L_dev_days", "kc_dev", selected_crop, l_ini_days)
            df, l_mid_days = calculate_kc_mid(df, crop_df, "L_mid_days", "kc_mid", selected_crop, l_ini_days,
                                              l_dev_days)
            df, l_late_days = calculate_kc_late(df, crop_df, "L_late_days", "kc_end", selected_crop, l_ini_days,
                                                l_dev_days, l_mid_days)
    return df


# crop_coefficients.py - Function 006: Calculates total crop coefficient by summing all growth stage coefficients
# Interactions: None
def calc_crop_kc(row, selected_crop):
    kc_ini_col = f"kc_ini_{selected_crop}"
    kc_dev_col = f"kc_dev_{selected_crop}"
    kc_mid_col = f"kc_mid_{selected_crop}"
    kc_end_col = f"kc_end_{selected_crop}"

    kc_ini = row[kc_ini_col] if kc_ini_col in row else 0
    kc_dev = row[kc_dev_col] if kc_dev_col in row else 0
    kc_mid = row[kc_mid_col] if kc_mid_col in row else 0
    kc_end = row[kc_end_col] if kc_end_col in row else 0

    return kc_ini + kc_dev + kc_mid + kc_end


# crop_coefficients.py - Function 007: Calculates irrigation crop coefficient (Kci) aggregated by plot
# Interactions: numpy, pandas
def calc_kci_by_plot(df_crop, df_cp, crops, num_plots):
    print("FUNCTION 18: calc_kci_by_plot() - Calculating Kci by plot")
    # Initialize columns for Kci by plot
    for i in range(1, num_plots + 1):
        df_crop[f"Kci_plot {i}"] = np.float32(0)

    # Map crop to plot
    crop_to_plot = dict(zip(df_cp["Crop"], df_cp["Plot"]))

    # Vectorized approach - much faster than iterrows
    for crop in crops:
        if crop and f"Kci_{crop}" in df_crop.columns:
            plot = crop_to_plot.get(crop, None)
            if plot:
                plot_number = plot.split(" ")[-1]
                plot_kci_column = f"Kci_plot {plot_number}"
                # Vectorized addition where Kci value is not 0
                mask = df_crop[f"Kci_{crop}"] != 0
                df_crop.loc[mask, plot_kci_column] = (
                    df_crop.loc[mask, plot_kci_column] + df_crop.loc[mask, f"Kci_{crop}"]
                ).astype(np.float32)
    return df_crop


# crop_coefficients.py - Function 008: Calculates Stage 1 crop coefficients aggregated by plot
# Interactions: numpy, pandas
def calculate_stage_1(df, crops, df_cp):
    # Create Stage 1 Kc values for each crop
    for crop in crops:
        df[f"Stage_1_{crop}"] = df[f"kc_ini_{crop}"]

    # Create a DataFrame to store the aggregated values
    df_stage_1_by_plot = df_cp[["Plot", "Crop"]].drop_duplicates()

    # Initialize columns for Stage 1 by plot
    for plot in df_stage_1_by_plot["Plot"].unique():
        df[f"Stage_1_{plot}"] = np.float32(0)

    # Vectorized aggregation - much faster than iterrows
    for _, row in df_stage_1_by_plot.iterrows():
        crop = row["Crop"]
        plot = row["Plot"]
        if f"Stage_1_{crop}" in df.columns:
            mask = df[f"Plot_{crop}"] == plot
            df.loc[mask, f"Stage_1_{plot}"] += df.loc[mask, f"Stage_1_{crop}"]
    return df