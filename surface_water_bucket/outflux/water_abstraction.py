"""
Water abstraction functions for surface water bucket

This module contains functions for calculating water abstraction:
- Abstracted surface water calculations

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates abstracted surface water based on available runoff and water needs
# ========================================
import numpy as np


# water_abstraction.py - Function 001: Calculates abstracted surface water
# Interactions: numpy
def calc_sw_abstracted(df_mm):
    conditions = [
        df_mm["Qom(m^3)"] - df_mm["SW_need"] < 0,
        df_mm["Qom(m^3)"] - df_mm["SW_need"] >= df_mm["SW_need"]
    ]

    choices = [df_mm["Qom(m^3)"], df_mm["SW_need"]]

    df_mm["SW_abstracted"] = np.select(conditions, choices, default=df_mm["Qom(m^3)"] - df_mm["SW_need"])
    return df_mm