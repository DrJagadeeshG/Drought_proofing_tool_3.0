# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:52:31 2024

@author: Dr. Jagadeesh, Consultant, IWMI
"""
import pandas as pd
import numpy as np
import crop_pattern
import manual_input
from user_input import to_float


# Define functions
# smd.py - Function 1: Determines soil evaporation stress condition based on water deficits
def calc_ks_soil_cond(kei, smdi, rewi, tewi):
    if kei == 0:
        return 0
    elif smdi < rewi:
        return 1
    elif rewi < smdi < tewi:
        return 2
    else:
        return 3


# smd.py - Function 2: Calculates soil evaporation stress coefficient based on moisture conditions
def calc_ks_soil(ks_soil_cond, tewi, smdi, rewi):
    if ks_soil_cond == 1:
        return 1
    elif ks_soil_cond == 2:
        return (tewi - smdi) / (tewi - rewi)
    else:
        return 0


# smd.py - Function 3: Calculates actual soil evaporation considering water stress and reduction factors
def calc_ae_soil(esi, pei, ks_soil_cond, ks_soil, x):
    if ks_soil_cond == 1 or pei > esi:
        return esi * x
    elif ks_soil_cond == 2 and pei < esi:
        return (pei + ks_soil * (esi - pei)) * x
    elif ks_soil_cond == 3 and pei < esi:
        return pei * x
    else:
        return 0


# smd.py - Function 4: Determines crop transpiration stress condition based on water availability
def calc_ks_crop_cond(kci, smdi, rawi, tawi):
    if kci == 0:
        return 0
    elif smdi < rawi:
        return 1
    elif rawi < smdi < tawi:
        return 2
    else:
        return 3


# smd.py - Function 5: Calculates crop transpiration stress coefficient based on soil moisture
def calc_ks_crop(ks_crop_cond, tawi, smdi, rawi):
    if ks_crop_cond == 1:
        return 1
    elif ks_crop_cond == 2:
        return (tawi - smdi) / (tawi - rawi)
    else:
        return 0


# smd.py - Function 6: Calculates actual crop evapotranspiration considering water stress
def calc_ae_crop(etci, pei, ks_crop_cond, ks_crop):
    if ks_crop_cond == 1 or pei > etci:
        return etci
    elif ks_crop_cond == 3 and pei < etci:
        return pei
    elif ks_crop_cond == 2 and pei < etci:
        return pei + ks_crop * (etci - pei)
    else:
        return 0


# smd.py - Function 7: Calculates soil moisture deficit using water balance approach
def calc_smd(smdi, ae_soil, ae_crop, pei):
    if smdi + ae_soil + ae_crop - pei < 0:
        return 0
    else:
        return smdi + ae_soil + ae_crop - pei


# smd.py - Function 8: Distributes plot-level actual evapotranspiration to individual crops
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
                    if df_crop.loc[i, sown_area_col] > 0:
                        # Update AE_{crop/soil}_{crop} with the value from AE_{crop/soil}_{plot}
                        df_crop.loc[i, ae_crop_col] = df_crop.loc[i, ae_plot_col]
                    else:
                        # Set AE_{crop/soil}_{crop} to 0 if sown area is 0
                        df_crop.loc[i, ae_crop_col] = np.float32(0)

    return df_crop


# smd.py - Function 9: Calculates groundwater natural recharge when soil is at field capacity
def calc_gwnr(smdi, smdi_shifted, ae_crop, ae_soil, pei):
    return abs(smdi_shifted + ae_crop + ae_soil - pei) if smdi == 0 else 0


# smd.py - Function 10: Updates groundwater natural recharge for all plots in dataset
def update_gwnr(df_crop, df_dd, all_plots):
    # Initialize a column for total GWnr
    df_crop["GWnr"] = np.float32(0)

    # Loop over each plot and calculate GWnr
    for plot in all_plots:
        smdi_col = f"SMDi_{plot}"
        smdi_shifted_col = f"SMDi_shifted_{plot}"
        ae_crop_col = f"AE_crop_{plot}"
        ae_soil_col = f"AE_soil_{plot}"

        # Calculate GWnr for each plot and store in a new column
        df_crop[f"GWnr_{plot}"] = df_crop.apply(
            lambda row: calc_gwnr(
                row[smdi_col],
                row[smdi_shifted_col],
                row[ae_crop_col],
                row[ae_soil_col],
                df_dd.loc[row.name, "Pei"]
            ),
            axis=1
        )

        # # Add to the total GWnr
        # df_crop["GWnr"] += df_crop[f"GWnr_{plot}"]

    # Ensure the total GWnr is of the correct type
    df_crop["GWnr"] = df_crop["GWnr"].astype("float32")

    return df_crop

# smd.py - Function 11: Aggregates daily groundwater recharge to monthly values for crops
def calc_monthly_gwnrm_crop(df_crop, df_mm, all_plots):
    print("FUNCTION 38: calc_monthly_gwnrm_crop() - Calculating monthly groundwater recharge")
    for plot in all_plots:
        # Resample the GWnr values for each crop to a monthly frequency and sum them
        gw_nrm = df_crop.resample("M", on="Date")[f"GWnr_{plot}"].sum().reset_index()

        # Merge the resampled monthly GWnr values into df_mm
        df_mm = df_mm.merge(gw_nrm, on="Date", how="left")

        # Rename the column appropriately
        df_mm.rename(columns={f"GWnr_{plot}": f"GWnrm_{plot}"}, inplace=True)

    return df_mm


# smd.py - Function 12: Calculates soil evaporation coefficient for fallow land
def calc_ke(kc_fallow):
    return 1.05 if kc_fallow == 0 else np.float32(0)


# smd.py - Function 13: Calculates potential soil evaporation for fallow areas
def calc_esi_fallow(row):
    e_si_fallow = row["EToi"] * row["Ke_Fallow"]
    return e_si_fallow


# smd.py - Function 14: Calculates soil moisture deficit for fallow land areas
def calc_smd_fallow(smdi, ae_soil, pei):
    if smdi + ae_soil - pei < 0:
        return 0
    else:
        return smdi + ae_soil - pei


# smd.py - Function 15: Calculates actual soil evaporation for fallow areas without crops
def calc_ae_soil_fallow(esi, pei, ks_soil_cond, ks_soil):
    if ks_soil_cond == 1 or pei > esi:
        return esi
    elif ks_soil_cond == 2 and pei < esi:
        return pei + ks_soil * (esi - pei)
    elif ks_soil_cond == 3 and pei < esi:
        return pei
    else:
        return 0


# smd.py - Function 16: Calculates groundwater natural recharge from fallow land areas
def calc_gwnr_fallow(smdi_fallow, smdi_shifted_fallow, ae_soil_fallow, pei):
    return abs(smdi_shifted_fallow + ae_soil_fallow - pei) if smdi_fallow == 0 else np.float32(0)


# smd.py - Function 17: Aggregates daily groundwater recharge from fallow areas to monthly totals
def calc_monthly_gwnrm_fallow(df_crop, df_mm):
    # Resample the GWnr values to a monthly frequency and sum them
    gw_nrmf = df_crop.resample("M", on="Date")["GWnr_Fallow"].sum().reset_index()
    # Merge the resampled monthly GWnr values into df_mm
    df_mm = df_mm.merge(gw_nrmf, on="Date", how="left")
    # Rename the column appropriately
    df_mm.rename(columns={"GWnr_Fallow": "GWnrm_Fallow"}, inplace=True)
    return df_mm


# smd.py - Function 18: Calculates total fallow area including non-crop land uses for recharge
def calc_fallow_area1(df_crop, fallow, builtup, water_bodies, pasture, forest):
    fallow_var = to_float(fallow, 0)
    builtup_var = to_float(builtup, 0)
    water_bodies_var = to_float(water_bodies, 0)
    pasture_var = to_float(pasture, 0)
    forest_var = to_float(forest, 0)
    df_crop["Fallow Area Recharge"] = fallow_var + builtup_var + water_bodies_var + pasture_var + forest_var
    return df_crop


# smd.py - Function 19: Calculates area-weighted average groundwater recharge across all land uses
def calc_recharge(row, all_plots, total_crop_areas):
    numerator = sum(row[f"{plot}_NSA"] * row[f"GWnr_{plot}"] for plot in all_plots)
    # Add the fallow area contribution to the numerator
    numerator += row["Fallow Area Recharge"] * row["GWnr_Fallow"]
    # Use sum of all crop areas + fallow area recharge as denominator
    denominator = total_crop_areas + row["Fallow Area Recharge"]
    return numerator / denominator if denominator != 0 else 0


# smd.py - Function 20: Aggregates daily recharge values to monthly totals for water balance
def calc_monthly_recharge(df_crop, df_mm):
    recharge = df_crop.resample("M", on="Date")["Recharge"].sum().reset_index()
    # Merge the resampled monthly GWnr values into df_mm
    df_mm = df_mm.merge(recharge, on="Date", how="left")
    return df_mm


# smd.py - Function 21: Calculates irrigation water requirements as difference between ET and actual ET
def calculate_iwr(df_dd, df_crop, crops):
    print("FUNCTION 39: calculate_iwr() - Calculating irrigation water requirements")
    for crop in crops:
        df_crop[f"IWR_{crop}"] = (df_dd[f"ETci_{crop}"] - df_crop[f"AE_crop_{crop}"]).clip(lower=0)
    return df_crop


# smd.py - Function 22: Aggregates daily irrigation water requirements to monthly values
def calculate_monthly_iwr(df_dd, df_mm, df_crop, crops):
    # Calculate IWR for all crops in a single step
    df_crop = calculate_iwr(df_dd, df_crop.copy(), crops)
    # Resample and merge IWR with other columns (can be vectorized)
    for crop in crops:
        iwr_resampled = df_crop.set_index("Date")[f"IWR_{crop}"].resample("M").sum().reset_index()
        df_mm = df_mm.merge(iwr_resampled, how="left", on="Date", suffixes=("", f"_{crop}"))
        ae_soil = df_crop[["Date", f"AE_soil_{crop}"]].set_index("Date").resample("M").sum().reset_index()
        ae_crop = df_crop[["Date", f"AE_crop_{crop}"]].set_index("Date").resample("M").sum().reset_index()
        df_mm = df_mm.merge(ae_soil, how="left", on="Date", suffixes=("", f"_soil_{crop}"))
        df_mm = df_mm.merge(ae_crop, how="left", on="Date", suffixes=("", f"_crop_{crop}"))
    return df_mm


# smd.py - Function 23: Calculates weighted irrigation efficiency from surface and groundwater sources
def calc_irr_eff(area_eff_list,inp_lulc_val_list):
    sw_area = to_float(area_eff_list[0],0)
    gw_area = to_float(area_eff_list[1], 0)
    net_crop_sown_area = to_float(inp_lulc_val_list[0], 0)
    sw_area_irr_eff = (to_float(area_eff_list[2], 0))/100
    gw_area_irr_eff = (to_float(area_eff_list[3], 0))/100
    # Calculate the percentages
    gw_area = round(crop_pattern.get_percentage(gw_area, net_crop_sown_area), 3)
    sw_area = round(crop_pattern.get_percentage(sw_area, net_crop_sown_area), 3)
    # Extract the irrigation efficiency or use the default
    sw_eff = sw_area_irr_eff if sw_area_irr_eff else (area_eff_list[4])/100
    gw_eff = gw_area_irr_eff if gw_area_irr_eff else (area_eff_list[4])/100
    # Calculate the irrigation efficiency
    irr_eff = round(((gw_area * gw_eff) + (sw_area * sw_eff)) / net_crop_sown_area, 3)
    return irr_eff


# smd.py - Function 24: Calculates overall irrigation efficiency considering all intervention types
def calc_overall_eff(df_mm, df_cc, crops, irr_eff):
    print("FUNCTION 40: calc_overall_eff() - Calculating overall irrigation efficiency")
    # Calculate Area_with_Intervention
    area_with_intervention = (df_cc["Drip_Area"] +
                              df_cc["Sprinkler_Area"] +
                              df_cc["BBF_Area"])
    
    # Calculate Intervention_area_eff
    intervention_area_eff = crop_pattern.safe_divide(
        (df_cc["Drip_Area"] * df_cc["Eff_Drip"] +
         df_cc["Sprinkler_Area"] * df_cc["Eff_Sprinkler"] +
         df_cc["BBF_Area"] * df_cc["Eff_BBF"]),
        area_with_intervention
    )

    # Calculate Water_saved_area
    water_saved_area = (df_cc["Land_Levelling_Area"] +
                        df_cc["DSR_Area"] +
                        df_cc["AWD_Area"] +
                        df_cc["SRI_Area"] +
                        df_cc["Ridge_Furrow_Area"] +
                        df_cc["Deficit_Area"])

    # Calculate Water_saved_eff
    water_saved_eff = crop_pattern.safe_divide(
        (df_cc["Land_Levelling_Area"] * df_cc["Eff_Land_Levelling"] +
         df_cc["DSR_Area"] * df_cc["Eff_DSR"] +
         df_cc["AWD_Area"] * df_cc["Eff_AWD"] +
         df_cc["SRI_Area"] * df_cc["Eff_SRI"] +
         df_cc["Ridge_Furrow_Area"] * df_cc["Eff_Ridge_Furrow"] +
         df_cc["Deficit_Area"] * df_cc["Eff_Deficit"]),
        water_saved_area
    )

    # Calculate Area_without_Intervention
    area_without_intervention = np.where(
        df_cc["Irr_Area"] >= area_with_intervention,
        df_cc["Irr_Area"] - area_with_intervention,
        np.nan  # Set to NaN if the condition is not met
    )

    # Calculate Overall_eff
    overall_eff = crop_pattern.safe_divide(
        (area_with_intervention * intervention_area_eff +
         area_without_intervention * irr_eff),
        df_cc["Irr_Area"]
    )

    # Calculate Area_without_Water_saving_Intervention
    area_without_water_saving_intervention = np.where(
        df_cc["Irr_Area"] >= water_saved_area,
        df_cc["Irr_Area"] - water_saved_area,
        np.nan  # Set to NaN if the condition is not met
    )

    # Calculate Overall_water_saved_eff
    overall_water_saved_eff = crop_pattern.safe_divide(
        (water_saved_area * water_saved_eff +
         area_without_water_saving_intervention * (to_float(manual_input.Eff_Water_Saved_Area_without_Interventions, 0)/100)),
        df_cc["Irr_Area"]
    )

    # Calculate Eff_after_WS and Eff_after_rf
    eff_after_ws = ((1 - overall_eff) * overall_water_saved_eff) + overall_eff
    eff_after_rf = ((1 - eff_after_ws) * df_cc["Over_all_rf"]) + eff_after_ws

    # Calculate Final_eff
    final_eff = eff_after_rf.fillna(0)

    # Concatenate the new columns back into df_cc
    df_cc = pd.concat([
        df_cc,
        pd.DataFrame({
            "Area_with_Intervention": area_with_intervention,
            "Intervention_area_eff": intervention_area_eff,
            "Water_saved_area": water_saved_area,
            "Water_saved_eff": water_saved_eff,
            "Area_without_Intervention": area_without_intervention,
            "Overall_eff": overall_eff,
            "Area_without_Water_saving_Intervention": area_without_water_saving_intervention,
            "Overall_water_saved_eff": overall_water_saved_eff,
            "Eff_after_WS": eff_after_ws,
            "Eff_after_rf": eff_after_rf,
            "Final_eff": final_eff
        }, index=df_cc.index)
    ], axis=1)

    # Iterate over each crop and calculate respective irrigation efficiency
    for crop in crops:
        irr_area_col = f"Irr_Area_{crop}"
        eff_col = f"Irrigation_eff_{crop}"
        iwr_col = f"IWR_{crop}"
        water_need_col = f"Irr_water_need_{crop}"
        final_eff_col = "Final_eff"  # Assuming "Final_eff" is present in df_cc

        # Ensure "Final_eff" is available in df_cc
        if final_eff_col in df_cc.columns:
            # Calculate irrigation efficiency for the crop
            df_mm[eff_col] = df_mm.apply(
                lambda row: df_cc.loc[crop, final_eff_col] if row[irr_area_col] > 0 else 0,
                axis=1
            ).astype(float)

        # Ensure columns exist in DataFrames
        if iwr_col in df_mm.columns and irr_area_col in df_mm.columns and eff_col in df_mm.columns:
            # Calculate irrigation water need for the crop
            df_mm[water_need_col] = crop_pattern.safe_divide(
                (df_mm[iwr_col] / 1000) * df_mm[irr_area_col] * 10000, df_mm[eff_col]
            )

    # Sum all crop irrigation water needs across the dataset
    df_mm["Irr_water_need"] = df_mm.filter(like="Irr_water_need_").sum(axis=1)
    df_mm["Total Irrigated Area"] = df_mm.filter(like="Irr_Area_").sum(axis=1)
    df_mm["Total Rainfed Area"] = df_mm.filter(like="Rainfed_Area_").sum(axis=1)

    # Print error message if Water_saved_area exceeds Irr_Area
    error_rows = df_cc[df_cc["Irr_Area"] < df_cc["Water_saved_area"]]
    if not error_rows.empty:
        print("Error: The following rows have Irr_Area <= Area_with_Intervention:")
        print(error_rows)

    # Convert data types for df_cc
    df_cc = crop_pattern.convert_dtypes(df_cc)

    return df_cc, df_mm
