from typing import Callable, Tuple
from utils import split_to_non_zero_monotonic_series
from config import COLUMNS, CENTER_ZONE_IDX, DIST_TO_PATH
import pandas as pd
import numpy as np
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
        required=True,
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


# ----------------------------- ESTIMATE VELOCITY ---------------------------- #


def estimate_velocity(series: list[Tuple[int, int]]) -> Tuple[int, float]:
    velocities = []

    for i in range(1, len(series)):
        s1 = series[i - 1]
        s2 = series[i]

        dt = s2[0] - s1[0]
        if dt == 0:
            continue

        dd = s2[1] - s1[1]

        velocity = s2[1] / np.sqrt(s2[1] ** 2 - DIST_TO_PATH**2) * dd / dt * 3.6
        velocities.append(velocity)

    return series[-1][0], abs(sum(velocities) / len(velocities))


def merge_adjecent_velocities(data: list[Tuple[int, float]]) -> list[Tuple[int, float]]:
    results = []
    temp = []

    for timestamp_ms, velocity_kmh in data:
        if len(temp) != 0:
            if abs(timestamp_ms - temp[-1][0]) > 1000:
                t = temp[-1][0]
                v = sum(velocity for _, velocity in temp) / len(temp)
                results.append((t, v))
                temp = []

        temp.append((timestamp_ms, velocity_kmh))

    return results


def estimate_velocities(partitioned_data: list[list[Tuple[int, int]]]) -> list[Tuple[int, float]]:
    results = [estimate_velocity(series) for series in partitioned_data]
    results = merge_adjecent_velocities(results)
    return results


# ----------------------------------- PLOT ----------------------------------- #

from matplotlib import pyplot as plt


def plot(partitioned_data: list[list[Tuple[int, int]]], velocity_labels: list[Tuple[int, float, float]]) -> None:
    velocities = estimate_velocities(partitioned_data)

    fig, ax1 = plt.subplots()

    for sequence in partitioned_data:
        timestamps = [sample[0] for sample in sequence]
        distances = [sample[1] for sample in sequence]

        color = "red" if distances[-1] < distances[0] else "blue"
        label = "Approaching" if color == "red" else "Moving away"

        ax1.scatter(timestamps, distances, color="black", s=5)
        ax1.plot(timestamps, distances, color=color, label=label)

    ax2 = ax1.twinx()  # Create a second y-axis for the velocities
    ax2.set_ylabel("Velocity (km/h)", color="green")  # Label for the velocity y-axis
    ax2.tick_params(axis="y", labelcolor="green")  # Set the color of the velocity y-axis ticks

    # Plot each velocity sample with a label
    for t, v in velocities:
        ax2.plot(t, v, "ro", label="Estimated velocity", markersize=4)  # 'go' for green circles

    # Plot GPS and video velocities with different markers
    for t, gps_v, video_v in velocity_labels:
        ax2.plot(t, gps_v, "gs", label="GPS velocity", markersize=4)  # 'rs' for red squares
        ax2.plot(t, video_v, "gs", label="Video velocity", markersize=4)  # 'bs' for blue squares

    # Update the legend to include new markers
    # Collect labels and handles and remove duplicates
    handles, labels = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    by_label = dict(zip(labels + labels2, handles + handles2))
    ax2.legend(by_label.values(), by_label.keys(), loc="upper left")

    fig.tight_layout()  # Adjust the layout to make room for the second y-axis
    plt.show()


# ----------------------------------- MAIN ----------------------------------- #


def main():
    args = parse_args()
    tmf8828_data = load_tmf8828_data(args.data)
    print(tmf8828_data.head())

    velocity_labels = load_velocity_labels(args.labels)
    print(velocity_labels.head())

    zone_distance = select_center_zone_distance(tmf8828_data, confidence_strategy)
    partitioned_data = partition_center_zone_distance_measurements(zone_distance, min_samples=2)

    plot(partitioned_data, velocity_labels.values.tolist())
    plt.show()


if __name__ == "__main__":
    main()
