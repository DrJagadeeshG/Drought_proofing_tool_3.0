# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 11:00:30 2024

@author: Dr. Jagadeesh, Consultant, IWMI
"""
# =============================================================================
# User Input
# =============================================================================
latitude = ["15N"]                  # Set the latitude (integer between 0 and 50) and hemisphere ("N" for north, "S" for south), e.g., "15N" or "22S"
climate = ["semi arid"]             # Set the climate type; options include "temperate" (KEI = 1.10) and "semi arid" (KEI = 1.05)

# Set primary and secondary soil types; options include: "Sand", "Sandy Loam", "Loam", "Clayey Loam", "Clay"
Soil_type1 = ["Clay"]
Soil_type2 = ["Clayey Loam"]

# Set Hydrologic Soil Class (HSC); options include: "Poor","Good"
HSC1 = ["Good"]
HSC2 = ["Good"]

# Set the percentage(%) distribution of soil types; values should sum to 100
dist1 = ["70"]
dist2 = ["30"]

# Set the depth of each soil type in meters
Soil_type1_dep = ["1"]              # Depth of Soil_type1 in meters ,used in calculation not asked on dashboard
Soil_type2_dep = ["1"]              # Depth of Soil_type2 in meters ,used in calculation not asked on dashboard

# Land use input in hectares (ha)
Net_Crop_Sown_Area = ["4708"]     # Net area sown with crops (in hectares)
Fallow = ["350"]                 # Fallow land (unused agricultural land, in hectares)
Builtup = ["468"]                 # Built-up area (urban/constructed land, in hectares)
Water_bodies = ["350"]             # Area covered by water bodies (in hectares)
Pasture = ["425"]                 # Area used for pasture (in hectares)
Forest = ["426"]                 # Forested area (in hectares)

# Crop input for Kharif, Rabi, and Summer seasons
# Kharif season crops input
Kharif_Crops = ["Chilli"]                    # Name of Kharif crop
Kharif_Sowing_Month = ["Aug"]              # Sowing month (use three-letter month abbreviation, e.g., "Jun" for June)
Kharif_Sowing_Week = ["1"]                 # Sowing week (choose from "1", "2", "3", or "4")
Kharif_Crops_Irr_Area = ["712"]         # Irrigated area for Kharif crops (in hectares)
Kharif_Crops_Rainfed_Area = ["0"]      # Rainfed area for Kharif crops (in hectares)
Kharif_Crops_Area = ["712"]             # Total area for Kharif crops (in hectares)
Kharif_Crops_Type = []                     # Type of Kharif crop (optional, defaults will be taken from crop_db if left empty)
Kharif_Crop_Sown_Type = []                 # Sowing type for Kharif crops (optional, defaults will be taken from crop_db if left empty)

# Rabi season crops input
Rabi_Crops = ["Tobacco", "Pulses"]
Rabi_Sowing_Month = ["Sep", "Nov"]
Rabi_Sowing_Week = ["1", "2"]
Rabi_Crops_Irr_Area = ["1880", "1150"]
Rabi_Crops_Rainfed_Area = ["0", "0"]
Rabi_Crops_Area = ["1880", "1150"]
Rabi_Crops_Type = []
Rabi_Crop_Sown_Type = []

# Summer season crops input
Summer_Crops = []
Summer_Sowing_Month = []
Summer_Sowing_Week = []
Summer_Crops_Irr_Area = []
Summer_Crops_Rainfed_Area = []
Summer_Crops_Area = []
Summer_Crops_Type = []
Summer_Crop_Sown_Type = []

# Irrigation and Domestic Water Use Details
SW_Area = ["70"]                             # Surface water area as a (%)(e.g., "10", "12", etc.) 
SW_Area_Irr_Eff = ["50"]                   # Irrigation efficiency for surface water (default value is "50")

GW_Area = ["30"]                            # Groundwater area as a (%)(e.g., "90", "88", etc.)
GW_Area_Irr_Eff = ["50"]                   # Irrigation efficiency for groundwater (default value is "50")

Aquifer_Depth = ["6"]                      # Depth of the aquifer in meters (m)
Starting_Level = ["0"]                      # Starting level of the aquifer in meters (m) below the surface
Specific_Yield = ["2"]                      # Specific yield of the aquifer as a percentage (%)(e.g.,"1.2","2.5")

Population = ["11200"]                       # Total population (number of people)
Domestic_Water_Use = ["120"]                # Domestic water use per person in liters per day (LPD)
Groundwater_Dependent = ["60"]              # Percentage (%) of the population dependent on groundwater for domestic use
Surface_Water_Dependent = ["40"]            # Percentage (%) of the population dependent on surface water for domestic use

Other = ["500"]                             # Other non-domestic water users (e.g., industrial use) in liters per day (LPD)
Other_Water_Use = ["30"]                    # Water use per other non-domestic user in liters per day (LPD)


# =============================================================================
# Supply-Side Interventions 
# =============================================================================
# This section outlines the specifications and costs for various water conservation structures, 
# including farm ponds (unlined and lined), check dams, infiltration ponds, and injection wells.

Time_Period = ["20"]                        # Total time period for which the rainfall data is provided (in years) (e.g.,"15")
Interest_Rate = ["8"]                       # Interest rate as a percentage (%) for economic analysis (e.g., "6", "7.2")

# Farm Pond (Unlined) Details
Farm_Pond_Vol = []                  # Volume of the unlined farm pond (in cubic meters)
Farm_Pond_Depth = ["2.5"]                   # Depth of the unlined farm pond (in meters)
Farm_Pond_Inf_Rate = ["9"]                  # Infiltration rate for the unlined farm pond (in mm/day)
Farm_Pond_Cost = ["80"]                     # Cost per cubic meter for constructing the unlined farm pond (in Rs/Cu.m)
Farm_Pond_Life_Span = ["10"]                # Life span of the unlined farm pond (in years)
Farm_Pond_Maintenance = ["0"]               # Annual maintenance cost in percentage(%)(e.g., "10","3.5")

# Farm Pond (Lined) Details
Farm_Pond_Lined_Vol = []            # Volume of the lined farm pond (in cubic meters)
Farm_Pond_Lined_Depth = ["2"]               # Depth of the lined farm pond (in meters)
Farm_Pond_Lined_Inf_Rate = ["0"]            # Infiltration rate for the lined farm pond (should be 0 as it is lined)
Farm_Pond_Lined_Cost = ["120"]              # Cost per cubic meter for constructing the lined farm pond (in Rs/Cu.m)
Farm_Pond_Lined_Life_Span = ["10"]          # Life span of the lined farm pond (in years)
Farm_Pond_Lined_Maintenance = ["6"]         # Annual maintenance cost in percentage(%)(e.g., "10","3.5")

# Check Dam Details
Check_Dam_Vol = []                   # Volume of the check dam (in cubic meters)
Check_Dam_Depth = ["2.5"]                   # Depth of the check dam (in meters)
Check_Dam_Inf_Rate = ["9"]                 # Infiltration rate for the check dam (in mm/day)
Check_Dam_Cost = ["100"]                    # Cost per cubic meter for constructing the check dam (in Rs/Cu.m)
Check_Dam_Life_Span = ["15"]                # Life span of the check dam (in years)
Check_Dam_Maintenance = ["2"]               # Annual maintenance cost in percentage(%)(e.g., "10","3.5")

# Infiltration Pond Details
Infiltration_Pond_Vol = []                  # Volume of the infiltration pond (in cubic meters)
Infiltration_Pond_Depth = ["1"]             # Depth of the infiltration pond (in meters)
Infiltration_Pond_Inf_Rate = ["50"]         # Infiltration rate for the infiltration pond (in mm/day)
Infiltration_Pond_Cost = ["85"]             # Cost per cubic meter for constructing the infiltration pond (in Rs/Cu.m)
Infiltration_Pond_Life_Span = ["7"]         # Life span of the infiltration pond (in years)
Infiltration_Pond_Maintenance = ["4"]       # Annual maintenance cost in percentage(%)(e.g., "10","3.5")

# Injection Wells Details
Injection_Wells_Vol = []                    # Volume of water injected by wells (in cubic meters/day)
Injection_Wells_Nos = ["2"]                 # Number of injection wells
Injection_Wells_Cost = ["120000"]           # Cost per injection well (in Rs)
Injection_Wells_Life_Span = ["7"]           # Life span of the injection wells (in years)
Injection_Wells_Maintenance = ["0"]         # Annual maintenance cost in percentage(%)(e.g., "10","3.5")

# =============================================================================
# Demand-Side Interventions
# =============================================================================
# This section includes various water-saving techniques for irrigation, such as drip, sprinkler, land levelling,
# and other advanced methods. It covers the cost, efficiency, and lifespan of each technique.

# Drip Irrigation
Kharif_Crop_Drip_Area = []                  # Area under drip irrigation for Kharif crops (in hectares)
Rabi_Crop_Drip_Area = []                    # Area under drip irrigation for Rabi crops (in hectares)
Summer_Crop_Drip_Area = []                  # Area under drip irrigation for Summer crops (in hectares)
Eff_Drip_irrigation = []                    # Efficiency of drip irrigation (default is 90, i.e., 90% efficiency)(e.g.,"90")
Drip_Irr_Cost = ["60000"]                   # Cost of drip irrigation per hectare (in Rs/ha)
Drip_Irr_Life_Span = ["8"]                  # Lifespan of drip irrigation system (in years)
Drip_Irr_Maintenance = ["6"]                # Annual maintenance cost in percentage(%)(e.g., "10","3.5")

# Sprinkler Irrigation
Kharif_Crop_Sprinkler_Area = []             # Area under sprinkler irrigation for Kharif crops (in hectares)
Rabi_Crop_Sprinkler_Area = []               # Area under sprinkler irrigation for Rabi crops (in hectares)
Summer_Crop_Sprinkler_Area = []             # Area under sprinkler irrigation for Summer crops (in hectares)
Eff_Sprinkler_irrigation = ["75"]               # Efficiency of sprinkler irrigation (default is 70, i.e., 70% efficiency)(e.g.,"70")
Sprinkler_Irr_Cost = ["25000"]              # Cost of sprinkler irrigation per hectare (in Rs/ha)
Sprinkler_Irr_Life_Span = ["10"]            # Lifespan of sprinkler irrigation system (in years)
Sprinkler_Irr_Maintenance = ["10"]          # Annual maintenance cost in percentage(%)(e.g., "10","3.5")

# Land Levelling
Kharif_Crop_Land_Levelling_Area = []        # Area under land levelling for Kharif crops (in hectares)
Rabi_Crop_Land_Levelling_Area = []          # Area under land levelling for Rabi crops (in hectares)
Summer_Crop_Land_Levelling_Area = []        # Area under land levelling for Summer crops (in hectares)
Eff_Land_Levelling = []                     # Efficiency of land levelling (default is 25, meaning 25% water saved)(e.g.,"25")
Land_Levelling_Cost = ["100"]               # Cost of land levelling per hectare (in Rs/ha)
Land_Levelling_Life_Span = ["3"]            # Lifespan of land levelling effects (in years)
Land_Levelling_Maintenance = ["2"]          # Annual maintenance cost in percentage(%)(e.g., "10","3.5")

# Direct Seeded Rice (DSR) (Applicable only to rice crops)
Kharif_Crop_DSR_Area = []                   # Area under direct-seeded rice for Kharif crops (in hectares)
Rabi_Crop_DSR_Area = []                     # Area under direct-seeded rice for Rabi crops (in hectares)
Summer_Crop_DSR_Area = []                   # Area under direct-seeded rice for Summer crops (in hectares)
Eff_Direct_Seeded_Rice = []                 # Efficiency of direct-seeded rice (default is 25, meaning 25% water saved)(e.g.,"25")
Direct_Seeded_Rice_Cost = ["50"]            # Cost of direct-seeded rice per hectare (in Rs/ha)
Direct_Seeded_Rice_Life_Span = ["1"]        # Lifespan of direct-seeded rice benefits (in years)

# Alternate Wetting & Drying (AWD)
Kharif_Crop_AWD_Area = []                   # Area under AWD for Kharif crops (in hectares)
Rabi_Crop_AWD_Area = []                     # Area under AWD for Rabi crops (in hectares)
Summer_Crop_AWD_Area = []                   # Area under AWD for Summer crops (in hectares)
Eff_Alternate_Wetting_And_Dry = []          # Efficiency of AWD (default is 25, meaning 25% water saved)(e.g.,"25")
Alternate_Wetting_And_Dry_Cost = ["50"]     # Cost of AWD per hectare (in Rs/ha)
Alternate_Wetting_And_Dry_Life_Span = ["2"] # Lifespan of AWD benefits (in years)

# System of Rice Intensification (SRI)
Kharif_Crop_SRI_Area = []                   # Area under SRI for Kharif crops (in hectares)
Rabi_Crop_SRI_Area = []                     # Area under SRI for Rabi crops (in hectares)
Summer_Crop_SRI_Area = []                   # Area under SRI for Summer crops (in hectares)
Eff_SRI = []                                # Efficiency of SRI (default is 50, meaning 50% water saved)(e.g.,"50")
SRI_Cost = ["50"]                           # Cost of SRI per hectare (in Rs/ha)
SRI_Life_Span = ["2"]                       # Lifespan of SRI benefits (in years)

# Ridge & Furrow Irrigation
Kharif_Crop_Ridge_Furrow_Area = []          # Area under ridge & furrow irrigation for Kharif crops (in hectares)
Rabi_Crop_Ridge_Furrow_Area = []            # Area under ridge & furrow irrigation for Rabi crops (in hectares)
Summer_Crop_Ridge_Furrow_Area = []          # Area under ridge & furrow irrigation for Summer crops (in hectares)
Eff_Ridge_Furrow_Irrigation = []            # Efficiency of ridge & furrow irrigation (default is 25, meaning 25% water saved)(e.g.,"25")
Ridge_Furrow_Irrigation_Cost = ["50"]       # Cost of ridge & furrow irrigation per hectare (in Rs/ha)
Ridge_Furrow_Irrigation_Life_Span = ["2"]   # Lifespan of ridge & furrow irrigation system (in years)

# Deficit Irrigation
Kharif_Crop_Deficit_Area = []               # Area under deficit irrigation for Kharif crops (in hectares)
Rabi_Crop_Deficit_Area = []                 # Area under deficit irrigation for Rabi crops (in hectares)
Summer_Crop_Deficit_Area = []               # Area under deficit irrigation for Summer crops (in hectares)
Eff_Deficit_Irrigation = []                 # Efficiency of deficit irrigation (default is 30, meaning 30% water saved)(e.g.,"30")
Deficit_Irrigation_Cost = ["50"]            # Cost of deficit irrigation per hectare (in Rs/ha)
Deficit_Irrigation_Life_Span = ["2"]        # Lifespan of deficit irrigation system (in years)


# =============================================================================
# Soil Moisture Interventions
# =============================================================================
# This section includes techniques to improve soil moisture retention, such as cover crops, mulching, 
# and conservation tillage. It covers the area, cost, efficiency, and lifespan of each intervention.

# Cover Crops
Kharif_Crop_Cover_Crops_Area = []           # Area under cover crops for Kharif crops (in hectares)
Rabi_Crop_Cover_Crops_Area = []             # Area under cover crops for Rabi crops (in hectares)
Summer_Crop_Cover_Crops_Area = []           # Area under cover crops for Summer crops (in hectares)
Red_CN_Cover_Crops = ["3"]                  # Reduction in Curve Number (CN) for cover crops (default is 3)
Cover_Crops_Cost = ["5000"]                 # Cost of implementing cover crops per hectare (in Rs/ha)
Cover_Crops_Life_Span = ["2"]               # Lifespan of cover crops' effect (in years)
Cover_Crops_Eva_Red = ["56"]                # Reduction in evaporation due to cover crops (in %, default is 50%)(e.g., "50")

# Mulching
Kharif_Crop_Mulching_Area = []              # Area under mulching for Kharif crops (in hectares)
Rabi_Crop_Mulching_Area = []                # Area under mulching for Rabi crops (in hectares)
Summer_Crop_Mulching_Area = []              # Area under mulching for Summer crops (in hectares)
Red_CN_Mulching = ["4"]                     # Reduction in Curve Number (CN) for mulching (default is 2)
Mulching_Cost = ["100"]                     # Cost of mulching per hectare (in Rs/ha)
Mulching_Life_Span = ["1"]                  # Lifespan of mulching effect (in years)
Mulching_Eva_Red = ["55"]                   # Reduction in evaporation due to mulching (in %, default is 25%)(e.g., "50")

# Broad Bed and Furrow (BBF)
Kharif_Crop_BBF_Area = []                   # Area under BBF for Kharif crops (in hectares)
Rabi_Crop_BBF_Area = []                     # Area under BBF for Rabi crops (in hectares)
Summer_Crop_BBF_Area = []                   # Area under BBF for Summer crops (in hectares)
Red_CN_BBF = ["4"]                          # Reduction in Curve Number (CN) for BBF (default is 3)
BBF_Cost = ["100"]                          # Cost of BBF per hectare (in Rs/ha)
BBF_Life_Span = ["1"]                       # Lifespan of BBF effect (in years)
BBF_Maintenance = ["0"]                     # Annual maintenance cost in percentage(%)(e.g., "50")
Eff_BBF = ["25"]                            # Efficiency of BBF in terms of water saved (in %, default is 25%)(e.g., "50")

# Contour / Vegetative Bunds
Kharif_Crop_Bunds_Area = []                 # Area under bunds for Kharif crops (in hectares)
Rabi_Crop_Bunds_Area = []                   # Area under bunds for Rabi crops (in hectares)
Summer_Crop_Bunds_Area = []                 # Area under bunds for Summer crops (in hectares)
Bund_Cost = ["100"]
Red_CN_Bund = ["3"]                         # Reduction in Curve Number (CN) for bunds (default is 3)
Bund_Life_Span = ["2"]                      # Lifespan of bund effect (in years)
Bund_Maintenance = ["5"]                    # Annual maintenance cost in percentage(%)(e.g., "50")

# Conservation Tillage
Kharif_Crop_Tillage_Area = []               # Area under conservation tillage for Kharif crops (in hectares)
Rabi_Crop_Tillage_Area = []                 # Area under conservation tillage for Rabi crops (in hectares)
Summer_Crop_Tillage_Area = []               # Area under conservation tillage for Summer crops (in hectares)
Red_CN_Tillage = ["3"]                      # Reduction in Curve Number (CN) for conservation tillage (default is 3)
Tillage_Cost = ["2000"]                     # Cost of conservation tillage per hectare (in Rs/ha)
Tillage_Life_Span = ["1"]                   # Lifespan of tillage effect (in years)
Tillage_Eva_Red = ["3"]                     # Reduction in evaporation due to conservation tillage (in %, default is 0%)(e.g., "50")

# Tank Desilting
Kharif_Crop_Tank_Area = []                  # Area impacted by tank desilting for Kharif crops (in hectares)
Rabi_Crop_Tank_Area = []                    # Area impacted by tank desilting for Rabi crops (in hectares)
Summer_Crop_Tank_Area = []                  # Area impacted by tank desilting for Summer crops (in hectares)
Red_CN_Tank = ["3"]                         # Reduction in Curve Number (CN) for tank desilting (default is 3)
Tank_Desilting_Life_Span = ["4"]            # Lifespan of tank desilting effect (in years)
Tank_Eva_Red = ["50"]                       # Reduction in evaporation due to tank desilting (in %, default is 50%)(e.g., "50")
Tank_Desilting_Vol = ["0"]                  # Volume of desilting material removed (in cubic meters) #used in calc not asked on dashboard 
Tank_Desilting_Depth = ["0.2"]              # Depth of desilting (in meters) #used in calc not asked on dashboard 
Tank_Desilting_Cost = ["1000"]              # Cost of tank desilting per hectare (in Rs/ha) 

# =============================================================================
# Fixed Input (Only change if needed)
# =============================================================================

# General Parameters
slope = 0                                  # Average land slope (default value is 15)
Soil_GWrecharge_coefficient = 0.13          # Soil-groundwater recharge coefficient (from Data Input Sheet: 13%)

# Available Water Capacity (AWC) for different soil types (in mm/m)
AWC_Sand = 90
AWC_Sandy_Loam = 125
AWC_Loam = 175
AWC_Clayey_Loam = 200
AWC_Clay = 215

# Soil Moisture with Practices (values represent % soil moisture retention)
Cover_Crops_SM_with_practice = 100          # Soil moisture retention with cover crops (%)
Mulching_SM_with_practice = 100             # Soil moisture retention with mulching (%)
BBF_SM_with_practice = 100                  # Soil moisture retention with broad bed and furrow (BBF) (%)
Bund_SM_with_practice = 100                 # Soil moisture retention with contour/vegetative bunds (%)
Tillage_SM_with_practice = 100              # Soil moisture retention with conservation tillage (%)
with_out_soil_con = 100                     # Soil moisture retention without soil conservation (%)

# Soil Water Parameters (in mm/m)
theta_FC = 420                              # Field capacity (the maximum amount of water soil can hold)
theta_WP = 300                              # Wilting point (the minimum water required by plants to avoid wilting)
Ze = 0.1                                    # Effective rooting depth for crops (in meters)

# Curve Numbers (CN2) for various land types
Builtup_cn2 = 90
WB_cn2 = 0
Pasture_cn2 = 79
Forest_cn2 = 70

# Initial abstraction (Ia) for Antecedent Moisture Conditions (AMC)
Ia_AMC1 = 0.2
Ia_AMC2 = 0.2
Ia_AMC3 = 0.2

# Storage and Recharge Parameters
Previous_Month_storage = 0                  # Initial storage from the previous month (in cubic meters)
Previous_Month_Rejected_Recharge = 0        # Initial rejected recharge from the previous month (in cubic meters)

# Irrigation Efficiency Parameters
Eff_Default_Irrigation = 50                 # Default irrigation efficiency (50%) for them SW_Area_Irr_Eff & GW_Area_Irr_Eff
Eff_Water_Saved_Area_without_Interventions = 0  # Efficiency of water saved without interventions

# Soil Moisture Deficit (SMD) for the first time step
SMDi_1 = 0                                 # Initial soil moisture deficit for the first time step

#Residual Storage - SW (cu.m) = check its values