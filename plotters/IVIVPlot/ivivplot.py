
import matplotlib.pyplot as plt
import numpy as np

# voltage1 = np.loadtxt("plotters/IVIVPlot/NoCV/IV/RAW_voltages_pad_IV.csv")
# current1 = np.loadtxt("plotters/IVIVPlot/NoCV/IV/RAW_currents_pad_7.csv")

# voltage2 = np.loadtxt("plotters/IVIVPlot/NoCV/IVRes/RAW_voltages_pad_IV.csv")
# current2 = np.loadtxt("plotters/IVIVPlot/NoCV/IVRes/RAW_currents_pad_7.csv")

# voltage3 = np.loadtxt("plotters/IVIVPlot/NoCV/IVRes2/RAW_voltages_pad_IV.csv")
# current3 = np.loadtxt("plotters/IVIVPlot/NoCV/IVRes2/RAW_currents_pad_7.csv")

# voltage4 = np.loadtxt("plotters/IVIVPlot/NoCV/IVRes3/RAW_voltages_pad_IV.csv")
# current4 = np.loadtxt("plotters/IVIVPlot/NoCV/IVRes3/RAW_currents_pad_7.csv")

voltage1 = np.loadtxt("plotters/IVIVPlot/-600mV_10MOhm/IV_NoRes/RAW_voltages_pad_IV.csv")
current1 = np.loadtxt("plotters/IVIVPlot/-600mV_10MOhm/IV_NoRes/RAW_currents_pad_7.csv")

voltage2 = np.loadtxt("plotters/IVIVPlot/-600mV_10MOhm/IV/RAW_voltages_pad_IV.csv")
current2 = np.loadtxt("plotters/IVIVPlot/-600mV_10MOhm/IV/RAW_currents_pad_7.csv")

# Plot VI curve
plt.figure(figsize=(5, 4))
plt.plot(voltage1[60:-60], current1[60:-60], label="RNPU 3T, no Resistor")
plt.plot(voltage2[60:-60], current2[60:-60], label="RNPU 3T, with Resistor")
# plt.plot(voltage3[60:-60], current3[60:-60], label="RNPU 2T, with 10MOhm Resistor")
# plt.plot(voltage4[60:-60], current4[60:-60], label="RNPU 2T, with Ohm Resistor")
plt.title("IV Curve of a 2T RNPU with and without 10MOhm Resistor and -600mV")
plt.xlabel("Voltage (V)")
plt.ylabel("Current (nA)")
plt.grid(True)
plt.axhline(0, color='k', alpha=0.4)
plt.axvline(0, color='k', alpha=0.4)
plt.legend()
plt.show()