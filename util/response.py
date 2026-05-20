
from typing import List
import numpy as np

class Response():
    """
    A response is the output of the RNPU after an input and control voltages have been applied.
    The data is split into two, representing up and down sweep.
    This class was made specifically for the genetic algorithm experiment class (`AI_GENETIC`),
    and expects the SWEEP Waveform to be used as the input waveform.

    @TODO: Expand the code so that any input waveform can be used.
    """

    def __init__(self, current_values: List[float]) -> None:
        self.data = np.asarray(current_values)
        self.up_sweep1, self.down_sweep1, self.up_sweep2, self.down_sweep2 = np.array_split(self.data, 4)
    
    def __getitem__(self, key: int) -> float:
        return self.data[key]
    
    def get_up_sweep(self) -> np.ndarray:
        return np.concatenate((self.up_sweep1, self.up_sweep2))
    
    def get_down_sweep(self) -> np.ndarray:
        return np.concatenate((self.down_sweep1, self.down_sweep2))

    def get_data(self) -> np.ndarray:
        return self.data
