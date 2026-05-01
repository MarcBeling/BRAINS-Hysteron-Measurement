from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# folder_name = "IV_SMU_SMU_NIDAQC_NRNPU-2026-02-02_11-28-34"
folder_name = "VI_SMU_SMU_NIDAQC_NRNPU-2026-02-02_11-40-27"

fig, ax = plt.subplots(figsize=(5, 5))
ydata_name = "currents_eo.csv"
ydata_file: Path = Path(folder_name)/ydata_name
ydata = np.loadtxt(ydata_file, delimiter=",")*(1e9)
ydata = ydata
ax.plot(-ydata)
ax.set_title("$I_o$ - SMU 1")
#ax.set_xticks(np.arange(-1.5, 2.0, 0.5))
ax.axvline(0, color='k', alpha=0.4)
ax.axhline(0, color='k', alpha=0.4)
ax.tick_params(direction='in')
ax.set_xlabel("Datapoints")
ax.set_ylabel("Current in nA")
ax.grid(True)
fig.tight_layout()
plt.show()