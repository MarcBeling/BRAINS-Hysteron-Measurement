
import matplotlib.pyplot as plt
import numpy as np

foldername1 = "IV_RNPU_1000mV_Reversed_Resistor_150Ohm-10-03-2026_13-56-35"
foldername2 = "IV_RNPU_1000mV_Reversed_NoResistor-10-03-2026_14-01-31"
foldername3 = "IV_RNPU_1000mV_Reversed_180k-10-03-2026_14-08-49"
foldername4 = "IV_RNPU_1000mV_Reversed_1500k-10-03-2026_14-16-34"

voltage1 = np.loadtxt(f"output/10-03-2026/{foldername1}/data/voltages_7.csv")
current1 = np.loadtxt(f"output/10-03-2026/{foldername1}/data/currents_IV.csv")

voltage2 = np.loadtxt(f"output/10-03-2026/{foldername2}/data/voltages_7.csv")
current2 = np.loadtxt(f"output/10-03-2026/{foldername2}/data/currents_IV.csv")

voltage3 = np.loadtxt(f"output/10-03-2026/{foldername3}/data/voltages_7.csv")
current3 = np.loadtxt(f"output/10-03-2026/{foldername3}/data/currents_IV.csv")

voltage4 = np.loadtxt(f"output/10-03-2026/{foldername4}/data/voltages_7.csv")
current4 = np.loadtxt(f"output/10-03-2026/{foldername4}/data/currents_IV.csv")

# Plot VI curve
plt.figure(figsize=(5, 4))

plt.plot(voltage2[60:-60], -current2[60:-60]*1e9, label="IV-Curve of RNPU with no resistor")
plt.plot(voltage1[60:-60], -current1[60:-60]*1e9, label="IV-Curve of RNPU with 150 resistor")
plt.plot(voltage3[60:-60], -current3[60:-60]*1e9, label="IV-Curve of RNPU with 180k resistor")
plt.plot(voltage4[60:-60], -current4[60:-60]*1e9, label="IV-Curve of RNPU with 1.5M resistor")
plt.title("IV Curve of a 4T RNPU with different Resistances")
plt.xlabel("Voltage @ Pad 7 in V")
plt.ylabel("Current @ SMU in nA")
plt.grid(True)
plt.axhline(0, color='k', alpha=0.4)
plt.axvline(0, color='k', alpha=0.4)
plt.legend()
plt.show()