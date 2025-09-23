"""
Aquifer storage capacity calculations for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates aquifer storage capacity limits based on depth, specific yield, and area parameters
# ========================================
from shared.utilities import to_float


# storage_capacity.py - Function 001: Calculates aquifer storage limit based on parameters
# Interactions: shared.utilities.to_float
def calculate_storage_limit(aquifer_para_list):
    aquifer_depth = to_float(aquifer_para_list[0], 0)
    specific_yield = to_float(aquifer_para_list[2], 0)
    total_area = to_float(aquifer_para_list[3], 0)
    storage_limit = aquifer_depth * (specific_yield / 100) * total_area * 10000
    return storage_limit