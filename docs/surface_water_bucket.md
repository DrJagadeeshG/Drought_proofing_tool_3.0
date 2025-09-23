# Surface Water Bucket

The Surface Water Bucket module manages surface water dynamics, runoff generation, and water storage in the three-bucket water balance system, implementing the SCS curve number methodology for rainfall-runoff transformation and surface water resource management.

## Overview

This module handles:

- **Runoff generation** using SCS curve number methodology with antecedent moisture conditions
- **Curve number calculations** for diverse land uses, crops, and conservation practices
- **Water supply management** including canal water availability and surface water abstraction
- **Surface water storage** with evaporation losses and water allocation
- **Precipitation processing** accounting for groundwater recharge components
- **Water demand calculations** for domestic, agricultural, and other uses
- **Final water balance** integrating runoff, storage, and abstraction processes

## Surface Water Bucket Flow

The surface water bucket implements comprehensive runoff generation and surface water management:

```mermaid
graph TD
    %% Inputs
    A[Precipitation P] --> B[Net Rainfall<br/>P - Recharge_src]

    %% Curve Number System
    C[Land Use] --> D[Curve Number Database]
    S[Soil Type] --> D
    H[Hydrologic Condition] --> D
    D --> D1[Base CN Values]

    %% Conservation Practices
    CP[Conservation Practices] --> CP1[CN Reduction<br/>Cover Crops, Mulching]
    CP1 --> D2[Adjusted CN Values]
    D1 --> D2

    %% Antecedent Moisture Conditions
    AMC[5-Day Rainfall] --> AMC1{AMC Condition}
    AMC1 --> AMC2[AMC I - Dry<br/>CN₁ = CN₂/2.281-0.01281×CN₂]
    AMC1 --> AMC3[AMC II - Normal<br/>CN₂ = Standard Value]
    AMC1 --> AMC4[AMC III - Wet<br/>CN₃ = CN₂/0.427+0.00573×CN₂]

    %% Slope Adjustment
    D2 --> SA[Slope Adjustment<br/>Williams Formula]
    SLOPE[Slope %] --> SA
    SA --> CNF[Final CN]

    %% SCS Runoff Calculation
    CNF --> SCS1[Potential Retention<br/>S = 25400/CN - 254]
    SCS1 --> SCS2[Initial Abstraction<br/>Ia = 0.2 × S]
    B --> SCS3[Runoff Calculation<br/>Q = P-Ia²/P+S-Ia]
    SCS2 --> SCS3

    %% Surface Water Storage
    SCS3 --> SW1[Surface Storage<br/>Farm Ponds, Tanks]
    CANAL[Canal Water Supply] --> SW1
    SW1 --> SW2[Storage Capacity Check]
    SW2 --> SW3[Water Allocation]

    %% Water Demands
    DOM[Domestic Demand] --> SW3
    IRR[Irrigation Demand] --> SW3
    OTHER[Other Demands] --> SW3

    %% Water Abstraction
    SW3 --> ABS[Surface Water Abstraction<br/>min(Available, Demand)]
    ABS --> ABS1[Remaining Surface Water]

    %% Evaporation Losses
    EV[Surface Area] --> EVAP[Evaporation Losses<br/>Area × ET₀]
    ABS1 --> EVAP
    EVAP --> FR[Final Runoff<br/>Including Rejected Recharge]

    %% Integration
    FR --> OUT[Surface Water Outputs<br/>Runoff + Abstractions]

    %% Styling
    style A fill:#e3f2fd
    style D fill:#fff3e0
    style SCS3 fill:#f3e5f5
    style SW1 fill:#e8f5e8
    style OUT fill:#ffebee
    style CP fill:#f1f8e9
```

## Module Structure

### Influx Calculations

**Water inputs to the surface water bucket:**

- **`influx/precipitation_processing.py`** - Processes precipitation data by calculating net rainfall after groundwater recharge
- **`influx/water_supply.py`** - Calculates water supply availability from external sources like canals

### Input Data Management

**Curve number data and surface characteristics:**

- **`input_data/curve_number_data.py`** - Retrieves curve number values with multiple fallback strategies for runoff calculations

### Outflux Calculations

**Water losses from the surface water bucket:**

- **`outflux/evaporation.py`** - Calculates potential evapotranspiration losses from surface water bodies
- **`outflux/runoff_disposal.py`** - Calculates final runoff disposal after accounting for captured runoff
- **`outflux/water_abstraction.py`** - Calculates abstracted surface water based on available runoff and needs
- **`outflux/water_demand.py`** - Calculates surface water demand requirements for domestic and other uses

### Processing Engine

**Core surface water calculations and transformations:**

- **`processing/curve_numbers.py`** - Comprehensive curve number calculations including crop CN values, land use consolidation, and moisture condition adjustments
- **`processing/moisture_conditions.py`** - Antecedent moisture condition calculations based on rainfall patterns and crop dormancy
- **`processing/runoff_calculations.py`** - Surface runoff calculations using SCS curve number method and water abstraction parameters
- **`processing/surface_calculations.py`** - Surface area calculations from volume and depth parameters for water storage structures
- **`processing/water_balance.py`** - Surface water balance calculations including domestic use abstractions and final runoff components

## Technical Implementation

### SCS Curve Number Methodology

The surface water bucket implements the Soil Conservation Service curve number method for runoff estimation:

```python
# runoff_calculations.py - Function 004: Calculates surface runoff using SCS curve number method
def runoff_cn(pi, iai, si):
    q = safe_divide((pi - iai) ** 2, (pi + si - iai))
    return q

# runoff_calculations.py - Function 003: Calculates water abstraction parameters for runoff calculation
def calc_abstraction(df_dd, df_crop, ia_amc1, ia_amc2, ia_amc3):
    print("FUNCTION 26: calc_abstraction() - Calculating water abstraction")
    si = (25400 / df_dd["CNi"]) - 254
    conditions = [
        df_crop["AMC"] == 1,
        df_crop["AMC"] == 2
    ]
    choices = [si * ia_amc1, si * ia_amc2]
    iai = np.select(conditions, choices, default=si * ia_amc3)
    return si, iai
```

Where:
- **Q** = Surface runoff (mm)
- **P** = Precipitation (mm)
- **Ia** = Initial abstraction (mm)
- **S** = Potential maximum retention (mm)
- **CN** = Curve number (dimensionless)

### Comprehensive Curve Number System

The module implements a sophisticated curve number system supporting multiple land uses and conservation practices:

```python
# curve_numbers.py - Function 001: Calculates consolidated curve numbers for crops and land use
def calc_crop_consolidated_cn(df_dd, df_crop, actual_cn2, df_cc, all_crops, inp_lulc_val_list, cn_values_list):
    print("FUNCTION 14: calc_crop_consolidated_cn() - Calculating crop consolidated CN values")
    area = calculate_total_area(inp_lulc_val_list)
    df_crop = update_cn2(df_crop, actual_cn2, df_cc, all_crops)
    df_crop = calculate_total_sown_area(df_crop, all_crops, inp_lulc_val_list[0])
    df_crop = calculate_consolidated_crop_cn2(df_crop, all_crops)

    # Calculate land use areas
    df_crop["Fallow_area"] = df_crop.apply(
        lambda row: calc_fallow_area(inp_lulc_val_list[0], row["Actual Crop Sown Area"], inp_lulc_val_list[1]), axis=1)
    df_crop["Builtup_area"] = df_crop.apply(lambda row: calc_lulc(inp_lulc_val_list[2], area), axis=1)
    df_crop["Waterbodies_area"] = df_crop.apply(lambda row: calc_lulc(inp_lulc_val_list[3], area), axis=1)
    df_crop["Pasture"] = df_crop.apply(lambda row: calc_lulc(inp_lulc_val_list[4], area), axis=1)
    df_crop["Forest"] = df_crop.apply(lambda row: calc_lulc(inp_lulc_val_list[5], area), axis=1)

    # Calculate final weighted curve number
    df_crop["Final_cn2"] = df_crop.apply(lambda row: calc_final_cn2(row["Builtup_area"], cn_values_list[2],
                                                                    row["Waterbodies_area"], cn_values_list[3],
                                                                    row["Pasture"], cn_values_list[4],
                                                                    row["Forest"], cn_values_list[5],
                                                                    row["Crop_Area"], row["consolidated_crop_cn2"],
                                                                    row["Fallow_Area"], row["Fallowcn2"]), axis=1)
    return df_crop
```

### Curve Number Database with Fallback Strategies

Robust curve number retrieval system with multiple fallback mechanisms:

```python
# curve_number_data.py - Function 001: Retrieves curve number values with multiple fallback strategies
def get_cn(crop_df, crop_type, crop_sown_type, hsc, soil_type, default_cn_value="0"):
    # Check if soil_type or hsc is empty, return default if so
    if not soil_type or not hsc:
        return default_cn_value

    # Primary lookup in the DataFrame
    cn = crop_df[(crop_df["Crop Type"] == crop_type) &
                 (crop_df["Crop Sown Type"] == crop_sown_type) &
                 (crop_df["HSC"] == hsc)]

    if soil_type in cn.columns:
        if not cn.empty:
            cn_value = cn[soil_type].iloc[0]
            if pd.notna(cn_value) and str(cn_value).strip():
                return cn_value

        # Fallback 1: Try with just crop_type and hsc (ignore crop_sown_type)
        cn_fallback1 = crop_df[(crop_df["Crop Type"] == crop_type) & (crop_df["HSC"] == hsc)]
        if not cn_fallback1.empty:
            valid_values = cn_fallback1[soil_type].dropna()
            valid_values = valid_values[valid_values.astype(str).str.strip() != '']
            if not valid_values.empty:
                return valid_values.iloc[0]

        # Fallback 2: Try with just crop_type (ignore crop_sown_type and hsc)
        cn_fallback2 = crop_df[crop_df["Crop Type"] == crop_type]
        if not cn_fallback2.empty:
            valid_values = cn_fallback2[soil_type].dropna()
            valid_values = valid_values[valid_values.astype(str).str.strip() != '']
            if not valid_values.empty:
                return valid_values.iloc[0]

        # Fallback 3: Crop-specific defaults based on typical values
        crop_defaults = {
            "Row Crops": {"Clay": 89, "Clayey Loam": 85, "Loam": 81, "Sandy Loam": 78, "Sand": 72},
            "Small Grains": {"Clay": 94, "Clayey Loam": 91, "Loam": 86, "Sandy Loam": 84, "Sand": 77},
            "Closed Seed or Broadcast legumes": {"Clay": 83, "Clayey Loam": 78, "Loam": 74, "Sandy Loam": 70, "Sand": 65}
        }

        if crop_type in crop_defaults and soil_type in crop_defaults[crop_type]:
            fallback_cn = crop_defaults[crop_type][soil_type]
            return fallback_cn

        return default_cn_value
    else:
        return default_cn_value
```

### Antecedent Moisture Conditions

Dynamic moisture condition assessment affecting curve number selection:

```python
# moisture_conditions.py - Function 001: Calculates antecedent moisture condition based on rainfall and dormancy
def calc_amc_cond(df_dd, df_crop):
    conditions = [
        (df_crop["Dormant"] == "N") & (df_dd["last_5_days_Rain"] < 36),
        (df_crop["Dormant"] == "N") & (df_dd["last_5_days_Rain"] > 53),
        (df_crop["Dormant"] == "N"),
        (df_dd["last_5_days_Rain"] < 13),
        (df_dd["last_5_days_Rain"] > 28)
    ]

    choices = [1, 3, 2, 1, 3]

    amc_cond = np.select(conditions, choices, default=2)
    return amc_cond
```

**Antecedent Moisture Conditions:**
- **AMC I (Dry)** - Low antecedent moisture, higher infiltration, lower runoff
- **AMC II (Normal)** - Average moisture conditions, standard curve numbers
- **AMC III (Wet)** - High antecedent moisture, lower infiltration, higher runoff

### Conservation Practice Integration

Implementation of curve number reductions for conservation interventions:

```python
# curve_numbers.py - Function 007: Calculates reduced curve numbers considering conservation interventions
def calc_red_cn_area(df_cc, all_crops, dict_actual_cn2, inp_source, master_path):
    print("FUNCTION 23: calc_red_cn_area() - Calculating reduced CN area")
    inp_var = collect_int_variables(inp_source, master_path)

    for crop in all_crops:
        if crop in dict_actual_cn2:
            # Total intervention area calculation
            df_cc.at[crop, "Total_Int_Area"] = (
                df_cc.at[crop, "Cover_Area"] + df_cc.at[crop, "Mulching_Area"] +
                df_cc.at[crop, "Bunds_Area"] + df_cc.at[crop, "Tillage_Area"] +
                df_cc.at[crop, "BBF_Area"] + df_cc.at[crop, "Tank_Area"]
            )

            if df_cc.at[crop, "Total_Int_Area"] != 0:
                # Calculate area-weighted curve number reduction
                df_cc.at[crop, "Red_CN2"] = safe_divide(
                    (
                        df_cc.at[crop, "Cover_Area"] * to_float(inp_var.get("Red_CN_Cover_Crops", 0)) +
                        df_cc.at[crop, "Mulching_Area"] * to_float(inp_var.get("Red_CN_Mulching", 0)) +
                        df_cc.at[crop, "Bunds_Area"] * to_float(inp_var.get("Red_CN_Bund", 0)) +
                        df_cc.at[crop, "Tillage_Area"] * to_float(inp_var["Red_CN_Tillage"], 0) +
                        df_cc.at[crop, "BBF_Area"] * to_float(inp_var["Red_CN_BBF"], 0) +
                        df_cc.at[crop, "Tank_Area"] * to_float(inp_var.get("Red_CN_Tillage", 0))
                    ),
                    df_cc.at[crop, "Total_Int_Area"]
                )
            else:
                df_cc.at[crop, "Red_CN2"] = 0

            # Apply curve number reduction
            df_cc.at[crop, "CN2"] = dict_actual_cn2[crop]["Actual_CN2"] - df_cc.at[crop, "Red_CN2"]

            # Calculate final weighted curve number
            df_cc.at[crop, "New_CN2"] = (
                (df_cc.at[crop, "Total_Int_Area"] * df_cc.at[crop, "CN2"]) +
                (df_cc.at[crop, "No_Int_Area"] * dict_actual_cn2[crop]["Actual_CN2"])
            ) / df_cc.at[crop, "Area"]

    return df_cc
```

### Mixed Soil Layer Curve Number Calculations

Weighted curve number calculation for heterogeneous soil profiles:

```python
# curve_numbers.py - Function 005: Calculates weighted actual CN2 value from two soil layer contributions
def calc_act_cn2(cn1, cn2, dist1, dist2):
    if cn1 is not None and cn2 is not None:
        try:
            cn = ((dist1 * float(cn1)) + (dist2 * float(cn2))) / 100
            return cn
        except ValueError:
            print("Error converting CN values to float.")
            return None
    else:
        print("Cannot calculate Actual CN2 due to missing CN values.")
        return None

# curve_numbers.py - Function 006: Calculates actual curve numbers for all crops using input distributions
def calculate_actual_cn(all_cn_values, inp_source, master_path):
    print("FUNCTION 22: calculate_actual_cn() - Calculating actual CN values")
    inp_var = collect_inp_variables(inp_source, master_path)
    updated_cn_values = {}

    for crop, cn_data in all_cn_values.items():
        cn1 = cn_data.get("CN1")
        cn2 = cn_data.get("CN2")

        loc_actual_cn2 = calc_act_cn2(cn1, cn2, to_float(inp_var["dist1"], 0), to_float(inp_var["dist2"], 0))

        updated_cn_values[crop] = {
            "CN1": cn1,
            "CN2": cn2,
            "Actual_CN2": loc_actual_cn2
        }

    return updated_cn_values
```

### Slope-Adjusted Curve Numbers

Implementation of slope correction using Williams formula:

```python
# curve_numbers.py - Function 014: Adjusts curve number based on slope using Williams formula
def calc_cn2_adjusted(final_cn2, inp_slope):
    inp_slope = inp_slope/100
    cn2_adjusted = final_cn2 * ((1.9274 * inp_slope + 2.1327) / (inp_slope + 2.1791))
    return np.minimum(cn2_adjusted, 100)

# curve_numbers.py - Function 015: Calculates CN1 (dry conditions) from CN2 using standard formula
def calc_cn1(final_cn2):
    cn1 = final_cn2 / (2.281 - 0.01281 * final_cn2)
    return cn1

# curve_numbers.py - Function 016: Calculates CN3 (wet conditions) from CN2 using standard formula
def calc_cn3(final_cn2):
    cn3 = final_cn2 / (0.427 + 0.00573 * final_cn2)
    return cn3
```

### Surface Water Supply and Abstraction

Canal water supply management and surface water allocation:

```python
# water_supply.py - Function 001: Calculates canal water supply availability
def calc_canal_supply(df_ir, df_mm):
    def get_canal_supply(row):
        month_index = row.name % 12
        value = df_ir.loc[month_index, "Canal_WA"]
        return 0 if np.isnan(value) else value

    df_mm["Canal_supply"] = df_mm.apply(get_canal_supply, axis=1)
    return df_mm

# water_abstraction.py - Function 001: Calculates abstracted surface water
def calc_sw_abstracted(df_mm):
    conditions = [
        df_mm["Qom(m^3)"] - df_mm["SW_need"] < 0,
        df_mm["Qom(m^3)"] - df_mm["SW_need"] >= df_mm["SW_need"]
    ]

    choices = [df_mm["Qom(m^3)"], df_mm["SW_need"]]

    df_mm["SW_abstracted"] = np.select(conditions, choices, default=df_mm["Qom(m^3)"] - df_mm["SW_need"])
    return df_mm

# water_demand.py - Function 001: Calculates surface water needs
def calc_sw_need(df_mm):
    df_mm["SW_need"] = df_mm["Domestic_need"] + df_mm["Other_need"] - df_mm["GW_need"]
    return df_mm
```

### Surface Water Evaporation

Potential evapotranspiration calculation from water bodies:

```python
# evaporation.py - Function 001: Calculates potential evapotranspiration from surface water
def calc_potential_et(total_surface_area_farm, df_mm):
    df_mm["Potential_ET"] = total_surface_area_farm * (df_mm["ETom"] / 1000)
    return df_mm
```

### Final Water Balance Components

Integration of runoff, storage, and abstraction processes:

```python
# runoff_disposal.py - Function 001: Calculates final runoff after storage
def calc_final_ro(df_mm):
    df_mm["final_ro"] = (df_mm["Qom"] - df_mm["Captured Runoff in m³_mm"]).clip(lower=0)
    return df_mm

# water_balance.py - Function 001: Calculates remaining water after domestic surface water use
def calc_value_after_subtracting_domestic_sw_use(df_mm):
    df_mm["value_after_subtracting_domestic_SW_use"] = df_mm["Qom(m^3)"] - df_mm["SW_abstracted"]
    return df_mm

# water_balance.py - Function 002: Calculates final runoff including rejected recharge
def calc_final_runoff(df_mm):
    df_mm["Final_Runoff"] = df_mm["final_ro"] + df_mm["Rejected_recharge_mm"]
    return df_mm
```

### Surface Area Calculations

Water storage structure geometry calculations:

```python
# surface_calculations.py - Function 001: Calculates surface area from volume and depth
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
```

### Precipitation Processing

Net rainfall calculation accounting for groundwater recharge:

```python
# precipitation_processing.py - Function 001: Calculates net rainfall after removing groundwater recharge
def get_rain_src_model(pi, recharge_src):
    rain = pi - recharge_src
    return rain
```

## Technical Methodology

### SCS Curve Number Framework

The surface water bucket implements the comprehensive SCS curve number methodology:

**Runoff Equation:**
```
Q = (P - Ia)² / (P - Ia + S)
```

**Where:**
- Q = Direct runoff (mm)
- P = Precipitation (mm)
- Ia = Initial abstraction (mm) = 0.2S
- S = Potential maximum retention (mm) = (25400/CN) - 254
- CN = Curve number (30-100)

**Curve Number Selection:**
- Depends on land use, soil type, hydrologic condition, and antecedent moisture
- Adjusted for slope using Williams formula
- Reduced for conservation practices

### Land Use Classification System

The module supports comprehensive land use mapping:

**Crop Categories:**
- Row crops (corn, cotton, vegetables)
- Small grains (wheat, barley, oats)
- Close-growing legumes (alfalfa, clover)
- Pasture and grassland

**Non-Agricultural Land:**
- Built-up areas with impervious surfaces
- Water bodies and wetlands
- Forest and woodland
- Fallow and bare soil

### Conservation Practice Framework

Systematic curve number reductions for drought-proofing interventions:

**Soil Moisture Conservation:**
- Cover crops - CN reduction based on coverage
- Mulching - Surface protection and infiltration enhancement
- Contour bunds - Slope length reduction
- Conservation tillage - Residue management benefits

**Water Harvesting Structures:**
- Farm ponds and check dams
- Broadbed and furrow systems
- Infiltration tanks and percolation ponds

## Key Parameters

### Curve Number Database
- **Crop-Soil Combinations** - CN values for various crop types and soil conditions
- **Hydrologic Soil Groups** - A, B, C, D classification based on infiltration rates
- **Treatment Conditions** - Poor, fair, good hydrologic conditions
- **Conservation Practice Reductions** - CN reductions for specific interventions

### Moisture Conditions
- **AMC I (Dry)** - 5-day antecedent rainfall < 36mm (growing season) or < 13mm (dormant season)
- **AMC II (Normal)** - Moderate antecedent rainfall conditions
- **AMC III (Wet)** - 5-day antecedent rainfall > 53mm (growing season) or > 28mm (dormant season)

### Surface Water Components
- **Canal Water Availability** - Monthly surface water supply from external sources
- **Storage Capacity** - Farm ponds, tanks, and water harvesting structure volumes
- **Evaporation Rates** - Reference ET-based evaporation from water surfaces
- **Domestic Water Demands** - Population-based surface water requirements

## Integration with Other Modules

### Input Dependencies
- **Orchestrator Module** - Receives input parameters for curve numbers and land use data
- **Shared Module** - Uses utilities for mathematical operations and land use calculations

### Output Provision
- **Soil Storage Bucket** - Provides effective rainfall (Pei) for soil moisture calculations
- **Aquifer Storage Bucket** - Supplies net rainfall and recharge components for groundwater analysis
- **Outputs Module** - Delivers runoff data for water balance assessment

### Data Flow Processing
1. **Precipitation Input** → Daily rainfall data with recharge separation
2. **Curve Number Assignment** → Land use and soil-based CN determination
3. **Antecedent Moisture** → 5-day rainfall totals for moisture condition assessment
4. **Conservation Adjustments** → CN reductions for implemented interventions
5. **Runoff Calculation** → SCS method implementation with slope corrections
6. **Surface Water Balance** → Storage, abstraction, and evaporation accounting
7. **Final Allocation** → Water distribution among domestic, irrigation, and environmental uses

## Usage in Drought Scenarios

The surface water bucket enables comprehensive surface water assessment through:

1. **Runoff Quantification** - Measures surface water generation under different rainfall patterns
2. **Conservation Practice Evaluation** - Quantifies runoff reduction benefits of soil and water conservation
3. **Water Harvesting Assessment** - Evaluates potential for surface water capture and storage
4. **Supply-Demand Analysis** - Balances surface water availability with multiple use requirements
5. **Drought Impact Modeling** - Assesses surface water availability under drought conditions

The module's robust curve number system and conservation practice integration support detailed evaluation of surface water management interventions for drought resilience planning.

---

*For detailed SCS curve number methodology and conservation practice effects, refer to the [Tool Technical Manual](../Tool_Technical Manual.pdf), Section 3.1.*