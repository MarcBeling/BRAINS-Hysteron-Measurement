from setupmanager import SetupManager
from equipment import SMU, NIDAQ_chassis, K195, K195

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
        currents_SMU_ei = []

        for index, input_current in enumerate(currents_ei):

            self.smu.set_current(input_current)

            voltage_ei = self.smu.measure_voltage()

            if index >= 60 and index < (len(currents_ei)-60):

                # current_eo = self.nidaq.measure_voltage(4)
                current_ec = self.nidaq.measure_voltage(4)
                current_SMU_ei = self.smu.measure_current()
                # currents_eo.append(current_eo)
                currents_ec.append(current_ec)
                voltages_ei.append(voltage_ei)
                currents_SMU_ei.append(current_SMU_ei)

            self.setupManager.log_info(f"Current @ {input_current:.2g}A / {voltage_ei:.2g}V \t|{index+1}/{len(currents_ei)}")

        self.setupManager.write_data_to_file("currents_eo.csv", currents_eo)
        self.setupManager.write_data_to_file("currents_ec.csv", currents_ec)
        self.setupManager.write_data_to_file("currents_ei.csv", currents_ei)
        self.setupManager.write_data_to_file("voltages_ei.csv", voltages_ei)
        self.setupManager.write_data_to_file("currents_SMU_ei.csv", currents_SMU_ei)      

    def shutdown(self):
        self.nidaq.shutdown()
        self.smu.shutdown()

class VI_Reversal(Experiment):

    def __init__(self, setupManager: SetupManager) -> None:
        self.setupManager: SetupManager = setupManager
        self.smu: SMU = SMU(setupManager)
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis(setupManager)
        atexit.register(self.shutdown)
        
    def run(self):

        self.nidaq.start_active_all_channels()

        input_current = np.loadtxt("currents_eo_from_IV.csv")

        ydata = input_current / (2 * 10**6)
        currents_ei = ydata  # A -> nA

        currents_eo = []
        currents_ec = []
        voltages_ei = []

        for index, input_current in enumerate(currents_ei):

            self.smu.set_current(input_current)

            voltage_ei = self.smu.measure_voltage()

            if index >= 60 and index < (len(currents_ei)-60):

                current_eo = self.nidaq.measure_voltage(2)
                current_ec = self.nidaq.measure_voltage(3)

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
        voltages_ei = self.setupManager.get_input_data()
        voltages_SMU_ei = []

        self.nidaq.start_active_all_channels()

        for index, input_voltage in enumerate(voltages_ei):

            self.smu.set_voltage(input_voltage)

            current_ei = self.smu.measure_current()

            self.setupManager.log_info(f"Voltage @ {input_voltage:.2g}V & {current_ei}A |\t{index+1}/{len(voltages_ei)}")

            if index >= 60 and index < (len(voltages_ei) - 60):

                #current_eo = self.nidaq.measure_voltage(1)
                current_ec = self.nidaq.measure_voltage(4)
                voltage_SMU_ei = self.smu.measure_voltage()

                #currents_eo.append(current_eo)
                currents_ec.append(current_ec)
                currents_ei.append(current_ei)
                voltages_SMU_ei.append(voltage_SMU_ei)

        self.setupManager.write_data_to_file("voltages_ei.csv", voltages_ei)
        self.setupManager.write_data_to_file("currents_eo.csv", currents_eo)
        self.setupManager.write_data_to_file("currents_ec.csv", currents_ec)
        self.setupManager.write_data_to_file("currents_ei.csv", currents_ei)
        self.setupManager.write_data_to_file("voltages_SMU_ei.csv", voltages_SMU_ei)

    def shutdown(self):
        self.smu.shutdown()
        self.nidaq.shutdown()

class TEST_VOLTMETER(Experiment):

    def __init__(self, setupManager: SetupManager) -> None:
        self.setupManager: SetupManager = setupManager
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis(setupManager)
        self.voltmeter: K195 = K195(setupManager)
        atexit.register(self.shutdown)

    def run(self):

        voltages_output = []
        voltages_input = self.setupManager.get_input_data()
        self.nidaq.start_active_all_channels()

        for index, input_voltage in enumerate(voltages_input):
            self.nidaq.set_voltage(4, input_voltage)
            self.nidaq.set_voltage(5, input_voltage)
            self.nidaq.set_voltage(6, input_voltage)
            self.nidaq.set_voltage(7, input_voltage)
            voltage_measured = self.voltmeter.measure_voltage()
            voltages_output.append(voltage_measured)
            self.setupManager.log_info(f"Set: {input_voltage:.2g}V, Measured: {voltage_measured:.2g}V \t| ({index+1}/{len(voltages_input)})")

        self.setupManager.write_data_to_file("voltages_input.csv", voltages_input)
        self.setupManager.write_data_to_file("voltages_output.csv", voltages_output)

    def shutdown(self):
        self.nidaq.shutdown()
        self.voltmeter.shutdown()

class IV_SMU_NI_VOLT(Experiment):

    def __init__(self, setupManager: SetupManager) -> None:
        super().__init__()
        self.setupManager: SetupManager = setupManager
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis(setupManager)
        self.voltmeter: K195 = K195(setupManager)
        self.smu: SMU = SMU(setupManager)
        atexit.register(self.shutdown)

    def run(self):

        voltages_ei = self.setupManager.get_input_data()
        currents_eo = []
        currents_ec = [] 
        currents_ei = []

        self.nidaq.start_active_all_channels()

        for index, input_voltage in enumerate(voltages_ei):
            
            self.smu.set_voltage(input_voltage)
            current_ei = self.smu.measure_current()

            self.setupManager.log_info(f"Voltage @ {input_voltage:.2g}V & {current_ei}A |\t{index+1}/{len(voltages_ei)}")

            if index >= 60 and index < (len(voltages_ei) - 60):

                current_eo = self.voltmeter.measure_current()
                current_ec = self.nidaq.measure_voltage(2)

                currents_eo.append(current_eo)
                currents_ec.append(current_ec)
                currents_ei.append(current_ei)
                
        self.setupManager.write_data_to_file("voltages_ei.csv", voltages_ei)
        self.setupManager.write_data_to_file("currents_eo.csv", currents_eo)
        self.setupManager.write_data_to_file("currents_ec.csv", currents_ec)
        self.setupManager.write_data_to_file("currents_ei.csv", currents_ec)

    def shutdown(self):
        self.nidaq.shutdown()
        self.smu.shutdown()
        self.voltmeter.shutdown()

class VI_SMU_NI_VOLT(Experiment):

    def __init__(self, setupManager: SetupManager) -> None:
        super().__init__()
        self.setupManager: SetupManager = setupManager
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis(setupManager)
        self.voltmeter: K195 = K195(setupManager)
        self.smu: SMU = SMU(setupManager)
        atexit.register(self.shutdown)

    def run(self):

        self.nidaq.start_active_all_channels()

        currents_ei = self.setupManager.get_input_data()
        currents_ec = []
        voltages_ei = []
        voltages_eo = []

        for index, input_current in enumerate(currents_ei):

            self.smu.set_current(input_current)

            voltage_ei = self.smu.measure_voltage()

            if index >= 60 and index < (len(currents_ei)-60):

                current_ec = self.nidaq.measure_voltage_all_channels()
                    
                voltage_eo = self.voltmeter.measure_voltage()

                currents_ec.append(current_ec)
                voltages_ei.append(voltage_ei)
                voltages_eo.append(voltage_eo)

            self.setupManager.log_info(f"Current @ {input_current:.2g}A / {voltage_ei:.2g}V \t|{index+1}/{len(currents_ei)}")

        keys = currents_ec[0].keys()
        arrays = [[d[k] for d in currents_ec] for k in keys]
        for i, ec in enumerate(arrays):
            self.setupManager.write_data_to_file(f"currents_ec{i}.csv", ec)
        self.setupManager.write_data_to_file("voltages_ei.csv", voltages_ei)
        self.setupManager.write_data_to_file("voltages_eo.csv", voltages_eo)
        self.setupManager.write_data_to_file("currents_ei.csv", currents_ei)

    def shutdown(self):
        self.nidaq.shutdown()
        self.smu.shutdown()
        self.voltmeter.shutdown()


class IV_SMU_SMU_NIDAQC(Experiment):

    def __init__(self, setupManager: SetupManager) -> None:
        super().__init__()
        self.setupManager: SetupManager = setupManager
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis(setupManager)
        self.smu1: SMU = SMU(setupManager, config_id='smu_1')
        self.smu2: SMU = SMU(setupManager, config_id='smu_2')
        atexit.register(self.shutdown)

    def run(self):

        self.nidaq.start_active_all_channels()

        voltages_ei = self.setupManager.get_input_data()
        voltages_eo = []
        currents_ec4 = []
        currents_ec7 = []
        currents_eo = []
        currents_ei = []

        for index, input_voltage in enumerate(voltages_ei):

            self.smu1.set_voltage(input_voltage)
            current_ei = self.smu1.measure_current()
            currents_ei.append(current_ei) 
            
            if index >= 60 and index < (len(voltages_ei)-60):

                current_ec4 = self.nidaq.measure_voltage(4)
                currents_ec4.append(current_ec4)

                current_ec7 = self.nidaq.measure_voltage(7)
                currents_ec7.append(current_ec7)

                current_eo = self.smu2.measure_current()
                currents_eo.append(current_eo)

                voltage_eo = self.smu2.measure_voltage()
                voltages_eo.append(voltage_eo)

            self.setupManager.log_info(f"Voltage @ {input_voltage:.2g}V/{current_ei:.2g}A \t|{index+1}/{len(voltages_ei)}")

        self.setupManager.write_data_to_file("voltages_ei.csv", voltages_ei)
        self.setupManager.write_data_to_file("voltages_eo.csv", voltages_eo)
        self.setupManager.write_data_to_file("currents_ec4.csv", currents_ec4)
        self.setupManager.write_data_to_file("currents_ec7.csv", currents_ec7)
        self.setupManager.write_data_to_file("currents_eo.csv", currents_eo)
        self.setupManager.write_data_to_file("currents_ei.csv", currents_ei)

    def shutdown(self):
        self.nidaq.shutdown()
        self.smu1.shutdown()
        self.smu2.shutdown()

class VI_SMU_SMU_NIDAQC(Experiment):

    def __init__(self, setupManager: SetupManager) -> None:
        super().__init__()
        self.setupManager: SetupManager = setupManager
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis(setupManager)
        self.smu1: SMU = SMU(setupManager, config_id='smu_1')
        self.smu2: SMU = SMU(setupManager, config_id='smu_2')
        atexit.register(self.shutdown)

    def run(self):

        self.nidaq.start_active_all_channels()

        currents_ei = self.setupManager.get_input_data()
        voltages_ei = []
        voltages_eo = []
        currents_ec = []
        currents_eo = []

        for index, input_current in enumerate(currents_ei):

            self.smu2.set_current(input_current)
            voltage_ei = self.smu2.measure_voltage()
            voltages_ei.append(voltage_ei) 
            
            if index >= 60 and index < (len(currents_ei)-60):

                current_ec = self.nidaq.measure_voltage(6)
                currents_ec.append(current_ec)

                current_eo = self.smu1.measure_current()
                currents_eo.append(current_eo)

                voltage_eo = self.smu1.measure_voltage()
                voltages_eo.append(voltage_eo)

            self.setupManager.log_info(f"Current @ {input_current:.2g}A/{voltage_ei:.2g}V \t|{index+1}/{len(currents_ei)}")

        self.setupManager.write_data_to_file("voltages_ei.csv", voltages_ei)
        self.setupManager.write_data_to_file("voltages_eo.csv", voltages_eo)
        self.setupManager.write_data_to_file("currents_ec.csv", currents_ec)
        self.setupManager.write_data_to_file("currents_eo.csv", currents_eo)
        self.setupManager.write_data_to_file("currents_ei.csv", currents_ei)

    def shutdown(self):
        self.nidaq.shutdown()
        self.smu1.shutdown()
        self.smu2.shutdown()

class IV_NIDAQ_8ALL(Experiment):

    
    def __init__(self, setupManager: SetupManager) -> None:
        super().__init__()
        self.setupManager: SetupManager = setupManager
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis(setupManager)
        
        atexit.register(self.shutdown)

    def run(self):
        self.nidaq.start_active_all_channels()
        voltages = self.setupManager.get_input_data()
        currents = [[] for _ in range(8)]
        self.chosen_electrode = 0

        for i, voltage in enumerate(voltages):
            if i < 60 or i > (len(voltages)-60):
                time.sleep(0.1)
                self.nidaq.set_voltage(self.chosen_electrode, voltage, False)
            if i >= 60 and i < (len(voltages)-60):
                self.nidaq.set_voltage(self.chosen_electrode, voltage, False)
                for j in range(8):
                    if j == 0:
                        current = (self.nidaq.measure_voltage(j))/(2 * 10**7)
                    else:
                        current = (self.nidaq.measure_voltage(j))/(2 * 10**6)
                    currents[j].append(current)
            self.setupManager.log_info(f"Voltage @ {voltage:.2g}V \t|{i+1}/{len(voltages)}")

        currents = np.array(currents)
        currents = currents * 1e9

        for i, electrode_current in enumerate(currents):
            self.setupManager.write_data_to_file(f"currents_e{i}.csv", electrode_current)
        self.setupManager.write_data_to_file(f"voltages_e{self.chosen_electrode}.csv", voltages)

    def plot(self):
        for i in range(8):
            self.setupManager.save_plot_from_csv_files(f"voltages_e{self.chosen_electrode}.csv",
                                                       f"currents_e{i}.csv",
                                                       f"Voltage applied at electrode {self.chosen_electrode} in V",
                                                       f"Current measured at electrode {i} in nA",
                                                       f"IV-Curve between electrode {self.chosen_electrode} and {i}")

    def shutdown(self):
        self.nidaq.shutdown()
