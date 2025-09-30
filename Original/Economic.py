
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:52:52 2024

@author: Dr. Jagadeesh, Consultant, IWMI
"""
import numpy as np
from user_input import collect_int_variables
from user_input import to_float


# Economic.py - Function 1: Calculates the number of intervention units needed based on economic life and lifespan
def calculate_number_of_units(current_economic_life, inp_life_spans):
    inp_life_spans = np.where(inp_life_spans == 0, np.nan, inp_life_spans)

    num_units = np.where(
        current_economic_life - np.array(inp_life_spans) <= 0,
        1,
        np.ceil(current_economic_life / np.array(inp_life_spans))
    )
    num_units = np.where(np.isnan(num_units) | np.isinf(num_units), 0, num_units)

    return num_units.astype(int).tolist()

# Economic.py - Function 2: Collects and structures supply-side intervention data including costs and specifications
def get_supplyside_int_data(economic_list,inp_source,master_path):
    user_input_vars = collect_int_variables(inp_source,master_path)
    interventions = [
        "Farm_Pond", "Farm_Pond_Lined", "Check_Dam", "Infiltration_Pond", "Injection_Wells"
    ]
    supply_side_int = {
        "Intervention": [intervention.replace("_", " ") for intervention in interventions],
        "Volume (Cu.m)/Area": [to_float(user_input_vars.get(f"{intervention}_Vol", 0)) for intervention in interventions],
        "Depth (m)": [to_float(user_input_vars.get(f"{intervention}_Depth", 0)) for intervention in interventions],
        "Infiltration Rate (mm/day)": [to_float(user_input_vars.get(f"{intervention}_Inf_Rate", 0)) for intervention in interventions],
        "Cost (Rs/Cu.m)": [to_float(user_input_vars.get(f"{intervention}_Cost", 0)) for intervention in interventions],
        "Life Span (years)": [to_float(user_input_vars.get(f"{intervention}_Life_Span", 0)) for intervention in interventions],
        "Maintenance (%)": [to_float(user_input_vars.get(f"{intervention}_Maintenance", 0)) for intervention in interventions],
        }

    life_spans = np.array(supply_side_int["Life Span (years)"])
    current_economic_life = economic_list[1]
    supply_side_int["Number of Units"] = calculate_number_of_units(current_economic_life, life_spans)
    
    return supply_side_int



# Economic.py - Function 3: Collects and structures demand-side intervention data from crop calendar areas
def get_demandside_int_data(df_cc, economic_list,inp_source,master_path):
    user_input_vars = collect_int_variables(inp_source,master_path)
    interventions = ["Drip_Irr", "Sprinkler_Irr", "Land_Levelling", "Direct_Seeded_Rice",
                     "Alternate_Wetting_And_Dry", "SRI",
                     "Ridge_Furrow_Irrigation", "Deficit_Irrigation"]

    demand_volume = [
        df_cc["Drip_Area"].sum(),
        df_cc["Sprinkler_Area"].sum(),
        df_cc["Land_Levelling_Area"].sum(),
        df_cc["DSR_Area"].sum(),
        df_cc["AWD_Area"].sum(),
        df_cc["SRI_Area"].sum(),
        df_cc["Ridge_Furrow_Area"].sum(),
        df_cc["Deficit_Area"].sum()
    ]

    demand_side_int = {
        "Intervention": [intervention.replace("_", " ") for intervention in interventions],
        "Volume (Cu.m)/Area": demand_volume, 
        "Depth (m)": [0] * len(interventions), 
        "Infiltration Rate (mm/day)": [0] * len(interventions),
        "Cost (Rs/Cu.m)": [to_float(user_input_vars.get(f"{intervention}_Cost", 0)) for intervention in interventions],
        "Life Span (years)": [to_float(user_input_vars.get(f"{intervention}_Life_Span", 0)) for intervention in interventions],
        "Maintenance (%)": [to_float(user_input_vars.get(f"{intervention}_Maintenance", 0)) for intervention in interventions],
    }

    life_spans = np.array(demand_side_int["Life Span (years)"])
    current_economic_life = economic_list[1]
    demand_side_int["Number of Units"] = calculate_number_of_units(current_economic_life, life_spans)
    return demand_side_int


# Economic.py - Function 4: Collects and structures soil moisture intervention data from crop calendar areas
def get_soil_moistureside_int_data(df_cc, economic_list,inp_source,master_path):
    user_input_vars = collect_int_variables(inp_source,master_path)
    interventions = ["Cover_Crops", "Mulching", "BBF", "Bund",
                     "Tillage", "Tank_Desilting"]

    soil_moisture_volume = [
        df_cc["Cover_Area"].sum(),
        df_cc["Mulching_Area"].sum(),
        df_cc["BBF_Area"].sum(),
        df_cc["Bunds_Area"].sum(),
        df_cc["Tillage_Area"].sum(),
        df_cc["Tank_Area"].sum()
    ]
    soil_moisture_int = {
        "Intervention": [intervention.replace("_", " ") for intervention in interventions],
        "Volume (Cu.m)/Area": soil_moisture_volume, 
        "Depth (m)": [0] * len(interventions), 
        "Infiltration Rate (mm/day)": [0] * len(interventions),
        "Cost (Rs/Cu.m)": [to_float(user_input_vars.get(f"{intervention}_Cost", 0)) for intervention in interventions],
        "Life Span (years)": [to_float(user_input_vars.get(f"{intervention}_Life_Span", 0)) for intervention in interventions],
        "Maintenance (%)": [to_float(user_input_vars.get(f"{intervention}_Maintenance", 0)) for intervention in interventions],
    }
    
    life_spans = np.array(soil_moisture_int["Life Span (years)"])
    current_economic_life = economic_list[1]
    soil_moisture_int["Number of Units"] = calculate_number_of_units(current_economic_life, life_spans)
    return soil_moisture_int


# Economic.py - Function 5: Combines supply-side, demand-side, and soil moisture intervention data into unified dataset
def create_intervention_data(supply_side_int, demand_side_int, soil_moisture_int):
    # Combine supply-side, demand-side, and soil moisture interventions
    combined_data = {
        key: supply_side_int[key] + demand_side_int[key] + soil_moisture_int[key]
        for key in supply_side_int.keys()
    }
    return combined_data


# Economic.py - Function 6: Calculates total cost by multiplying volume and unit cost
def calc_cost(v, c):
    return v * c


# Economic.py - Function 7: Calculates Equalized Annual Cost using capital recovery factor
def calculate_eac(total_capital_cost, interest_rate, time_period):
    # Check for zero values that might cause division by zero
    if interest_rate == 0:
        raise ValueError("Interest rate cannot be 0 to avoid division by zero.")
    if time_period == 0:
        raise ValueError("Time period cannot be 0 to avoid division by zero.")
    return (total_capital_cost * (interest_rate / 100)) / (1 - (1 + (interest_rate / 100)) ** (-time_period))


# Economic.py - Function 8: Calculates annual maintenance costs based on percentage of equalized annual cost
def calculate_maintenance_cost(df, time_period):
    # Ensure "Equalized Annual Cost" and "Maintenance (%)" columns exist in the DataFrame
    if "Equalized Annual Cost" not in df.columns or "Maintenance (%)" not in df.columns:
        raise ValueError("DataFrame must contain 'Equalized Annual Cost' and 'Maintenance (%)' columns")
    # Calculate Maintenance Cost
    df["Maintenance Cost"] = df["Equalized Annual Cost"] * (df["Maintenance (%)"] / 100) * time_period
    return df


# Economic.py - Function 9: Calculates Net Present Value of intervention costs over project lifetime
def calc_npv(maintenance_cost, equalized_annual_cost, interest_rate, time_period):
    return maintenance_cost + (1 - (1 / ((1 + (interest_rate / 100)) ** time_period))) * (
                equalized_annual_cost / (interest_rate / 100))
