"""
Main controller functions for drought proofing tool

@author: Dr. Jagadeesh, Consultant, IWMI
"""

# ========================================
# FILE PURPOSE: Controls main drought proofing routines including scenario management, data processing orchestration, and output generation
# ========================================

import os
import sys
import getopt
import shutil
import pandas as pd
from shared import config_constants
from orchestrator.input_collector import collect_inp_variables, collect_int_variables
from shared.data_readers import get_file_paths, get_crop_data, get_pcp_value, process_monthly_data, get_seasons_val, get_cover_type, get_season_data, get_seasons_data, get_land_use_types
from outputs.output_aggregator import get_resample_yr_optimized, calculate_weighted_averages, process_year_data, process_water_year_data, calc_weighted_avg
from outputs.yield_calculations import calc_yield, calculate_yield_wyr
from shared.utilities import convert_dtypes
from shared.crop_processing import assign_plots_to_crops, select_valid_crops, attribute_names, crop_details, process_seasonal_crops, yield_columns, other_columns
from soil_storage_bucket.outflux.evapotranspiration import calculate_daily_etoi, calc_etci_plot
from soil_storage_bucket.input_data.soil_properties import calculate_awc_capacity, soil_calculation
from soil_storage_bucket.processing.conservation_practices import calculate_soil_moisture_sums, calculate_awc_soil, calculate_capacity
from soil_storage_bucket.processing.water_storage import calc_crop_int
from shared.land_use import calculate_total_area
from shared.irrigation_efficiency import calc_irr_eff, calc_overall_eff
from aquifer_storage_bucket.processing.storage_capacity import calculate_storage_limit
from aquifer_storage_bucket.influx.recharge_capacity import calc_recharge_capacity
from surface_water_bucket.processing.curve_numbers import process_cn_values, calc_crop_consolidated_cn
from surface_water_bucket.processing.runoff_calculations import calc_discharge, process_monthly_qi
from soil_storage_bucket.processing.soil_moisture_deficit import calc_smdi_plot
from aquifer_storage_bucket.influx.recharge_calculations import calc_gwnr_fallow_plot
from orchestrator.water_balance_coordinator import process_water_management, process_final_wb
from shared.economics import calculate_intervention_economics


# main_controller.py - Function 001: Saves all output dataframes to CSV files in scenario-specific folders
# Interactions: orchestrator.input_collector.collect_inp_variables, orchestrator.input_collector.collect_int_variables, pandas, os
def save_dataframes_scenario(val_scenario, master_path, output_dictionary, inp_source):

    # main_controller.py - Function 001.1: Saves input and intervention variables to CSV files
    # Interactions: orchestrator.input_collector.collect_inp_variables, orchestrator.input_collector.collect_int_variables, pandas, os
    def save_dictionaries_to_csv(val_scenario, inp_source, scenario_folder):
        # Collect variables
        inp_var = collect_inp_variables(inp_source, master_path)
        int_var = collect_int_variables(inp_source, master_path, val_scenario)

        # Convert values to string representation to handle multi-value entries
        inp_var_str = {}
        for k, v in inp_var.items():
            if isinstance(v, list):
                inp_var_str[k] = ', '.join(map(str, v)) if len(v) > 1 else str(v[0]) if v else ''
            else:
                inp_var_str[k] = str(v)

        int_var_str = {}
        for k, v in int_var.items():
            if isinstance(v, list):
                int_var_str[k] = ', '.join(map(str, v)) if len(v) > 1 else str(v[0]) if v else ''
            else:
                int_var_str[k] = str(v)

        # Create DataFrames for each dictionary
        df_inp_var = pd.DataFrame.from_dict(inp_var_str, orient='index', columns=['Value'])
        df_int_var = pd.DataFrame.from_dict(int_var_str, orient='index', columns=['Value'])

        # Pre-compute output paths
        if val_scenario == 0:
            baseline_path = os.path.join(scenario_folder, 'Input_variables_Baseline_Scenario_baseline.csv')
            intervention_path = os.path.join(scenario_folder, 'Input_variables_Baseline_Scenario_intervention.csv')
        else:
            baseline_path = os.path.join(scenario_folder, f"Input_variables_Scenario_{val_scenario}_baseline.csv")
            intervention_path = os.path.join(scenario_folder, f"Input_variables_Scenario_{val_scenario}_intervention.csv")

        try:
            # Save to CSV files - much faster than Excel
            df_inp_var.to_csv(baseline_path, index=True)
            df_int_var.to_csv(intervention_path, index=True)
        except Exception as e:
            print(f"Error saving input and integer variables to CSV: {e}")

    # Pre-compute output directory and scenario folder
    output_dir = os.path.join(master_path, "Datasets", "Outputs")

    # Create the scenario folder based on the scenario number or baseline
    if val_scenario == 0:
        scenario_folder = os.path.join(output_dir, "Baseline_Scenario")
    else:
        scenario_folder = os.path.join(output_dir, f"Scenario_{val_scenario}")

    # Create directories once upfront
    os.makedirs(scenario_folder, exist_ok=True)

    # Save the input and integer variable dictionaries to CSV
    save_dictionaries_to_csv(val_scenario, inp_source, scenario_folder)

    dict_save_file = []

    # Pre-compute all file paths for batch processing
    file_paths = {}
    for filename in output_dictionary.keys():
        if val_scenario == 0:
            scenario_filename = f"{filename.replace('.csv', '')}_Baseline_Scenario.csv"
        else:
            scenario_filename = f"{filename.replace('.csv', '')}_Scenario_{val_scenario}.csv"
        file_paths[filename] = os.path.join(scenario_folder, scenario_filename)

    # Batch save all DataFrames with optimized settings
    for filename, df in output_dictionary.items():
        output_path = file_paths[filename]

        try:
            # Optimize CSV writing with faster engine and compression
            save_index = filename == "df_cc.csv"
            df.to_csv(output_path, index=save_index,
                     float_format='%.6g')  # Reduce precision for smaller files
            dict_save_file.append(output_path)
        except Exception as e:
            print(f"Error saving {filename} to CSV: {e}")

    return dict_save_file


# main_controller.py - Function 002: Processes yearly data and calculates weighted averages
# Interactions: outputs.output_aggregator.get_resample_yr_optimized, outputs.yield_calculations.calc_yield, outputs.output_aggregator.calculate_weighted_averages, shared.utilities.convert_dtypes
def process_yearly_df(df_mm, df_cc, all_crops, yield_columns, other_columns):
    print("FUNCTION 28: process_yearly_df() - Processing yearly data aggregations")
    df_yr = get_resample_yr_optimized(df_mm, all_crops)
    df_yr = calc_yield(df_cc, df_yr, all_crops)
    df_yr = calculate_weighted_averages(df_cc, df_yr, all_crops, yield_columns, other_columns)
    df_yr = convert_dtypes(df_yr)
    return df_yr


# main_controller.py - Function 003: Processes command line arguments and runs the scenario
# Interactions: getopt, sys, run_dr_pf_routines, save_dataframes_scenario
def main(argument):
    # Options
    runfile = ''
    scenario_no = ''
    year_type = ''
    base_path = ''
    run_type = ''
    # input_area_of_interest = ''

    options = "hm:s:c:d:"

    # Long options
    long_options = ["Help", "manual = ", "scenario_no = ", "cycle = ", "directory ="]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argument, options, long_options)
    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))
        print("refer help:       python drought_proofing_tool.py -h")

    # checking each argument
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-h", "--Help"):
            print(''' 
            Help for generating baseline and scenarios using the water balance model in drought proofing interventions

            python drought_proofing_tool.py -m True -s 0 -c 'crop' -d Output/folder/path 

            where,
            -m, -manual         Is input data provided from config_constants.py then: True. 
                                If input from csv files placed in Inputs/csv_inputs/ then: False
            -s, -scenario_no    Count of current scenario run. NOTE: First run is the baseline run.
                                Use 0 for baseline
                                    1 onwards for scenarios. 
                                Note: Please make necessary changes in the input parameters (interventions) for each scenario
            -c, -cycle          If running by crop growing season: 'crop'
                                If running by year (January-December): 'calender'
            -d, -directory      All input output dataset folder location. Inputs and outputs should be as subfolders.
                                Follow the same folder hierarchy structure as mentioned in the supporting document. 
            ''')
            sys.exit()

        elif currentArgument in ("-m", "--manual"):
            runfile = currentValue  # e.g. True = manual and False=  csv
        elif currentArgument in ("-s", "--scenario_no"):
            scenario_no = int(currentValue)  # e.g. 1
        elif currentArgument in ("-c", "--cycle"):
            year_type = currentValue  # e.g. crop or calender
        elif currentArgument in ("-d", "--directory"):
            base_path = currentValue  # e.g. "D:\scripts\python\WRD_project"

    runfile = runfile.capitalize()
    if runfile == 'True':
        run_type = 'manual'
    else:
        run_type = 'csv'

    print("processing scenario:", scenario_no)
    final_dataframe_drpr = run_dr_pf_routines(run_type, base_path, year_type, counter)
    saved_files = save_dataframes_scenario(scenario_no, base_path, final_dataframe_drpr, run_type)
    print("scenario:", scenario_no, 'completed')


# main_controller.py - Function 004: Copies scenario-specific intervention file to main interventions.csv
# Interactions: os, shutil
def copy_scenario_intervention_file(scenario_no, base_path):
    csv_dir = os.path.join(base_path, 'Datasets', 'Inputs', 'csv_inputs')
    
    # Determine source file based on scenario number
    if scenario_no == 0:
        source_file = os.path.join(csv_dir, 'interventions_baseline.csv')
    else:
        source_file = os.path.join(csv_dir, f'interventions_scenario_{scenario_no}.csv')
    
    target_file = os.path.join(csv_dir, 'interventions.csv')
    
    # Check if scenario-specific file exists
    if os.path.exists(source_file):
        shutil.copy2(source_file, target_file)
        print(f"Using interventions from: {os.path.basename(source_file)}")
    else:
        print(f"Warning: {os.path.basename(source_file)} not found. Using default interventions.csv")


# main_controller.py - Function 005: Main orchestrator running all drought proofing processes
# Interactions: orchestrator.input_collector, shared.data_readers, shared.crop_processing, soil_storage_bucket.outflux.evapotranspiration, soil_storage_bucket.input_data.soil_properties, soil_storage_bucket.processing.conservation_practices, soil_storage_bucket.processing.water_storage, shared.land_use, shared.irrigation_efficiency, aquifer_storage_bucket.processing.storage_capacity, aquifer_storage_bucket.influx.recharge_capacity, surface_water_bucket.processing.curve_numbers, surface_water_bucket.processing.runoff_calculations, soil_storage_bucket.processing.soil_moisture_deficit, aquifer_storage_bucket.influx.recharge_calculations, orchestrator.water_balance_coordinator, shared.economics, outputs.output_aggregator, outputs.yield_calculations, pandas, shared.config_constants
def dr_prf_all_processes(inp_source,master_path,file_paths,year_type, counter, scenario_num=0):
    print("FUNCTION 30: dr_prf_all_processes() - Running all drought proofing processes")
    inp_var = collect_inp_variables(inp_source,master_path)
    int_var = collect_int_variables(inp_source,master_path, scenario_num)
    crop_df = get_crop_data(file_paths["crop_db"])
    season_data = get_season_data(inp_source,master_path)
    df_cp, num_plots = assign_plots_to_crops(season_data)
    df_dd = get_pcp_value(file_paths["daily_data"])
    df_mm = process_monthly_data(df_dd, file_paths,inp_source,master_path)
    df_dd = calculate_daily_etoi(df_mm, df_dd)
    df_crop = pd.DataFrame(df_dd["Date"])
    valid_crops_df = select_valid_crops(df_cp)
    all_crops = valid_crops_df["Crop"].tolist()
    all_plots = valid_crops_df["Plot"].unique().tolist()
    df_cc = crop_details(attribute_names, all_crops, crop_df,inp_source,master_path, scenario_num)
    season = get_seasons_val(inp_source,master_path)
    df_crop = process_seasonal_crops(df_crop, crop_df, df_cp, season)
    df_dd, df_crop, df_mm = calc_etci_plot(df_crop, df_cc, df_cp, df_dd, df_mm, all_plots, all_crops,
                                           num_plots, counter, inp_var["kei"], valid_crops_df, crop_df)
    soil_output_list = soil_calculation(inp_source,master_path)
    # Calculate AWC capacity
    depth, awc, awc_capacity = calculate_awc_capacity(soil_output_list[6], soil_output_list[7], soil_output_list[8],
                                                            soil_output_list[9], soil_output_list[0],soil_output_list[1])
    # Assuming df_cc is your DataFrame
    df_cc, overall_sum = calculate_soil_moisture_sums(df_cc)
    # Calculate AWC for soil
    awc_soil_con = calculate_awc_soil(df_cc, config_constants.Cover_Crops_SM_with_practice,
                                            config_constants.Mulching_SM_with_practice,
                                            config_constants.BBF_SM_with_practice, config_constants.Bund_SM_with_practice,
                                            config_constants.Tillage_SM_with_practice,
                                            awc_capacity)
    df_cc = get_cover_type(df_cc, crop_df)
    seasons = get_seasons_data(inp_source,master_path)
    df_cc, actual_fallow_cn2, actual_cn2 = process_cn_values(seasons, df_cc, crop_df, soil_output_list,
                                                                            all_crops,inp_source,master_path)
    
    # land_use_types = get_land_use_types()
    crop_area_inp_list = list(get_land_use_types(inp_source,master_path).values())
    cn_lulc_values_list = [config_constants.slope, actual_fallow_cn2] + [getattr(config_constants, attr) for attr in
                                                                     ["Builtup_cn2", "WB_cn2", "Pasture_cn2",
                                                                      "Forest_cn2"]]
    total_area = calculate_total_area(crop_area_inp_list)
    capacity = calculate_capacity(awc_capacity, config_constants.with_out_soil_con, total_area, overall_sum, awc_soil_con)
    soil_prop_list = [capacity, config_constants.theta_FC, config_constants.theta_WP, config_constants.Ze]
    
    
    df_crop = calc_crop_int(df_crop, df_cc, df_cp, valid_crops_df, all_plots, all_crops, soil_prop_list)

    df_crop = calc_crop_consolidated_cn(df_dd, df_crop, actual_cn2, df_cc, all_crops, crop_area_inp_list,
                                                       cn_lulc_values_list)
    fixed_values = {
        "Ia_AMC1": config_constants.Ia_AMC1,
        "Ia_AMC2": config_constants.Ia_AMC2,
        "Ia_AMC3": config_constants.Ia_AMC3,
        "Soil_GWrecharge_coefficient": config_constants.Soil_GWrecharge_coefficient
    }
    fixed_values_list = list(fixed_values.values())
    df_dd = calc_discharge(df_dd, df_crop, fixed_values_list)
    aquifer_para_list = [inp_var["Aquifer_Depth"], inp_var["Starting_Level"], inp_var["Specific_Yield"], total_area]
    df_mm = process_monthly_qi(df_dd, df_mm, aquifer_para_list)
    df_crop = calc_smdi_plot(df_crop, df_dd, valid_crops_df, all_plots, config_constants.SMDi_1)
    df_crop, df_mm, df_dd = calc_gwnr_fallow_plot(df_crop, df_mm, df_dd, all_plots, all_crops, crop_area_inp_list, df_cc)
    area_eff_list = [
        inp_var.get(attr) for attr in ["SW_Area", "GW_Area", "SW_Area_Irr_Eff", "GW_Area_Irr_Eff"]
    ] + [config_constants.Eff_Default_Irrigation]
    
    irr_eff = calc_irr_eff(area_eff_list, crop_area_inp_list)
    df_cc, df_mm = calc_overall_eff(df_mm, df_cc, all_crops, irr_eff)
    storage_limit = calculate_storage_limit(aquifer_para_list)
    surface_areas, added_recharges, added_recharge_capacity, sw_storage_capacity_created = calc_recharge_capacity(
        int_var["Farm_Pond_Vol"], int_var["Farm_Pond_Depth"], int_var["Farm_Pond_Inf_Rate"],
        int_var["Farm_Pond_Lined_Vol"], int_var["Farm_Pond_Lined_Depth"], int_var["Farm_Pond_Lined_Inf_Rate"],
        int_var["Check_Dam_Vol"], int_var["Check_Dam_Depth"], int_var["Check_Dam_Inf_Rate"],
        int_var["Infiltration_Pond_Vol"], int_var["Infiltration_Pond_Depth"], int_var["Infiltration_Pond_Inf_Rate"],
        int_var["Injection_Wells_Vol"], int_var["Injection_Wells_Nos"]
    )
    
    water_resource_list = [
        inp_var.get(attr) for attr in [
            "Population", "Domestic_Water_Use", "Other", "Other_Water_Use", "Groundwater_Dependent"
        ]] + [sw_storage_capacity_created, added_recharge_capacity, storage_limit]
    df_mm = process_water_management(df_mm, all_crops, surface_areas, added_recharges, water_resource_list,
                                                    aquifer_para_list, file_paths["irrigation"])
    df_mm = process_final_wb(df_mm, all_crops, df_cc, df_crop)
    df_yr = process_yearly_df(df_mm, df_cc, all_crops, yield_columns,
                                             other_columns)
    economic_list = [float(int_var["Interest_Rate"]), float(int_var["Time_Period"])]
    df_int = calculate_intervention_economics(economic_list, df_cc,inp_source,master_path, scenario_num)
    df_crop_yr, df_wb_yr, df_wb_mm = process_water_year_data(df_mm, df_cp, all_crops, year_type)
    df_crop_yr = calculate_yield_wyr(df_cc, df_crop_yr, all_crops)
    df_crop_yr = calc_weighted_avg(df_cc, df_crop_yr, all_crops, yield_columns,
                                      other_columns)
    df_cwr, df_cwr_met, df_yield, df_drought = process_year_data(df_yr, df_crop_yr, all_crops, year_type)
# Removed from here - moved to proper location in calc_gwnr_fallow_plot
    output_dictionary = {
        "df_dd.csv": df_dd,
        "df_mm.csv": df_mm,
        "df_crop.csv": df_crop,
        "df_yr.csv": df_yr,
        "df_wb_mm_output.csv": df_wb_mm,
        "df_cwr_output.csv": df_cwr,
        "df_cwr_met_output.csv": df_cwr_met,
        "df_yield_output.csv": df_yield,
        "df_drought_output.csv": df_drought,
        "df_cc.csv": df_cc,  # Ensure df_cc is saved with its index,
        "df_int.csv": df_int,
        "df_wb_yr_output.csv": df_wb_yr
    }
    
    return output_dictionary


# main_controller.py - Function 006: Entry point for drought proofing routines
# Interactions: shared.data_readers.get_file_paths, dr_prf_all_processes
def run_dr_pf_routines(inp_source, master_path, year_type, counter, scenario_num=0):
    print("FUNCTION 31: run_dr_pf_routines() - Starting main drought proofing routines")
    file_paths = get_file_paths(inp_source, master_path)
    consolidated_dataframes = dr_prf_all_processes(inp_source, master_path, file_paths, year_type, counter, scenario_num)
    return consolidated_dataframes