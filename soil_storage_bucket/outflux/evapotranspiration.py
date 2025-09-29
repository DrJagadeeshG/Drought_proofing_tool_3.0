"""
ET and evaporation calculations for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Calculates evapotranspiration and evaporation for crops and soil including reference ET, daily ET distribution, and actual ET calculations
# ========================================

import numpy as np
from shared.utilities import to_float, safe_divide, calc_monthly_remaining_growth_days
from orchestrator.input_collector import collect_inp_variables, collect_int_variables
from shared.data_readers import get_radiation_db
from soil_storage_bucket.processing.crop_coefficients import calc_crop_kc, calc_kci_by_plot, calculate_stage_1
from soil_storage_bucket.processing.root_depth import calc_final_crop_rd
from soil_storage_bucket.processing.water_stress import calc_final_depletion_factor


# evapotranspiration.py - Function 001: Calculates monthly reference evapotranspiration using Hargreaves method
# Interactions: shared.data_readers.get_radiation_db, orchestrator.input_collector.collect_inp_variables, numpy
def calc_etom(df_mm,file_paths,inp_source,master_path):
    print("FUNCTION 27: calc_etom() - Calculating reference evapotranspiration")
    # df_rd = get_radiation_db(drought_proofing_tool.radiation_db, user_input.latitude)
    
    radiation_db = file_paths["radiation_db"]
    df_rd = get_radiation_db(radiation_db, collect_inp_variables(inp_source,master_path)["latitude"])
    # Initialize the ETom column with zeros
    df_mm["ETom"] = 0.0

    # Vectorized ETom calculation - much faster than iterrows
    df_mm["month_index"] = df_mm.index % 12
    df_mm["radiation"] = df_mm["month_index"].map(df_rd["Radiation"])
    df_mm["ETom"] = (0.0023 * df_mm["radiation"] * np.sqrt(df_mm["Tmax"] - df_mm["Tmin"]) *
                     (df_mm["Tmean"] + 17.8) * df_mm["Days"])
    df_mm.drop(["month_index", "radiation"], axis=1, inplace=True)
    return df_mm


# evapotranspiration.py - Function 002: Distributes monthly reference ET to daily values
# Interactions: pandas
def calculate_daily_etoi(df_mm, df_dd):
    print("FUNCTION 28: calculate_daily_etoi() - Calculating daily ET reference")
    # Vectorized approach - much faster than nested loops
    daily_etoi = df_mm["ETom"] / df_mm["Days"]
    df_dd["EToi"] = daily_etoi.repeat(df_mm["Days"]).values
    return df_dd


# evapotranspiration.py - Function 003: Applies evaporation reduction factors based on conservation practices
# Interactions: orchestrator.input_collector.collect_int_variables, shared.utilities.to_float
def apply_eva_red(row, default_val_eva_red,inp_source,master_path):
    int_var = collect_int_variables(inp_source,master_path)
    # Convert "Cover_Crops_Eva_Red" based on "Cover_Area"
    row["Cover_Eva_Red"] = ((
        to_float(int_var["Cover_Crops_Eva_Red"], default_val_eva_red["Cover_Crops_Eva_Red"])
        if to_float(row["Cover_Area"]) > 0
        else default_val_eva_red["Cover_Crops_Eva_Red"]
    ))/100
    row["Mulching_Eva_Red"] = ((
        to_float(int_var["Mulching_Eva_Red"], default_val_eva_red["Mulching_Eva_Red"])
        if to_float(row["Mulching_Area"]) > 0
        else default_val_eva_red["Mulching_Eva_Red"]
    ))/100
    row["Tank_Eva_Red"] = ((
        to_float(int_var["Tank_Eva_Red"], default_val_eva_red["Tank_Eva_Red"])
        if to_float(row["Tank_Area"]) > 0
        else default_val_eva_red["Tank_Eva_Red"]
    ))/100
    row["Tillage_Eva_Red"] = ((
        to_float(int_var["Tillage_Eva_Red"], default_val_eva_red["Tillage_Eva_Red"])
        if to_float(row["Tillage_Area"]) > 0
        else default_val_eva_red["Tillage_Eva_Red"]
    ))/100
    return row


# evapotranspiration.py - Function 004: Calculates average soil evaporation reduction from conservation practices
# Interactions: pandas
def calc_red_soil_evap(row):
    # Calculate the mean of the specified evaporation reduction columns
    row["red_soil_evap"] = row[["Tillage_Eva_Red", "Tank_Eva_Red", "Mulching_Eva_Red", "Cover_Eva_Red"]].mean()
    return row


# evapotranspiration.py - Function 005: Calculates crop evapotranspiration with special rice preparation handling
# Interactions: shared.utilities.safe_divide
def calc_etci(df_cc, etoi, kci, local_crop, counter):
    if local_crop == "Rice":
        if not all(col in df_cc.columns for col in ["Area", "DSR_Area"]):
            raise ValueError("Required columns not found in df_cc")

        # Calculate kc_prep for Rice only
        if "Rice" not in df_cc.index:
            raise ValueError("'Rice' not found in the DataFrame index")

        rice_area = df_cc.loc["Rice", "Area"]
        rice_dsr_area = df_cc.loc["Rice", "DSR_Area"]
        kc_prep = safe_divide((rice_area - rice_dsr_area) * 15, rice_area)

        # Calculate ETci for Rice with counter logic
        if kci > 0:
            if counter[0] < 20:
                counter[0] += 1
                etc_i = etoi * kci + kc_prep  # Include kc_prep for the first 20 occurrences when kci > 0
            else:
                etc_i = etoi * kci  # Regular calculation if counter exceeds 20
        else:
            counter[0] = 0  # Reset the counter if kci is 0
            etc_i = etoi * kci  # Calculate normally when kci is 0
    else:
        # For crops other than Rice
        etc_i = etoi * kci  # Calculate normally if not Rice
    return etc_i


# evapotranspiration.py - Function 006: Calculates soil evaporation coefficient (Kei) for all plots
# Interactions: pandas
def calc_kei(df_crop, kei, all_plots):
    for plot in all_plots:
        kei_values = df_crop.apply(lambda row: kei if row[f"Kci_{plot}"] == 0 or row[f"Stage_1_{plot}"] > 0 else 0,
                                   axis=1)
        df_crop[f"Kei_{plot}"] = kei_values
    return df_crop


# evapotranspiration.py - Function 007: Calculates daily soil evaporation (ESi) for all plots
# Interactions: pandas
def calculate_daily_esi(df_dd, df_crop, all_plots):
    for plot in all_plots:
        df_dd[f"ESi_{plot}"] = df_dd["EToi"] * df_crop[f"Kei_{plot}"]
    return df_dd


# evapotranspiration.py - Function 008: Calculates actual soil evaporation considering water stress and reduction factors
# Interactions: None
def calc_ae_soil(esi, pei, ks_soil_cond, ks_soil, x):
    if ks_soil_cond == 1 or pei > esi:
        return esi * x
    elif ks_soil_cond == 2 and pei < esi:
        return (pei + ks_soil * (esi - pei)) * x
    elif ks_soil_cond == 3 and pei < esi:
        return pei * x
    else:
        return 0


# evapotranspiration.py - Function 009: Calculates actual crop evapotranspiration considering water stress
# Interactions: None
def calc_ae_crop(etci, pei, ks_crop_cond, ks_crop):
    if ks_crop_cond == 1 or pei > etci:
        return etci
    elif ks_crop_cond == 3 and pei < etci:
        return pei
    elif ks_crop_cond == 2 and pei < etci:
        return pei + ks_crop * (etci - pei)
    else:
        return 0


# evapotranspiration.py - Function 010: Distributes plot-level actual evapotranspiration to individual crops
# Interactions: numpy, pandas
def calc_ae_per_crop(df_crop, valid_crops_df, ae_type):
    print(f"FUNCTION 37: calc_ae_per_crop() - Calculating actual evapotranspiration for {ae_type}")
    # ae_type can be either "crop" or "soil"
    ae_plot_col_template = f"AE_{ae_type}_{{plot}}"
    ae_crop_col_template = f"AE_{ae_type}_{{crop}}"

    # Iterate over each unique plot
    for plot in valid_crops_df["Plot"].unique():
        # Get the crops associated with the current plot
        crops_in_plot = valid_crops_df.loc[valid_crops_df["Plot"] == plot, "Crop"].tolist()

        for i in range(len(df_crop)):
            for crop in crops_in_plot:
                sown_area_col = f"{crop}_Sown_Area"
                ae_plot_col = ae_plot_col_template.format(plot=plot)
                ae_crop_col = ae_crop_col_template.format(crop=crop)

                if sown_area_col in df_crop.columns:
                    # ALWAYS assign plot AE to crop regardless of sown area (1:1 mapping)
                    df_crop.loc[i, ae_crop_col] = df_crop.loc[i, ae_plot_col]

    return df_crop


# evapotranspiration.py - Function 011: Calculates soil evaporation coefficient for fallow land
# Interactions: numpy
def calc_ke(kc_fallow):
    return 1.05 if kc_fallow == 0 else np.float32(0)


# evapotranspiration.py - Function 012: Calculates potential soil evaporation for fallow areas
# Interactions: None
def calc_esi_fallow(row):
    e_si_fallow = row["EToi"] * row["Ke_Fallow"]
    return e_si_fallow


# evapotranspiration.py - Function 013: Calculates actual soil evaporation for fallow areas without crops
# Interactions: None
def calc_ae_soil_fallow(esi, pei, ks_soil_cond, ks_soil):
    if ks_soil_cond == 1 or pei > esi:
        return esi
    elif ks_soil_cond == 2 and pei < esi:
        return pei + ks_soil * (esi - pei)
    elif ks_soil_cond == 3 and pei < esi:
        return pei
    else:
        return 0


# evapotranspiration.py - Function 014: Calculates crop evapotranspiration for each plot
# Interactions: soil_storage_bucket.processing.crop_coefficients.calc_crop_kc, soil_storage_bucket.processing.crop_coefficients.calc_kci_by_plot, calc_etci, soil_storage_bucket.processing.crop_coefficients.calculate_stage_1, calc_kei, calculate_daily_esi, shared.utilities.calc_monthly_remaining_growth_days, soil_storage_bucket.processing.root_depth.calc_final_crop_rd, soil_storage_bucket.processing.water_stress.calc_final_depletion_factor, pandas
def calc_etci_plot(df_crop, df_cc, df_cp, df_dd, df_mm, all_plots, all_crops, num_plots, counter, kei, valid_crops_df,
                   crop_df):
    print("FUNCTION 23: calc_etci_plot() - Calculating ETc for each plot")
    # Calculate Kci for each crop
    for crop in all_crops:
        df_crop[f"Kci_{crop}"] = df_crop.apply(lambda row: calc_crop_kc(row, crop), axis=1)

    df_crop = calc_kci_by_plot(df_crop, df_cp, all_crops, num_plots)

    for crop in all_crops:
        # Call the combined function for each crop
        monthly_etci = df_dd.apply(
            lambda row: calc_etci(df_cc, row["EToi"], df_crop.loc[row.name, f"Kci_{crop}"], crop, counter), axis=1)
        # Create a new column in df_dd for the ETci values of the current crop
        df_dd[f"ETci_{crop}"] = monthly_etci
        # Resample and sum the monthly ETci values for the current crop
        monthly_etci_sum = df_dd.resample("M", on="Date")[f"ETci_{crop}"].sum().reset_index()
        # Merge the monthly ETci with df_mm
        df_mm = df_mm.merge(monthly_etci_sum, on="Date", how="left")

    for plot in all_plots:
        # Ensure the column name is formatted correctly
        kci_column = f"Kci_{plot}"

        # Check if the Kci column exists in df_crop
        if kci_column in df_crop.columns:
            # Calculate ETci for each plot
            df_dd[f"ETci_{plot}"] = df_dd.apply(
                lambda row: calc_etci(
                    df_cc,
                    row["EToi"],
                    df_crop.loc[row.name, kci_column]
                    , crop, counter),
                axis=1
            )
        else:
            print(f"Column {kci_column} not found in df_crop")

        monthly_etci = df_dd.resample("M", on="Date")[f"ETci_{plot}"].sum().reset_index()
        df_mm = df_mm.merge(monthly_etci, on="Date", how="left")

    total_etci_columns = [f"ETci_{plot}" for plot in all_plots]
    df_dd["ETci"] = df_dd[total_etci_columns].sum(axis=1)
    df_crop = calculate_stage_1(df_crop, all_crops, df_cp)
    df_crop = calc_kei(df_crop, kei, all_plots)
    df_dd = calculate_daily_esi(df_dd, df_crop, all_plots)
    df_mm = calc_monthly_remaining_growth_days(df_crop, all_crops, df_mm, df_cc)
    df_crop = calc_final_crop_rd(df_crop, crop_df, all_crops, valid_crops_df)
    df_crop = calc_final_depletion_factor(df_crop, crop_df, all_crops, valid_crops_df)
    return df_dd, df_crop, df_mm


# evapotranspiration.py - Function 015: Calculates final evapotranspiration from water balance
# Interactions: pandas
def calc_final_et(df_mm):
    df_mm["Final_ET"] = (df_mm["Rain"] - df_mm["Final_Runoff"] - df_mm["Final_Recharge"]).clip(lower=0)
    return df_mm


# evapotranspiration.py - Function 016: Calculates biological evapotranspiration from crop and soil
# Interactions: pandas
def calc_final_et_biological(df_mm, crops, df_cc, df_crop):
    """
    Calculate ET_Biological using area-weighted average of all biological AE components.
    This is a new column separate from Final_ET, using area-weighted averaging.
    """
    # Initialize components for area-weighted calculation
    total_weighted_ae = 0.0
    total_area = 0.0

    # Calculate area-weighted evapotranspiration from all crops
    for crop in crops:
        ae_crop_col = f"AE_crop_{crop}"
        ae_soil_col = f"AE_soil_{crop}"

        if ae_crop_col in df_mm.columns and ae_soil_col in df_mm.columns and crop in df_cc.index:
            crop_area = df_cc.at[crop, "Area"]
            crop_total_ae = df_mm[ae_crop_col] + df_mm[ae_soil_col]
            total_weighted_ae += crop_total_ae * crop_area
            total_area += crop_area

    # Add fallow area evapotranspiration if available (use dynamic fallow area)
    if "AE_soil_Fallow" in df_mm.columns and "Fallow Area Recharge" in df_crop.columns:
        # Get fallow area from the first row (assuming it's constant)
        fallow_area = df_crop["Fallow Area Recharge"].iloc[0]
        total_weighted_ae += df_mm["AE_soil_Fallow"] * fallow_area
        total_area += fallow_area

    # Calculate area-weighted average
    df_mm["ET_Biological"] = total_weighted_ae / total_area if total_area > 0 else 0.0

    # Keep original water balance ET calculation unchanged
    df_mm["Final_ET"] = (df_mm["Rain"] - df_mm["Final_Runoff"] - df_mm["Final_Recharge"]).clip(lower=0)

    return df_mm