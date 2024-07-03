from typing import Callable, Tuple
from utils import split_to_non_zero_monotonic_series
from config import COLUMNS, CENTER_ZONE_IDX
import pandas as pd
import argparse

# ----------------------------------- ARGS ----------------------------------- #


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Script for visualizing velocity labels from GPS and video.",
    )
    parser.add_argument(
        "--data",
        required=True,
        type=str,
        help="Path of the tmf8828 data CSV file",
    )
    parser.add_argument(
        "--labels",
        # required=True,
        type=str,
        help="Path of the velocity labels CSV file",
    )
    return parser.parse_args()


# --------------------------------- LOAD DATA -------------------------------- #


def load_tmf8828_data(file: str) -> pd.DataFrame:
    return pd.read_csv(
        file,
        sep=",",
        names=COLUMNS,
    ).drop(columns=["ambient_light"])


def load_velocity_labels(file: str) -> pd.DataFrame:
    return pd.read_csv(file, names=["timestamp_ms", "gps_velocity_kmh", "video_velocity_kmh"], skiprows=1)


# --------------------- APPLY DISTANCE SELECTION STRATEGY -------------------- #


def confidence_strategy(zone_data: pd.Series) -> pd.Int64Dtype:
    conf0, dist0, conf1, dist1 = zone_data
    return dist0 if conf0 >= conf1 else dist1


def target_0_strategy(zone_data: pd.Series) -> pd.Int64Dtype:
    _, dist0, _, _ = zone_data
    return dist0


def select_center_zone_distance(df: pd.DataFrame, strategy: Callable[[pd.Series], pd.Int64Dtype]) -> pd.Series:
    select_zone_data = lambda zone_idx: df.filter(like=f"zone{zone_idx}")
    zone_data = select_zone_data(CENTER_ZONE_IDX)
    df[f"zone{CENTER_ZONE_IDX}_distance"] = zone_data.apply(strategy, axis=1)
    return df


# ------ PARTITION DISTANCE MEASUREMENTS INTO NON-ZERO MONOTONIC SERIES ------ #


def partition_center_zone_distance_measurements(df: pd.DataFrame, min_samples: int = 0) -> list[list[Tuple[int, int]]]:
    samples = df[["timestamp_ms", f"zone{CENTER_ZONE_IDX}_distance"]].values.tolist()
    return split_to_non_zero_monotonic_series(samples, min_samples=min_samples)


# ----------------------------------- PLOT ----------------------------------- #


def plot(partitioned_data: list[list[Tuple[int, int]]]) -> None:

    for sequence in partitioned_data:
        timestamps = []
        distances = []

        for sample in sequence:
            timestamps.append(sample[0])
            distances.append(sample[1])

        color = "red" if distances[-1] < distances[0] else "blue"
        label = "Approaching" if color == "red" else "Moving away"

        plt.scatter(timestamps, distances, color="black", s=5)
        plt.plot(timestamps, distances, color=color, label=label)

    # This ensures that each label is only added once to the legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())


# ----------------------------------- MAIN ----------------------------------- #

from matplotlib import pyplot as plt


def main():
    args = parse_args()
    print(args)
    tmf8828_data = load_tmf8828_data(args.data)
    print(tmf8828_data.head())

    # velocity_labels = load_velocity_labels(args.labels)
    # print(velocity_labels.head())

    zone_distance = select_center_zone_distance(tmf8828_data, target_0_strategy)
    partitioned_data = partition_center_zone_distance_measurements(zone_distance, min_samples=3)

    plot(partitioned_data)
    plt.show()


if __name__ == "__main__":
    main()
