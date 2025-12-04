from configreader import Config
from pathlib import Path
from setupmanager import SetupManager
import experiment as ep

CONFIG_SETUP = Config(str(Path('configs')/'Setup.yaml'))

if __name__=="__main__":

    setupManager: SetupManager = SetupManager(CONFIG_SETUP)
    experiment: ep.NGR_Experiment = ep.NGR_Experiment(setupManager)
    try:
        experiment.run()
    except KeyboardInterrupt:
        pass
    finally:
        setupManager.log_warning("Program interrupted by user.")
        experiment.shutdown()
        

