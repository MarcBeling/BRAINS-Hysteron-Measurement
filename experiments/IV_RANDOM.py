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

class IV_RANDOM(Experiment):
    
    def __init__(self) -> None:
        super().__init__()
        self.sm: SetupManager = SetupManager()
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis()
        self.smu: K2400 = K2400()
        self.config = self.sm.get_config()

    def run(self):

        self.input_pad_id = self.config["input_pad"]
        self.readout_pad_id = self.config["readout_pad"]

        for self.id in range(self.sm.get_config()["num_of_randoms"]):
            self.sm.log_info(f"Randomized Set #{self.id}")
            self.sm.log_info(f"Randomized Voltages: {self.nidaq.set_random_control()}")
            self.voltage_input = self.sm.get_input_data()
            self.current_readout: List[float] = []

            for i, voltage in enumerate(self.voltage_input):
                self.smu.set_voltage(voltage)
                self.current_readout.append(self.smu.measure_current()*1e9)

            self.sm.log_info("Experiment complete, saving data...")
            self.sm.write_1d_array(f"RND_num_{self.id}_voltages_pad_{self.input_pad_id}.csv", self.voltage_input)
            self.sm.write_1d_array(f"RND_num_{self.id}_currents_pad_{self.readout_pad_id}.csv", self.current_readout)
            self.sm.log_info(f"Data saved in {self.sm.get_folder()}/data.")
            self.plot()

    def plot(self):
        plot_iv_curve(self.voltage_input,
                      self.current_readout,
                      f"IV Curve RNPU @ Pad {self.input_pad_id} and {self.input_pad_id}",
                      f"{self.sm.get_folder()}/plots/rnd_{self.id}_iv_plot_{self.input_pad_id}_{self.input_pad_id}.png")

    def close(self):
        self.nidaq.shutdown()
        self.smu.shutdown()
