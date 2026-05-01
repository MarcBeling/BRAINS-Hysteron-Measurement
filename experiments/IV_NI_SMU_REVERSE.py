from equipment.K2400 import K2400
from experiments._experiment import Experiment
from equipment.NIDAQ import NIDAQ_chassis
import atexit
from typing import Dict, List, Optional
import math
import numpy as np
import matplotlib.pyplot as plt
from util.setupmanager import SetupManager

class IV_NI_SMU_REVERSE(Experiment):
    
    def __init__(self) -> None:
        super().__init__()
        self.sm: SetupManager = SetupManager()
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis()
        self.smu: K2400 = K2400()
        self.config = self.sm.get_config()
        atexit.register(self.close)

    def run(self):

        self.input_pad_id = self.config["input_pad"]
        self.output_pad_id: int = self.config["output_pad"]
        self.cv1_pad_id = self.config["CV1_pad"]
        self.cv2_pad_id = self.config["CV2_pad"]
        self.nidaq.start_active_all_channels()

        self.voltage_input = self.sm.get_input_data()
        #self.voltage_out = []
        self.current_in = []
        self.current_o: List = []
        self.current_cv1 = []
        self.current_cv2 = []

        for i, voltage in enumerate(self.voltage_input):

            self.nidaq.set_voltage(self.input_pad_id, voltage)
            self.current_o.append(self.smu.measure_current())

            results = self.nidaq.get_currents_bulk([self.input_pad_id, self.cv1_pad_id, self.cv2_pad_id])
            self.current_in.append(self.voltage_to_current(results[self.input_pad_id], self.input_pad_id))
            self.current_cv1.append(self.voltage_to_current(results[self.cv1_pad_id], self.cv1_pad_id))
            self.current_cv2.append(self.voltage_to_current(results[self.cv2_pad_id], self.cv2_pad_id))

            #self.voltage_out.append(self.smu.measure_voltage())

            self.sm.log_info(f"{(i+1)}/{len(self.voltage_input)} | {math.floor(((i+1)/len(self.voltage_input))*100)}%")

        self.sm.log_info("Experiment complete, saving data...")
        self.sm.write_1d_array(f"voltages_{self.input_pad_id}.csv", self.voltage_input)
        self.sm.write_1d_array(f"currents_{self.input_pad_id}.csv", self.current_in)
        self.sm.write_1d_array(f"currents_{self.output_pad_id}.csv", self.current_o)
        self.sm.write_1d_array(f"currents_{self.cv1_pad_id}.csv", self.current_cv1)
        self.sm.write_1d_array(f"currents_{self.cv2_pad_id}.csv", self.current_cv2)
        self.sm.log_info(f"Data saved in {self.sm.get_folder()}/data.")

    def plot(self):
        """
        Creates IV subplots arranged in exactly 2 rows.
        Number of columns is computed automatically.
        
        Saves:
        - all_iv_plots_grid.png
        - iv_plot_pad_{pad}.png
        """

        voltage = self.voltage_input
        current = self.current_o

        # Basic consistency check
        if len(voltage) != len(current):
            raise ValueError("Voltage and current files must contain the same number of data points.")
        
        # Plot VI curve
        plt.figure(figsize=(5, 4))
        plt.plot(voltage[60:-60], current[60:-60])

        plt.title("IV Curve of a 4T RNPU without Resistor")
        plt.xlabel("Voltage (V)")
        plt.ylabel("Current (nA)")
        plt.grid(True)
        plt.axhline(0, color='k', alpha=0.4)
        plt.axvline(0, color='k', alpha=0.4)

        foldername = self.sm.get_folder()
        plt.savefig(f"{foldername}/plots/iv_plot_pad_{self.input_pad_id}_to_{self.output_pad_id}.png", dpi=300)

    def get_setup_manager(self) -> SetupManager:
        return self.sm

    def close(self):
        self.nidaq.shutdown()
        self.smu.shutdown()
