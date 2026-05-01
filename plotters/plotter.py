import matplotlib.pyplot as plt

def plot_vi_curve(current, voltage, title):

    plt.figure(figsize=(5, 4))
    plt.plot(current, voltage)
    plt.title(title)
    plt.xlabel("Current in nA")
    plt.ylabel("Voltage in V")
    plt.grid(True)
    plt.show()

def plot_iv_curve(voltage, current, title, savename = None):

    plt.figure(figsize=(5, 4))
    plt.plot(voltage, current)
    plt.title(title)
    plt.ylabel("Current in nA")
    plt.xlabel("Voltage in V")
    plt.grid(True)
    plt.tight_layout()
    if savename != None:
        plt.savefig(f"{savename}")
    else:
        plt.show()

def plot_vv_curve(voltage1, voltage2, title, savename = None):

    plt.figure(figsize=(5, 4))
    plt.plot(voltage1, voltage2)
    plt.title(title)
    plt.xlabel("Voltage in V")
    plt.ylabel("Voltage in V")
    plt.grid(True)
    if savename != None:
        plt.savefig(f"{savename}")
    else:
        plt.show()