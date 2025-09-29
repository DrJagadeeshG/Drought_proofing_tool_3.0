"""
Irrigation demand calculations for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates irrigation water requirements and demands based on crop ET and actual ET differences
# ========================================


# irrigation_demand.py - Function 001: Calculates irrigation water requirements as difference between ET and actual ET
# Interactions: None
def calculate_iwr(df_dd, df_crop, crops):
    print("FUNCTION 39: calculate_iwr() - Calculating irrigation water requirements")
    for crop in crops:
        df_crop[f"IWR_{crop}"] = (df_dd[f"ETci_{crop}"] - df_crop[f"AE_crop_{crop}"]).clip(lower=0)
    return df_crop


# irrigation_demand.py - Function 002: Aggregates daily irrigation water requirements to monthly values
# Interactions: calculate_iwr
def calculate_monthly_iwr(df_dd, df_mm, df_crop, crops):
    # Calculate IWR for all crops in a single step
    df_crop = calculate_iwr(df_dd, df_crop.copy(), crops)
    # Resample and merge IWR with other columns (can be vectorized)
    for crop in crops:
        iwr_resampled = df_crop.set_index("Date")[f"IWR_{crop}"].resample("M").sum().reset_index()
        df_mm = df_mm.merge(iwr_resampled, how="left", on="Date", suffixes=("", f"_{crop}"))
        ae_soil = df_crop[["Date", f"AE_soil_{crop}"]].set_index("Date").resample("M").sum().reset_index()
        ae_crop = df_crop[["Date", f"AE_crop_{crop}"]].set_index("Date").resample("M").sum().reset_index()
        df_mm = df_mm.merge(ae_soil, how="left", on="Date", suffixes=("", f"_soil_{crop}"))
        df_mm = df_mm.merge(ae_crop, how="left", on="Date", suffixes=("", f"_crop_{crop}"))

    # Add fallow area evapotranspiration aggregation if available (only if not already present)
    if "AE_soil_Fallow" in df_dd.columns and "AE_soil_Fallow" not in df_mm.columns:
        ae_soil_fallow = df_dd[["Date", "AE_soil_Fallow"]].set_index("Date").resample("M").sum().reset_index()
        df_mm = df_mm.merge(ae_soil_fallow, how="left", on="Date")

    return df_mm


# irrigation_demand.py - Function 003: Calculates irrigation water requirement after canal supply
# Interactions: None
def get_iwr_after_canal(df_mm):
    df_mm["IWR_after_canal"] = df_mm["Irr_water_need"] - df_mm["Canal_supply"]
    return df_mm