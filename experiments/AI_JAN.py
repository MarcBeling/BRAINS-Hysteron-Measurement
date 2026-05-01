from experiments._experiment import Experiment
import torch

from brainspy.processors.processor import Processor
from brainspy.processors.dnpu import DNPU
from brainspy.utils.pytorch import TorchUtils as TU

from util.setupmanager import SetupManager
import matplotlib.pyplot as plt

class AI_JAN(Experiment):

    def __init__(self) -> None:
        super().__init__()
        self.sm: SetupManager = SetupManager()
        self.config = self.sm.get_config()
        model_data = torch.load('surrogate_models/surrogate_model.pt',
                                map_location=TU.get_device(),
                                weights_only=False)
        self.p = Processor(self.config.get_data(),
                           info=model_data['info'])
        self.rnpu = DNPU(self.p,
                         data_input_indices=self.config['input_electrodes'])

    def run(self) -> None:
        self.input_data = TU.format(self.sm.get_input_data())
        self.prediction: torch.Tensor = self.rnpu(self.input_data)

    def plot(self) -> None:
        plt.figure()
        plt.plot(self.prediction.detach().numpy())
        plt.show()

    def close(self) -> None:
        self.p.close()

