"""
Curve number data retrieval functions for surface water bucket

This module contains functions for retrieving curve number data:
- CN values with multiple fallback strategies
- CN values for fallow land based on soil type

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Retrieves curve number values from database with fallback strategies for runoff calculations
# ========================================
import pandas as pd


# curve_number_data.py - Function 001: Retrieves curve number (CN) values with multiple fallback strategies
# Interactions: pandas
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
            "Closed Seed or Broadcast legumes": {"Clay": 83, "Clayey Loam": 78, "Loam": 74, "Sandy Loam": 70, "Sand": 65}
        }
        
        if crop_type in crop_defaults and soil_type in crop_defaults[crop_type]:
            fallback_cn = crop_defaults[crop_type][soil_type]
            return fallback_cn
        
        return default_cn_value
    else:
        return default_cn_value


# curve_number_data.py - Function 002: Retrieves curve number for fallow land based on soil type
# Interactions: None
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