import os
import atexit
from datetime import datetime
from pathlib import Path
from util.configreader import Config
from util.waveform import Waveform, WaveType
import numpy as np
from typing import List, Dict, Optional, Any
from util.global_states import global_variables
import math
import matplotlib.pyplot as plt

class Singleton(type):
    """Metaclass to enforce Singleton behavior."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class SetupManager(metaclass=Singleton):
    """
    SetupManager - Singleton class for managing experimental setup configuration and data logging.
    This class handles the initialization and management of experimental data collection,
    including configuration management, input and output file creation, experiment logging, and shutdown.
    Attributes:
        start_time (datetime.datetime): Timestamp when SetupManager was initialized.
        config (Config): Configuration dictionary containing setup parameters.
        root_folder (Path): Root directory for storing all experiment data.
        metadata_file (Path): Path to the setup metadata file.
        output_voltage_file (Path): Path to the output voltage CSV file.
        output_current_file (Path): Path to the output current CSV file.
        log_file (Path): Path to the setup log file.
        input_file (Path): Path to the input current CSV file.
        terminated_normally (bool): Flag indicating if the program terminated normally.
    """

    def __init__(self):
        super().__init__()
        self.config = Config(f"configs/{global_variables.EXPERIMENT_NAME}.yaml")
        self.start_time =datetime.now()
        today_str = datetime.today().strftime("%d-%m-%Y")
        save_name: Path = Path(f"output/{today_str}/{self.config['name']}-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}")
        self.root_folder = save_name
        self.metadata_file: Path = save_name/"setup.META"
        self.log_file: Path = save_name/"setup.LOG"
        self.save_name = save_name
        self.terminated_normally = True

        # Create folder if it doesn't exist
        if not os.path.exists(save_name):
            os.makedirs(save_name)

        data_folder: Path = self.root_folder / "data" 
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        plot_folder: Path = self.root_folder / "plots" 
        if not os.path.exists(plot_folder):
            os.makedirs(plot_folder)

        self._create_metafile()
        self._create_input_data()
        self.log_file.touch(exist_ok=False)
        atexit.register(self._on_exit)

        self.log_info("SetupManager initialized.")

    def get_voltage_range(self) -> List[float]:
        """
        Gets the voltage range from the configuration.
        
        :param self: Instance of SetupManager
        :return: List of voltage range values, of the format [voltage_min, voltage_max]
        :rtype: List[float]
        """
        return self.config['voltage_range']
    
    def get_current_range(self) -> np.ndarray:
        """
        Gets the current range from the configuration.
        
        :param self: Instance of SetupManager
        :return: List of current range values, of the format [current_min, current_max]
        :rtype: List[float]
        """
        return np.array([float(x) for x in self.config['current_range']])

    def get_config(self) -> Config:
        """
        Gets the setup configuration.
        
        :param self: Instance of SetupManager
        :return: Returns the Config object of the setup config used to create the SetupManager.
        It includes all information about the experiment.
        :rtype: Config
        """

        return self.config

    def _create_input_data(self):
        """
        Creates the input data based on the wave type defined in the experiments yaml configuration file

        Raises:
            ValueError: This error is thrown when an unknown Waveform is used. See `waveform.py` in `util` to see what waveforms are possible.
        """        
        content: Waveform

        try:
            wave_type = WaveType[self.config["wavetype"]]
        except KeyError:
            raise ValueError(f"Unknown waveform type: {self.config['wavetype']}")

        content = Waveform(wave_type,
                           self.config['min_value'],
                           self.config['max_value'],
                           self.config['data_density'])


        self.input_data = content.get_waveform_data()

    def write_1d_array(self, filename: str, data: Any):
        """
        Writes a 1d list to the savefile folder.

        Args:
            filename (str): The filename that the data should be saved under
            data (Any): _description_
        """        
        filepath = self.root_folder / "data" / filename
        np.savetxt(filepath, data, delimiter=",")

    def write_dict(self, filename: str, current_dict: Dict[int, List[float]]) -> None:
        """
        Writes one CSV file per pad, named 'currents_pad_{i}.csv'.
        Values may be Python lists or NumPy arrays.
        """
        
        for pad, currents in current_dict.items():
            # Convert to numpy array if needed
            arr = np.asarray(currents, dtype=float).reshape(-1, 1)

            filepath = self.root_folder / "data" /  f"{filename}_{pad}.csv"
            np.savetxt(filepath, arr, delimiter=",")

    def get_folder(self) -> str:
        return str(self.root_folder)
    
    def create_subfolder(self, foldername: str) -> None:
        """
        Creates a subfolder under the main savefile folder.
        
        Args:
            foldername (str): Name of the subfolder.

        Example:
            If foldername is "run1", then the folder structure looks like: root_folder_name > run1
        """        
        subfolder: Path = self.root_folder / foldername 
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)
        

    def plot_list(self,
                  currents_list: List[float],
                  foldername: str = "/") -> None:
        """
        Plots a list of currents in an IV Curve

        Args:
            currents_list (List[float]): The list of currents that should be plotted
            foldername (str, optional): Name of the subfolder where the plot should be saved instead. Defaults to "/".
        """        

        np_currents_list = np.asarray(currents_list)
        plt.figure(figsize=(5,4))
        plt.title("IV Curve RNPU")
        plt.axhline(0, color='k', alpha=0.6)
        plt.axvline(0, color='k', alpha=0.6)
        plt.grid()
        plt.plot(self.get_input_data(), np_currents_list*1e9, color='r')
        plt.xlabel("Voltage in V")
        plt.ylabel("Currents in nA")
        plt.savefig(f"{self.save_name}/plots{foldername}iv_plot.png", dpi=300)
        plt.close()

    def plot_dict(self,
                  currents_dict: Dict[str, List[float]],
                  foldername: str = "/",
                  cmap: Optional[str] = "tab10"):
        """
        Creates IV subplots arranged in exactly 2 rows.
        Number of columns is computed automatically.
        
        Saves:
          - all_iv_plots_grid.png
          - iv_plot_pad_{pad}.png
        """

        pads = list(currents_dict.keys())
        n = len(pads)

        # ---- FIXED two rows ----
        rows = 2
        cols = math.ceil(n / 2)

        fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows), sharex=False)
        axes = np.array(axes).reshape(rows, cols)

        # ---- Colormap ----
        cm = plt.get_cmap(cmap)
        colors = [cm(i / max(1, n - 1)) for i in range(n)]

        voltage = self.get_input_data()

        # ---- Plotting ----
        for idx, (pad, color) in enumerate(zip(pads, colors)):
            r = idx // cols
            c = idx % cols
            ax = axes[r, c]

            current = np.asarray(currents_dict[pad], dtype=float)

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
            indiv_ax.set_title(f"IV Curve — Pad {pad}")
            indiv_ax.set_xlabel("Voltage (V)")
            indiv_ax.set_ylabel("Current (nA)")
            indiv_ax.grid(True)
            indiv_ax.axhline(0, color='k', alpha=0.6)
            indiv_ax.axvline(0, color='k', alpha=0.6)
            indiv_fig.tight_layout()
            indiv_fig.savefig(f"{self.save_name}/plots{foldername}iv_plot_pad_{pad}.png", dpi=300)
            plt.close(indiv_fig)

        # ---- Remove empty axes (if any) ----
        for i in range(n, rows * cols):
            r = i // cols
            c = i % cols
            fig.delaxes(axes[r, c])

        # ---- Save full grid ----
        fig.tight_layout()
        fig.savefig(f"{self.save_name}/plots{foldername}all_iv_plots_grid.png", dpi=300)
        plt.close(fig)

        self.log_info("Saved: RAW_all_iv_plots_grid.png and RAW_iv_plot_pad_{pad}.png files.")        

    def _create_metafile(self):
        """
        Creates a meta-file that includes information like the contents of the setup config.
        
        :param self: Instance of SetupManager
        """
        content = f" === [META INFORMATION - {self.start_time}] === \n" + str(self.config)
        with open(self.metadata_file, "w") as file:
            file.write(content)

    def log_info(self, message: str):
        """
        Logs an informational message. This will be indicated as `[INFO]` in the log.
        
        :param self: Instance of SetupManager
        :param message: The message that should be logged.
        :type message: str
        """
        message = f"[{datetime.now().isoformat()}] [INFO] {message}\n"
        print(message.rstrip('\n'))
        with open(self.log_file, "a") as f:
            f.write(message)

    def log_warning(self, message: str):
        """
        Logs a warning message. This will be indicated as `[WARNING]` in the log.
        
        :param self: Instance of SetupManager
        :param message: The message that should be logged.
        :type message: str
        """
        message = f"[{datetime.now().isoformat()}] [WARNING] {message}\n"
        print(message.rstrip('\n'))
        with open(self.log_file, "a") as f:
            f.write(message)

    def log_error(self, message: str):
        """
        Logs an error message. This will be indicated as `[ERROR]` in the log.
        This will change the property `terminated_normaly` to `FALSE`,
        indicating that the program encountered a serious problem during execution.
        
        :param self: Instance of SetupManager
        :param message: The message that should be logged.
        :type message: str
        """
        self.terminated_normally = False
        message = f"[{datetime.now().isoformat()}] [ERROR] {message}\n"
        print(message.rstrip('\n'))
        with open(self.log_file, "a") as f:
            f.write(message)

    def wait_for_user_input(self):
        """
        Asks the user to confirm to continue the program.
        Useful to call before running an experiment to allow the user to check for any device configuration mishaps
        
        :param self: Instance of SetupManager
        """
        while True:
            choice = input("Enter Y to continue or N to stop: ").strip().upper()
            if choice == "Y":
                break
            elif choice == "N":
                self.log_info("User chose to end the program when prompted.")
                print("Stopping program...")
                exit(0)  # Terminates the program
            else:
                print("Invalid input. Please enter Y or N.")

    def _on_exit(self):
        """
        Shuts off the SetupManager. This does not shut down any devices involved in the Experiment.
        This should be done in your custom Experiments class.
        
        :param self: Instance of SetupManager
        """
        if self.terminated_normally:
            self.log_info("Program ended normally")
        else:
            self.log_warning("Program terminated by user or unexpectedly")

    def get_input_data(self):
        return self.input_data