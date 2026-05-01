
from experiments._experiment import Experiment
from equipment.NIDAQ import NIDAQ_chassis
import atexit
from typing import Dict, List, Optional
import math
from plotters.plotter import plot_iv_curve
from util.setupmanager import SetupManager

class IV_MARTIN(Experiment):
    
    def __init__(self) -> None:
        super().__init__()
        self.sm: SetupManager = SetupManager()
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis()
        self.config = self.sm.get_config()
        atexit.register(self.close)

    def run(self):

        readout_pad_ids = self.config["nidaq"]["readout_channels"]
        self.channel_in_ids = self.config["nidaq"]["channels_in"]
        self.channel_out_ids = self.config["nidaq"]["channels_out"]
        self.nidaq.start_active_all_channels()

        self.voltage_input = self.sm.get_input_data()
        self.currents_dict: Dict[int, List[float]] = {id: [] for id in readout_pad_ids}

        for i, voltage in enumerate(self.voltage_input):

            self.nidaq.set_voltage_configuration_all(voltage, self.channel_in_ids)
            currents_list = self.nidaq.get_currents_bulk(list(self.currents_dict.keys()))

            for k in self.currents_dict.keys():
                self.currents_dict[k].append(self.voltage_to_current(currents_list[k], k))

            self.sm.log_info(f"{(i+1)}/{len(self.voltage_input)} | {math.floor(((i+1)/len(self.voltage_input))*100)}%")
        
        self.sm.log_info("Experiment complete, saving data...")
        self.sm.write_1d_array(f"RAW_voltages.csv", self.voltage_input)
        self.sm.write_dict("currents", self.currents_dict)
        self.sm.log_info(f"Data saved in {self.sm.get_folder()}/data.")

    def plot(self):
        sum_currents = [sum(elements) for elements in zip(*[self.currents_dict[key] for key in self.channel_out_ids])]
        plot_iv_curve(self.voltage_input, sum_currents, "IV Curve of 8T Martin Config",
                      f"{self.sm.get_folder()}/plots/iv_sum.png")


    def get_setup_manager(self) -> SetupManager:
        return self.sm

    def close(self):
        self.nidaq.shutdown()
