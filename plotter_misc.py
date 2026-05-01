import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt



def factor_current(ydata):
    ydata = ydata / (2 * 10**6)
    ydata = ydata * 1e9  # A -> nA
    return ydata

def plot(xdata_name, ydata_name, folder_name='', label=""):

    fig, ax = plt.subplots()
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

def plot_single(ydata_name, folder_name='', label=""):

    fig, ax = plt.subplots()
    ydata_file: Path = Path(folder_name)/ydata_name
    if ydata_name == "currents_eo.csv" or ydata_name == "currents_ec.csv":
        ydata = np.loadtxt(ydata_file, delimiter=",")
        ydata = ydata / (2 * 10**6)
    else:
        ydata = np.loadtxt(ydata_file, delimiter=",")
    ydata = ydata * 1e9
    ax.plot(ydata)

    ax.set_title("Current - SMU")
    #ax.set_xticks(np.arange(-1.5, 2.0, 0.5))
    ax.axvline(0, color='k', alpha=0.4)
    ax.axhline(0, color='k', alpha=0.4)
    ax.tick_params(direction='in')
    ax.set_xlabel("Datapoints")
    ax.set_ylabel(label)
    ax.grid(True)
    ax.legend()
    fig.tight_layout()
    plt.show()

# folder_name = "VI_SMU_SMU_NIDAQC_NRNPU-2026-02-02_11-40-27"
folder_name = "IV_SMU_SMU_NIDAQC_NRNPU-2026-02-02_11-28-34"

# plot_single("currents_ei.csv","VI_SMU_SMU_NIDAQC_NRNPU-2026-02-02_11-40-27")
# plot_single("voltages_ei.csv","IV_SMU_SMU_NIDAQC_NRNPU-2026-02-02_11-28-34")

fig, ax = plt.subplots()
ydata_name = "currents_ei.csv"
ydata_file: Path = Path(folder_name)/ydata_name
if ydata_name == "currents_eo.csv" or ydata_name == "currents_ec.csv":
    ydata = np.loadtxt(ydata_file, delimiter=",")[60:-60]
    ydata = ydata / (2 * 10**6)
else:
    ydata = np.loadtxt(ydata_file, delimiter=",")[60:-60]
ydata = ydata * 1e9
ax.plot(ydata)

ax.set_title("Current - SMU 1")
#ax.set_xticks(np.arange(-1.5, 2.0, 0.5))
ax.axvline(0, color='k', alpha=0.4)
ax.axhline(0, color='k', alpha=0.4)
ax.tick_params(direction='in')
ax.set_xlabel("Datapoints")
ax.set_ylabel("Current provided by SMU in nA")
ax.grid(True)
fig.tight_layout()
plt.show()

#
fig, ax = plt.subplots()
ydata_name = "currents_ec.csv"
ydata_file: Path = Path(folder_name)/ydata_name
if ydata_name == "currents_eo.csv" or ydata_name == "currents_ec.csv":
    ydata = np.loadtxt(ydata_file, delimiter=",")
    ydata = ydata / (2 * 10**6)
else:
    ydata = np.loadtxt(ydata_file, delimiter=",")
ydata = ydata * 1e9
ax.plot(ydata)
ax.set_title("Current - NIDAQ")
#ax.set_xticks(np.arange(-1.5, 2.0, 0.5))
ax.axvline(0, color='k', alpha=0.4)
ax.axhline(0, color='k', alpha=0.4)
ax.tick_params(direction='in')
ax.set_xlabel("Datapoints")
ax.set_ylabel("Current measured by NI in nA")
ax.grid(True)
fig.tight_layout()
plt.show()

#
fig, ax = plt.subplots()
ydata_name = "voltages_eo.csv"
ydata_file: Path = Path(folder_name)/ydata_name
ydata = np.loadtxt(ydata_file, delimiter=",")
ax.plot(ydata)
ax.set_title("Current - SMU 2")
#ax.set_xticks(np.arange(-1.5, 2.0, 0.5))
ax.axvline(0, color='k', alpha=0.4)
ax.axhline(0, color='k', alpha=0.4)
ax.tick_params(direction='in')
ax.set_xlabel("Datapoints")
ax.set_ylabel("Voltage measured by K195 in V")
ax.grid(True)
fig.tight_layout()
plt.show()

# 
fig, ax = plt.subplots()
ydata_name = "voltages_ei.csv"
ydata_file: Path = Path(folder_name)/ydata_name
ydata = np.loadtxt(ydata_file, delimiter=",")
ydata = ydata
ax.plot(ydata)
ax.set_title("Voltage - SMU 1")
#ax.set_xticks(np.arange(-1.5, 2.0, 0.5))
ax.axvline(0, color='k', alpha=0.4)
ax.axhline(0, color='k', alpha=0.4)
ax.tick_params(direction='in')
ax.set_xlabel("Datapoints")
ax.set_ylabel("Voltage provided by SMU in V")
ax.grid(True)
fig.tight_layout()
plt.show()

#
fig, ax = plt.subplots()
y0data_name = "currents_ei.csv"
ydata_name = "currents_ec.csv"
y0data_file: Path = Path(folder_name)/y0data_name
ydata_file: Path = Path(folder_name)/ydata_name
y0data = np.loadtxt(y0data_file, delimiter=",")
ydata = np.loadtxt(ydata_file, delimiter=",")
ydata = ydata / (2 * 10**6)
y0data = y0data * 1e9
ydata = ydata * 1e9
ax.plot(y0data[60:-60] - ydata)
ax.set_title("Current [SMU-NIDAQ]")
#ax.set_xticks(np.arange(-1.5, 2.0, 0.5))
ax.axvline(0, color='k', alpha=0.4)
ax.axhline(0, color='k', alpha=0.4)
ax.tick_params(direction='in')
ax.set_xlabel("Datapoints")
ax.set_ylabel("Current left in the resistor to the K195 in nA")
ax.grid(True)
fig.tight_layout()
plt.show()