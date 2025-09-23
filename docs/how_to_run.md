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
├── run.py                      # Main entry point
├── aquifer_storage_bucket/     # Groundwater management
├── orchestrator/               # Main coordination
├── outputs/                    # Results processing
├── shared/                     # Common utilities
├── soil_storage_bucket/        # Soil moisture dynamics
├── surface_water_bucket/       # Surface water management
├── Datasets/                   # Input/output data
└── docs/                       # Documentation
```

## Running the Tool

### Basic Usage

```bash
# Navigate to the drought_proofing_tool directory
cd drought_proofing_tool

# Run baseline scenario (default)
python3 run.py
```

### Running Specific Scenarios

```bash
# Run baseline scenario (0)
python3 run.py

# Run scenario 1
python3 run.py 1

# Run scenario 2
python3 run.py 2

# Run scenario 3
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

The `run.py` script:

1. **Accepts scenario number** as command line argument (0-3)
2. **Calls the orchestrator** to coordinate all three buckets
3. **Processes the scenario** using CSV input data
4. **Saves results** to `Datasets/Outputs/` directory
5. **Reports completion** with number of files saved

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