from setupmanager import SetupManager
from instruments import SMU, NIDAQ_chassis
import numpy as np
from typing import List, Dict
from abc import ABC, abstractmethod
import atexit
import time

class Experiment(ABC):
    """
    Abstract class to unifying Experiment implementation.
    Requires an implementation of a setup manager, and a run function.
    """
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass

class RNPU_Experiment(Experiment):
    """
    RNPU_Experiment handles the execution of experiments using SMU and NIDAQ equipment.
    This class orchestrates the measurement workflow by:
    1. Initializing hardware interfaces (SMU and NIDAQ)
    2. Sweeping through input currents via SMU
    3. Measuring voltages and currents across all active NIDAQ channels
    4. Recording and writing results to the setup manager
    5. Properly shutting down all equipment
    Attributes:
        setupManager (SetupManager): Manages experiment configuration and data I/O
        smu (SMU): Source Measurement Unit interface for setting currents
        nidaq (NIDAQ_chassis): National Instruments DAQ chassis for voltage/current measurements
    """
    def __init__(self, setupManager: SetupManager) -> None:
        self.setupManager: SetupManager = setupManager
        self.smu: SMU = SMU(setupManager)
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis(setupManager)
        atexit.register(self.shutdown)
        
    def run(self):
        self.nidaq.start_active_all_channels()
        voltages: List[Dict[int, float]] = []
        input_data = self.setupManager.get_input_data()
        for index, input_current in enumerate(input_data):
            self.smu.set_current(input_current)
            drive_voltage = self.smu.measure_voltage()
            if index > 60 and index < len(input_data - 60):
                voltages.append(self.nidaq.measure_voltage_all_channels())
            self.setupManager.log_info(f"Current @ {input_current:.2g}A / {drive_voltage:.2g}V \t|{index+1}/{len(input_data)}")
    
        self.setupManager.write_voltage(voltages)
        self.shutdown()

    def shutdown(self):
        self.nidaq.shutdown()
        self.smu.shutdown()

class NGR_Experiment(Experiment):
    def __init__(self, setupManager: SetupManager) -> None:
        self.setupManager: SetupManager = setupManager
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis(setupManager)
        self.smu: SMU = SMU(setupManager)
        atexit.register(self.shutdown)

    def run(self):
        self.nidaq.start_active_all_channels()
        currents = []
        input_data = self.setupManager.get_input_data()
        for index, input_voltage in enumerate(input_data):
            self.smu.set_voltage(input_voltage)
            drive_current = self.smu.measure_current()
            if index > 60 and index < len(input_data - 60):
                currents.append(self.nidaq.measure_current(5))
            self.setupManager.log_info(f"Voltage @ {input_voltage:.2g}V/{drive_current}A \t{index+1}/{len(input_data)}")
        self.setupManager.write_current_numpy(np.asarray(currents))

    def shutdown(self):
        self.nidaq.shutdown()
        self.smu.shutdown()

class VI_NIDAQ_Only(Experiment):
    def __init__(self, setupManager: SetupManager) -> None:
        self.setupManager: SetupManager = setupManager
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis(setupManager)
        atexit.register(self.shutdown)

    def run(self):
        self.nidaq.start_active_all_channels()
        currents = []
        input_data = self.setupManager.get_input_data()
        for index, input_voltage in enumerate(input_data):
            self.nidaq.set_voltage(11, input_voltage)
            currents.append(self.nidaq.measure_voltage(2))
            self.setupManager.log_info(f"Voltage @ {input_voltage:.2g}V |\t{index+1}/{len(input_data)}")
        self.setupManager.write_current_numpy(np.asarray(currents))

    def shutdown(self):
        self.nidaq.shutdown()

class IV_SMU_ONLY(Experiment):
    def __init__(self, setupManager: SetupManager) -> None:
        self.setupManager: SetupManager = setupManager
        self.smu: SMU = SMU(setupManager)
        atexit.register(self.shutdown)

    def run(self):
        currents = []
        input_data = self.setupManager.get_input_data()
        for index, input_voltage in enumerate(input_data):
            self.smu.set_voltage(input_voltage)
            current = self.smu.measure_current()
            self.setupManager.log_info(f"Voltage @ {input_voltage:.2g}V |\t{index+1}/{len(input_data)}")
            if index > 60 and index < len(input_data - 60):
                currents.append(current)
        self.setupManager.write_current_numpy(np.asarray(currents))

    def shutdown(self):
        self.smu.shutdown()


class IV_SMU_NIDAQ(Experiment):
    def __init__(self, setupManager: SetupManager) -> None:
        self.setupManager: SetupManager = setupManager
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis(setupManager)
        self.smu: SMU = SMU(setupManager)
        atexit.register(self.shutdown)

    def run(self):
        currents = []
        self.nidaq.start_active_all_channels()
        input_data = self.setupManager.get_input_data()
        for index, input_voltage in enumerate(input_data):
            self.smu.set_voltage(input_voltage)
            current = self.nidaq.measure_voltage(2)
            drive_current = self.smu.measure_current()
            self.setupManager.log_info(f"Voltage @ {input_voltage:.2g}V & {drive_current}A |\t{index+1}/{len(input_data)}")
            if index > 60 and index < len(input_data - 60):
                currents.append(current)
        self.setupManager.write_current_numpy(np.asarray(currents))

    def shutdown(self):
        self.smu.shutdown()