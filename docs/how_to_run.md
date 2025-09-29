# How to Run This?

This guide provides step-by-step instructions for setting up and running the Drought Proofing Tool.

## Prerequisites

Before running the tool, ensure you have:

- **Python 3.x** installed on your system
- **Command line access** (Terminal, Command Prompt, or PowerShell)

## Project Structure

The tool is organized into modular buckets:

```
drought_proofing_tool/
├── run.py                      # Main entry point (with auto-conversion)
├── converter.py                # NEW: Converts tabular → key-value files
├── aquifer_storage_bucket/     # Groundwater management
├── orchestrator/               # Main coordination
├── outputs/                    # Results processing
├── shared/                     # Common utilities
├── soil_storage_bucket/        # Soil moisture dynamics
├── surface_water_bucket/       # Surface water management
├── Datasets/                   # Input/output data
│   └── Inputs/
│       └── csv_inputs/
│           ├── input.csv                              # Main input file
│           ├── interventions_scenario_X_correct.csv   # NEW: User-friendly files
│           ├── interventions_scenario_X.csv           # System files (auto-generated)
│           └── interventions_scenario_X_original_backup.csv  # Backups
└── docs/                       # Documentation
```

## Plot-Based System (NEW!)

The tool now uses a **plot-based approach** instead of seasonal assignments:

- **Plot 1, 2, 3** instead of rigid Kharif/Rabi/Summer seasons
- **Dynamic crop-plot mapping** - automatically detects crops per plot from input data
- **Fully configurable** - no hardcoded crop assignments, adaptable to any crop pattern
- **Backward compatible** - still works with existing seasonal input data

## Running the Tool

### New User-Friendly Workflow

#### Step 1: Edit User-Friendly Intervention Files
The tool now supports user-friendly tabular CSV files that you can edit directly:

```bash
# Edit these files in Excel or any text editor:
Datasets/Inputs/csv_inputs/interventions_scenario_1_correct.csv
Datasets/Inputs/csv_inputs/interventions_scenario_2_correct.csv  
Datasets/Inputs/csv_inputs/interventions_scenario_3_correct.csv
```

**File Structure:** Each file contains three sections in tabular format:
- **Supply Side Interventions**: Farm ponds, check dams, injection wells
- **Demand Side Interventions**: Drip irrigation, sprinkler, land levelling  
- **Soil Management Interventions**: Cover crops, mulching, bunds

#### Step 2: Auto-Conversion Feature (NEW!)
The system automatically converts user files when running scenarios:

```bash
# Navigate to the drought_proofing_tool directory
cd drought_proofing_tool

# Run scenarios - auto-conversion happens automatically
python3 run.py 1    # Auto-converts correct file → runs scenario 1
python3 run.py 2    # Auto-converts correct file → runs scenario 2  
python3 run.py 3    # Auto-converts correct file → runs scenario 3

# Run baseline scenario (no conversion needed)
python3 run.py      # Runs baseline scenario (0)
```

### Manual Conversion (Optional)

```bash
# Convert specific scenario manually if needed
python converter.py 1

# Convert all scenarios at once
python converter.py all
```

### Basic Usage (Legacy)

```bash
# Run baseline scenario (default)
python3 run.py

# Run specific scenarios
python3 run.py 1
python3 run.py 2
python3 run.py 3
```

### Running Multiple Scenarios in Parallel

Open separate terminals and run:

```bash
# Terminal 1
python3 run.py 1 &

# Terminal 2
python3 run.py 2 &

# Terminal 3
python3 run.py 3 &
```

## How It Works

The enhanced `run.py` script:

1. **Accepts scenario number** as command line argument (0-3)
2. **Auto-converts user files** (NEW!) - Automatically runs `converter.py` for intervention scenarios
3. **Copies scenario files** - Uses appropriate intervention file for the scenario
4. **Calls the orchestrator** to coordinate all three buckets with plot-based processing
5. **Processes the scenario** using CSV input data with dynamic intervention detection
6. **Saves results** to `Datasets/Outputs/[Scenario_Name]/` directory
7. **Reports completion** with number of files saved

## Configuration

- **Input Source**: Uses CSV files from `Datasets/Inputs/`
- **Scenario Data**: Different intervention parameters per scenario
- **Output Location**: Results saved to `Datasets/Outputs/[Scenario_Name]/`

## Three-Bucket Architecture

The tool coordinates:

- **Surface Water Bucket** - Runoff generation and surface storage
- **Soil Storage Bucket** - Crop water dynamics and soil moisture
- **Aquifer Storage Bucket** - Groundwater recharge and extraction

## Getting Help

If you encounter issues:

1. **Check input data** - Ensure all required CSV files are present in `Datasets/Inputs/`
2. **Verify scenario number** - Must be 0, 1, 2, or 3
3. **Check module documentation** - Each bucket has detailed technical documentation
4. **Contact support** - Reach out to the project team (see [Contact](contact.md) page)

---

*For detailed technical information about each module, refer to the [Modules](index.md#core-modules) section.*