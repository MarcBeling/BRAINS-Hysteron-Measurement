import csv
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import numpy as np
folder = Path("VI_TEST_VOLT_8T_MARTEEN-2026-01-27_16-14-51")

y_files = [
    "currents_ec1.csv",
    "currents_ec2.csv",
    "currents_ec3.csv"
]

import csv
import matplotlib.pyplot as plt
from pathlib import Path

folder = Path("VI_TEST_VOLT_8T_MARTEEN-2026-01-27_16-43-23")

y_files = [f"currents_ec{i}.csv" for i in range(6)]

y_col_index = 0
plt.figure(figsize=(12, 6))

for filename in y_files:
    y_values = []

    with open(folder / filename, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            y_values.append(float(row[y_col_index]))

    x_values = list(range(len(y_values)))  # index as x

    plt.plot(x_values, np.asarray(y_values)*500, label=filename)

plt.xlabel("Index")
plt.ylabel("Y Value")
plt.title("CSV files plotted over index (no headers)")
plt.legend()
plt.grid(True)
plt.show()
