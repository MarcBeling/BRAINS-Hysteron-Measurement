from typing import Dict

from equipment.K2400 import K2400
from experiments._experiment import Experiment
from equipment.NIDAQ import NIDAQ_chassis
import atexit
from util.setupmanager import SetupManager
from itertools import product
import numpy as np
import os
import matplotlib.pyplot as plt

class IV_MATRIX(Experiment):
    
    def __init__(self) -> None:
        super().__init__()
        self.sm: SetupManager = SetupManager()
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis()
        self.smu: K2400 = K2400()
        self.config = self.sm.get_config()

        self.pad_i = self.config["input_pad"]
        self.pad_o = self.config["output_pad"]
        self.pad_c1 = self.config["control_pad_1"]
        self.pad_c2 = self.config["control_pad_2"]

        atexit.register(self.close)

    def run(self):

        self.v_in = self.sm.get_input_data()

        
        i = 0
        for cv1, cv2, cv3 in product(self.config["cv1"], self.config["cv2"], self.config["cv3"]):
            i = i + 1
        self.sm.log_info(f"Total Number of runs: {i}")


        for cv1, cv2, cv3 in product(self.config["cv1"], self.config["cv2"], self.config["cv3"]):
            
            self.sm.log_info(f"{cv1}V x {cv2}V x {cv3}V: Running")

            self.nidaq.set_voltage(self.pad_c1, cv1, True)
            self.nidaq.set_voltage(self.pad_c2, cv2, True)
            self.nidaq.set_voltage(self.pad_o, cv3, True)
            c_o = []
            c_c1 = []
            c_c2 = []
            c = []
            c_in = []

            for v in self.v_in:

                self.smu.set_voltage(v)
                c_in.append(self.smu.measure_current())

                channel_voltages = self.nidaq.get_currents_bulk([self.pad_o, self.pad_c1, self.pad_c2])

                c_o_i = self.voltage_to_current(channel_voltages[self.pad_o],self.pad_o)
                c_o.append(c_o_i)

                c_c1_i = self.voltage_to_current(channel_voltages[self.pad_c1],self.pad_c1)
                c_c1.append(c_c1_i)

                c_c2_i = self.voltage_to_current(channel_voltages[self.pad_c2],self.pad_c2)
                c_c2.append(c_c2_i)

                c_i = c_o_i + c_c1_i + c_c2_i
                c.append(c_i)

            self.current_dict: Dict[str, np.ndarray] = {
                str(self.pad_o): np.asarray(c_o),
                str(self.pad_c1): np.asarray(c_c1),
                str(self.pad_c2): np.asarray(c_c2),
                "RNPU_all": np.asarray(c),
                str(self.pad_i): np.asarray(c_in)
            }
            
            self.folder_name = f"{cv1}V_{cv2}V_{cv3}V"

            if not os.path.exists(f"{self.sm.get_folder()}/data/{self.folder_name}"):
                os.makedirs(f"{self.sm.get_folder()}/data/{self.folder_name}")

            if not os.path.exists(f"{self.sm.get_folder()}/plots/{self.folder_name}"):
                os.makedirs(f"{self.sm.get_folder()}/plots/{self.folder_name}")

            self.sm.write_1d_array(f"{self.folder_name}/voltage_{self.pad_i}.csv", self.v_in)
            for pad, currents in self.current_dict.items():
                self.sm.write_1d_array(f"{self.folder_name}/current_{pad}.csv", currents)
                # self.plot_and_save(self.v_in, currents, cv1, cv2, pad)

            self.sm.log_info(f"{cv1}V x {cv2}V x {cv3}V: Complete")

    def plot_and_save(self, voltage, current, cv1, cv2, pad):
        plt.figure(figsize=(5,4))
        plt.ylabel(f"Current in nA @ {pad}")
        plt.xlabel(f"Voltage in V @ {self.pad_i}")
        plt.title(f"IV Curve @ ({cv1}V,{cv2}V) at 4T RNPU, no Resistor")
        plt.axhline(0, color='k', alpha=0.6)
        plt.axvline(0, color='k', alpha=0.6)
        plt.grid()
        plt.plot(voltage[60:-60], current[60:-60])
        plt.tight_layout()
        plt.savefig(f"{self.sm.get_folder()}/plots/{self.folder_name}/iv_{self.pad_i}_{pad}.png")
        plt.close()

    def plot(self):
        pass

    def close(self) -> None:
        self.nidaq.shutdown()
        self.smu.shutdown()