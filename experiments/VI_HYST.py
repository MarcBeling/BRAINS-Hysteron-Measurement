
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

class VI_HYST(Experiment):
    
    def __init__(self) -> None:
        super().__init__()
        self.sm: SetupManager = SetupManager()
        self.nidaq: NIDAQ_chassis = NIDAQ_chassis()
        self.smu: K2400 = K2400()
        self.voltmeter: HP34401A = HP34401A()
        self.config = self.sm.get_config()
        atexit.register(self.close)

    def run(self):

        self.pad_input: int = self.config["input_pad"]
        self.pad_control: int = self.config["control_pad"]
        self.pad_voltmeter: int = self.config["voltmeter_pad"]
        self.pad_output: int = self.config["output_pad"]

        self.nidaq.start_active_all_channels()

        self.current_input = self.sm.get_input_data()
        self.voltages_voltmeter: List[float] = []

        self.voltage_input: List[float] = []
        self.current_control: List[float] = []
        self.current_voltmeter: List[float] = []
        self.current_output: List[float] = []

        for i, current in enumerate(self.current_input):
            
            self.smu.set_current(current)

            self.voltages_voltmeter.append(self.voltmeter.measure_voltage())
            
            self.current_voltmeter.append(self.voltmeter.measure_current())
            
            self.voltage_input.append(self.smu.measure_voltage())

            self.current_control.append(self.nidaq.measure_voltage(self.pad_control))

            self.current_output.append(self.nidaq.measure_voltage(self.pad_output))
            
            self.sm.log_info(f"{i+1}/{len(self.current_input)} | {math.floor(((i+1)/len(self.current_input))*100)}%")
        
        self.sm.log_info("Experiment complete, saving data...")

        self.sm.write_1d_array(f"RAW_currents_pad_{self.pad_input}.csv", self.current_input)
        self.sm.write_1d_array(f"RAW_voltages_pad_{self.pad_voltmeter}.csv", self.voltages_voltmeter)

        self.sm.write_1d_array(f"RAW_voltages_pad_{self.pad_input}.csv", self.voltage_input)
        self.sm.write_1d_array(f"RAW_currents_pad_{self.pad_control}.csv", self.current_control)
        self.sm.write_1d_array(f"RAW_currents_pad_{self.pad_voltmeter}.csv", self.current_voltmeter)
        self.sm.write_1d_array(f"RAW_currents_pad_{self.pad_output}.csv", self.current_output)

        self.sm.log_info(f"Data saved in {self.sm.get_folder()}/data.")

    def process(self):
        
        new_current_input = np.asarray(self.current_input)[60:-60] * 1e9
        new_current_control = np.asarray(self.current_control)[60:-60] * (1e9/2e6)
        new_current_output = np.asarray(self.current_output)[60:-60] * (1e9/2e6)
        new_current_voltmeter = np.asanyarray(self.current_voltmeter)[60:-60] * 1e9

        self.new_voltages_voltmeter = np.asarray(self.voltages_voltmeter)[60:-60]
        self.new_voltages_input = np.asarray(self.current_input)[60:-60]

        dict_currents = {
            self.pad_input: new_current_input,
            self.pad_control: new_current_control,
            self.pad_voltmeter: new_current_voltmeter,
            self.pad_output: new_current_output
        }

        return dict_currents

    def plot(self, cmap: Optional[str] = "tab10", raw=False):

        if raw:
            dict_currents = {
                self.pad_input: self.current_input,
                self.pad_control: self.current_control,
                self.pad_voltmeter: self.current_voltmeter,
                self.pad_output: self.current_output
            }            
        else:
            dict_currents = self.process() 


        cm = plt.get_cmap(cmap)
        colors = [cm(i / max(1, 3)) for i in range(4)]

        foldername: Path = Path(self.sm.get_folder())

        # voltage_input over all currents
        for index, (pad, current) in enumerate(dict_currents.items()):
            fig, ax = plt.subplots(figsize=(5, 4))
            if raw:
                ax.plot(current, self.voltage_input, linewidth=1.8, color=colors[index])
            else:
                ax.plot(current, self.new_voltages_input, linewidth=1.8, color=colors[index])
            ax.set_title(f"VI Curve — Pad {pad} to {self.pad_input}")
            ax.set_ylabel("Voltage (V)")
            if pad==self.pad_voltmeter and raw:
                ax.set_xlabel("Current (A)")
            else:
                ax.set_xlabel("Current (nA)")
            ax.grid(True)
            fig.tight_layout()
            fig.savefig(f"{foldername}/plots/vi_plot_pad_{pad}_to_{self.pad_input}.png", dpi=300)
            plt.close(fig)

        for index, (pad, current) in enumerate(dict_currents.items()):
            fig, ax = plt.subplots(figsize=(5, 4))
            if raw:
                ax.plot(current, self.voltages_voltmeter , linewidth=1.8, color=colors[index])
            else:
                ax.plot(current, self.new_voltages_voltmeter, linewidth=1.8, color=colors[index])
            ax.set_title(f"VI Curve — Pad {pad} to {self.pad_voltmeter}")
            ax.set_ylabel("Voltage (V)")
            if pad==self.pad_voltmeter and raw:
                ax.set_xlabel("Current (A)")
            else:
                ax.set_xlabel("Current (nA)")
            ax.grid(True)
            fig.tight_layout()
            fig.savefig(f"{foldername}/plots/vi_plot_pad_{pad}_to_{self.pad_voltmeter}.png", dpi=300)
            plt.close(fig)

        self.make_image_grid(foldername/"plots", 2, 4, "vi_overview.png")

        fig, ax = plt.subplots(figsize=(5, 4))
        if raw:
            ax.plot(self.voltage_input, self.voltages_voltmeter, linewidth=1.8)
        else:
            ax.plot(self.new_voltages_input, self.new_voltages_voltmeter, linewidth=1.8)
        ax.set_title(f"VV Curve {self.pad_input} to {self.pad_voltmeter}")
        ax.set_xlabel(f"Voltage (V) of Pad {self.pad_input}")
        ax.set_ylabel(f"Voltage (V) of Pad {self.pad_voltmeter}")
        ax.grid(True)
        fig.tight_layout()
        if raw:
            fig.savefig(f"{foldername}/plots/RAW_vv_plot_pad_{self.pad_input}_to_{self.pad_voltmeter}.png", dpi=300)
        else:
            fig.savefig(f"{foldername}/plots/vv_plot_pad_{self.pad_input}_to_{self.pad_voltmeter}.png", dpi=300)            
        plt.close(fig)


    def make_image_grid(self, folder, rows, cols, output):
        """
        Create a simple grid image from all images in a folder.
        - Images are placed back-to-back.
        - Automatically resizes each cell to the smallest image size found.
        """

        folder = Path(folder)
        image_paths = sorted([p for p in folder.iterdir() if p.suffix.lower() in
                            [".jpg", ".jpeg", ".png", ".bmp", ".webp"]])

        if not image_paths:
            raise ValueError("No images found in folder.")

        # Only use as many images as needed to fill the grid
        needed = rows * cols
        image_paths = image_paths[:needed]

        # Load images
        images = [Image.open(p) for p in image_paths]

        # Use the smallest width/height so all cells align cleanly
        min_w = min(img.width for img in images)
        min_h = min(img.height for img in images)

        # Resize all images to the same size
        images = [img.resize((min_w, min_h)) for img in images]

        # Create blank canvas
        grid_w = cols * min_w
        grid_h = rows * min_h
        grid = Image.new("RGB", (grid_w, grid_h))

        # Paste images
        idx = 0
        for r in range(rows):
            for c in range(cols):
                if idx >= len(images):
                    break
                x = c * min_w
                y = r * min_h
                grid.paste(images[idx], (x, y))
                idx += 1

        # Save result
        grid.save(folder/output)
        print(f"Saved grid to: {output}")


    def close(self):
        self.nidaq.shutdown()
        self.smu.shutdown()
        self.voltmeter.shutdown()


