# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:51:05 2024

@author: Dr. Jagadeesh, Consultant, IWMI
"""
import math
import pandas as pd
import numpy as np
import crop_pattern
import manual_input
from user_input import collect_inp_variables
from user_input import collect_int_variables
from user_input import to_float


# kc_et.py - Function 1: Calculates initial crop coefficient (Kc) for initial growth stage
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


# kc_et.py - Function 2: Calculates crop coefficient (Kc) for development growth stage
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

    # Vectorized approach - much faster than iterrows
    for start_date in df["start_date"].unique():
        adj_start_date = start_date + pd.Timedelta(days=l_ini_days)
        end_date = adj_start_date + pd.Timedelta(days=l_dev_days)
        mask = (df["Date"] >= adj_start_date) & (df["Date"] < end_date)
        df.loc[mask, kc_col_name] = np.float32(kc_value)
    return df, l_dev_days


# kc_et.py - Function 3: Calculates crop coefficient (Kc) for mid-season growth stage
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


# kc_et.py - Function 4: Calculates crop coefficient (Kc) for late season growth stage
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


# kc_et.py - Function 5: Processes all crop coefficients through all growth stages for multiple crops
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


# kc_et.py - Function 6: Calculates total crop coefficient by summing all growth stage coefficients
def calc_crop_kc(row, selected_crop):
    kc_ini_col = f"kc_ini_{selected_crop}"
    kc_dev_col = f"kc_dev_{selected_crop}"
    kc_mid_col = f"kc_mid_{selected_crop}"
    kc_end_col = f"kc_end_{selected_crop}"

    kc_ini = row[kc_ini_col] if kc_ini_col in row else 0
    kc_dev = row[kc_dev_col] if kc_dev_col in row else 0
    kc_mid = row[kc_mid_col] if kc_mid_col in row else 0
    kc_end = row[kc_end_col] if kc_end_col in row else 0

    crop_total_kc = kc_ini + kc_dev + kc_mid + kc_end
    return crop_total_kc


# kc_et.py - Function 7: Calculates irrigation crop coefficient (Kci) aggregated by plot
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


# kc_et.py - Function 8: Calculates crop evapotranspiration with special rice preparation handling
def calc_etci(df_cc, etoi, kci, local_crop, counter):
    if local_crop == "Rice":
        if not all(col in df_cc.columns for col in ["Area", "DSR_Area"]):
            raise ValueError("Required columns not found in df_cc")

        # Calculate kc_prep for Rice only
        if "Rice" not in df_cc.index:
            raise ValueError("'Rice' not found in the DataFrame index")

        rice_area = df_cc.loc["Rice", "Area"]
        rice_dsr_area = df_cc.loc["Rice", "DSR_Area"]
        kc_prep = crop_pattern.safe_divide((rice_area - rice_dsr_area) * 15, rice_area)

        # Calculate ETci for Rice with counter logic
        if kci > 0:
            if counter[0] < 20:
                counter[0] += 1
                etc_i = etoi * kci + kc_prep  # Include kc_prep for the first 20 occurrences when kci > 0
            else:
                etc_i = etoi * kci  # Regular calculation if counter exceeds 20
        else:
            counter[0] = 0  # Reset the counter if kci is 0
            etc_i = etoi * kci  # Calculate normally when kci is 0
    else:
        # For crops other than Rice
        etc_i = etoi * kci  # Calculate normally if not Rice
    return etc_i


# kc_et.py - Function 9: Calculates Stage 1 crop coefficients aggregated by plot
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


# kc_et.py - Function 10: Calculates soil evaporation coefficient (Kei) for all plots
def calc_kei(df_crop, kei, all_plots):
    for plot in all_plots:
        kei_values = df_crop.apply(lambda row: kei if row[f"Kci_{plot}"] == 0 or row[f"Stage_1_{plot}"] > 0 else 0,
                                   axis=1)
        df_crop[f"Kei_{plot}"] = kei_values
    return df_crop


# kc_et.py - Function 11: Calculates daily soil evaporation (ESi) for all plots
def calculate_daily_esi(df_dd, df_crop, all_plots):
    for plot in all_plots:
        df_dd[f"ESi_{plot}"] = df_dd["EToi"] * df_crop[f"Kei_{plot}"]
    return df_dd


# kc_et.py - Function 12: Retrieves total growth days for a specific crop from crop database
def get_total_growth_days(crop_df, selected_crop):
    crop_row = crop_df[crop_df["Crops"] == selected_crop]
    if crop_row.empty:
        raise ValueError(f"Selected crop {selected_crop} not found in crop_df")
    try:
        return float(crop_row["Total Growth Days"].values[0])
    except ValueError:
        raise ValueError(f"Invalid total growth days value for crop {selected_crop}")


# kc_et.py - Function 13: Calculates crop sowing start date based on year, month, and week
def find_start_date(year, sowing_month_num, sowing_week):
    start_date = pd.to_datetime(f"{year}-{sowing_month_num}-01") + pd.Timedelta(days=(int(sowing_week) - 1) * 7)
    return start_date


# kc_et.py - Function 14: Calculates remaining growth days for initial year of crop cycle
def calc_rg_days_ini(df, crop_df, selected_crop, sowing_month, sowing_week):
    sowing_month_num = pd.to_datetime(f"{sowing_month} 1, 2000").month
    total_growth_days = get_total_growth_days(crop_df, selected_crop)
    rg_days_col_name = f"RG_days_{selected_crop}"

    # Calculate start dates for all entries in the DataFrame
    df["start_date"] = df["Date"].dt.year.apply(find_start_date, args=(sowing_month_num, sowing_week))

    # Calculate remaining growth days for the first year - vectorized
    df[rg_days_col_name] = 0
    end_date = df["start_date"] + pd.Timedelta(days=total_growth_days)
    mask = (df["start_date"] <= df["Date"]) & (df["Date"] < end_date)
    days_passed = (df["Date"] - df["start_date"]).dt.days
    remaining_days = (total_growth_days - days_passed - 1).clip(lower=0)
    df.loc[mask, rg_days_col_name] = remaining_days.loc[mask]

    df.drop("start_date", axis=1, inplace=True)
    return df


# kc_et.py - Function 15: Calculates remaining growth days for subsequent years of crop cycle
def calc_remaining_days(df, crop_df, selected_crop, sowing_month, sowing_week):
    sowing_month_num = pd.to_datetime(f"{sowing_month} 1, 2000").month
    total_growth_days = get_total_growth_days(crop_df, selected_crop)
    rg_days_col_name = f"RG_days_{selected_crop}"

    def find_start_date_row(row):
        start_date = pd.to_datetime(f"{row['Date'].year}-{sowing_month_num}-01") + pd.Timedelta(
            days=(int(sowing_week) - 1) * 7)
        return start_date if start_date <= row["Date"] else start_date - pd.DateOffset(years=1)

    df["start_date"] = df.apply(find_start_date_row, axis=1)
    df[rg_days_col_name] = (df["start_date"] + pd.Timedelta(days=total_growth_days) - df["Date"] - pd.Timedelta(
        days=1)).dt.days.clip(lower=0)
    df.drop("start_date", axis=1, inplace=True)
    return df


# kc_et.py - Function 16: Processes remaining growth days for all years in dataset
def process_yearly_rg_days(df, crop_df, crops, months, weeks):
    print("FUNCTION 19: process_yearly_rg_days() - Processing yearly remaining growth days")
    first_year = df["Date"].dt.year.min()
    first_year_df = df[df["Date"].dt.year == first_year].copy()
    remaining_years_df = df[df["Date"].dt.year != first_year].copy()

    for i, selected_crop in enumerate(crops):
        if not selected_crop:  # Skip empty or None crops
            continue
        sowing_month = months[i]
        sowing_week = weeks[i]

        # Process the first year
        first_year_df = calc_rg_days_ini(first_year_df, crop_df, selected_crop, sowing_month, sowing_week)

        # Process the remaining years
        remaining_years_df = calc_remaining_days(remaining_years_df, crop_df, selected_crop, sowing_month, sowing_week)

    # Combine and sort the DataFrame
    df_combined = pd.concat([first_year_df, remaining_years_df]).sort_values(by="Date").reset_index(drop=True)
    return df_combined


# kc_et.py - Function 17: Calculates monthly remaining growth days and updates monthly dataframe
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


# kc_et.py - Function 18: Calculates crop root depth based on growth stage and crop parameters
def root_dep(row, min_root_depth, max_root_depth, total_growth_days, selected_crop):
    try:
        if row[f"RG_days_{selected_crop}"] == 0:
            crop_rd = 0
        else:
            crop_rd = min_root_depth + (max_root_depth - min_root_depth) * \
                      (total_growth_days - row[f"RG_days_{selected_crop}"]) / total_growth_days
        return crop_rd
    except ValueError:
        return None


# kc_et.py - Function 19: Calculates root depth for a specific crop throughout growing season
def calculate_crop_rd(df_crop, crop_df, selected_crop):
    crop_row = crop_df[crop_df["Crops"] == selected_crop]

    if not crop_row.empty:
        min_root_depth_str = crop_row["Min root depth"].values[0]
        total_growth_days_str = crop_row["Total Growth Days"].values[0]
        max_root_depth_str = crop_row["Max root depth"].values[0]

        try:
            min_root_depth = float(min_root_depth_str)
            max_root_depth = float(max_root_depth_str)
            total_growth_days = float(total_growth_days_str)

            df_crop[f"{selected_crop}_crop_rd"] = df_crop.apply(
                lambda row: root_dep(row, min_root_depth, max_root_depth, total_growth_days, selected_crop), axis=1
            )
        except ValueError:
            raise ValueError(
                f"Invalid values found: Min root depth={min_root_depth_str}, Max root depth={max_root_depth_str}, "
                f"Total Growth Days={total_growth_days_str}")
    else:
        print(f"No '{selected_crop}' crop found in the crop data.")


# kc_et.py - Function 20: Calculates final aggregated root depth by plot for all crops
def calc_final_crop_rd(df_crop, crop_df, all_crops, valid_crops_df):
    print("FUNCTION 21: calc_final_crop_rd() - Calculating final crop root depth")
    # Step 1: Calculate root depth for each crop
    for selected_crop in all_crops:
        calculate_crop_rd(df_crop, crop_df, selected_crop)

    # Step 2: Initialize columns for each plot
    plot_numbers = valid_crops_df["Plot"].unique()
    for plot in plot_numbers:
        df_crop[f"crop_rd_{plot}"] = 0

    # Step 3: Sum root depth for each plot
    for plot in plot_numbers:
        # Get the list of crops for this plot
        crops_in_plot = valid_crops_df[valid_crops_df["Plot"] == plot]["Crop"].tolist()

        # Calculate sum of root depth for crops in this plot
        if crops_in_plot:
            df_crop[f"crop_rd_{plot}"] = df_crop.apply(
                lambda row: sum(row[f"{crop}_crop_rd"] for crop in crops_in_plot if f"{crop}_crop_rd" in row.index),
                axis=1
            )
    return df_crop


# kc_et.py - Function 21: Calculates depletion factor for water stress threshold of specific crop
def calculate_depletion_factor(df_crop, crop_df, selected_crop):
    crop_row = crop_df[crop_df["Crops"] == selected_crop]

    if not crop_row.empty:
        depletion_factor_str = crop_row["Depletion fraction - p"].values[0]

        try:
            temp_p = float(depletion_factor_str)
            # Apply the depletion factor only where crop_rd is greater than 0
            p = np.where(df_crop[f"{selected_crop}_crop_rd"] > 0, temp_p, 0)
        except ValueError:
            raise ValueError(f"Invalid depletion factor value: {depletion_factor_str}")
    else:
        print(f"No '{selected_crop}' crop found in the crop database.")
        p = np.zeros(df_crop.shape[0])  # Default to zeros if crop not found
    return p


# kc_et.py - Function 22: Calculates final aggregated depletion factor by plot for all crops
def calc_final_depletion_factor(df_crop, crop_df, all_crops, valid_crops_df):
    # Step 1: Calculate depletion factor for each crop
    for selected_crop in all_crops:
        df_crop[f"{selected_crop}_depletion"] = calculate_depletion_factor(df_crop, crop_df, selected_crop)

    # Step 2: Initialize columns for each plot
    plot_numbers = valid_crops_df["Plot"].unique()
    for plot in plot_numbers:
        df_crop[f"final_depletion_{plot}"] = 0

    # Step 3: Sum depletion factors by plot
    for plot in plot_numbers:
        # Get the list of crops for this plot
        crops_in_plot = valid_crops_df[valid_crops_df["Plot"] == plot]["Crop"].tolist()

        # Calculate sum of depletion factors for crops in this plot
        if crops_in_plot:
            df_crop[f"final_depletion_{plot}"] = df_crop.apply(
                lambda row: sum(row[f"{crop}_depletion"] for crop in crops_in_plot if f"{crop}_depletion" in row.index),
                axis=1
            )
    return df_crop


# Function to calculate AWC based on soil type
# kc_et.py - Function 23: Returns available water content based on soil type classification
def calculate_awc(soil_type):
    awc_values = {
        "Sand": manual_input.AWC_Sand,
        "Sandy Loam": manual_input.AWC_Sandy_Loam,
        "Loam": manual_input.AWC_Loam,
        "Clayey Loam": manual_input.AWC_Clayey_Loam,
        "Clay": manual_input.AWC_Clay
    }

    awc = awc_values.get(soil_type)
    if awc is None:
        raise ValueError("Unknown soil type")
    return awc


# kc_et.py - Function 24: Extracts and validates soil type from input data structure
def get_soil_type(soil):
    # Check if the input is a list
    if isinstance(soil, list) and len(soil) > 0:
        soil_type = str(soil[0])  # Convert the first element to string
        return soil_type
    elif isinstance(soil, str):
        return soil  # Return the string as is
    else:
        # Debug: Print error messages based on the input
        if not isinstance(soil, list) and not isinstance(soil, str):
            print("Error: The input is neither a list nor a string. Type received:", type(soil))
        elif isinstance(soil, list) and len(soil) == 0:
            print("Warning: The soil list is empty.")
    return None


# Function to calculate depth, AWC, and AWC capacity
# kc_et.py - Function 25: Calculates weighted average water content capacity for mixed soil layers
def calculate_awc_capacity(dist1, dist2, soil_type1_dep, soil_type2_dep, local_awc_1=None, local_awc_2=None):
    dist1 = to_float(dist1, 0)
    dist2 = to_float(dist2, 0)
    soil_type1_dep = to_float(soil_type1_dep, 0)
    soil_type2_dep = to_float(soil_type2_dep, 0)
    # If only Soil_type1 is provided, assume dist2 and soil_type2_dep are 0
    if local_awc_2 is None:
        dist2 = 0
        soil_type2_dep = 0
        local_awc_2 = 0

    depth = ((dist1 * soil_type1_dep) + (dist2 * soil_type2_dep)) / 100
    awc = ((local_awc_1 * dist1) + (local_awc_2 * dist2)) / 100
    awc_capacity = depth * awc
    return depth, awc, awc_capacity


# Function to calculate the overall sum of soil moisture areas
# kc_et.py - Function 26: Calculates total area under soil moisture conservation practices
def calculate_soil_moisture_sums(df):
    soil_moisture_columns = ["BBF_Area", "Cover_Area", "Mulching_Area", "Bunds_Area", "Tillage_Area"]
    overall_sum = df[soil_moisture_columns].sum().sum()
    return df, overall_sum


# Function to calculate AWC for soil based on practices
# kc_et.py - Function 27: Calculates soil water content with conservation practice adjustments
def calculate_awc_soil(df, cover_crops_practice, mulching_practice, bbf_practice, bund_practice, tillage_practice,
                       awc_capacity):
    practices = {
        "Cover_Crops_SM_with_practice": cover_crops_practice,
        "Mulching_SM_with_practice": mulching_practice,
        "BBF_SM_with_practice": bbf_practice,
        "Bund_SM_with_practice": bund_practice,
        "Tillage_SM_with_practice": tillage_practice
    }

    area_columns = {
        "Cover_Crops_SM_with_practice": "Cover_Area",
        "Mulching_SM_with_practice": "Mulching_Area",
        "BBF_SM_with_practice": "BBF_Area",
        "Bund_SM_with_practice": "Bunds_Area",
        "Tillage_SM_with_practice": "Tillage_Area"
    }

    df, overall_sum = calculate_soil_moisture_sums(df)

    if overall_sum == 0:
        awc_soil_con = 0
    else:
        x = 0  # Initialize x
        for practice_column, practice_percentage in practices.items():
            area_column = area_columns.get(practice_column)
            if area_column in df.columns:
                x += df[area_column].sum() * (practice_percentage / 100)
        awc_soil = (x * awc_capacity) / overall_sum
        awc_soil_con = awc_soil
    return awc_soil_con


# kc_et.py - Function 28: Calculates final field capacity considering conservation and non-conservation areas
def calculate_capacity(awc_capacity, with_out_soil_con, total_area, overall_sum, awc_soil_con):
    awc_capacity = to_float(awc_capacity, 0)
    with_out_soil_con = to_float(with_out_soil_con, 0)
    total_area = to_float(total_area, 0)
    overall_sum = to_float(overall_sum, 0)
    awc_soil_con = to_float(awc_soil_con, 0)

    capacity = ((awc_capacity * (with_out_soil_con / 100) * (total_area - overall_sum)) + (
            overall_sum * awc_soil_con)) / total_area
    return capacity


# kc_et.py - Function 29: Calculates total available water (TAW) for each plot based on root depth
def calc_taw(df_crop, capacity, all_plots):
    for plot in all_plots:
        df_crop[f"TAWi_{plot}"] = capacity * df_crop[f"crop_rd_{plot}"]
    return df_crop


# kc_et.py - Function 30: Calculates readily available water (RAW) based on depletion factors
def calc_raw(df_crop, all_plots):
    for plot in all_plots:
        df_crop[f"RAWi_{plot}"] = df_crop[f"final_depletion_{plot}"] * df_crop[f"TAWi_{plot}"]
    return df_crop


# kc_et.py - Function 31: Calculates total evaporable water (TEW) from soil surface layer
def calc_tew(df_crop, theta_fc, theta_wp, all_plots):
    for plot in all_plots:
        df_crop[f"TEWi_{plot}"] = (theta_fc - 0.5 * theta_wp) * df_crop["Ze"]
    return df_crop


# kc_et.py - Function 32: Calculates readily evaporable water (REW) from soil surface
def calc_rew(df_crop, all_plots):
    for plot in all_plots:
        df_crop[f"REWi_{plot}"] = 0.4 * df_crop[f"TEWi_{plot}"]
    return df_crop


# kc_et.py - Function 33: Determines sown area based on remaining growth days
def calc_sown_area(remaining_growth_day, area):
    return area if remaining_growth_day > 0 else 0


# kc_et.py - Function 34: Processes sown area calculations for all crops in crop pattern
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


# kc_et.py - Function 35: Calculates net sown area aggregated by plot from crop calendar
def calculate_net_sown_area_by_plot(df_crop, valid_crops_df, df_cc):
    for plot in valid_crops_df["Plot"].unique():
        # Get the crops associated with the current plot
        crops_in_plot = valid_crops_df.loc[valid_crops_df["Plot"] == plot, "Crop"].tolist()
        
        # Calculate the constant total area for this plot from df_cc
        total_plot_area = 0
        for crop in crops_in_plot:
            if crop in df_cc.index:
                total_plot_area += df_cc.at[crop, "Area"]
        
        # Set constant NSA for the plot (doesn't change with growing season)
        df_crop[f"{plot}_NSA"] = total_plot_area
    return df_crop

# kc_et.py - Function 36: Calculates soil evaporation reduction factors for conservation practices
def calc_soil_ke(df_crop, df_cc, all_crops):
    new_columns = {}

    for crop in all_crops:
        eva_red_area = []
        eva_red = []

        # Vectorized calculation - much faster than iterrows
        mask = df_crop[f"{crop}_Sown_Area"] > 0
        area_calc = (
            df_cc.at[crop, "Tillage_Area"] +
            df_cc.at[crop, "Mulching_Area"] +
            df_cc.at[crop, "Cover_Area"] +
            df_cc.at[crop, "Tank_Area"]
        )
        
        eva_red_area = np.where(mask, area_calc, 0)
        eva_red = np.where(mask & (area_calc > 0), df_cc.at[crop, "red_soil_evap"], 0)

        new_columns[f"eva_red_area_{crop}"] = eva_red_area
        new_columns[f"eva_red_{crop}"] = eva_red

    # Add all new columns at once to avoid fragmentation
    df_crop = pd.concat([df_crop, pd.DataFrame(new_columns)], axis=1)

    return df_crop

# kc_et.py - Function 37: Calculates final evaporation reduction factors for each crop
def calc_final_evap_red(df_crop, all_crops):
    new_columns = {}
    for crop in all_crops:
        final_evap_red = []

        # Vectorized calculation - much faster than iterrows
        sown_area = df_crop.get(f"{crop}_Sown_Area", pd.Series([0] * len(df_crop)))
        eva_red_area = df_crop.get(f"eva_red_area_{crop}", pd.Series([0] * len(df_crop)))
        eva_red = df_crop.get(f"eva_red_{crop}", pd.Series([0] * len(df_crop)))
        
        # Calculate final_evap_red vectorized
        mask_valid = ~pd.isna(sown_area) & (sown_area > 0)
        final_evap_red = np.where(
            mask_valid,
            1 - ((eva_red_area * eva_red) / sown_area),
            1
        )

        new_columns[f"Final_Evap_Red_{crop}"] = final_evap_red
    df_crop = pd.concat([df_crop, pd.DataFrame(new_columns)], axis=1)
    return df_crop


# kc_et.py - Function 38: Calculates weighted evaporation reduction factors aggregated by plot
def calc_final_evap_red_plot_wise(df_crop, all_crops, all_plots):
    # Initialize the new column with zeros
    plot_columns = {f"Final_Evap_Red_{plot}": [0.0] * len(df_crop) for plot in all_plots}
    df_crop = pd.concat([df_crop, pd.DataFrame(plot_columns)], axis=1)

    for plot in all_plots:
        for crop in all_crops:
            # Filter rows where plot is present
            plot_df = df_crop[df_crop.apply(lambda row: any(
                row[f"Plot_{crop_name}"] == plot for crop_name in all_crops), axis=1)]

            if plot_df.empty:
                continue

            if f"Final_Evap_Red_{crop}" in df_crop.columns:
                sown_area_col = f"{crop}_Sown_Area"
                if sown_area_col in plot_df.columns:
                    weighted_evap_red = (plot_df[sown_area_col] *
                                         plot_df[f"Final_Evap_Red_{crop}"]
                                         ).sum() / plot_df[sown_area_col].sum()
                    df_crop.loc[plot_df.index, f"Final_Evap_Red_{plot}"] = weighted_evap_red

    return df_crop


# kc_et.py - Function 39: Retrieves cover type and treatment type for crops from database
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


# kc_et.py - Function 40: Retrieves curve number (CN) values with multiple fallback strategies
def get_cn(crop_df, crop_type, crop_sown_type, hsc, soil_type, default_cn_value="0"):
    # Check if soil_type or hsc is empty, return a default value if so
    if not soil_type or not hsc:
        return default_cn_value

    # Perform the lookup in the DataFrame
    cn = crop_df[(crop_df["Crop Type"] == crop_type) &
                 (crop_df["Crop Sown Type"] == crop_sown_type) &
                 (crop_df["HSC"] == hsc)]

    if soil_type in cn.columns:
        if not cn.empty:
            cn_value = cn[soil_type].iloc[0]
            # Check if CN value is not empty/NaN
            if pd.notna(cn_value) and str(cn_value).strip():
                return cn_value
        
        # Fallback 1: Try with just crop_type and hsc (ignore crop_sown_type)
        cn_fallback1 = crop_df[(crop_df["Crop Type"] == crop_type) & (crop_df["HSC"] == hsc)]
        if not cn_fallback1.empty:
            # Vectorized search - faster than iterrows
            valid_values = cn_fallback1[soil_type].dropna()
            valid_values = valid_values[valid_values.astype(str).str.strip() != '']
            if not valid_values.empty:
                return valid_values.iloc[0]
        
        # Fallback 2: Try with just crop_type (ignore crop_sown_type and hsc)
        cn_fallback2 = crop_df[crop_df["Crop Type"] == crop_type]
        if not cn_fallback2.empty:
            # Vectorized search - faster than iterrows
            valid_values = cn_fallback2[soil_type].dropna()
            valid_values = valid_values[valid_values.astype(str).str.strip() != '']
            if not valid_values.empty:
                return valid_values.iloc[0]
        
        # Fallback 3: Crop-specific defaults based on typical values
        crop_defaults = {
            "Row Crops": {"Clay": 89, "Clayey Loam": 85, "Loam": 81, "Sandy Loam": 78, "Sand": 72},
            "Small Grains": {"Clay": 94, "Clayey Loam": 91, "Loam": 86, "Sandy Loam": 84, "Sand": 77},
            "Closed Seed or Broadcast Legumes": {"Clay": 83, "Clayey Loam": 78, "Loam": 74, "Sandy Loam": 70, "Sand": 65},
            "Closed Seed or Broadcast legumes": {"Clay": 83, "Clayey Loam": 78, "Loam": 74, "Sandy Loam": 70, "Sand": 65}
        }
        
        if crop_type in crop_defaults and soil_type in crop_defaults[crop_type]:
            fallback_cn = crop_defaults[crop_type][soil_type]
            return fallback_cn
        
        return default_cn_value
    else:
        return default_cn_value


# kc_et.py - Function 41: Calculates curve number values for all crops considering two soil layers
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


# Function to calculate Actual CN2
# kc_et.py - Function 42: Calculates weighted actual CN2 value from two soil layer contributions
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


# kc_et.py - Function 43: Calculates actual curve numbers for all crops using input distributions
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


# kc_et.py - Function 44: Calculates reduced curve numbers considering conservation interventions
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
                df_cc.at[crop, "Red_CN2"] = crop_pattern.safe_divide(
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


# kc_et.py - Function 45: Retrieves curve number for fallow land based on soil type
def get_fallow_cn_soil_type(crop_df, soil_type):
    if not soil_type:  # Check if soil_type is empty
        return None


    if soil_type in crop_df.columns:
        try:
            # Assuming you're getting the CN value for a specific row, index 4 is used here
            # Ensure that row index 4 is appropriate for your needs
            value = crop_df[soil_type].iloc[4]
            return value
        except IndexError:
            print(f"Index {4} is out of bounds for the DataFrame. Returning None.")
            return None
    else:
        print(f"Column {soil_type} not found in DataFrame")
        return None


# kc_et.py - Function 46: Calculates actual fallow curve number from two soil layer contributions
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



# kc_et.py - Function 47: Returns curve number for crop based on sown area status
def calc_crop_cn2(sown_area, actual_cn2):
    return actual_cn2 if sown_area > 0 else 0


# kc_et.py - Function 48: Updates crop curve numbers in dataframe for all crops
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


# kc_et.py - Function 49: Calculates total sown area across all crops with area limit enforcement
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

# kc_et.py - Function 50: Calculates area-weighted consolidated curve number for all crops
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


# kc_et.py - Function 51: Calculates fallow area from net sown area and actual crop areas
def calc_fallow_area(net_crop_sown_area, sown_area, fallow):
    net_crop_sown_area = to_float(net_crop_sown_area, 0.0)
    fallow = to_float(fallow, 0)
    fallow_area = net_crop_sown_area - sown_area + fallow
    return fallow_area


# kc_et.py - Function 52: Calculates land use fraction from area and total area
def calc_lulc(x, total_area):
    # Convert x and total_area to float if they are lists
    x = to_float(x, 0)
    total_area = to_float(total_area, 0)

    # Calculate the value
    y = x / total_area if total_area != 0 else 0  # Avoid division by zero
    return y

# df_crop["Fallowcn2"] = df_crop["Fallow_area"].apply(lambda x: kc_et.calc_fallowcn2(x, cn_values_list[1]))
# kc_et.py - Function 53: Returns fallow curve number based on fallow area presence
def calc_fallowcn2(fallow_area, actual_fallow_cn2):
    return actual_fallow_cn2 if fallow_area > 0 else 0


_calc_final_cn2_printed = False

# kc_et.py - Function 54: Calculates area-weighted final curve number from all land uses
def calc_final_cn2(x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6):
    global _calc_final_cn2_printed
    if not _calc_final_cn2_printed:
        print("FUNCTION 25: calc_final_cn2() - Calculating final CN2 values")
        _calc_final_cn2_printed = True
    y = x1 * y1 + x2 * y2 + x3 * y3 + x4 * y4 + x5 * y5 + x6 * y6
    return y


# kc_et.py - Function 55: Adjusts curve number based on slope using Williams formula
def calc_cn2_adjusted(final_cn2, inp_slope):
    inp_slope = inp_slope/100
    cn2_adjusted = final_cn2 * ((1.9274 * inp_slope + 2.1327) / (inp_slope + 2.1791))
    return np.minimum(cn2_adjusted, 100)


# kc_et.py - Function 56: Calculates CN1 (dry conditions) from CN2 using standard formula
def calc_cn1(final_cn2):
    cn1 = final_cn2 / (2.281 - 0.01281 * final_cn2)
    return cn1


# kc_et.py - Function 57: Calculates CN3 (wet conditions) from CN2 using standard formula
def calc_cn3(final_cn2):
    cn3 = final_cn2 / (0.427 + 0.00573 * final_cn2)
    return cn3


# kc_et.py - Function 58: Determines crop dormancy status based on sown area
def calc_dormant(sown_area):
    return "N" if sown_area > 0 else "Y"


# kc_et.py - Function 59: Calculates antecedent moisture condition based on rainfall and dormancy
def calc_amc_cond(df_dd, df_crop):
    conditions = [
        (df_crop["Dormant"] == "N") & (df_dd["last_5_days_Rain"] < 36),
        (df_crop["Dormant"] == "N") & (df_dd["last_5_days_Rain"] > 53),
        (df_crop["Dormant"] == "N"),
        (df_dd["last_5_days_Rain"] < 13),
        (df_dd["last_5_days_Rain"] > 28)
    ]

    choices = [1, 3, 2, 1, 3]

    amc_cond = np.select(conditions, choices, default=2)
    return amc_cond


# kc_et.py - Function 60: Selects appropriate curve number based on antecedent moisture condition
def calc_cn(df_crop):
    conditions = [
        df_crop["AMC"] == 1,
        df_crop["AMC"] == 2
    ]
    choices = [df_crop["Final_CN1"], df_crop["Final_CN2"]]
    cn = np.select(conditions, choices, default=df_crop["Final_CN3"])
    return cn


# kc_et.py - Function 61: Calculates water abstraction parameters for runoff calculation
def calc_abstraction(df_dd, df_crop, ia_amc1, ia_amc2, ia_amc3):
    print("FUNCTION 26: calc_abstraction() - Calculating water abstraction")
    si = (25400 / df_dd["CNi"]) - 254
    conditions = [
        df_crop["AMC"] == 1,
        df_crop["AMC"] == 2
    ]
    choices = [si * ia_amc1, si * ia_amc2]
    iai = np.select(conditions, choices, default=si * ia_amc3)
    return si, iai


# kc_et.py - Function 62: Calculates groundwater recharge from precipitation
def get_recharge(pi, soil_gwrecharge_coefficient):
    recharge = pi * soil_gwrecharge_coefficient
    return recharge


# kc_et.py - Function 63: Calculates net rainfall after removing groundwater recharge
def get_rain_src_model(pi, recharge_src):
    rain = pi - recharge_src
    return rain


# kc_et.py - Function 64: Calculates surface runoff using SCS curve number method
def runoff_cn(pi, iai, si):
    q = crop_pattern.safe_divide((pi - iai) ** 2, (pi + si - iai))
    return q


# kc_et.py - Function 65: Applies runoff calculation only when rainfall exceeds initial abstraction
def calc_runoff_cn(rain_src, iai, runoff):
    return 0 if rain_src < iai else runoff


# kc_et.py - Function 66: Calculates effective rainfall by subtracting runoff from net rainfall
def get_eff_rain(rain_src, runoff):
    peff = rain_src - runoff
    return peff


# kc_et.py - Function 67: Aggregates daily runoff to monthly totals and merges with monthly data
def calculate_monthly_qi(df_dd, df_mm):
    # Resample the Qi values to a monthly frequency and sum them
    qom = df_dd.resample("M", on="Date")["Qi"].sum().reset_index()

    # Merge the resampled monthly Qi values into df_mm
    df_mm = df_mm.merge(qom, on="Date", how="left")

    # Rename the column appropriately
    df_mm.rename(columns={"Qi": "Qom"}, inplace=True)

    return df_mm