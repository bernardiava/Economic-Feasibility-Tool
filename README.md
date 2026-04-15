# Interactive CGE Simulation with Subsidy Analysis

## Overview
This repository contains a **Computable General Equilibrium (CGE)** simulation model designed to analyze the economic impacts of production subsidies. It features both a Python backend for batch processing and a fully interactive HTML frontend for real-time policy experimentation.

The model simulates a simplified economy with two sectors (Agriculture and Manufacturing) and two factors of production (Labor and Capital), utilizing Cobb-Douglas production and utility functions to determine equilibrium prices, outputs, and welfare effects.

## ⚠️ Legal Notice & Licensing

**© bernardiava. All Rights Reserved.**

- **Usage Restrictions**: This software is provided for educational and research purposes only. Commercial use, redistribution, or modification without explicit written permission from the copyright holder is strictly prohibited.
- **Citation Requirement**: If you use this code, model, or any generated results in your research, publications, or presentations, you **must** cite this repository properly (see Citation section below).
- **No Warranty**: The software is provided "as is", without warranty of any kind, express or implied.

## Features

### 1. Interactive HTML Dashboard (`cge_interactive.html`)
A standalone, browser-based interface that requires no installation.
- **Real-time Sliders**: Adjust subsidy rates (0-50%), factor endowments, and consumer preferences.
- **Sector Selection**: Toggle subsidies between Agriculture and Manufacturing.
- **Visualizations**: Dynamic charts showing output changes, factor allocation, and price effects.
- **Instant Feedback**: Recalculates general equilibrium instantly upon parameter changes.

### 2. Python Simulation Engine (`cge_subsidy_simulation.py`)
A scriptable backend for detailed analysis and batch runs.
- **Configurable Inputs**: Supports JSON configuration files and command-line arguments.
- **Detailed Output**: Generates CSV reports with baseline vs. policy scenario comparisons.
- **Extensible**: Easy to modify production functions or add more sectors.

## Economic Feasibility & Model Structure

### Theoretical Framework
The model solves for a Walrasian General Equilibrium where:
1.  **Producers** maximize profits given technology and factor prices.
2.  **Consumers** maximize utility given income and goods prices.
3.  **Markets Clear**: Supply equals demand for all goods and factors.

### Key Equations
- **Production**: $Q_i = A_i \cdot L_i^{\alpha} \cdot K_i^{1-\alpha}$
- **Utility**: $U = \prod C_i^{\beta_i}$
- **Subsidy Mechanism**: Effective producer price $P_{prod} = P_{market} \cdot (1 + \text{subsidy\_rate})$

### Feasibility Checks
The simulation includes internal checks to ensure:
- Non-negative prices and quantities.
- Market clearing conditions are met within a defined tolerance.
- Government budget constraints are tracked (subsidy expenditure).

## How to Use

### Option A: Interactive HTML (Recommended for Exploration)
1.  Download `cge_interactive.html` from this repository.
2.  Open the file in any modern web browser (Chrome, Firefox, Edge).
3.  Use the controls on the left panel to adjust parameters:
    -   **Subsidy Rate**: Slide to increase/decrease subsidy.
    -   **Target Sector**: Select which industry receives support.
    -   **Endowments**: Change total Labor and Capital available.
4.  Click **"Run Simulation"** to update charts and tables.

### Option B: Python Script (Recommended for Analysis)
**Prerequisites**: Python 3.x installed. No external libraries required (uses standard library).

#### 1. Run with Default Settings
```bash
python cge_subsidy_simulation.py
```
This generates a `cge_results.csv` file with default parameters.

#### 2. Run with Custom Arguments
```bash
python cge_subsidy_simulation.py --sector Manufacturing --rate 0.25
```
Available arguments:
-   `--sector`: Target sector ("Agriculture" or "Manufacturing")
-   `--rate`: Subsidy rate (e.g., 0.2 for 20%)
-   `--labor`: Total labor endowment
-   `--capital`: Total capital endowment

#### 3. Run with Configuration File
Create a `config.json`:
```json
{
  "subsidy_rate": 0.15,
  "target_sector": "Agriculture",
  "labor_endowment": 100,
  "capital_endowment": 100,
  "preference_agri": 0.5
}
```
Run:
```bash
python cge_subsidy_simulation.py --config config.json
```

## Interpreting Results

-   **Output Change (%)**: Percentage change in sectoral production relative to baseline.
-   **Price Change (%)**: Change in consumer prices due to resource reallocation.
-   **Welfare Change (%)**: Change in aggregate consumer utility (measure of overall economic well-being).
-   **Factor Prices**: Changes in wages (Labor) and rental rates (Capital).
-   **Govt. Expenditure**: Total cost of the subsidy to the government budget.

## Citation

If you use this software or its outputs in your work, please cite it as follows:

**BibTeX:**
```bibtex
@software{cge_subsidy_sim_2024,
  author = {Bernardia Vitri Arumsari},
  title = {Interactive CGE Simulation with Subsidy Analysis},
  year = {2026},
  url = {[https://github.com/bernardiava/Economic-Feasibility-Tool/]},
  note = {All Rights Reserved. Used with permission.}
}
```

**APA Style:**
> Bernardia Vitri Arumsari (2026). *Interactive CGE Simulation with Subsidy Analysis* [Computer software]. Retrieved from https://github.com/bernardiava/Economic-Feasibility-Tool/

## Disclaimer
This model is a simplified representation of an economy intended for educational and illustrative purposes. It should not be used as the sole basis for real-world policy decisions without further validation and calibration by qualified economists.

---
**Copyright © 2024 Bernardia Vitri Arumsari. All Rights Reserved.**
