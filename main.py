from configreader import Config
from pathlib import Path
from setupmanager import SetupManager
import experiment as ep
CONFIG_SETUP = Config(str(Path('configs')/'IV_Setup.yaml'))

if __name__=="__main__":

    setupManager: SetupManager = SetupManager(CONFIG_SETUP)
    experiment: ep.IV_SMU_NIDAQ = ep.IV_SMU_NIDAQ(setupManager)
    try:
        experiment.run()
    except KeyboardInterrupt:
        pass
        