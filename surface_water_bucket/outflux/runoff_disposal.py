"""
Final runoff disposal functions for surface water bucket

This module contains functions for calculating final runoff disposal:
- Final runoff calculations after storage

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates final runoff disposal after accounting for captured runoff in storage structures
# ========================================


# runoff_disposal.py - Function 001: Calculates final runoff after storage
# Interactions: None
def calc_final_ro(df_mm):
    df_mm["final_ro"] = (df_mm["Qom"] - df_mm["Captured Runoff in m³_mm"]).clip(lower=0)
    return df_mm