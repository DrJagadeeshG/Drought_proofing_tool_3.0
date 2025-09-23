"""
Groundwater storage tracking for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Tracks groundwater storage levels and calculates residual storage capacity
# ========================================
from shared.utilities import to_float


# storage_tracking.py - Function 001: Calculates residual groundwater storage
# Interactions: shared.utilities.to_float
def calc_storage_residualgw(df_mm,aquifer_para_list):
    
    df_mm.loc[0, "Residual_storage"] = to_float(aquifer_para_list[2], 0) * (
        to_float(aquifer_para_list[1], 0) / 100) * to_float(
            aquifer_para_list[3], 0) * 10000

    return df_mm