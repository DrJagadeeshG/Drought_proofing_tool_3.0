"""
Surface water balance calculations for surface water bucket

This module contains functions for calculating surface water balance:
- Remaining water calculations after domestic use
- Final runoff calculations including rejected recharge

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates surface water balance including domestic use abstractions and final runoff components
# ========================================


# water_balance.py - Function 001: Calculates remaining water after domestic surface water use
# Interactions: None
def calc_value_after_subtracting_domestic_sw_use(df_mm):
    df_mm["value_after_subtracting_domestic_SW_use"] = df_mm["Qom(m^3)"] - df_mm["SW_abstracted"]
    return df_mm


# water_balance.py - Function 002: Calculates final runoff including rejected recharge
# Interactions: None
def calc_final_runoff(df_mm):
    df_mm["Final_Runoff"] = df_mm["final_ro"] + df_mm["Rejected_recharge_mm"]
    return df_mm