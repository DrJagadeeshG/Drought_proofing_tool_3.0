# Soil Storage Bucket

The Soil Storage Bucket module manages soil moisture dynamics, crop water requirements, and actual evapotranspiration in the three-bucket water balance system, implementing the core crop water stress calculations for drought proofing analysis.

## Overview

This module handles:

- **Soil properties** including available water content and weighted capacity calculations
- **Crop coefficient calculations** through all growth stages (initial, development, mid-season, late)
- **Evapotranspiration processes** including crop ET, soil evaporation, and reference ET calculations
- **Water stress modeling** with crop and soil stress coefficients under water deficit conditions
- **Root depth dynamics** throughout crop growing seasons
- **Conservation practice effects** on soil moisture retention and evaporation reduction
- **Irrigation water demand** calculations based on crop water deficits

## Soil Storage Bucket Flow

The soil storage bucket implements comprehensive soil moisture and crop water dynamics:

```mermaid
graph TD
    %% Inputs
    A[Precipitation] --> B[Effective Rainfall<br/>Pei = P - Runoff]
    C[Reference ET₀<br/>Hargreaves Method] --> D[Crop Coefficients]

    %% Crop Development
    D --> D1[Growth Stages<br/>Initial, Dev, Mid, Late]
    D1 --> D2[Crop ET<br/>ETc = ET₀ × Kc]

    %% Soil Water Dynamics
    B --> E[Soil Moisture Deficit<br/>SMD = SMD₋₁ + AE - P]
    D2 --> E

    %% Water Capacity Calculations
    F[Soil Properties<br/>AWC, Field Capacity] --> G[Water Capacities]
    G --> G1[TAW = AWC × Root Depth]
    G --> G2[RAW = TAW × Depletion Factor]
    G --> G3[TEW = θfc - 0.5×θwp × Ze]
    G --> G4[REW = 0.4 × TEW]

    %% Water Stress Assessment
    E --> H[Water Stress Conditions]
    G1 --> H
    G2 --> H
    G3 --> H
    G4 --> H

    H --> H1[Crop Stress<br/>Ks_crop = f(SMD,RAW,TAW)]
    H --> H2[Soil Evap Stress<br/>Ks_soil = f(SMD,REW,TEW)]

    %% Actual Evapotranspiration
    D2 --> I[Actual Crop ET<br/>AEc = ETc × Ks_crop]
    ET0[Soil Evaporation<br/>Es = ET₀ × Ke] --> I2[Actual Soil Evap<br/>AEs = Es × Ks_soil]

    %% Conservation Practices
    CP[Conservation Practices] --> CP1[Evaporation Reduction<br/>Mulching, Cover Crops]
    CP1 --> I2

    %% Root Depth Dynamics
    RD[Root Depth Growth<br/>Min to Max Depth] --> G1

    %% Irrigation Requirements
    I --> J[Irrigation Water Requirement<br/>IWR = ETc - AEc]
    J --> K[Monthly IWR Aggregation]

    %% Final Outputs
    I --> L[Soil Water Balance]
    I2 --> L
    K --> L
    L --> M[Soil Moisture Status<br/>For Next Time Step]

    %% Styling
    style A fill:#e3f2fd
    style E fill:#f3e5f5
    style H fill:#fff3e0
    style L fill:#ffebee
    style CP fill:#f1f8e9
```

## Module Structure

### Input Data Processing

**Soil characteristics and water capacity management:**

- **`input_data/soil_properties.py`** - Calculates soil properties including AWC, soil types, and weighted capacity for mixed soil layers

### Outflux Calculations

**Water losses from the soil storage bucket:**

- **`outflux/evapotranspiration.py`** - Comprehensive ET calculations including reference ET, crop ET, soil evaporation, and actual ET under water stress
- **`outflux/irrigation_demand.py`** - Calculates irrigation water requirements and aggregates to monthly demands

### Processing Engine

**Core soil moisture and crop water dynamics:**

- **`processing/conservation_practices.py`** - Effects of conservation practices on soil moisture, field capacity, and evaporation reduction
- **`processing/crop_coefficients.py`** - Crop coefficient calculations for all growth stages with plot aggregation
- **`processing/root_depth.py`** - Dynamic root depth calculations based on growth stages and crop parameters
- **`processing/soil_moisture_deficit.py`** - Soil moisture deficit calculations using water balance approach
- **`processing/water_capacity.py`** - Total and readily available water calculations for crops and evaporation
- **`processing/water_demand.py`** - Irrigation water demand calculations and monthly aggregation
- **`processing/water_storage.py`** - Orchestrates soil water storage calculations and evaporation parameters
- **`processing/water_stress.py`** - Water stress coefficients and depletion factors for crops and soil

## Technical Implementation

### Soil Properties and Available Water Content

The module implements comprehensive soil property calculations with support for mixed soil layers:

```python
# soil_properties.py - Function 001: Calculates soil properties including AWC and depths
def soil_calculation(inp_source, master_path):
    inp_vars = collect_inp_variables(inp_source, master_path)

    soil_type1 = get_soil_type(inp_vars["Soil_type1"])
    soil_type2 = get_soil_type(inp_vars["Soil_type2"])
    hsc1 = get_soil_type(inp_vars["HSC1"])
    hsc2 = get_soil_type(inp_vars["HSC2"])
    awc_1 = calculate_awc(soil_type1)
    awc_2 = calculate_awc(soil_type2) if soil_type2 else None

    loc_soil_list = [awc_1, awc_2, hsc1, hsc2, soil_type1, soil_type2, dist1, dist2, soil_type1_dep, soil_type2_dep]
    return loc_soil_list

# soil_properties.py - Function 002: Returns available water content based on soil type classification
def calculate_awc(soil_type):
    awc_values = {
        "Sand": 90,
        "Sandy Loam": 125,
        "Loam": 175,
        "Clayey Loam": 200,
        "Clay": 215
    }
    awc = awc_values.get(soil_type)
    if awc is None:
        raise ValueError("Unknown soil type")
    return awc
```

### Weighted Average Water Content for Mixed Soil Layers

Advanced soil layer management supporting heterogeneous soil profiles:

```python
# soil_properties.py - Function 004: Calculates weighted average water content capacity for mixed soil layers
def calculate_awc_capacity(dist1, dist2, soil_type1_dep, soil_type2_dep, local_awc_1=None, local_awc_2=None):
    dist1 = to_float(dist1, 0)
    dist2 = to_float(dist2, 0)
    soil_type1_dep = to_float(soil_type1_dep, 0)
    soil_type2_dep = to_float(soil_type2_dep, 0)

    # Handle single soil type scenarios
    if local_awc_2 is None:
        dist2 = 0
        soil_type2_dep = 0
        local_awc_2 = 0

    depth = ((dist1 * soil_type1_dep) + (dist2 * soil_type2_dep)) / 100
    awc = ((local_awc_1 * dist1) + (local_awc_2 * dist2)) / 100
    awc_capacity = depth * awc
    return depth, awc, awc_capacity
```

### Reference Evapotranspiration Calculations

Implementation of Hargreaves method for reference ET calculation:

```python
# evapotranspiration.py - Function 001: Calculates monthly reference evapotranspiration using Hargreaves method
def calc_etom(df_mm, file_paths, inp_source, master_path):
    print("FUNCTION 27: calc_etom() - Calculating reference evapotranspiration")

    radiation_db = file_paths["radiation_db"]
    df_rd = get_radiation_db(radiation_db, collect_inp_variables(inp_source, master_path)["latitude"])

    # Initialize the ETom column with zeros
    df_mm["ETom"] = 0.0

    # Vectorized ETom calculation - much faster than iterrows
    df_mm["month_index"] = df_mm.index % 12
    df_mm["radiation"] = df_mm["month_index"].map(df_rd["Radiation"])
    df_mm["ETom"] = (0.0023 * df_mm["radiation"] * np.sqrt(df_mm["Tmax"] - df_mm["Tmin"]) *
                     (df_mm["Tmean"] + 17.8) * df_mm["Days"])
    df_mm.drop(["month_index", "radiation"], axis=1, inplace=True)
    return df_mm
```

### Crop Coefficient Calculations Through Growth Stages

Comprehensive crop coefficient system implementing FAO-56 methodology:

```python
# crop_coefficients.py - Function 001: Calculates initial crop coefficient (Kc) for initial growth stage
def calculate_kc_ini(df, crop_df, sowing_week, sowing_month, stage_column, kc_column, selected_crop):
    sowing_month_num = pd.to_datetime(f"{sowing_month} 1, 2000").month

    def local_find_start_date(year):
        local_start_date = pd.to_datetime(f"{year}-{sowing_month_num}-01")
        local_start_date += pd.Timedelta(days=(int(sowing_week) - 1) * 7)
        return local_start_date

    df["start_date"] = df["Date"].dt.year.apply(local_find_start_date)

    crop_row = crop_df[crop_df["Crops"] == selected_crop]
    if crop_row.empty:
        raise ValueError(f"Selected crop {selected_crop} not found in crop_df")

    l_days_str = crop_row[stage_column].values[0]
    kc_value = float(crop_row[kc_column].values[0])

    # Round up if decimal part exceeds 0.5
    try:
        l_ini_days_float = float(l_days_str)
        if (l_ini_days_float % 1) > 0.5:
            l_ini_days = math.ceil(l_ini_days_float)
        else:
            l_ini_days = int(l_ini_days_float)
    except ValueError:
        raise ValueError(f"Invalid {stage_column} value: {l_days_str}")

    kc_col_name = f"{kc_column}_{selected_crop}"
    df[kc_col_name] = np.float32(0)

    # Vectorized approach - much faster than iterrows
    for start_date in df["start_date"].unique():
        end_date = start_date + pd.Timedelta(days=l_ini_days)
        mask = (df["Date"] >= start_date) & (df["Date"] < end_date)
        df.loc[mask, kc_col_name] = np.float32(kc_value)
    return df, l_ini_days
```

### Crop Evapotranspiration with Rice Preparation

Specialized handling for rice crop evapotranspiration including preparation phase:

```python
# evapotranspiration.py - Function 005: Calculates crop evapotranspiration with special rice preparation handling
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
```

### Conservation Practice Effects

Implementation of conservation practice impacts on soil moisture and evaporation:

```python
# conservation_practices.py - Function 002: Calculates soil water content with conservation practice adjustments
def calculate_awc_soil(df, cover_crops_practice, mulching_practice, bbf_practice, bund_practice, tillage_practice, awc_capacity):
    practices = {
        "Cover_Crops_SM_with_practice": cover_crops_practice,
        "Mulching_SM_with_practice": mulching_practice,
        "BBF_SM_with_practice": bbf_practice,
        "Bund_SM_with_practice": bund_practice,
        "Tillage_SM_with_practice": tillage_practice
    }

    area_columns = {
        "Cover_Crops_SM_with_practice": "Cover_Area",
        "Mulching_SM_with_practice": "Mulching_Area",
        "BBF_SM_with_practice": "BBF_Area",
        "Bund_SM_with_practice": "Bunds_Area",
        "Tillage_SM_with_practice": "Tillage_Area"
    }

    df, overall_sum = calculate_soil_moisture_sums(df)

    if overall_sum == 0:
        awc_soil_con = 0
    else:
        x = 0  # Initialize x
        for practice_column, practice_percentage in practices.items():
            area_column = area_columns.get(practice_column)
            if area_column in df.columns:
                x += df[area_column].sum() * (practice_percentage / 100)
        awc_soil = (x * awc_capacity) / overall_sum
        awc_soil_con = awc_soil
    return awc_soil_con
```

### Dynamic Root Depth Calculations

Growth stage-based root depth development throughout the growing season:

```python
# root_depth.py - Function 001: Calculates crop root depth based on growth stage and crop parameters
def root_dep(row, min_root_depth, max_root_depth, total_growth_days, selected_crop):
    try:
        if row[f"RG_days_{selected_crop}"] == 0:
            crop_rd = 0
        else:
            crop_rd = min_root_depth + (max_root_depth - min_root_depth) * \
                      (total_growth_days - row[f"RG_days_{selected_crop}"]) / total_growth_days
        return crop_rd
    except ValueError:
        return None

# root_depth.py - Function 003: Calculates final aggregated root depth by plot for all crops
def calc_final_crop_rd(df_crop, crop_df, all_crops, valid_crops_df):
    print("FUNCTION 21: calc_final_crop_rd() - Calculating final crop root depth")

    # Step 1: Calculate root depth for each crop
    for selected_crop in all_crops:
        calculate_crop_rd(df_crop, crop_df, selected_crop)

    # Step 2: Initialize columns for each plot
    plot_numbers = valid_crops_df["Plot"].unique()
    for plot in plot_numbers:
        df_crop[f"crop_rd_{plot}"] = 0

    # Step 3: Sum root depth for each plot
    for plot in plot_numbers:
        # Get the list of crops for this plot
        crops_in_plot = valid_crops_df[valid_crops_df["Plot"] == plot]["Crop"].tolist()

        # Calculate sum of root depth for crops in this plot
        if crops_in_plot:
            df_crop[f"crop_rd_{plot}"] = df_crop.apply(
                lambda row: sum(row[f"{crop}_crop_rd"] for crop in crops_in_plot if f"{crop}_crop_rd" in row.index),
                axis=1
            )
    return df_crop
```

### Water Stress Modeling

Implementation of water stress coefficients for crop and soil evaporation:

```python
# water_stress.py - Function 003: Determines soil evaporation stress condition based on water deficits
def calc_ks_soil_cond(kei, smdi, rewi, tewi):
    if kei == 0:
        return 0
    elif smdi < rewi:
        return 1
    elif rewi < smdi < tewi:
        return 2
    else:
        return 3

# water_stress.py - Function 004: Calculates soil evaporation stress coefficient based on moisture conditions
def calc_ks_soil(ks_soil_cond, tewi, smdi, rewi):
    if ks_soil_cond == 1:
        return 1
    elif ks_soil_cond == 2:
        return (tewi - smdi) / (tewi - rewi)
    else:
        return 0

# water_stress.py - Function 005: Determines crop transpiration stress condition based on water availability
def calc_ks_crop_cond(kci, smdi, rawi, tawi):
    if kci == 0:
        return 0
    elif smdi < rawi:
        return 1
    elif rawi < smdi < tawi:
        return 2
    else:
        return 3
```

### Soil Moisture Deficit Calculations

Water balance approach for soil moisture deficit tracking:

```python
# soil_moisture_deficit.py - Function 001: Calculates soil moisture deficit index for each plot
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

            # Calculate stress conditions and coefficients
            df_crop.loc[i, f"Ks_soil_cond_{plot}"] = calc_ks_soil_cond(df_crop.loc[i, f"Kei_{plot}"],
                                                                       df_crop.loc[i, f"SMDi_shifted_{plot}"],
                                                                       df_crop.loc[i, f"REWi_{plot}"],
                                                                       df_crop.loc[i, f"TEWi_{plot}"])

            df_crop.loc[i, f"Ks_soil_{plot}"] = calc_ks_soil(df_crop.loc[i, f"Ks_soil_cond_{plot}"],
                                                             df_crop.loc[i, f"TEWi_{plot}"],
                                                             df_crop.loc[i, f"SMDi_shifted_{plot}"],
                                                             df_crop.loc[i, f"REWi_{plot}"])

            # Calculate actual evapotranspiration
            df_crop.loc[i, f"AE_soil_{plot}"] = calc_ae_soil(df_dd.loc[i, f"ESi_{plot}"],
                                                             df_dd.loc[i, "Pei"],
                                                             df_crop.loc[i, f"Ks_soil_cond_{plot}"],
                                                             df_crop.loc[i, f"Ks_soil_{plot}"],
                                                             df_crop.loc[i, f"Final_Evap_Red_{plot}"])

            # Calculate soil moisture deficit
            smdi_value = calc_smd(df_crop.loc[i, f"SMDi_shifted_{plot}"],
                                  df_crop.loc[i, f"AE_soil_{plot}"],
                                  df_crop.loc[i, f"AE_crop_{plot}"],
                                  df_dd.loc[i, "Pei"])

            df_crop.loc[i, f"SMDi_{plot}"] = np.float32(smdi_value)

    return df_crop

# soil_moisture_deficit.py - Function 002: Calculates soil moisture deficit using water balance approach
def calc_smd(smdi, ae_soil, ae_crop, pei):
    if smdi + ae_soil + ae_crop - pei < 0:
        return 0
    else:
        return smdi + ae_soil + ae_crop - pei
```

### Water Capacity Calculations

Total and readily available water calculations for crop water management:

```python
# water_capacity.py - Function 001: Calculates total available water (TAW) for each plot based on root depth
def calc_taw(df_crop, capacity, all_plots):
    for plot in all_plots:
        df_crop[f"TAWi_{plot}"] = capacity * df_crop[f"crop_rd_{plot}"]
    return df_crop

# water_capacity.py - Function 002: Calculates readily available water (RAW) based on depletion factors
def calc_raw(df_crop, all_plots):
    for plot in all_plots:
        df_crop[f"RAWi_{plot}"] = df_crop[f"final_depletion_{plot}"] * df_crop[f"TAWi_{plot}"]
    return df_crop

# water_capacity.py - Function 003: Calculates total evaporable water (TEW) from soil surface layer
def calc_tew(df_crop, theta_fc, theta_wp, all_plots):
    for plot in all_plots:
        df_crop[f"TEWi_{plot}"] = (theta_fc - 0.5 * theta_wp) * df_crop["Ze"]
    return df_crop

# water_capacity.py - Function 004: Calculates readily evaporable water (REW) from soil surface
def calc_rew(df_crop, all_plots):
    for plot in all_plots:
        df_crop[f"REWi_{plot}"] = 0.4 * df_crop[f"TEWi_{plot}"]
    return df_crop
```

### Irrigation Water Demand

Calculation of irrigation requirements based on crop water deficits:

```python
# irrigation_demand.py - Function 001: Calculates irrigation water requirements as difference between ET and actual ET
def calculate_iwr(df_dd, df_crop, crops):
    print("FUNCTION 39: calculate_iwr() - Calculating irrigation water requirements")
    for crop in crops:
        df_crop[f"IWR_{crop}"] = (df_dd[f"ETci_{crop}"] - df_crop[f"AE_crop_{crop}"]).clip(lower=0)
    return df_crop

# irrigation_demand.py - Function 002: Aggregates daily irrigation water requirements to monthly values
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
```

## Technical Methodology

### FAO-56 Crop Coefficient Approach

The soil storage bucket implements the FAO-56 dual crop coefficient approach:

- **Basal Crop Coefficient (Kcb)** - Transpiration component
- **Soil Evaporation Coefficient (Ke)** - Evaporation from soil surface
- **Total Crop Coefficient (Kc)** = Kcb + Ke

Growth stages are modeled with distinct coefficients:
- **Initial Stage** - Kc_ini for crop establishment
- **Development Stage** - Kc_dev for vegetative growth
- **Mid-Season Stage** - Kc_mid for peak water demand
- **Late Season Stage** - Kc_end for maturity

### Water Stress Framework

The module implements comprehensive water stress modeling:

**Soil Evaporation Stress:**
- Readily Evaporable Water (REW) threshold
- Total Evaporable Water (TEW) capacity
- Stress coefficient Ks_soil = (TEW - SMD) / (TEW - REW)

**Crop Transpiration Stress:**
- Readily Available Water (RAW) threshold based on depletion factors
- Total Available Water (TAW) based on root depth
- Stress coefficient Ks_crop = (TAW - SMD) / (TAW - RAW)

### Conservation Practice Integration

The soil storage bucket quantifies conservation practice benefits:

**Soil Moisture Conservation:**
- Cover crops soil moisture improvement
- Mulching water retention benefits
- Broad bed and furrow (BBF) effects
- Contour bunds and conservation tillage

**Evaporation Reduction:**
- Practice-specific evaporation reduction factors
- Area-weighted reduction calculations
- Final evaporation reduction by plot

## Key Parameters

### Soil Properties
- **Soil Types** - Sand, Sandy Loam, Loam, Clayey Loam, Clay with specific AWC values
- **Available Water Content** - 90-215 mm/m based on soil texture
- **Field Capacity and Wilting Point** - Soil water content thresholds
- **Effective Depth** - Root zone depth for water storage calculations

### Crop Parameters
- **Growth Stage Duration** - Initial, development, mid-season, late season days
- **Crop Coefficients** - Stage-specific Kc values from crop database
- **Root Depth** - Minimum and maximum root depths with growth dynamics
- **Depletion Factors** - Crop-specific water stress thresholds (p-values)

### Conservation Practices
- **Area Coverage** - Hectares under each conservation practice
- **Soil Moisture Benefits** - Percentage improvement in soil water retention
- **Evaporation Reduction** - Percentage reduction in soil surface evaporation

## Integration with Other Modules

### Input Dependencies
- **Orchestrator Module** - Receives input parameters and coordinates soil calculations
- **Shared Module** - Uses utilities for data processing, crop management, and mathematical operations

### Output Provision
- **Surface Water Bucket** - Provides actual evapotranspiration for runoff calculations
- **Aquifer Storage Bucket** - Supplies soil moisture data for recharge calculations
- **Outputs Module** - Delivers crop evapotranspiration and irrigation requirements for yield analysis

### Data Flow Processing
1. **Soil Properties** → AWC calculations and capacity determination
2. **Crop Coefficients** → Growth stage-based Kc calculation through all phases
3. **Reference ET** → Hargreaves method for climate-based ET₀
4. **Crop ET** → ETc = ET₀ × Kc for potential crop water requirements
5. **Water Stress** → Ks calculation based on soil moisture deficit
6. **Actual ET** → ETa = ETc × Ks for water-limited conditions
7. **Irrigation Demand** → IWR = ETc - ETa for supplemental water needs

## Usage in Drought Scenarios

The soil storage bucket enables detailed drought impact assessment through:

1. **Crop Water Stress Quantification** - Measures actual vs potential evapotranspiration
2. **Irrigation Demand Assessment** - Calculates supplemental water requirements
3. **Conservation Practice Evaluation** - Quantifies soil moisture conservation benefits
4. **Root Zone Management** - Models dynamic water storage based on crop development
5. **Multi-Crop Analysis** - Handles complex cropping systems with multiple seasons

The module's plot-based calculations enable field-level drought analysis while the conservation practice integration supports evaluation of drought-proofing interventions at the farm scale.

---

*For detailed crop coefficient methodology and water stress equations, refer to the [Tool Technical Manual](../Tool_Technical Manual.pdf), Sections 3.2-3.6.*