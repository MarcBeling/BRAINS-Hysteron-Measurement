from configreader import Config
from pathlib import Path
from setupmanager import SetupManager
import experiment as ep
CONFIG_SETUP = Config(str(Path('configs')/'VI_Setup.yaml'))

if __name__=="__main__":

    setupManager: SetupManager = SetupManager(CONFIG_SETUP)
    experiment: ep.VI_SMU_NIDAQ = ep.VI_SMU_NIDAQ(setupManager)
    try:
        experiment.run()
    except KeyboardInterrupt:
        pass
        