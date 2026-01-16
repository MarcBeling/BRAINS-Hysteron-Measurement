import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

def factor_current(ydata):
    ydata = ydata / (2 * 10**6)
    ydata = ydata * 1e9  # A -> nA
    return ydata

def plot(xdata_name, ydata_name, folder_name='', label=""):

    xdata_file: Path = Path(folder_name)/xdata_name
    ydata_file: Path = Path(folder_name)/ydata_name

    xdata = np.loadtxt(xdata_file, delimiter=",")
    if ydata_name == "currents_eo.csv" or ydata_name == "currents_ec.csv":
        ydata = np.loadtxt(ydata_file, delimiter=",")
        ydata = ydata / (2 * 10**6)
    else:
        ydata = np.loadtxt(ydata_file, delimiter=",")
    ydata = ydata * 1e9
    ax.plot(xdata, ydata, label=label)

plot("voltages_ei.csv","currents_SMU_ei.csv","VI_RNPU_3T_ALLINFO_FULLRANGE-2026-01-05_16-40-31", label="Current driven setup")
plot("voltages_SMU_ei.csv","currents_ei.csv","IV_RNPU_3T_ALLINFO-2026-01-05_16-10-18", label="Voltage driven setup")
ax.axhspan(-50, -40, color='lightblue', alpha=0.3, label="Hysterisis effect")
ax.set_title("IV Difference between SMU in current and voltage driven mode")
ax.set_xticks(np.arange(-1.5, 2.0, 0.5))
ax.axvline(0, color='k', alpha=0.4)
ax.axhline(0, color='k', alpha=0.4)
ax.tick_params(direction='in')
ax.set_xlabel("Voltage in V at $e_i\\rightarrow$ GND")
ax.set_ylabel("Current in nA at $e_o$")
ax.grid(True)
ax.legend()
fig.tight_layout()
plt.show()