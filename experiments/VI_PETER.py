from experiments._experiment import Experiment
from equipment.NIDAQ import NIDAQ_chassis
from equipment.K2400 import K2400
from equipment.HP34410A import HP34401A
import atexit
from typing import List, Optional
import math
import numpy as np
import matplotlib.pyplot as plt
from util.setupmanager import SetupManager
from PIL import Image
from pathlib import Path
from plotters.plotter import plot_vi_curve

class IV_VI_PETER(Experiment):

    def __init__(self) -> None:
        super().__init__()
        self.sm: SetupManager = SetupManager()
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis()
        self.smu: K2400 = K2400()
        self.voltmeter: HP34401A = HP34401A()
        self.config = self.sm.get_config()
        atexit.register(self.close)

    def run(self):
        
        self.input_pad = self.config["input_pad"]
        self.output_pad = self.config["output_pad"]
        self.voltmeter_pad = self.config["voltmeter_pad"]
        self.cv1_pad = self.config["cv1_pad"]
        self.cv1_value = self.config["cv1"]

        self.nidaq.start_active_all_channels()
    
        self.currents_in = self.sm.get_input_data()
        self.currents_out: List = []
        self.currents_c1: List = []
        self.voltages_in: List = []
        self.voltages_out: List = []

        self.nidaq.start_active_all_channels()

        for i, current in enumerate(self.currents_in):
            self.smu.set_current(current)
            voltage_offset = self.smu.measure_voltage()
            self.voltages_in.append(voltage_offset)
            self.voltages_out.append(self.voltmeter.measure_voltage())
            self.nidaq.set_voltage(self.cv1_pad, self.cv1_value-voltage_offset)
            self.currents_c1.append(self.voltage_to_current(
                self.nidaq.measure_voltage(self.cv1_pad), self.cv1_pad))
            
            self.sm.log_info(f"{(i+1)}/{len(self.currents_in)} | {math.floor(((i+1)/len(self.currents_in))*100)}%")

        self.sm.write_1d_array(f"currents_pad_{self.input_pad}.csv", self.currents_in)
        self.sm.write_1d_array(f"currents_pad_{self.output_pad}.csv", self.currents_out)
        self.sm.write_1d_array(f"currents_pad_{self.cv1_pad}.csv", self.currents_c1)
        self.sm.write_1d_array(f"voltages_pad_{self.voltmeter_pad}.csv", self.voltages_out)
        self.sm.write_1d_array(f"voltages_pad_{self.input_pad}.csv", self.voltages_in)

    def plot(self):
        plot_vi_curve(self.voltages_in, self.currents_in, f"4T RNPU - {self.input_pad} > {self.input_pad}")
        plot_vi_curve(self.voltages_in, self.currents_out, f"4T RNPU - {self.input_pad} > {self.output_pad}")
        plot_vi_curve(self.voltages_in, self.currents_c1, f"4T RNPU - {self.input_pad} > {self.cv1_pad}")
        plot_vi_curve(self.voltages_in, self.currents_in, f"4T RNPU - {self.input_pad} > {self.input_pad}")
        plot_vi_curve(self.voltages_in, self.currents_out, f"4T RNPU - {self.input_pad} > {self.output_pad}")
        plot_vi_curve(self.voltages_in, self.currents_c1, f"4T RNPU - {self.input_pad} > {self.cv1_pad}")


    def close(self):
        self.nidaq.shutdown()
        self.smu.shutdown()
        self.voltmeter.shutdown()