from configreader import Config
from pathlib import Path
from setupmanager import SetupManager
from experiment import RNPU_Experiment

CONFIG_SETUP = Config(str(Path('configs')/'Setup.yaml'))

if __name__=="__main__":

    setupManager: SetupManager = SetupManager(CONFIG_SETUP)
    experiment: RNPU_Experiment = RNPU_Experiment(setupManager)
    try:
        experiment.run()
    except KeyboardInterrupt:
        setupManager.log_warning("Program interrupted by user.")
