import numpy as np
from pathlib import Path
import sys
import matplotlib.pyplot as plt

def plot(xdata_name, ydata_name, folder_name='', type="IV", title=""):

    xdata_file: Path = Path(folder_name)/xdata_name
    ydata_file: Path = Path(folder_name)/ydata_name

    xdata = np.loadtxt(xdata_file, delimiter=",")
    ydata = np.loadtxt(ydata_file, delimiter=",")

    fig, ax = plt.subplots()

    if type == "IV":
        ydata = ydata / (2 * 10**6)
        ydata = ydata * 1e9  # A -> nA

        ax.set_xlabel("Voltage in V applied at $e_i$")
        ax.set_ylabel("Current in nA measured at $e_o$")

        ax.set_xticks(np.arange(-1.5, 2.0, 0.5))

        ax.axvline(0, color='k', alpha=0.4)
        ax.axhline(0, color='k', alpha=0.4)
        #ax.axhline(0, color='k', alpha=0.4)
        #ax.axhspan(-50, -40, color='lightblue', alpha=0.3, label="Hysterisis effect")
        ax.plot(xdata[60:-60], ydata, label="IV Curve RNPU @ -300mV")
        ax.set_title(title)
        ax.tick_params(direction='in')
        ax.grid(True)
        ax.legend()
        fig.tight_layout()

    elif type == "VI":
        xdata = xdata * 1e9
        ax.set_xlabel("Current in nA applied at $e_i$")
        ax.set_ylabel("Voltage in V measured at $e_i \\rightarrow$GND")

        ax.axvline(0, color='k', alpha=0.4)
        ax.axhline(0, color='k', alpha=0.4)
        #ax.axvspan(-50, -40, color='lightblue', alpha=0.3, label="Hysterisis effect")
        ax.plot(xdata[60:-60], ydata, label="VI Curve RNPU @ 0mV")
        ax.set_title(title)
        ax.tick_params(direction='in')
        ax.grid(True)
        ax.legend()
        fig.tight_layout()

    elif type == "1-1":
        ax.set_xlabel(xdata_name)
        ax.set_ylabel(ydata_name)

        ax.axvline(0, color='k', alpha=0.4)
        ax.axhline(0, color='k', alpha=0.4)
        ax.plot(xdata, ydata)
        ax.set_title(title)
        ax.tick_params(direction='in')
        ax.grid(True)
        ax.legend()
        fig.tight_layout()       

    plt.show()

if __name__ == "__main__":
    
    if len(sys.argv) > 4:
        plot(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "")