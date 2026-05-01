import os
import atexit
import datetime
from pathlib import Path
from configreader import Config
from waveform import Waveform, WaveType
import numpy as np
from typing import List, Dict
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

    def __init__(self, config_setup: Config):
        self.start_time = datetime.datetime.now()
        self.config = config_setup
        save_name: Path = Path(f"{self.config['name']}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
        self.root_folder = save_name
        self.metadata_file: Path = save_name/"setup.META"
        self.log_file: Path = save_name/"setup.LOG"
        self.save_name = save_name
        self.terminated_normally = True

        # Create folder if it doesn't exist
        if not os.path.exists(save_name):
            os.makedirs(save_name)

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

    def get_input_data(self) -> np.ndarray:
        """
        Gets the input data from the input file and returns it as a numpy array.
        
        :param self: Instance of SetupManager
        :return: Numpy array containing the input data.
        :rtype: ndarray[Any, Any]
        """
        return self.input_data

    def get_setup_config(self) -> Config:
        """
        Gets the setup configuration.
        
        :param self: Instance of SetupManager
        :return: Returns the Config object of the setup config used to create the SetupManager.
        It includes all information about the experiment.
        :rtype: Config
        """
        return self.config

    def _create_input_data(self):
        if self.config['waveform'] == "WILFRED":
            content = Waveform(WaveType.WILFRED,
                           self.config['min_value'],
                           self.config['max_value'],
                           self.config['data_density']).get_waveform_data()
        elif self.config['waveform'] == "REZA":
            content = Waveform(WaveType.REZA,
                           self.config['min_value'],
                           self.config['max_value'],
                           self.config['data_density']).get_waveform_data()
        else:
            raise ValueError("Incorrect Waveform Keyword provided")        
        self.input_data = content

    def write_data_to_file(self, filename: str, data):
        filepath = self.root_folder / filename
        np.savetxt(filepath, data, delimiter=",")


    def save_plot_from_csv_files(self, filename_x: str, filename_y: str, labelx, labely, title):
        """
        Saves a plot from data in two CSV files.
        
        :param self: Instance of SetupManager
        :param filename_x: Name of the CSV file for x-axis data
        :param filename_y: Name of the CSV file for y-axis data
        """
        filepath_x = self.root_folder / filename_x
        filepath_y = self.root_folder / filename_y
        
        data_x = np.loadtxt(filepath_x, delimiter=",")
        data_y = np.loadtxt(filepath_y, delimiter=",")
        
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.plot(data_x[60:-60], data_y)
        ax.set_xlabel(labelx)
        ax.set_ylabel(labely)
        ax.set_title(title)
        ax.grid()
        ax.axhline(0, alpha=0.4)
        ax.axvline(0, alpha=0.4)
        ax.tick_params(direction='in')
        ax.set_xticks(np.arange(-2.0, 2.0, 0.5))
        fig.tight_layout()

        plot_filename = f"{filename_x.split('.')[0]}_{filename_y.split('.')[0]}.png"
        plot_filepath = self.root_folder / plot_filename
        fig.savefig(plot_filepath)

        self.log_info(f"Plot saved to {plot_filename}")

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
        message = f"[{datetime.datetime.now().isoformat()}] [INFO] {message}\n"
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
        message = f"[{datetime.datetime.now().isoformat()}] [WARNING] {message}\n"
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
        message = f"[{datetime.datetime.now().isoformat()}] [ERROR] {message}\n"
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

