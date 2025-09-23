"""
Land use calculations for drought proofing tool

This module contains functions for land use analysis:
- Total area calculations
- Land use category processing

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates total area from different land use categories for drought proofing analysis
# ========================================


# land_use.py - Function 001: Calculates total area from all land use categories
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