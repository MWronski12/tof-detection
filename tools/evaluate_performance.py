import pandas as pd
import sys

# ---------------------------------------------------------------------------- #

if len(sys.argv) != 2:
    print("Usage python3 evaluate_performance.py <csv file>")
    sys.exit(1)

file = sys.argv[1]
print("Data file:", file, end="\n\n")


# ---------------------------------------------------------------------------- #

NUM_ZONES = 9
NUM_TARGETS = 2
CENTER_ZONE = 5


make_confidence_distance_pair = lambda zone_idx, target_idx: (
    f"zone{zone_idx}_conf{target_idx}",
    f"zone{zone_idx}_dist{target_idx}",
)

distance_columns = [
    col
    for pair in [make_confidence_distance_pair(z, t) for z in range(1, NUM_ZONES + 1) for t in range(NUM_TARGETS)]
    for col in pair
]

dtypes = {
    "timestamp": "int64",
    "ambient_light": "int16",
    **{col: "int16" for col in distance_columns},
}


df = pd.read_csv(
    file,
    sep=",",
    names=["timestamp", "ambient_light", *distance_columns],
    index_col="timestamp",
    dtype=dtypes,
)

df.drop(["ambient_light"], axis=1, inplace=True)

df.replace(-1, pd.NA, inplace=True)

confidence_columns = df.filter(regex="zone[0-9]*_conf[0-9]*").columns
df[confidence_columns] = df[confidence_columns].apply(lambda confidence: confidence / 255.0)


# ---------------------------------------------------------------------------- #


zone_data = lambda zone_idx: df.filter(like=f"zone{zone_idx}")


def unpack_zone_data(row):
    conf_target1 = row.iloc[0]
    dist_target1 = row.iloc[1]
    conf_target2 = row.iloc[2]
    dist_target2 = row.iloc[3]

    return conf_target1, dist_target1, conf_target2, dist_target2


def confidence_strategy(row):
    conf_target1, dist_target1, conf_target2, dist_target2 = unpack_zone_data(row)

    if pd.isna(conf_target1) and pd.isna(conf_target2):
        return pd.NA

    if pd.isna(conf_target1):
        return dist_target2

    if pd.isna(conf_target2):
        return dist_target1

    return dist_target1 if conf_target1 >= conf_target2 else dist_target2


def mean_strategy(row):
    conf_target1, dist_target1, conf_target2, dist_target2 = unpack_zone_data(row)

    if pd.isna(conf_target1) and pd.isna(conf_target2):
        return pd.NA

    if pd.isna(conf_target1):
        return dist_target2

    if pd.isna(conf_target2):
        return dist_target1

    return (dist_target1 + dist_target2) / 2


def weighted_mean_strategy(row):
    conf_target1, dist_target1, conf_target2, dist_target2 = unpack_zone_data(row)

    if pd.isna(conf_target1) and pd.isna(conf_target2):
        return pd.NA

    if pd.isna(conf_target1):
        return dist_target2

    if pd.isna(conf_target2):
        return dist_target1

    return (conf_target1 * dist_target1 + conf_target2 * dist_target2) / (conf_target1 + conf_target2)


def target0_strategy(row):
    _, dist_target1, _, _ = unpack_zone_data(row)

    return dist_target1

# ---------------------------------------------------------------------------- #

import numpy as np

strategy = weighted_mean_strategy
zone = CENTER_ZONE
a = 1300

df["d"] = zone_data(zone).apply(strategy, axis=1)
df["dt"] = df.index.to_series().diff()
df["dd"] = df["d"].diff()

df["velocity"] = df.apply(
    lambda row: (
        (row["d"] / np.sqrt(row["d"] ** 2 - a**2)) * (row["dd"] / row["dt"]) * 3.6
        if not pd.isna(row["d"]) and not pd.isna(row["dd"]) and not pd.isna(row["dt"]) and row["d"] ** 2 - a**2 > 0
        else pd.NA
    ),
    axis=1,
)

print(f"Mean dt: {df['dt'].mean()} +- {df['dt'].std()} [{df['dt'].min()} - {df['dt'].max()}]")

# ---------------------------------------------------------------------------- #

# import matplotlib.pyplot as plt


# x = df.index - df.index.min()
# y1 = df["d"].replace(pd.NA, 0)
# y2 = df["velocity"].replace(pd.NA, 0)

# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 10))
# ax1.scatter(x, y1, c="orange")
# ax2.scatter(x, y2, c="blue")

# plt.show()
