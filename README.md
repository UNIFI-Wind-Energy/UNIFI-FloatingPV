# Simple Floating PV power output estimator from UNIFI

## Overview
This script post-processes an NSRDB (NREL) CSV time series to estimate plane-of-array (POA) irradiance, PV cell temperature, temperature-derated efficiency, and resulting PV power output (or specific power output).

<img width="3127" height="3307" alt="FPV model" src="https://github.com/user-attachments/assets/f2fe69f4-0652-4d4b-bc59-75e442d9e2cb" />


Main steps:
1. Read hourly irradiance and meteo data (GHI, DNI, DHI, air temperature, wind speed) from an NSRDB CSV export.
2. Compute solar position (apparent zenith and azimuth) for the selected latitude, longitude, and time zone.
3. Transpose irradiance from horizontal to the plane of array using `pvlib.irradiance.get_total_irradiance`.
4. Estimate PV cell temperature using the PVsyst temperature model (`pvlib.temperature.pvsyst_cell`) with user-defined coefficients.
5. Apply a linear temperature derate to module efficiency relative to STC.
6. Compute:
   - Example plant power time series (kW) given an installed capacity
   - Specific power time series (kW/m²)
   - Optional multiplicative loss factors (wave-induced losses and humidity losses)

The script also generates diagnostic plots (irradiance components, solar angles, POA components, temperatures, efficiency, power).

---

## Citation
If this script is used in scientific work, please cite:

F. Superchi, R. Travaglini and A. Bianchini, *Renewable Energy*, vol. 260, p. 125194, 2026.  
"Critical issues for the deployment of floating offshore hybrid energy systems comprising wind and solar: a case study analysis for the Mediterranean Sea"  
DOI: `10.1016/j.renene.2026.125194`  
URL: https://doi.org/10.1016/j.renene.2026.125194

---

## Credits and acknowledgements

### Software
This script relies on the open-source Python library pvlib for solar position, irradiance transposition, and PV temperature modeling (e.g., `pvlib.location.Location`, `pvlib.irradiance.get_total_irradiance`, and `pvlib.temperature.pvsyst_cell`). Please cite pvlib appropriately and follow the pvlib license terms.
[pvlib repository](https://github.com/pvlib)

### Data sources
Solar irradiance and meteorological inputs are intended to be sourced from the National Solar Radiation Database (NSRDB) by NREL, as indicated in the script.

### Modeling assumptions and parameter sources
Key modeling assumptions and parameter values in this script (including, but not limited to, wave-induced losses (WIL), humidity losses (HL), PVsyst heat transfer coefficients (`u_c`, `u_v`), and efficiency temperature derating parameters) are taken from, or calibrated based on, the scientific literature explicitly referenced in the code comments and DOI links. For transparency and reproducibility, users should consult and cite those references when reusing the corresponding assumptions or parameter values.

  - FPV technical assumptions from https://doi.org/10.1016/j.apenergy.2020.116084
  - Temperature effect on efficiency from https://doi.org/10.1016/j.heliyon.2022.e11896
  - Humidity loss coefficient from http://doi.org/10.5455/jjee.204-1667584023
  - Wave induced loss coefficient from https://doi.org/10.1016/j.solener.2025.113439
---

## Requirements

### Python dependencies
- `pvlib`
- `pandas`
- `numpy`
- `matplotlib`

Install:
```bash
pip install pvlib 
```

---

## Input data

### NSRDB CSV
Download an hourly time series from the NSRDB data viewer:
https://nsrdb.nrel.gov/data-viewer

Suggested: TMY with all attributes (DHI, DNI, GHI, wind speed at 2 m, temperature, etc.).

The CSV is expected to contain (at minimum) these columns because they are referenced directly:
- `Year`, `Month`, `Day`, `Hour`
- `GHI`, `DNI`, `DHI` (W/m²)
- `Temperature` (air temperature)
- `Wind Speed` (m/s)

If the CSV uses different header names, update the column names in the script accordingly.

---

## User parameters to edit in the script

### Geometry and site
- `tilt` [deg]
- `surface_azimuth` [deg] (example: 180 for south-facing in the northern hemisphere)
- `tz` (example: `"CET"`)
- `lat`, `lon`

### Input file and time range placeholders
- CSV path:
  - `df_NREL = pd.read_csv('xxx.csv', skiprows=2)`
- Start and end dates used to build a date index:
  - `date = pd.date_range(start='xx-xx-xxxx', end='xx-xx-xxxx', freq='1h')`

### Thermal and efficiency model parameters
- PVsyst temperature coefficients:
  - `u_c`, `u_v`
- STC and temperature coefficient:
  - `T_stc`, `gamma`, `eta_stc`

### Loss factors
- `WIL` (wave-induced losses)
- `HL` (humidity losses)

---

## How to run
1. Place the NSRDB CSV in the working directory (or update the path).
2. Replace placeholders (`xx.xxxx`, `xxx.csv`, `xx-xx-xxxx`) with real values.
3. Run:
```bash
python your_script_name.py
```

---

## Outputs
The script writes two CSV files (semicolon separated):

1. `POA_irradiance_NREL.csv`  
   Key columns include:
   - `poa_global`, `poa_direct`, `poa_diffuse`
   - `temp_air`, `wind_speed`
   - `T cell` (cell temperature)
   - `eta` (temperature-adjusted efficiency)
   - `power` (example plant power in kW, based on `P_installed` and module assumptions)

2. `df_PV_p_spec_WIL_HL.csv`  
   Key columns include:
   - `P_spec` (kW/m²)
   - `P_WIL` (after wave-induced losses)
   - `P_WIL_HL` (after wave-induced + humidity losses)

Plots are displayed during execution. The script does not save figures by default.

---

## Notes and known limitations
- The script assumes specific column names from the NSRDB CSV.
- Efficiency is modeled with a simple linear derate:
  - `eta = eta_stc * (1 - gamma*(T - T_stc))`
  This is a simplified approach and may not capture full module behavior across irradiance and temperature.





---


