
# RNPU Measurements Project

## Overview
This is the code responsible to measure and characterize hysteron behaviour.
The main setup for this code is a NIDAQ 9147 chassis and a Keithley 2401 source measurement unit.
The code was created to try and syncronize the current sweep of the SMU with the NIDAQs. 

## Project Structure
```
├── control_voltages/   # Storing important static control voltages to get the RNPU to have 
└── configs/            # Storing Experiment setup yaml-configs.
```

## Getting Started
1. Clone or download this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure measurement parameters in `config/`
4. Run experiments: `python src/main.py`

## Results
Results are stored in the root folder with timestamp and the current experiment name, based on the setup config.

## Contributing
Document any new experiments or modifications to the measurement protocol.

