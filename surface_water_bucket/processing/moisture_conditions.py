"""
Antecedent moisture conditions for surface water bucket

This module contains functions for calculating antecedent moisture conditions:
- Moisture condition calculations based on rainfall and dormancy

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates antecedent moisture conditions based on rainfall patterns and crop dormancy status
# ========================================
import numpy as np


# moisture_conditions.py - Function 001: Calculates antecedent moisture condition based on rainfall and dormancy
# Interactions: numpy
def calc_amc_cond(df_dd, df_crop):
    conditions = [
        (df_crop["Dormant"] == "N") & (df_dd["last_5_days_Rain"] < 36),
        (df_crop["Dormant"] == "N") & (df_dd["last_5_days_Rain"] > 53),
        (df_crop["Dormant"] == "N"),
        (df_dd["last_5_days_Rain"] < 13),
        (df_dd["last_5_days_Rain"] > 28)
    ]

    choices = [1, 3, 2, 1, 3]

    amc_cond = np.select(conditions, choices, default=2)
    return amc_cond