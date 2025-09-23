"""
Precipitation processing functions for surface water bucket

This module contains functions for processing precipitation data:
- Net rainfall calculations after removing groundwater recharge

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Processes precipitation data by calculating net rainfall after accounting for groundwater recharge
# ========================================


# precipitation_processing.py - Function 001: Calculates net rainfall after removing groundwater recharge
# Interactions: None
def get_rain_src_model(pi, recharge_src):
    rain = pi - recharge_src
    return rain