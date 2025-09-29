"""
Input data collection and organization for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Collects and organizes all input and intervention variables from various sources into structured dictionaries
# ========================================

from shared.input_utilities import (
    get_kei_value, get_variable_value, get_crops_variable_values,
    get_supply_side_int_values, get_demand_side_interv_area_values,
    get_demand_side_interv_values, get_soil_moisture_interv_area_values,
    get_soil_moisture_interv_values
)


# input_collector.py - Function 001: Collects and organizes all input variables into ordered dictionary
# Interactions: shared.input_utilities.get_kei_value, shared.input_utilities.get_variable_value, shared.input_utilities.get_crops_variable_values
def collect_inp_variables(inp_source,master_path):
    variables_list = [
        # (index, "variable_name", function_call)
        (1, "kei", lambda: get_kei_value(get_variable_value(inp_source,master_path,"climate", 1))),
        
        # Kharif Crops
        (16, "Kharif_Crops", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Crops", 16)),
        (17, "Kharif_Sowing_Month", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Sowing_Month", 17)),
        (18, "Kharif_Sowing_Week", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Sowing_Week", 18)),
        (19, "Kharif_Crops_Irr_Area", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Crops_Irr_Area", 19)),
        (20, "Kharif_Crops_Rainfed_Area", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Crops_Rainfed_Area", 20)),
        (21, "Kharif_Crops_Area", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Crops_Area", 21)),
        (22, "Kharif_Crops_Type", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Crops_Type", 22)),
        (23, "Kharif_Crop_Sown_Type", lambda: get_crops_variable_values(inp_source,master_path,"Kharif_Crop_Sown_Type", 23)),
        
        # Rabi Crops
        (24, "Rabi_Crops", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Crops", 24)),
        (25, "Rabi_Sowing_Month", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Sowing_Month", 25)),
        (26, "Rabi_Sowing_Week", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Sowing_Week", 26)),
        (27, "Rabi_Crops_Irr_Area", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Crops_Irr_Area", 27)),
        (28, "Rabi_Crops_Rainfed_Area", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Crops_Rainfed_Area", 28)),
        (29, "Rabi_Crops_Area", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Crops_Area", 29)),
        (30, "Rabi_Crops_Type", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Crops_Type", 30)),
        (31, "Rabi_Crop_Sown_Type", lambda: get_crops_variable_values(inp_source,master_path,"Rabi_Crop_Sown_Type", 31)),
        
        # Summer Crops
        (32, "Summer_Crops", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Crops", 32)),
        (33, "Summer_Sowing_Month", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Sowing_Month", 33)),
        (34, "Summer_Sowing_Week", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Sowing_Week", 34)),
        (35, "Summer_Crops_Irr_Area", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Crops_Irr_Area", 35)),
        (36, "Summer_Crops_Rainfed_Area", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Crops_Rainfed_Area", 36)),
        (37, "Summer_Crops_Area", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Crops_Area", 37)),
        (38, "Summer_Crops_Type", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Crops_Type", 38)),
        (39, "Summer_Crop_Sown_Type", lambda: get_crops_variable_values(inp_source,master_path,"Summer_Crop_Sown_Type", 39)),
        
        # General Variables
        (0, "latitude", lambda: get_variable_value(inp_source,master_path,"latitude", 0)),
        # (1, "climate", lambda: get_variable_value("climate", 1)),
        (2, "Soil_type1", lambda: get_variable_value(inp_source,master_path,"Soil_type1", 2)),
        (3, "Soil_type2", lambda: get_variable_value(inp_source,master_path,"Soil_type2", 3)),
        (4, "HSC1", lambda: get_variable_value(inp_source,master_path,"HSC1", 4)),
        (5, "HSC2", lambda: get_variable_value(inp_source,master_path,"HSC2", 5)),
        (6, "dist1", lambda: get_variable_value(inp_source,master_path,"dist1", 6)),
        (7, "dist2", lambda: get_variable_value(inp_source,master_path,"dist2", 7)),
        (8, "Soil_type1_dep", lambda: get_variable_value(inp_source,master_path,"Soil_type1_dep", 8)),
        (9, "Soil_type2_dep", lambda: get_variable_value(inp_source,master_path,"Soil_type2_dep", 9)),
        (10, "Net_Crop_Sown_Area", lambda: get_variable_value(inp_source,master_path,"Net_Crop_Sown_Area", 10)),
        (11, "Fallow", lambda: get_variable_value(inp_source,master_path,"Fallow", 11)),
        (12, "Builtup", lambda: get_variable_value(inp_source,master_path,"Builtup", 12)),
        (13, "Water_bodies", lambda: get_variable_value(inp_source,master_path,"Water_bodies", 13)),
        (14, "Pasture", lambda: get_variable_value(inp_source,master_path,"Pasture", 14)),
        (15, "Forest", lambda: get_variable_value(inp_source,master_path,"Forest", 15)),
        (40, "SW_Area", lambda: get_variable_value(inp_source,master_path,"SW_Area", 40)),
        (41, "SW_Area_Irr_Eff", lambda: get_variable_value(inp_source,master_path,"SW_Area_Irr_Eff", 41)),
        (42, "GW_Area", lambda: get_variable_value(inp_source,master_path,"GW_Area", 42)),
        (43, "GW_Area_Irr_Eff", lambda: get_variable_value(inp_source,master_path,"GW_Area_Irr_Eff", 43)),
        (44, "Aquifer_Depth", lambda: get_variable_value(inp_source,master_path,"Aquifer_Depth", 44)),
        (45, "Starting_Level", lambda: get_variable_value(inp_source,master_path,"Starting_Level", 45)),
        (46, "Specific_Yield", lambda: get_variable_value(inp_source,master_path,"Specific_Yield", 46)),
        (47, "Population", lambda: get_variable_value(inp_source,master_path,"Population", 47)),
        (48, "Domestic_Water_Use", lambda: get_variable_value(inp_source,master_path,"Domestic_Water_Use", 48)),
        (49, "Groundwater_Dependent", lambda: get_variable_value(inp_source,master_path,"Groundwater_Dependent", 49)),
        (50, "Surface_Water_Dependent", lambda: get_variable_value(inp_source,master_path,"Surface_Water_Dependent", 50)),
        (51, "Other", lambda: get_variable_value(inp_source,master_path,"Other", 51)),
        (52, "Other_Water_Use", lambda: get_variable_value(inp_source,master_path,"Other_Water_Use", 52)),
        
    ]
    # Sort the list based on indices
    variables_list.sort(key=lambda x: x[0])
    # Create the ordered dictionary
    variables_dict = {}
    for index, var_name, func in variables_list:
        variables_dict[var_name] = func()
    return variables_dict


# input_collector.py - Function 002: Collects and organizes all intervention variables into ordered dictionary
# Interactions: shared.input_utilities.get_supply_side_int_values, shared.input_utilities.get_demand_side_interv_area_values, shared.input_utilities.get_demand_side_interv_values, shared.input_utilities.get_soil_moisture_interv_area_values, shared.input_utilities.get_soil_moisture_interv_values
def collect_int_variables(inp_source,master_path, scenario_num=0):
    variables_list = [
        (0, "Time_Period", lambda: get_supply_side_int_values(inp_source,master_path,"Time_Period", 0, scenario_num)),
        (1, "Interest_Rate", lambda: get_supply_side_int_values(inp_source,master_path,"Interest_Rate", 1, scenario_num)),
        
        (2, "Farm_Pond_Vol", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Vol", 2, scenario_num)),
        (3, "Farm_Pond_Depth", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Depth", 3, scenario_num)),
        (4, "Farm_Pond_Inf_Rate", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Inf_Rate", 4, scenario_num)),
        (5, "Farm_Pond_Cost", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Cost", 5, scenario_num)),
        (6, "Farm_Pond_Life_Span", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Life_Span", 6, scenario_num)),
        (7, "Farm_Pond_Maintenance", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Maintenance", 7, scenario_num)),
        
        (8, "Farm_Pond_Lined_Vol", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Lined_Vol", 8, scenario_num)),
        (9, "Farm_Pond_Lined_Depth", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Lined_Depth", 9, scenario_num)),
        (10, "Farm_Pond_Lined_Inf_Rate", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Lined_Inf_Rate", 10, scenario_num)),
        (11, "Farm_Pond_Lined_Cost", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Lined_Cost", 11, scenario_num)),
        (12, "Farm_Pond_Lined_Life_Span", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Lined_Life_Span", 12, scenario_num)),
        (13, "Farm_Pond_Lined_Maintenance", lambda: get_supply_side_int_values(inp_source,master_path,"Farm_Pond_Lined_Maintenance", 13, scenario_num)),
        
        (14, "Check_Dam_Vol", lambda: get_supply_side_int_values(inp_source,master_path,"Check_Dam_Vol", 14, scenario_num)),
        (15, "Check_Dam_Depth", lambda: get_supply_side_int_values(inp_source,master_path,"Check_Dam_Depth", 15, scenario_num)),
        (16, "Check_Dam_Inf_Rate", lambda: get_supply_side_int_values(inp_source,master_path,"Check_Dam_Inf_Rate", 16, scenario_num)),
        (17, "Check_Dam_Cost", lambda: get_supply_side_int_values(inp_source,master_path,"Check_Dam_Cost", 17, scenario_num)),
        (18, "Check_Dam_Life_Span", lambda: get_supply_side_int_values(inp_source,master_path,"Check_Dam_Life_Span", 18, scenario_num)),
        (19, "Check_Dam_Maintenance", lambda: get_supply_side_int_values(inp_source,master_path,"Check_Dam_Maintenance", 19, scenario_num)),
        
        (20, "Infiltration_Pond_Vol", lambda: get_supply_side_int_values(inp_source,master_path,"Infiltration_Pond_Vol", 20, scenario_num)),
        (21, "Infiltration_Pond_Depth", lambda: get_supply_side_int_values(inp_source,master_path,"Infiltration_Pond_Depth", 21, scenario_num)),
        (22, "Infiltration_Pond_Inf_Rate", lambda: get_supply_side_int_values(inp_source,master_path,"Infiltration_Pond_Inf_Rate", 22, scenario_num)),
        (23, "Infiltration_Pond_Cost", lambda: get_supply_side_int_values(inp_source,master_path,"Infiltration_Pond_Cost", 23, scenario_num)),
        (24, "Infiltration_Pond_Life_Span", lambda: get_supply_side_int_values(inp_source,master_path,"Infiltration_Pond_Life_Span", 24, scenario_num)),
        (25, "Infiltration_Pond_Maintenance", lambda: get_supply_side_int_values(inp_source,master_path,"Infiltration_Pond_Maintenance", 25, scenario_num)),
        
        (26, "Injection_Wells_Vol", lambda: get_supply_side_int_values(inp_source,master_path,"Injection_Wells_Vol", 26, scenario_num)),
        (27, "Injection_Wells_Nos", lambda: get_supply_side_int_values(inp_source,master_path,"Injection_Wells_Nos", 27, scenario_num)),
        (28, "Injection_Wells_Cost", lambda: get_supply_side_int_values(inp_source,master_path,"Injection_Wells_Cost", 28, scenario_num)),
        (29, "Injection_Wells_Life_Span", lambda: get_supply_side_int_values(inp_source,master_path,"Injection_Wells_Life_Span", 29, scenario_num)),
        (30, "Injection_Wells_Maintenance", lambda: get_supply_side_int_values(inp_source,master_path,"Injection_Wells_Maintenance", 30, scenario_num)),
        
        # Direct plot-based intervention areas (no seasonal breakdown)
        (31, "Drip_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Drip_Area", 31, scenario_num)),
        (32, "Eff_Drip_irrigation", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Drip_irrigation", 32, scenario_num)),
        
        (33, "Sprinkler_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Sprinkler_Area", 33, scenario_num)),
        (34, "Eff_Sprinkler_irrigation", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Sprinkler_irrigation", 34, scenario_num)),
        
        (35, "Land_Levelling_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Land_Levelling_Area", 35, scenario_num)),
        (36, "Eff_Land_Levelling", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Land_Levelling", 36, scenario_num)),
        
        (37, "DSR_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"DSR_Area", 37, scenario_num)),
        (38, "Eff_Direct_Seeded_Rice", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Direct_Seeded_Rice", 38, scenario_num)),
        
        (39, "AWD_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"AWD_Area", 39, scenario_num)),
        (40, "Eff_Alternate_Wetting_And_Dry", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Alternate_Wetting_And_Dry", 40, scenario_num)),
        
        (41, "SRI_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"SRI_Area", 41, scenario_num)),
        (42, "Eff_SRI", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_SRI", 42, scenario_num)),
        
        (43, "Ridge_Furrow_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Ridge_Furrow_Area", 43, scenario_num)),
        (44, "Eff_Ridge_Furrow_Irrigation", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Ridge_Furrow_Irrigation", 44, scenario_num)),
        
        (45, "Deficit_Area", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Deficit_Area", 45, scenario_num)),
        (46, "Eff_Deficit_Irrigation", lambda: get_demand_side_interv_area_values(inp_source,master_path,"Eff_Deficit_Irrigation", 46, scenario_num)),
        
        # Costs and Lifespan variables
        (47, "Drip_Irr_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Drip_Irr_Cost", 47, scenario_num)),
        (48, "Drip_Irr_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Drip_Irr_Life_Span", 48, scenario_num)),
        (49, "Drip_Irr_Maintenance", lambda: get_demand_side_interv_values(inp_source,master_path,"Drip_Irr_Maintenance", 49, scenario_num)),
        
        (50, "Sprinkler_Irr_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Sprinkler_Irr_Cost", 50, scenario_num)),
        (51, "Sprinkler_Irr_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Sprinkler_Irr_Life_Span", 51, scenario_num)),
        (52, "Sprinkler_Irr_Maintenance", lambda: get_demand_side_interv_values(inp_source,master_path,"Sprinkler_Irr_Maintenance", 52, scenario_num)),
        
        (53, "Land_Levelling_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Land_Levelling_Cost", 53, scenario_num)),
        (54, "Land_Levelling_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Land_Levelling_Life_Span", 54, scenario_num)),
        (55, "Land_Levelling_Maintenance", lambda: get_demand_side_interv_values(inp_source,master_path,"Land_Levelling_Maintenance", 55, scenario_num)),
        
        (56, "Direct_Seeded_Rice_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Direct_Seeded_Rice_Cost", 56, scenario_num)),
        (57, "Direct_Seeded_Rice_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Direct_Seeded_Rice_Life_Span", 57, scenario_num)),
        
        (58, "Alternate_Wetting_And_Dry_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Alternate_Wetting_And_Dry_Cost", 58, scenario_num)),
        (59, "Alternate_Wetting_And_Dry_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Alternate_Wetting_And_Dry_Life_Span", 59, scenario_num)),
        
        (60, "SRI_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"SRI_Cost", 60, scenario_num)),
        (61, "SRI_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"SRI_Life_Span", 61, scenario_num)),
        
        (62, "Ridge_Furrow_Irrigation_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Ridge_Furrow_Irrigation_Cost", 62, scenario_num)),
        (63, "Ridge_Furrow_Irrigation_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Ridge_Furrow_Irrigation_Life_Span", 63, scenario_num)),
        
        (64, "Deficit_Irrigation_Cost", lambda: get_demand_side_interv_values(inp_source,master_path,"Deficit_Irrigation_Cost", 64, scenario_num)),
        (65, "Deficit_Irrigation_Life_Span", lambda: get_demand_side_interv_values(inp_source,master_path,"Deficit_Irrigation_Life_Span", 65, scenario_num)),
        
        # Soil moisture intervention variables - direct plot-based areas (no seasonal breakdown)
        (66, "Cover_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Cover_Area", 66, scenario_num)),
        (67, "Mulching_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Mulching_Area", 67, scenario_num)),
        (68, "BBF_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"BBF_Area", 68, scenario_num)),
        (69, "Bunds_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Bunds_Area", 69, scenario_num)),
        (70, "Tillage_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Tillage_Area", 70, scenario_num)),
        (71, "Tank_Area", lambda: get_soil_moisture_interv_area_values(inp_source,master_path,"Tank_Area", 71, scenario_num)),
        
        (85, "Red_CN_Cover_Crops", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Red_CN_Cover_Crops", 85, scenario_num)),
        (86, "Cover_Crops_Cost", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Cover_Crops_Cost", 86, scenario_num)),
        (87, "Cover_Crops_Life_Span", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Cover_Crops_Life_Span", 87, scenario_num)),
        (88, "Cover_Crops_Eva_Red", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Cover_Crops_Eva_Red", 88, scenario_num)),
        
        (92, "Red_CN_Mulching", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Red_CN_Mulching", 92, scenario_num)),
        (93, "Mulching_Cost", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Mulching_Cost", 93, scenario_num)),
        (94, "Mulching_Life_Span", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Mulching_Life_Span", 94, scenario_num)),
        (95, "Mulching_Eva_Red", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Mulching_Eva_Red", 95, scenario_num)),
        
        (99, "Red_CN_BBF", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Red_CN_BBF", 99, scenario_num)),
        (100, "BBF_Cost", lambda: get_soil_moisture_interv_values(inp_source,master_path,"BBF_Cost", 100, scenario_num)),
        (101, "BBF_Life_Span", lambda: get_soil_moisture_interv_values(inp_source,master_path,"BBF_Life_Span", 101, scenario_num)),
        (102, "BBF_Maintenance", lambda: get_soil_moisture_interv_values(inp_source,master_path,"BBF_Maintenance", 102, scenario_num)),
        (103, "Eff_BBF", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Eff_BBF", 103, scenario_num)),
        
        (107, "Red_CN_Bund", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Red_CN_Bund", 107, scenario_num)),
        (108, "Bund_Cost", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Bund_Cost", 108, scenario_num)),
        (109, "Bund_Life_Span", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Bund_Life_Span", 109, scenario_num)),
        (110, "Bund_Maintenance", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Bund_Maintenance", 110, scenario_num)),
        
        (114, "Red_CN_Tillage", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Red_CN_Tillage", 114, scenario_num)),
        (115, "Tillage_Cost", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tillage_Cost", 115, scenario_num)),
        (116, "Tillage_Life_Span", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tillage_Life_Span", 116, scenario_num)),
        (117, "Tillage_Eva_Red", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tillage_Eva_Red", 117, scenario_num)),
        
        (121, "Red_CN_Tank", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Red_CN_Tank", 121, scenario_num)),
        (122, "Tank_Desilting_Life_Span", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tank_Desilting_Life_Span", 122, scenario_num)),
        (123, "Tank_Eva_Red", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tank_Eva_Red", 123, scenario_num)),
        (124, "Tank_Desilting_Vol", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tank_Desilting_Vol", 124, scenario_num)),
        (125, "Tank_Desilting_Depth", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tank_Desilting_Depth", 125, scenario_num)),
        (126, "Tank_Desilting_Cost", lambda: get_soil_moisture_interv_values(inp_source,master_path,"Tank_Desilting_Cost", 126, scenario_num)),
        ]
        
    # Sort the list based on indices
    variables_list.sort(key=lambda x: x[0])

    # Create the ordered dictionary
    variables_dict = {}
    for index, var_name, func in variables_list:
        variables_dict[var_name] = func()

    return variables_dict