# recharge_calculations.py

Natural groundwater recharge calculations from soil moisture surplus.

## Source Code

```python
--8<-- "aquifer_storage_bucket/influx/recharge_calculations.py"
```

## Overview

This module calculates groundwater recharge from various sources including:

- Natural recharge from soil moisture surplus
- Fallow area contributions
- Surface infiltration structures
- Multiple crop interactions

## Key Functions

- `calc_gwnr_fallow()` - Calculate natural groundwater recharge for fallow conditions
- `calc_monthly_gwnrm_fallow()` - Aggregate daily values to monthly totals
- `calc_recharge()` - Calculate total recharge considering all crop areas
- `calc_monthly_recharge()` - Monthly aggregation of recharge values

## Dependencies

- numpy, pandas for data processing
- shared.utilities for type conversion
- soil_storage_bucket modules for soil calculations
- orchestrator.input_collector for parameter collection

---

*Part of the Aquifer Storage Bucket module in the Drought Proofing Tool*