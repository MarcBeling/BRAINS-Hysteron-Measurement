import numpy as np
from enum import Enum

class WaveType(Enum):
    """
    Defines the type of waveform that should be generated when intializing a Waveform object.
    Attributes:
        SAWTOOTH: Sawtooth wave going from 0 -> min -> max -> 0
        LINSPACE: Linear function going from 0 -> max
        WILFRED: Adjusted Sawtooth wave covering multiple phases. Goes from 0 -> min -> max -> min -> max -> 0
    """
    SAWTOOTH = 0
    LINSPACE = 1
    WILFRED = 2

class Waveform():
    """
    Class wrapping methods to create a Waveform. Covers the generation of data values based on WaveType.
    Attributes:
        min_value (float): Minimum value of the Waveform
        max_value (float): Maximum value of the Waveform
        data_per_sec (int): Number of datapoints for each section of the waveform, not the entire waveform.
    """

    def __init__(self, type: WaveType, min_value, max_value, datapoint_per_section):
        self.min_value = np.float64(min_value)
        self.max_value = np.float64(max_value)
        self.data_per_sec = datapoint_per_section

        if type == WaveType.SAWTOOTH:
            self.generate_sawtooth()
        elif type == WaveType.LINSPACE:
            self.generate_linspace()
        elif type == WaveType.WILFRED:
            self.generate_wilfred()
        else:
            raise ValueError('Unfamiliar WaveType Enum.')
        
    def generate_sawtooth(self):
        step1 = np.linspace(0, self.min_value, self.data_per_sec)
        step2 = np.linspace(self.min_value, self.max_value, self.data_per_sec)
        step3 = np.linspace(self.max_value, 0, self.data_per_sec)
        self._data = np.concatenate((step1, step2, step3))
        return self
    
    def generate_wilfred(self):
        step1 = np.linspace(0, self.min_value, self.data_per_sec)
        step2 = np.linspace(self.min_value, self.max_value, 2 * self.data_per_sec)
        step3 = np.linspace(self.max_value, self.min_value, 2 * self.data_per_sec)
        step4 = np.linspace(self.min_value, self.max_value, 2 * self.data_per_sec)
        step5 = np.linspace(self.max_value, 0, self.data_per_sec)
        self._data = np.concatenate((step1, step2, step3, step4, step5))
        return self
    
    def clip_waveform(self, min_value, max_value):
        self._data = np.clip(self._data, min_value, max_value)
        return self

    def generate_linspace(self):
        self._data = np.linspace(self.min_value, self.max_value, self.data_per_sec)
        return self

    def transform_waveform(self, transforming_function):
        self._data = transforming_function(self._data)
        return self

    def get_waveform_data(self):
        return self._data
    
    def get_selection(self, lower_boundary, upper_boundary):
        return self._data[(self._data >= lower_boundary) & (self._data <= upper_boundary)]
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, index):
        return self._data[index]
    
    def __str__(self):
        if self._data.ndim == 1:
            return ",".join(map(str, self._data))
        else:
            return "\n".join(",".join(map(str, row)) for row in self._data)

    