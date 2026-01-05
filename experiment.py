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

class VI_SMU_NIDAQ(Experiment):
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

        currents_ei = self.setupManager.get_input_data()
        currents_eo = []
        currents_ec = []
        voltages_ei = []

        for index, input_current in enumerate(currents_ei):

            self.smu.set_current(input_current)

            current_eo = self.nidaq.measure_voltage(2)
            current_ec = self.nidaq.measure_voltage(3)
            voltage_ei = self.smu.measure_voltage()

            if index >= 60 and index < (len(currents_ei)-60):

                currents_eo.append(current_eo)
                currents_ec.append(current_ec)
                voltages_ei.append(voltage_ei)

            self.setupManager.log_info(f"Current @ {input_current:.2g}A / {voltage_ei:.2g}V \t|{index+1}/{len(currents_ei)}")

        self.setupManager.write_data_to_file("currents_eo.csv", currents_eo)
        self.setupManager.write_data_to_file("currents_ec.csv", currents_ec)
        self.setupManager.write_data_to_file("currents_ei.csv", currents_ei)
        self.setupManager.write_data_to_file("voltages_ei.csv", voltages_ei)

    def shutdown(self):
        self.nidaq.shutdown()
        self.smu.shutdown()

class IV_SMU_NIDAQ(Experiment):

    def __init__(self, setupManager: SetupManager) -> None:
        self.setupManager: SetupManager = setupManager
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis(setupManager)
        self.smu: SMU = SMU(setupManager)
        atexit.register(self.shutdown)

    def run(self):

        currents_eo = []
        currents_ec = []
        currents_ei = []
        voltage_ei = self.setupManager.get_input_data()

        self.nidaq.start_active_all_channels()

        for index, input_voltage in enumerate(voltage_ei):

            self.smu.set_voltage(input_voltage)

            current_eo = self.nidaq.measure_voltage(2)
            current_ec = self.nidaq.measure_voltage(3)
            current_ei = self.smu.measure_current()

            self.setupManager.log_info(f"Voltage @ {input_voltage:.2g}V & {current_ei}A |\t{index+1}/{len(voltage_ei)}")

            if index >= 60 and index < (len(input_voltage) - 60):
                currents_eo.append(current_eo)
                currents_ec.append(current_ec)
                currents_ei.append(current_ei)

        self.setupManager.write_data_to_file("voltage_ei.csv", voltage_ei)
        self.setupManager.write_data_to_file("currents_eo.csv", currents_eo)
        self.setupManager.write_data_to_file("currents_ec.csv", currents_ec)
        self.setupManager.write_data_to_file("currents_ei.csv", currents_ei)

    def shutdown(self):
        self.smu.shutdown()
        self.nidaq.shutdown()