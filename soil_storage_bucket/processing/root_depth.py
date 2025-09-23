"""
Root depth calculations for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates crop root depths based on growth stages and aggregates by plot for soil moisture calculations
# ========================================


# root_depth.py - Function 001: Calculates crop root depth based on growth stage and crop parameters
# Interactions: None
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


# root_depth.py - Function 002: Calculates root depth for a specific crop throughout growing season
# Interactions: root_dep
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


# root_depth.py - Function 003: Calculates final aggregated root depth by plot for all crops
# Interactions: calculate_crop_rd
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