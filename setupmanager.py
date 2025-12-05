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
        self.output_voltage_file: Path = save_name/"output_voltage.csv"
        self.output_current_file: Path = save_name/"output_current.csv"
        self.log_file: Path = save_name/"setup.LOG"
        self.input_file: Path = save_name/"input_current.csv"

        self.terminated_normally = True

        # Create folder if it doesn't exist
        if not os.path.exists(save_name):
            os.makedirs(save_name)

        self._create_metafile()
        self._create_input_file()
        self.log_file.touch(exist_ok=False)
        self.output_voltage_file.touch(exist_ok=False)
        self.output_current_file.touch(exist_ok=False)
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
    
    def get_current_range(self) -> List[float]:
        """
        Gets the current range from the configuration.
        
        :param self: Instance of SetupManager
        :return: List of current range values, of the format [current_min, current_max]
        :rtype: List[float]
        """
        return self.config['current_range']

    def get_input_data(self) -> np.ndarray:
        """
        Gets the input data from the input file and returns it as a numpy array.
        
        :param self: Instance of SetupManager
        :return: Numpy array containing the input data.
        :rtype: ndarray[Any, Any]
        """
        return np.loadtxt(self.input_file, delimiter=",")

    def get_setup_config(self) -> Config:
        """
        Gets the setup configuration.
        
        :param self: Instance of SetupManager
        :return: Returns the Config object of the setup config used to create the SetupManager.
        It includes all information about the experiment.
        :rtype: Config
        """
        return self.config


    def _create_input_file(self):
        """
        Creates a CSV file and fills it with data based on the information in the config setup file.
        It creates a Waveform of Type Wilfred, generated data from it and formats it into a CSV file.
        The data generated is exactly what will be used as input in the experiment.
        
        :param self: Instance of SetupManager
        """
        content = str(Waveform(WaveType.WILFRED,
                           self.config['min_value'],
                           self.config['max_value'],
                           self.config['data_density']))
        with open(self.input_file, "a") as file:
            file.write(content) 

    def _create_metafile(self):
        """
        Creates a meta-file that includes information like the contents of the setup config.
        
        :param self: Instance of SetupManager
        """
        content = f" === [META INFORMATION - {self.start_time}] === \n" + str(self.config)
        with open(self.metadata_file, "w") as file:
            file.write(content)
        with open(self.metadata_file, "a") as file:
            file.write(str(self.config))

    def _create_output_files(self):
        """
        Creates empty output files, that later will be filled out by the experiment.
        
        :param self: Instance of SetupManager
        """
        with open(self.output_voltage_file, "a") as f:
            f.write(",".join(f"Channel {n}" for n in self.config['nidaq']['readout_channels']))
        with open(self.output_current_file, "a") as f:
            f.write(",".join(f"Channel{n}" for n in self.config['nidaq']['readout_channels']))


    def write_voltage(self, voltages: List[Dict[int, float]]):
        """
        Writes a set of voltages to the voltage output file.
        
        :param self: Instance of SetupManager
        :param voltages: A list of voltages, where each column corresponds to a NIDAQ channel.
        Each row represents a datapoint for each channel. The key (type: int) of the dict represents the id of the channel.
        :type voltages: List[Dict[int, float]]
        """
        keys = list(voltages[0].keys())
        rows = [[d[k] for k in keys] for d in voltages]
        array = np.array(rows)
        with open(self.output_voltage_file, "a") as f:
            f.write("\n".join(",".join(map(str, row)) for row in array))

    def write_current(self, currents: List[Dict[int, float]]):
        """
        Writes a set of currents to the current output file.
        
        :param self: Instance of SetupManager
        :param currents: A list of currents, where each column corresponds to a NIDAQ channel.
        Each row represents a datapoint for each channel. The key (type: int) of the dict represents the id of the channel.
        :type currents: List[Dict[int, float]]
        """
        keys = list(currents[0].keys())
        rows = [[d[k] for k in keys] for d in currents]
        array = np.array(rows)
        with open(self.output_current_file, "a") as f:
            f.write("\n".join(",".join(map(str, row)) for row in array))

    def write_current_numpy(self, currents: np.ndarray):
            np.savetxt(self.output_current_file, currents, delimiter=",")

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


    def get_current_data(self):
        return np.loadtxt(self.output_current_file, delimiter=",")
    
    def get_voltage_data(self):
        return np.loadtxt(self.output_voltage_file, delimiter=",")

    def plot(self):
        plt.plot(self.get_input_data(), self.get_current_data())
        plt.grid()
        plt.show()

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


