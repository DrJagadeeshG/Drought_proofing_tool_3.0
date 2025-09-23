"""
Water supply availability functions for surface water bucket

This module contains functions for calculating water supply availability:
- Canal water supply availability calculations

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates water supply availability from external sources like canals
# ========================================
import numpy as np


# water_supply.py - Function 001: Calculates canal water supply availability
# Interactions: numpy
def calc_canal_supply(df_ir, df_mm):
    def get_canal_supply(row):
        month_index = row.name % 12
        value = df_ir.loc[month_index, "Canal_WA"]
        return 0 if np.isnan(value) else value

    df_mm["Canal_supply"] = df_mm.apply(get_canal_supply, axis=1)
    return df_mm