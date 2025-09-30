"""
Drought proofing metrics for drought proofing tool outputs

This module contains functions for calculating drought proofing metrics:
- Drought proofing index calculations
- Drought metrics for calendar and crop years

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates drought proofing indices and metrics for evaluating intervention effectiveness
# ========================================
import pandas as pd


# drought_metrics.py - Function 001: Gets drought proofing index
# Interactions: pandas
def get_drought_proofness(df_yr):
    df_drought = pd.DataFrame({"Date": df_yr["Date"]})
    df_drought["Drought Proofing"] = df_yr["Drought Proofing"]
    return df_drought


# drought_metrics.py - Function 002: Gets drought proofing index for crop year
# Interactions: pandas
def get_drought_proofness_cyr(df_crop_yr):
    df_drought = pd.DataFrame({"Date": df_crop_yr["water_year"]})
    df_drought["Drought Proofing"] = df_crop_yr["Drought Proofing"]
    return df_drought