from equipment.K2400 import K2400
from experiments._experiment import Experiment
from equipment.NIDAQ import NIDAQ_chassis
import atexit
from typing import Dict, List, Optional
import math
import numpy as np
import matplotlib.pyplot as plt
from util.setupmanager import SetupManager
from plotters.plotter import plot_iv_curve
class IV_NI_SMU(Experiment):
    
    def __init__(self) -> None:
        super().__init__()
        self.sm: SetupManager = SetupManager()
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis()
        self.smu: K2400 = K2400()
        self.config = self.sm.get_config()
        atexit.register(self.close)

    def run(self):

        self.input_pad_id = self.config["input_pad"]
        self.readout_pad_ids = self.config["nidaq"]["readout_channels"]
        self.nidaq.start_active_all_channels()

        self.voltage_input = self.sm.get_input_data()

        self.current_dict: Dict[int, List[float]] = {
            self.input_pad_id: []
        }
        for k in self.readout_pad_ids:
            self.current_dict[k] = []

        for i, voltage in enumerate(self.voltage_input):

            self.smu.set_voltage(voltage)
            self.current_dict[self.input_pad_id].append(self.smu.measure_current()*1e9)
            currents_list = self.nidaq.get_currents_bulk(self.readout_pad_ids)
            for k in self.readout_pad_ids:
                self.current_dict[k].append(self.voltage_to_current(currents_list[k], k))
            
            self.sm.log_info(f"{(i+1)}/{len(self.voltage_input)} | {math.floor(((i+1)/len(self.voltage_input))*100)}%")

        self.sm.log_info("Experiment complete, saving data...")
        self.sm.write_1d_array(f"voltages_pad_{self.input_pad_id}.csv", self.voltage_input)
        self.sm.write_dict("currents", self.current_dict)
        self.sm.log_info(f"Data saved in {self.sm.get_folder()}/data.")

    def plot(self):
        for i in self.current_dict.keys():
            plot_iv_curve(self.voltage_input, self.current_dict[i], f"IV Curve 4T @ Pad {self.input_pad_id} and {i}", f"output/{self.sm.get_folder}/plots/iv_plot_{self.input_pad_id}_{i}.png")


    def close(self):
        self.nidaq.shutdown()
        self.smu.shutdown()
