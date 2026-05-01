from matplotlib import legend
import matplotlib.pyplot as plt
import numpy as np

def plot_viiv_curve(iv_voltage_file, iv_current_file, vi_current_file, vi_voltage_file):

    
    # Load data (assuming a simple one-column file)
    iv_voltage = np.loadtxt(iv_voltage_file)
    iv_current = np.loadtxt(iv_current_file)
    vi_voltage = np.loadtxt(vi_voltage_file)
    vi_current = np.loadtxt(vi_current_file)
    
    # Plot VI curve
    plt.figure(figsize=(5, 4))
    plt.plot(iv_current[60:-60] * (1e9/2e6), iv_voltage[60:-60], label="Original IV-Curve (I, V swapped)")
    plt.plot(vi_current[60:-60] * (1e9/2e6), vi_voltage[60:-60], label = "VI Curve")
    plt.title("VI Curve of an IV and VI Measurement Run")
    plt.xlabel("Current (nA)")
    plt.ylabel("Voltage (V)")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__=="__main__":

    VOLT_PORT = "VVII"
    plot_viiv_curve(f"plotters/VIIVPlot/IV/RAW_voltages_pad_{VOLT_PORT}.csv",
                    f"plotters/VIIVPlot/IV/RAW_currents_pad_7.csv",
                    f"plotters/VIIVPlot/VI/RAW_currents_pad_7.csv",
                    f"plotters/VIIVPlot/VI/RAW_voltages_pad_{VOLT_PORT}.csv")