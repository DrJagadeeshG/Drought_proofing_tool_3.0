# storage_capacity.py

Maximum storage capacity calculations based on aquifer properties.

## Source Code

```python
--8<-- "aquifer_storage_bucket/processing/storage_capacity.py"
```

## Overview

This module calculates the maximum storage capacity of the aquifer based on physical parameters:

- Aquifer depth
- Specific yield
- Total watershed area
- Unit conversions

## Key Functions

- `calculate_storage_limit()` - Main function for storage capacity calculation

## Formula

Storage Limit = Aquifer Depth × (Specific Yield / 100) × Total Area × 10000

Where:
- Aquifer Depth: Depth of the water-bearing formation (m)
- Specific Yield: Fraction of water that drains from saturated rock (%)
- Total Area: Watershed area contributing to storage (ha)
- 10000: Unit conversion factor

---

*Part of the Aquifer Storage Bucket module in the Drought Proofing Tool*