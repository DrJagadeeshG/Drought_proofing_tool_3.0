"""
Surface water demand functions for surface water bucket

This module contains functions for calculating surface water demand:
- Surface water needs calculations

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates surface water demand requirements for domestic and other uses
# ========================================


# water_demand.py - Function 001: Calculates surface water needs
# Interactions: None
def calc_sw_need(df_mm):
    df_mm["SW_need"] = df_mm["Domestic_need"] + df_mm["Other_need"] - df_mm["GW_need"]
    return df_mm