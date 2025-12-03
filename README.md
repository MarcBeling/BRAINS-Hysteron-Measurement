
# RNPU Hysteron Measurements Project

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
3. Create a config file in `config/` similar to the setup config shown below.
4. Implement your experiment code in experiments.py
5. Run the experiment in main.py

## Results
Results are stored in the root folder with timestamp and the current experiment name, based on the setup config.

## Contributing
Document any new experiments or modifications to the measurement protocol.

## Example config: Setup.yaml

```yaml
name: "Experiment Name"
description: "Description of the experiment"

min_value: -150e-9
max_value: 150e-9
data_density: 30
voltage_range: [-3, 3]
current_range: [-0.01, 0.01]
amplification: 28
ramp_points: 30

nidaq:
  activation_module_id: 'cDAQ1Mod1'
  readout_module_id: 'cDAQ1Mod2'
  sample_frequency: 10000.0
  update_frequency: 1000.0
  samples_per_measurement: 5
  readout_channels: [0, 1, 2, 3, 4, 5, 6, 7] # 0-7
  control_voltages:
    0: 1
    1: 2
    2: 1.5
    3: 2.5
    4: -1
    5: -2
    6: -1.5
    7: -2.5

smu:
  device_id: 'GPIB0::15::INSTR'
  timeout: 50000
  drive_mode: 'CURRENT_DRIVEN'
  tolerance_voltage: 0.01
  tolerance_current: 10e-9
  pause_between_set: 0.02
```

