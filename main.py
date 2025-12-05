from configreader import Config
from pathlib import Path
from setupmanager import SetupManager
import experiment as ep

CONFIG_SETUP = Config(str(Path('configs')/'Setup.yaml'))

if __name__=="__main__":

    setupManager: SetupManager = SetupManager(CONFIG_SETUP)
    experiment: ep.RNPU_Experiment = ep.RNPU_Experiment(setupManager)
    try:
        experiment.run()
        setupManager.plot()
    except KeyboardInterrupt:
        pass
        

