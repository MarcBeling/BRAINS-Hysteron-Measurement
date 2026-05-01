
from experiments._experiment import Experiment
from equipment.NIDAQ import NIDAQ_chassis
import atexit
from typing import Dict, List, Optional
import math
import numpy as np
import matplotlib.pyplot as plt
from util.setupmanager import SetupManager

class IV_NI(Experiment):
    
    def __init__(self) -> None:
        super().__init__()
        self.sm: SetupManager = SetupManager()
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis()
        self.config = self.sm.get_config()
        atexit.register(self.close)

    def run(self):

        readout_pad_ids = self.config["nidaq"]["readout_channels"]
        self.input_pad_id = self.config["input_pad"]
        self.nidaq.start_active_all_channels()

        self.voltage_input = self.sm.get_input_data()
        self.currents_dict: Dict[int, List[float]] = {id: [] for id in readout_pad_ids}

        for i, voltage in enumerate(self.voltage_input):

            self.nidaq.set_voltage(self.input_pad_id, voltage)
            currents_list = self.nidaq.get_currents_bulk(list(self.currents_dict.keys()))

            for k in self.currents_dict.keys():
                self.currents_dict[k].append(currents_list[k])

            self.sm.log_info(f"{(i+1)}/{len(self.voltage_input)} | {math.floor(((i+1)/len(self.voltage_input))*100)}%")
        
        self.sm.log_info("Experiment complete, saving data...")
        self.sm.write_1d_array(f"RAW_voltages_pad_{self.input_pad_id}.csv", self.voltage_input)
        self.sm.write_dict("RAW_currents_pad", self.currents_dict)
        self.sm.log_info(f"Data saved in {self.sm.get_folder()}/data.")

    def plot(self, cmap: Optional[str] = "tab10"):
        """
        Creates IV subplots arranged in exactly 2 rows.
        Number of columns is computed automatically.
        
        Saves:
          - all_iv_plots_grid.png
          - iv_plot_pad_{pad}.png
        """

        for key, currents in self.currents_dict.items():
            new_currents = []
            for current in currents:
                new_currents.append(self.voltage_to_current(current, key))
            self.currents_dict[key] = new_currents

        foldername = self.sm.get_folder()
        voltage = self.voltage_input
        pads = list(self.currents_dict.keys())
        n = len(pads)

        # ---- FIXED two rows ----
        rows = 2
        cols = math.ceil(n / 2)

        fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows), sharex=False)
        axes = np.array(axes).reshape(rows, cols)

        # ---- Colormap ----
        cm = plt.get_cmap(cmap)
        colors = [cm(i / max(1, n - 1)) for i in range(n)]

        # ---- Plotting ----
        for idx, (pad, color) in enumerate(zip(pads, colors)):
            r = idx // cols
            c = idx % cols
            ax = axes[r, c]

            current = np.asarray(self.currents_dict[pad], dtype=float)

            if len(current) != len(voltage):
                raise ValueError(f"Pad {pad}: voltage and current lengths differ.")

            ax.plot(voltage, current, color=color)
            ax.set_title(f"IV Curve of {self.config['device_measured']} - Pad {pad}")
            ax.set_xlabel("Voltage (V)")
            ax.set_ylabel("Current (nA)")
            ax.grid(True, alpha=0.35)
            ax.axhline(0, color='k', alpha=0.6)
            ax.axvline(0, color='k', alpha=0.6)

            # ---- Save individual plot ----
            indiv_fig = plt.figure(figsize=(5, 4))
            indiv_ax = indiv_fig.add_subplot(111)
            indiv_ax.plot(voltage, current, color=color)
            indiv_ax.set_title(f"IV Curve — Pad {self.input_pad_id} to {pad}")
            indiv_ax.set_xlabel("Voltage (V)")
            indiv_ax.set_ylabel("Current (nA)")
            indiv_ax.grid(True)
            indiv_ax.axhline(0, color='k', alpha=0.6)
            indiv_ax.axvline(0, color='k', alpha=0.6)
            indiv_fig.tight_layout()
            indiv_fig.savefig(f"{foldername}/plots/iv_plot_pad_{self.input_pad_id}_to_{pad}.png", dpi=300)
            plt.close(indiv_fig)

        # ---- Remove empty axes (if any) ----
        for i in range(n, rows * cols):
            r = i // cols
            c = i % cols
            fig.delaxes(axes[r, c])

        # ---- Save full grid ----
        fig.tight_layout()
        fig.savefig(f"{foldername}/plots/all_iv_plots_grid.png", dpi=300)
        plt.close(fig)

        self.sm.log_info("Saved: RAW_all_iv_plots_grid.png and RAW_iv_plot_pad_{pad}.png files.")
        
    def get_setup_manager(self) -> SetupManager:
        return self.sm

    def close(self):
        self.nidaq.shutdown()
