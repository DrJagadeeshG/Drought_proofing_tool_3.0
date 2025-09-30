
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:52:52 2024

@author: Dr. Jagadeesh, Consultant, IWMI
"""
import pandas as pd
import time
import os
import drpf_functions
import getopt
import sys
from user_input import collect_inp_variables
from user_input import collect_int_variables
from user_input import clear_file_paths_cache
from analyze_by_rainfall_category import analyze_outputs_by_rainfall_category


counter = [0]  # static input for paddy to consider farm flooding period. DONOT modify

# drought_proofing_tool.py - Function 1: Saves all output dataframes to CSV files in scenario-specific folders
def save_dataframes_scenario(val_scenario, master_path, output_dictionary, inp_source):
    
    # drought_proofing_tool.py - Function 1.1: Saves input and intervention variables to CSV files
    def save_dictionaries_to_csv(val_scenario, inp_source, scenario_folder):
        # Collect variables
        inp_var = collect_inp_variables(inp_source, master_path)
        int_var = collect_int_variables(inp_source, master_path)
        
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
    output_dir = os.path.join(master_path, r"Datasets\Outputs")
    
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




# drought_proofing_tool.py - Function 2: Processes command line arguments and runs the scenario
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
            -m, -manual         Is input data provided from manual_input.py then: True. 
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
    final_dataframe_drpr = drpf_functions.run_dr_pf_routines(run_type, base_path, year_type, counter)
    saved_files = save_dataframes_scenario(scenario_no, base_path, final_dataframe_drpr, run_type)
    print("scenario:", scenario_no, 'completed')


# drought_proofing_tool.py - Function 3: Copies scenario-specific intervention file to main interventions.csv
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
        import shutil
        shutil.copy2(source_file, target_file)
        print(f"Using interventions from: {os.path.basename(source_file)}")
    else:
        print(f"Warning: {os.path.basename(source_file)} not found. Using default interventions.csv")

if __name__ == "__main__":
    # # # FOR COMMAND LINE
    # main(sys.argv[1:])
    # # #python D:\scripts\python\WRD_projects\Drought_proofing\drought_proofing_tool.py -m True -s 3 -c crop -d D:\scripts\python\WRD_projects

    # # FOR IDE BASED RUN UNCOMMENT BELOW LINES
    # drought_proofing_tool.py - Function 4: Main execution starting
    # Clear the file paths cache to ensure fresh input data reading
    clear_file_paths_cache()
    # Record the start time
    st_time = time.time()
    # Check if scenario number is provided as command line argument
    if len(sys.argv) > 1:
        scenario_no = int(sys.argv[1])
    else:
        scenario_no = 0  # Default to baseline
    run_type = "csv"                 # Set to "manual" when manually defining input data in the script.
                                        # Set to "csv" when importing data from CSV files.
    year_type = "calendar"                  # Set to "crop" for crop-year-based analysis or "calendar" for calendar-year-based analysis.
    base_path = os.getcwd()   # Use current working directory
    
    # Copy the appropriate intervention file for this scenario
    copy_scenario_intervention_file(scenario_no, base_path)
    # drought_proofing_tool.py - Function 5: Starting main processing
    final_dataframe_drpr = drpf_functions.run_dr_pf_routines(run_type, base_path, year_type, counter)
    # drought_proofing_tool.py - Function 6: Saving scenario outputs
    saved_files = save_dataframes_scenario(scenario_no, base_path, final_dataframe_drpr, run_type)
    
    # Run rainfall category analysis
    # drought_proofing_tool.py - Function 7: Running rainfall category analysis
    # Get the scenario folder path
    output_dir = os.path.join(base_path, r"Datasets\Outputs")
    if scenario_no == 0:
        scenario_folder = os.path.join(output_dir, "Baseline_Scenario")
    else:
        scenario_folder = os.path.join(output_dir, f"Scenario_{scenario_no}")
    
    try:
        analyze_outputs_by_rainfall_category(base_path, scenario_folder)
        print("   Rainfall category analysis completed successfully")
    except Exception as e:
        print(f"   Warning: Could not complete rainfall category analysis: {e}")
    
    # Record the end time
    end_time = time.time()
    # Calculate the total runtime
    runtime = end_time - st_time
    print(f"Plot execution completed in {runtime:.1f} seconds")
