"""
Surface area calculations for surface water bucket

This module contains functions for calculating surface area:
- Surface area calculations from volume and depth

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates surface areas from volume and depth parameters for water storage structures
# ========================================
from shared.utilities import to_float


# surface_calculations.py - Function 001: Calculates surface area from volume and depth
# Interactions: shared.utilities.to_float
def calc_surface_area(vol, depth):
    vol = to_float(vol, 0)
    depth = to_float(depth, 0)
    # Check if both vol and depth are 0
    if vol == 0 and depth == 0:
        return 0
    # Prevent division by zero
    if depth == 0:
        raise ValueError("Depth cannot be zero unless volume is also zero.")
    return vol / depth