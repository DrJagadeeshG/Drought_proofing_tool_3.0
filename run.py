"""
Drought Proofing Tool - Main Runner Script

Usage:
    python3 run.py [scenario_number]

Examples:
    python3 run.py     # Runs baseline scenario (0)
    python3 run.py 1   # Runs scenario 1
    python3 run.py 2   # Runs scenario 2
    python3 run.py 3   # Runs scenario 3

Running Multiple Scenarios in Parallel:
    # Open separate terminals and run:
    python3 run.py 1 &   # Scenario 1 in background
    python3 run.py 2 &   # Scenario 2 in background
    python3 run.py 3 &   # Scenario 3 in background
"""

# ========================================
# FILE PURPOSE: Main entry point for running drought proofing scenarios with command line interface
# ========================================

import os
import sys
from orchestrator.main_controller import run_dr_pf_routines, save_dataframes_scenario

# Get scenario number from command line argument, default to 0 (baseline)
if len(sys.argv) > 1:
    try:
        scenario = int(sys.argv[1])
    except ValueError:
        print("Error: Scenario must be a number (0, 1, 2, or 3)")
        print("Usage: python3 run.py [scenario_number]")
        print("Examples:")
        print("  python3 run.py     # Runs baseline scenario (0)")
        print("  python3 run.py 1   # Runs scenario 1")
        print("  python3 run.py 2   # Runs scenario 2")
        print("  python3 run.py 3   # Runs scenario 3")
        sys.exit(1)
else:
    scenario = 0  # Default to baseline scenario

counter = [0]
base_path = os.getcwd()

print(f"Running scenario {scenario}...")
results = run_dr_pf_routines('csv', base_path, 'calendar', counter)
saved_files = save_dataframes_scenario(scenario, base_path, results, 'csv')
print(f"Completed! {len(saved_files)} files saved")