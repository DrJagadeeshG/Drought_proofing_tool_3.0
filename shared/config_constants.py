"""
Configuration constants for drought proofing tool

This module contains all configuration constants previously in manual_input.py
These are default values that can be used throughout the application.

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Stores configuration constants and default values for soil, irrigation, and hydrological parameters
# ========================================

# Land and soil parameters
slope = 0                                    # Average land slope (default value is 15)
theta_FC = 420                              # Field capacity (the maximum amount of water soil can hold)
theta_WP = 300                              # Wilting point (the minimum water required by plants to avoid wilting)
Ze = 0.1                                    # Effective rooting depth for crops (in meters)

# Soil moisture retention with conservation practices (%)
Cover_Crops_SM_with_practice = 100          # Soil moisture retention with cover crops (%)
Mulching_SM_with_practice = 100             # Soil moisture retention with mulching (%)
BBF_SM_with_practice = 100                  # Soil moisture retention with broad bed and furrow (BBF) (%)
Bund_SM_with_practice = 100                 # Soil moisture retention with contour/vegetative bunds (%)
Tillage_SM_with_practice = 100              # Soil moisture retention with conservation tillage (%)
with_out_soil_con = 100                     # Soil moisture retention without soil conservation (%)

# Irrigation parameters
Eff_Default_Irrigation = 50                 # Default irrigation efficiency (50%) for SW_Area_Irr_Eff & GW_Area_Irr_Eff

# Initial conditions
SMDi_1 = 0                                  # Initial soil moisture deficit for the first time step

# Curve Number (CN2) values for different land uses
Builtup_cn2 = 90                           # Curve number for built-up areas
WB_cn2 = 0                                  # Curve number for water bodies
Pasture_cn2 = 79                           # Curve number for pasture land
Forest_cn2 = 70                            # Curve number for forest land

# Soil and groundwater parameters
Soil_GWrecharge_coefficient = 0.13          # Soil-groundwater recharge coefficient (from Data Input Sheet: 13%)

# Initial abstraction parameters for different AMC conditions
Ia_AMC1 = 0.2
Ia_AMC2 = 0.2
Ia_AMC3 = 0.2