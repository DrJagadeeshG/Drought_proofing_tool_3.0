"""
Soil moisture deficit calculations for soil storage bucket

This module contains functions for calculating soil moisture deficit:
- SMD calculations for each plot
- SMD calculations using water balance approach
- SMD calculations for fallow land areas

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates soil moisture deficit using water balance approach for different plots and crops
# ========================================

import numpy as np
import pandas as pd
from soil_storage_bucket.processing.water_stress import calc_ks_soil_cond, calc_ks_soil, calc_ks_crop_cond, calc_ks_crop
from soil_storage_bucket.outflux.evapotranspiration import calc_ae_soil, calc_ae_crop, calc_ae_per_crop
from aquifer_storage_bucket.influx.recharge_calculations import update_gwnr


# soil_moisture_deficit.py - Function 001: Calculates soil moisture deficit index for each plot
# Interactions: soil_storage_bucket.processing.water_stress.calc_ks_soil_cond, soil_storage_bucket.processing.water_stress.calc_ks_soil, soil_storage_bucket.processing.water_stress.calc_ks_crop_cond, soil_storage_bucket.processing.water_stress.calc_ks_crop, soil_storage_bucket.outflux.evapotranspiration.calc_ae_soil, soil_storage_bucket.outflux.evapotranspiration.calc_ae_crop, calc_smd, soil_storage_bucket.outflux.evapotranspiration.calc_ae_per_crop, aquifer_storage_bucket.influx.recharge_calculations.update_gwnr, pandas, numpy
def calc_smdi_plot(df_crop, df_dd, valid_crops_df, all_plots, smdi_1):
    print("FUNCTION 18: calc_smdi_plot() - Calculating soil moisture deficit for each plot")
    smdi_shifted_dict = {}
    smdi_dict = {}

    for plot in all_plots:
        # Initialize the first value and store it in the dictionary
        smdi_shifted_dict[f"SMDi_shifted_{plot}"] = [smdi_1] + [0] * (len(df_crop) - 1)
        # Create an array of zeros for SMDi_{plot}
        smdi_dict[f"SMDi_{plot}"] = np.zeros(len(df_crop), dtype=np.float32)

    # Convert dictionaries to DataFrames
    smdi_shifted_df = pd.DataFrame(smdi_shifted_dict, dtype=np.float32)
    smdi_df = pd.DataFrame(smdi_dict)

    # Assign the new columns to df_crop at once
    df_crop = pd.concat([df_crop, smdi_shifted_df, smdi_df], axis=1)
    for plot in all_plots:
        for i in range(len(df_crop)):
            if i > 0:
                df_crop.loc[i, f"SMDi_shifted_{plot}"] = df_crop.loc[i - 1, f"SMDi_{plot}"]

            df_crop.loc[i, f"Ks_soil_cond_{plot}"] = calc_ks_soil_cond(df_crop.loc[i, f"Kei_{plot}"],
                                                                       df_crop.loc[i, f"SMDi_shifted_{plot}"],
                                                                       df_crop.loc[i, f"REWi_{plot}"],
                                                                       df_crop.loc[i, f"TEWi_{plot}"])

            df_crop.loc[i, f"Ks_soil_{plot}"] = calc_ks_soil(df_crop.loc[i, f"Ks_soil_cond_{plot}"],
                                                             df_crop.loc[i, f"TEWi_{plot}"],
                                                             df_crop.loc[i, f"SMDi_shifted_{plot}"],
                                                             df_crop.loc[i, f"REWi_{plot}"])

            df_crop.loc[i, f"AE_soil_{plot}"] = calc_ae_soil(df_dd.loc[i, f"ESi_{plot}"],
                                                             df_dd.loc[i, "Pei"],
                                                             df_crop.loc[i, f"Ks_soil_cond_{plot}"],
                                                             df_crop.loc[i, f"Ks_soil_{plot}"],
                                                             df_crop.loc[i, f"Final_Evap_Red_{plot}"])

            df_crop.loc[i, f"Ks_crop_cond_{plot}"] = calc_ks_crop_cond(df_crop.loc[i, f"Kci_{plot}"],
                                                                       df_crop.loc[i, f"SMDi_shifted_{plot}"],
                                                                       df_crop.loc[i, f"RAWi_{plot}"],
                                                                       df_crop.loc[i, f"TAWi_{plot}"])

            df_crop.loc[i, f"Ks_crop_{plot}"] = calc_ks_crop(df_crop.loc[i, f"Ks_crop_cond_{plot}"],
                                                             df_crop.loc[i, f"TAWi_{plot}"],
                                                             df_crop.loc[i, f"SMDi_shifted_{plot}"],
                                                             df_crop.loc[i, f"RAWi_{plot}"])

            df_crop.loc[i, f"AE_crop_{plot}"] = calc_ae_crop(df_dd.loc[i, f"ETci_{plot}"],
                                                             df_dd.loc[i, "Pei"],
                                                             df_crop.loc[i, f"Ks_crop_cond_{plot}"],
                                                             df_crop.loc[i, f"Ks_crop_{plot}"])

            smdi_value = calc_smd(df_crop.loc[i, f"SMDi_shifted_{plot}"],
                                  df_crop.loc[i, f"AE_soil_{plot}"],
                                  df_crop.loc[i, f"AE_crop_{plot}"],
                                  df_dd.loc[i, "Pei"])

            df_crop.loc[i, f"SMDi_{plot}"] = np.float32(smdi_value)

    for plot in all_plots:
        columns_to_convert = [
            f"SMDi_shifted_{plot}", f"Ks_soil_cond_{plot}", f"Ks_soil_{plot}",
            f"AE_soil_{plot}", f"Ks_crop_cond_{plot}", f"Ks_crop_{plot}",
            f"AE_crop_{plot}", f"SMDi_{plot}"
        ]

        df_crop[columns_to_convert] = df_crop[columns_to_convert].astype("float32")

    df_crop = calc_ae_per_crop(df_crop, valid_crops_df, ae_type="crop")
    df_crop = calc_ae_per_crop(df_crop, valid_crops_df, ae_type="soil")
    df_crop = update_gwnr(df_crop, df_dd, all_plots)
    return df_crop


# soil_moisture_deficit.py - Function 002: Calculates soil moisture deficit using water balance approach
# Interactions: None
def calc_smd(smdi, ae_soil, ae_crop, pei):
    if smdi + ae_soil + ae_crop - pei < 0:
        return 0
    else:
        return smdi + ae_soil + ae_crop - pei


# calc_smd_fallow function moved to aquifer_storage_bucket/influx/recharge_calculations.py
# to break circular import dependency