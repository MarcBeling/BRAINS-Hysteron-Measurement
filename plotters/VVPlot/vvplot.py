import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === CONFIGURATION ===
X_KEYWORD = "_IV"     # identifies x‑axis files
Y_KEYWORD = "_VVII"     # identifies y‑axis files

def main():
    # Folder containing this script
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # List all subfolders
    subfolders = [
        f.path for f in os.scandir(base_dir)
        if f.is_dir()
    ]

    if not subfolders:
        print("No subfolders found.")
        return
    
    cmap = plt.get_cmap('rainbow')
    colors = cmap(np.linspace(1, 0, len(subfolders)))

    # Create figure
    fig, ax = plt.subplots(figsize=(5, 4))

    for i, folder in enumerate(subfolders):

        # Find CSVs inside the folder
        csv_files = glob.glob(os.path.join(folder, "*.csv"))

        # Identify x and y files
        x_files = [f for f in csv_files if X_KEYWORD in os.path.basename(f)]
        y_files = [f for f in csv_files if Y_KEYWORD in os.path.basename(f)]

        x_file = x_files[0]
        y_file = y_files[0]

        # Read numeric columns (assumes 1-column CSV)
        x = pd.read_csv(x_file).iloc[:, 0]
        y = pd.read_csv(y_file).iloc[:, 0]

        # Folder name becomes label
        label = os.path.basename(folder)

        color=colors[i]

        if label == "0mV":
            ax.plot(x[60:-60], y[60:-60], label=label, color="k", linewidth=1)
        else:
            ax.plot(x[60:-60], y[60:-60], label=label, color=color, linewidth=1)

    # Plot styling
    ax.set_title("Voltage warping between Source and Voltmeter")
    ax.set_xlabel("Voltage applied at IV in Volt")
    ax.set_ylabel("Voltage measured with Voltmeter at VVII")
    ax.axhline(0, color="k", alpha=0.6)
    ax.axvline(0, color="k", alpha=0.6)

    ax.grid()
    ax.legend(title="Control Voltages")

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()