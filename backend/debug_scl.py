import rasterio
import numpy as np

with rasterio.open("../datasets/hyderabad/SCL_20m.jp2") as src:
    scl = src.read(1)

values, counts = np.unique(scl, return_counts=True)

print("SCL Value Distribution")
print("----------------------")

for value, count in zip(values, counts):
    percentage = (count / scl.size) * 100
    print(f"{value:2d} : {percentage:.2f}%")