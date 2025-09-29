"""
Intervention CSV Converter
==========================

This module converts tabular "correct" CSV files to key-value pair CSV files.

User Flow:
1. Users edit: interventions_scenario_X_correct.csv (tabular format)
2. This converter creates: interventions_scenario_X.csv (key-value format)
3. System uses: The generated key-value files

Usage:
    python converter.py [scenario_number]
    python converter.py all
"""

import pandas as pd
import os
import sys

def read_correct_csv(scenario_num):
    """Read the tabular 'correct' CSV file for a scenario."""
    file_path = f"Datasets/Inputs/csv_inputs/interventions_scenario_{scenario_num}_correct.csv"
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Correct CSV file not found: {file_path}")
    
    # Read the CSV file
    df = pd.read_csv(file_path, header=None)
    return df

def parse_tabular_data(df):
    """Parse the tabular CSV data into structured format."""
    data = {}
    
    # Find the general settings
    for i, row in df.iterrows():
        if pd.notna(row[0]) and row[0] == 'Time_Period':
            data['Time_Period'] = row[1]
        elif pd.notna(row[0]) and row[0] == 'Interest_Rate':
            data['Interest_Rate'] = row[1]
    
    # Find the intervention data section
    intervention_start = None
    for i, row in df.iterrows():
        if pd.notna(row[0]) and 'SUPPLY SIDE INTERVENTIONS' in str(row[0]):
            intervention_start = i
            break
    
    if intervention_start is None:
        raise ValueError("Could not find intervention data section")
    
    # Parse headers (should be at intervention_start + 1)
    header_row = df.iloc[intervention_start + 1]
    
    # Find column indices for each section
    supply_cols = {}
    demand_cols = {}
    soil_cols = {}
    
    # Map column indices
    for idx, col_name in enumerate(header_row):
        if pd.isna(col_name):
            continue
        col_name = str(col_name).strip()
        
        # Supply side columns (0-7)
        if idx <= 7:
            if 'Supply Intervention' in col_name:
                supply_cols['name'] = idx
            elif 'Vol' in col_name:
                supply_cols['vol'] = idx
            elif 'Depth' in col_name:
                supply_cols['depth'] = idx
            elif 'Inf_Rate' in col_name:
                supply_cols['inf_rate'] = idx
            elif 'Cost' in col_name:
                supply_cols['cost'] = idx
            elif 'Life_Span' in col_name:
                supply_cols['life_span'] = idx
            elif 'Maintenance' in col_name:
                supply_cols['maintenance'] = idx
            elif 'Units' in col_name:
                supply_cols['units'] = idx
        
        # Demand side columns (9-16)
        elif 9 <= idx <= 16:
            if 'Demand Intervention' in col_name:
                demand_cols['name'] = idx
            elif 'Crop_Area_1' in col_name:
                demand_cols['area_1'] = idx
            elif 'Crop_Area_2' in col_name:
                demand_cols['area_2'] = idx
            elif 'Crop_Area_3' in col_name:
                demand_cols['area_3'] = idx
            elif 'Eff' in col_name:
                demand_cols['eff'] = idx
            elif 'Cost' in col_name:
                demand_cols['cost'] = idx
            elif 'Life_Span' in col_name:
                demand_cols['life_span'] = idx
            elif 'Maintenance' in col_name:
                demand_cols['maintenance'] = idx
        
        # Soil side columns (18-25)
        elif 18 <= idx <= 25:
            if 'Soil Intervention' in col_name:
                soil_cols['name'] = idx
            elif 'Crop_Area_1' in col_name:
                soil_cols['area_1'] = idx
            elif 'Crop_Area_2' in col_name:
                soil_cols['area_2'] = idx
            elif 'Crop_Area_3' in col_name:
                soil_cols['area_3'] = idx
            elif 'Red_CN' in col_name:
                soil_cols['red_cn'] = idx
            elif 'Eva_Red' in col_name:
                soil_cols['eva_red'] = idx
            elif 'Cost' in col_name:
                soil_cols['cost'] = idx
            elif 'Life_Span' in col_name:
                soil_cols['life_span'] = idx
            elif 'Maintenance' in col_name:
                soil_cols['maintenance'] = idx
    
    # Parse intervention data rows
    interventions = {}
    
    # Start from the row after headers
    for i in range(intervention_start + 2, len(df)):
        row = df.iloc[i]
        
        # Parse supply side interventions
        if supply_cols.get('name') is not None and pd.notna(row[supply_cols['name']]):
            intervention_name = str(row[supply_cols['name']]).strip()
            if intervention_name and intervention_name != '':
                interventions[f"{intervention_name}_Vol"] = row[supply_cols.get('vol', 0)] or 0
                interventions[f"{intervention_name}_Depth"] = row[supply_cols.get('depth', 0)] or 0
                interventions[f"{intervention_name}_Inf_Rate"] = row[supply_cols.get('inf_rate', 0)] or 0
                interventions[f"{intervention_name}_Cost"] = row[supply_cols.get('cost', 0)] or 0
                interventions[f"{intervention_name}_Life_Span"] = row[supply_cols.get('life_span', 0)] or 0
                interventions[f"{intervention_name}_Maintenance"] = row[supply_cols.get('maintenance', 0)] or 0
                
                # Handle units/nos naming
                if intervention_name == "Injection_Wells":
                    interventions[f"{intervention_name}_Nos"] = row[supply_cols.get('units', 0)] or 0
                else:
                    interventions[f"{intervention_name}_Units"] = row[supply_cols.get('units', 0)] or 0
        
        # Parse demand side interventions
        if demand_cols.get('name') is not None and pd.notna(row[demand_cols['name']]):
            intervention_name = str(row[demand_cols['name']]).strip()
            if intervention_name and intervention_name != '':
                # Map intervention names to area names
                if intervention_name == "Drip_irrigation":
                    area_suffix = "Drip_Area"
                elif intervention_name == "Sprinkler_irrigation":
                    area_suffix = "Sprinkler_Area"
                else:
                    area_suffix = f"{intervention_name}_Area"
                
                interventions[f"Crop_Area_1_{area_suffix}"] = row[demand_cols.get('area_1', 0)] or 0
                interventions[f"Crop_Area_2_{area_suffix}"] = row[demand_cols.get('area_2', 0)] or 0
                interventions[f"Crop_Area_3_{area_suffix}"] = row[demand_cols.get('area_3', 0)] or 0
                interventions[f"Eff_{intervention_name}"] = row[demand_cols.get('eff', 0)] or 0
                
                # Handle different cost naming conventions
                if intervention_name == "Drip_irrigation":
                    interventions["Drip_Irr_Cost"] = row[demand_cols.get('cost', 0)] or 0
                    interventions["Drip_Irr_Life_Span"] = row[demand_cols.get('life_span', 0)] or 0
                    interventions["Drip_Irr_Maintenance"] = row[demand_cols.get('maintenance', 0)] or 0
                elif intervention_name == "Sprinkler_irrigation":
                    interventions["Sprinkler_Irr_Cost"] = row[demand_cols.get('cost', 0)] or 0
                    interventions["Sprinkler_Irr_Life_Span"] = row[demand_cols.get('life_span', 0)] or 0
                    interventions["Sprinkler_Irr_Maintenance"] = row[demand_cols.get('maintenance', 0)] or 0
                else:
                    interventions[f"{intervention_name}_Cost"] = row[demand_cols.get('cost', 0)] or 0
                    interventions[f"{intervention_name}_Life_Span"] = row[demand_cols.get('life_span', 0)] or 0
                    interventions[f"{intervention_name}_Maintenance"] = row[demand_cols.get('maintenance', 0)] or 0
        
        # Parse soil side interventions
        if soil_cols.get('name') is not None and pd.notna(row[soil_cols['name']]):
            intervention_name = str(row[soil_cols['name']]).strip()
            if intervention_name and intervention_name != '':
                # Handle Tank naming - use original naming convention
                if intervention_name == "Tank":
                    interventions[f"Crop_Area_1_Tank_Area"] = row[soil_cols.get('area_1', 0)] or 0
                    interventions[f"Crop_Area_2_Tank_Area"] = row[soil_cols.get('area_2', 0)] or 0
                    interventions[f"Crop_Area_3_Tank_Area"] = row[soil_cols.get('area_3', 0)] or 0
                    interventions[f"Red_CN_Tank"] = row[soil_cols.get('red_cn', 0)] or 0
                    interventions[f"Tank_Eva_Red"] = row[soil_cols.get('eva_red', 0)] or 0
                    interventions[f"Tank_Desilting_Life_Span"] = row[soil_cols.get('life_span', 0)] or 0
                    interventions[f"Tank_Desilting_Vol"] = row[soil_cols.get('vol', 0)] or 0
                    interventions[f"Tank_Desilting_Depth"] = row[soil_cols.get('depth', 0)] or 0
                    interventions[f"Tank_Desilting_Cost"] = row[soil_cols.get('cost', 0)] or 0
                else:
                    interventions[f"Crop_Area_1_{intervention_name}_Area"] = row[soil_cols.get('area_1', 0)] or 0
                    interventions[f"Crop_Area_2_{intervention_name}_Area"] = row[soil_cols.get('area_2', 0)] or 0
                    interventions[f"Crop_Area_3_{intervention_name}_Area"] = row[soil_cols.get('area_3', 0)] or 0
                    interventions[f"Red_CN_{intervention_name}"] = row[soil_cols.get('red_cn', 0)] or 0
                    interventions[f"{intervention_name}_Eva_Red"] = row[soil_cols.get('eva_red', 0)] or 0
                    interventions[f"{intervention_name}_Cost"] = row[soil_cols.get('cost', 0)] or 0
                    interventions[f"{intervention_name}_Life_Span"] = row[soil_cols.get('life_span', 0)] or 0
                    interventions[f"{intervention_name}_Maintenance"] = row[soil_cols.get('maintenance', 0)] or 0
    
    # Add general settings
    interventions['Time_Period'] = data.get('Time_Period', 20)
    interventions['Interest_Rate'] = data.get('Interest_Rate', 7)
    
    return interventions

def generate_keyvalue_csv(interventions, scenario_num):
    """Generate key-value pair CSV file from interventions data."""
    output_file = f"Datasets/Inputs/csv_inputs/interventions_scenario_{scenario_num}.csv"
    
    # Define the order of parameters to match existing files
    parameter_order = [
        'Time_Period', 'Interest_Rate',
        # Supply side interventions
        'Farm_Pond_Vol', 'Farm_Pond_Depth', 'Farm_Pond_Inf_Rate', 'Farm_Pond_Cost', 
        'Farm_Pond_Life_Span', 'Farm_Pond_Maintenance', 'Farm_Pond_Units',
        'Farm_Pond_Lined_Vol', 'Farm_Pond_Lined_Depth', 'Farm_Pond_Lined_Inf_Rate', 
        'Farm_Pond_Lined_Cost', 'Farm_Pond_Lined_Life_Span', 'Farm_Pond_Lined_Maintenance', 'Farm_Pond_Lined_Width',
        'Farm_Pond_Lined_Units',
        'Check_Dam_Vol', 'Check_Dam_Depth', 'Check_Dam_Inf_Rate', 'Check_Dam_Cost', 
        'Check_Dam_Life_Span', 'Check_Dam_Maintenance', 'Check_Dam_Units',
        'Infiltration_Pond_Vol', 'Infiltration_Pond_Depth', 'Infiltration_Pond_Inf_Rate', 
        'Infiltration_Pond_Cost', 'Infiltration_Pond_Life_Span', 'Infiltration_Pond_Maintenance',
        'Injection_Wells_Vol', 'Injection_Wells_Nos', 'Injection_Wells_Cost', 
        'Injection_Wells_Life_Span', 'Injection_Wells_Maintenance',
        # Demand side interventions
        'Crop_Area_1_Drip_Area', 'Crop_Area_2_Drip_Area', 'Crop_Area_3_Drip_Area',
        'Eff_Drip_irrigation', 'Drip_Irr_Cost', 'Drip_Irr_Life_Span', 'Drip_Irr_Maintenance',
        'Crop_Area_1_Sprinkler_Area', 'Crop_Area_2_Sprinkler_Area', 'Crop_Area_3_Sprinkler_Area',
        'Eff_Sprinkler_irrigation', 'Sprinkler_Irr_Cost', 'Sprinkler_Irr_Life_Span', 'Sprinkler_Irr_Maintenance',
        'Crop_Area_1_Land_Levelling_Area', 'Crop_Area_2_Land_Levelling_Area', 'Crop_Area_3_Land_Levelling_Area',
        'Eff_Land_Levelling', 'Land_Levelling_Cost', 'Land_Levelling_Life_Span', 'Land_Levelling_Maintenance',
        'Crop_Area_1_DSR_Area', 'Crop_Area_2_DSR_Area', 'Crop_Area_3_DSR_Area',
        'Eff_Direct_Seeded_Rice', 'Direct_Seeded_Rice_Cost', 'Direct_Seeded_Rice_Life_Span',
        'Crop_Area_1_AWD_Area', 'Crop_Area_2_AWD_Area', 'Crop_Area_3_AWD_Area',
        'Eff_Alternate_Wetting_And_Dry', 'Alternate_Wetting_And_Dry_Cost', 'Alternate_Wetting_And_Dry_Life_Span',
        'Crop_Area_1_SRI_Area', 'Crop_Area_2_SRI_Area', 'Crop_Area_3_SRI_Area',
        'Eff_SRI', 'SRI_Cost', 'SRI_Life_Span',
        'Crop_Area_1_Ridge_Furrow_Area', 'Crop_Area_2_Ridge_Furrow_Area', 'Crop_Area_3_Ridge_Furrow_Area',
        'Eff_Ridge_Furrow_Irrigation', 'Ridge_Furrow_Irrigation_Cost', 'Ridge_Furrow_Irrigation_Life_Span',
        'Crop_Area_1_Deficit_Area', 'Crop_Area_2_Deficit_Area', 'Crop_Area_3_Deficit_Area',
        'Eff_Deficit_Irrigation', 'Deficit_Irrigation_Cost', 'Deficit_Irrigation_Life_Span',
        # Soil interventions
        'Crop_Area_1_Cover_Crops_Area', 'Crop_Area_2_Cover_Crops_Area', 'Crop_Area_3_Cover_Crops_Area',
        'Red_CN_Cover_Crops', 'Cover_Crops_Cost', 'Cover_Crops_Life_Span', 'Cover_Crops_Eva_Red',
        'Crop_Area_1_Mulching_Area', 'Crop_Area_2_Mulching_Area', 'Crop_Area_3_Mulching_Area',
        'Red_CN_Mulching', 'Mulching_Cost', 'Mulching_Life_Span', 'Mulching_Eva_Red',
        'Crop_Area_1_BBF_Area', 'Crop_Area_2_BBF_Area', 'Crop_Area_3_BBF_Area',
        'Red_CN_BBF', 'BBF_Cost', 'BBF_Life_Span', 'BBF_Maintenance', 'Eff_BBF',
        'Crop_Area_1_Bunds_Area', 'Crop_Area_2_Bunds_Area', 'Crop_Area_3_Bunds_Area',
        'Red_CN_Bund', 'Bund_Cost', 'Bund_Life_Span', 'Bund_Maintenance',
        'Crop_Area_1_Tillage_Area', 'Crop_Area_2_Tillage_Area', 'Crop_Area_3_Tillage_Area',
        'Red_CN_Tillage', 'Tillage_Cost', 'Tillage_Life_Span', 'Tillage_Eva_Red',
        'Crop_Area_1_Tank_Area', 'Crop_Area_2_Tank_Area', 'Crop_Area_3_Tank_Area',
        'Red_CN_Tank', 'Tank_Desilting_Life_Span', 'Tank_Eva_Red', 
        'Tank_Desilting_Vol', 'Tank_Desilting_Depth', 'Tank_Desilting_Cost'
    ]
    
    # Write to CSV file
    with open(output_file, 'w', newline='') as f:
        for param in parameter_order:
            value = interventions.get(param, 0)
            # Handle empty values
            if pd.isna(value) or value == '' or value is None:
                value = 0
            f.write(f"{param},{value}\n")
    
    print(f"Generated: {output_file}")

def convert_scenario(scenario_num):
    """Convert a single scenario from tabular to key-value format."""
    try:
        print(f"Converting scenario {scenario_num}...")
        
        # Read the correct CSV file
        df = read_correct_csv(scenario_num)
        
        # Parse the tabular data
        interventions = parse_tabular_data(df)
        
        # Generate key-value CSV
        generate_keyvalue_csv(interventions, scenario_num)
        
        print(f"✅ Successfully converted scenario {scenario_num}")
        
    except Exception as e:
        print(f"❌ Error converting scenario {scenario_num}: {str(e)}")
        raise

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python converter.py [scenario_number|all]")
        print("Examples:")
        print("  python converter.py 1")
        print("  python converter.py all")
        return
    
    arg = sys.argv[1].lower()
    
    if arg == 'all':
        # Convert all scenarios
        for scenario in [1, 2, 3]:
            try:
                convert_scenario(scenario)
            except Exception as e:
                print(f"Failed to convert scenario {scenario}: {e}")
    else:
        # Convert specific scenario
        try:
            scenario_num = int(arg)
            if scenario_num not in [1, 2, 3]:
                print("Error: Scenario number must be 1, 2, or 3")
                return
            convert_scenario(scenario_num)
        except ValueError:
            print("Error: Invalid scenario number")

if __name__ == "__main__":
    main()
