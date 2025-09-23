"""
Soil properties and AWC calculations for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates soil properties including available water content and weighted capacity for different soil layers
# ========================================
from shared.utilities import to_float
from orchestrator.input_collector import collect_inp_variables


# soil_properties.py - Function 001: Calculates soil properties including AWC and depths
# Interactions: orchestrator.input_collector.collect_inp_variables, get_soil_type, calculate_awc
def soil_calculation(inp_source,master_path):
    inp_vars = collect_inp_variables(inp_source,master_path)

    soil_type1 = get_soil_type(inp_vars["Soil_type1"])
    soil_type2 = get_soil_type(inp_vars["Soil_type2"])
    hsc1 = get_soil_type(inp_vars["HSC1"])
    hsc2 = get_soil_type(inp_vars["HSC2"])
    awc_1 = calculate_awc(soil_type1)
    awc_2 = calculate_awc(soil_type2) if soil_type2 else None
    dist1 = inp_vars["dist1"]
    dist2 = inp_vars["dist2"]
    soil_type1_dep = inp_vars["Soil_type1_dep"]
    soil_type2_dep = inp_vars["Soil_type2_dep"]
    
    loc_soil_list = [awc_1, awc_2, hsc1, hsc2, soil_type1, soil_type2, dist1, dist2, soil_type1_dep, soil_type2_dep]
    return loc_soil_list


# soil_properties.py - Function 002: Returns available water content based on soil type classification
# Interactions: None
def calculate_awc(soil_type):
    awc_values = {
        "Sand": 90,
        "Sandy Loam": 125,
        "Loam": 175,
        "Clayey Loam": 200,
        "Clay": 215
    }

    awc = awc_values.get(soil_type)
    if awc is None:
        raise ValueError("Unknown soil type")
    return awc


# soil_properties.py - Function 003: Extracts and validates soil type from input data structure
# Interactions: None
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


# soil_properties.py - Function 004: Calculates weighted average water content capacity for mixed soil layers
# Interactions: shared.utilities.to_float
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