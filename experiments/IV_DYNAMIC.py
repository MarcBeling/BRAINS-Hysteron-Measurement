
from multiprocessing import process
from experiments._experiment import Experiment
from equipment.NIDAQ import NIDAQ_chassis
from equipment.K2400 import K2400
import atexit
from typing import Dict, List, Optional
import math
import numpy as np
import matplotlib.pyplot as plt
from util.setupmanager import SetupManager
from plotters.plotter import plot_iv_curve, plot_vv_curve

class IV_DYNAMIC(Experiment):
    
    def __init__(self) -> None:
        super().__init__()
        self.sm: SetupManager = SetupManager()
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis()
        self.smu: K2400 = K2400()
        self.config = self.sm.get_config()
        atexit.register(self.close)

    def run(self):

        self.input_pad = self.config["input_pad"]
        self.output_pad = self.config["output_pad"]
        self.cv1_pad = self.config["cv1_pad"]
        self.cv2_pad = self.config["cv2_pad"]

        self.V_C1 = self.config["nidaq"]["control_voltages"][self.cv1_pad]
        self.V_C2 = self.config["nidaq"]["control_voltages"][self.cv2_pad]

        self.voltages_in = self.sm.get_input_data()
        self.currents_in: List = []
        self.currents_c1: List = []
        self.currents_c2: List = []

        self.currents_out: List = []
        self.voltages_out: List = []

        self.nidaq.start_active_all_channels()

        for i, voltage in enumerate(self.voltages_in):
            self.nidaq.set_voltage(self.input_pad, voltage)
            I_out = self.smu.measure_current()

            result_cv1 = self.adjust_CV(self.V_C1, voltage, self.cv1_pad)
            result_cv2 = self.adjust_CV(self.V_C2, voltage, self.cv2_pad)

            if result_cv1 == False or result_cv2 == False:
                self.sm.log_warning(f"{voltage}: Control Voltages could not be adjusted!")
            else:    
                self.nidaq.set_voltage(self.cv1_pad, result_cv1)
                self.nidaq.set_voltage(self.cv2_pad, result_cv2)
            
            self.currents_out.append(self.smu.measure_current()*1e9)

            result_currents = self.nidaq.get_currents_bulk([self.input_pad, self.cv1_pad, self.cv2_pad])
            self.currents_in.append(self.voltage_to_current(result_currents[self.input_pad], self.input_pad))
            self.currents_c1.append(self.voltage_to_current(result_currents[self.cv1_pad], self.cv1_pad))
            self.currents_c2.append(self.voltage_to_current(result_currents[self.cv2_pad], self.cv2_pad))

            self.voltages_out.append(self.smu.measure_voltage())
            self.sm.log_info(f"{(i+1)}/{len(self.voltages_in)} | {math.floor(((i+1)/len(self.voltages_in))*100)}%")

        self.sm.write_1d_array(f"voltages_pad_{self.input_pad}.csv", self.voltages_in)
        self.sm.write_1d_array(f"currents_pad_{self.input_pad}.csv", self.currents_in)
        self.sm.write_1d_array(f"currents_pad_{self.output_pad}.csv", self.currents_out)
        self.sm.write_1d_array(f"currents_pad_{self.cv1_pad}.csv", self.currents_c1)
        self.sm.write_1d_array(f"currents_pad_{self.cv2_pad}.csv", self.currents_c2)
        self.sm.write_1d_array(f"voltages_pad_{self.output_pad}.csv", self.voltages_out)
        
    def plot(self):

        folderstring = f"{self.sm.get_folder()}/plots"

        plot_iv_curve(self.voltages_in, self.currents_in,
                      f"IV Curve, 4T RNPU:\nx = Pad {self.input_pad}, y = Pad {self.input_pad}",
                      f"{folderstring}/IV_x_{self.input_pad}_y_{self.input_pad}.png")
        plot_iv_curve(self.voltages_in, self.currents_out,
                      f"IV Curve, 4T RNPU:\nx = Pad {self.input_pad}, y = Pad {self.output_pad}",
                      f"{folderstring}/IV_x_{self.input_pad}_y_{self.output_pad}.png")
        plot_iv_curve(self.voltages_in, self.currents_c1,
                      f"IV Curve, 4T RNPU:\nx = Pad {self.input_pad}, y = Pad {self.cv1_pad}",
                      f"{folderstring}/IV_x_{self.input_pad}_y_{self.cv1_pad}.png")
        plot_iv_curve(self.voltages_in, self.currents_c2,
                      f"IV Curve, 4T RNPU:\nx = Pad {self.input_pad}, y = Pad {self.cv2_pad}",
                      f"{folderstring}/IV_x_{self.input_pad}_y_{self.cv2_pad}.png")
        plot_vv_curve(self.voltages_in, self.voltages_out,
                      f"VV Curve, 4T RNPU:\nx = Pad {self.input_pad}, y = Pad {self.output_pad}",
                      f"{folderstring}/VV_x_{self.input_pad}_y_{self.output_pad}.png")


    def adjust_CV(self, V_c, V_in, pad_id):
        if V_in > 0:
            new_control_voltage = float(V_c) * (1 + 0.5 * float(V_in))
            if abs(new_control_voltage) > max(self.sm.get_config()["voltage_range"]):
                self.sm.log_info(f"({pad_id}) V_in: {V_in}V, V_c: {V_c}V -> {new_control_voltage}V : Too high!")
                return False
            else:
                self.sm.log_info(f"({pad_id}) V_in: {V_in}V, {V_c}V -> {new_control_voltage}V")
                return new_control_voltage
        else:
            return V_c


    def close(self):
        self.nidaq.shutdown()
        self.smu.shutdown()
