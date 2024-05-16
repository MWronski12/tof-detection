import pandas as pd
import sys

if len(sys.argv) != 2:
    print("Usage python3 evaluate_performance.py <csv file>")
    sys.exit(1)

file = sys.argv[1]
print("Data file:", file, end="\n\n")

# Read CSV data into a DataFrame
column_names = ["timestamp", "z1", "z2", "z3", "z4", "z5", "z6", "z7", "z8", "z9"]
df = pd.read_csv(file, names=column_names)

# Calculate mean and standard deviation of a specific column (e.g., 'column_name')
center_zone_col = "z5"  # Replace 'your_center_zone' with the name of the column
center_zone = df[center_zone_col]
center_zone_non_zero = df.loc[df[center_zone_col] != 0, center_zone_col]
periods = df["timestamp"].diff()

data_presence = len(center_zone_non_zero) / len(df)
mean_dist = center_zone_non_zero.mean()
std_dev_dist = center_zone_non_zero.std()
mean_period = periods.mean()
std_dev_period = periods.std()

print(f"Data present: {data_presence:.2%}")
print(f"Mean period: {round(mean_period, 2):.2f} +- {round(std_dev_period, 2):.2f} ms")
print(f"Mean dist: {int(mean_dist)} +- {int(std_dev_dist)} mm")
print(f"Max dist: {center_zone.max()} mm")
