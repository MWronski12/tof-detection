from typing import Callable, Tuple, Optional
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


DistanceSelectionStrategy = Callable[[pd.Series], pd.Int64Dtype]


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


class MonotonicSeries:
    def __init__(self, samples: list[Tuple[int, int]]) -> None:
        self._samples = samples
        self._validate_monotonicity()

        self.time_start = samples[0][0]
        self.time_end = samples[-1][0]
        self.time_total = self.time_end - self.time_start

        self.dist_start = samples[0][1]
        self.dist_end = samples[-1][1]
        self.dist_avg = sum(dist for _, dist in samples) / len(samples)

        self.direction = 1 if self.dist_end > self.dist_start else -1
        self.velocity = self._calculate_avg_velocity()

    def __len__(self) -> int:
        return len(self._samples)

    def _validate_monotonicity(self) -> None:
        if len(self._samples) < 2:
            raise ValueError("Series must have at least 2 samples")

        direction = self._samples[1] > self._samples[0]
        for i in range(1, len(self._samples)):
            if (self._samples[i] > self._samples[i - 1]) != direction:
                raise ValueError("Monotonicity violated")

    def _calculate_avg_velocity(self) -> float:
        velocities = []
        for i in range(1, len(self._samples)):
            t1, d1 = self._samples[i - 1]
            t2, d2 = self._samples[i]

            dt = t2 - t1
            dd = d2 - d1

            if (dt == 0) or (d2**2 - DIST_TO_PATH**2 <= 0):
                print("WARNING: Zero division would occur, skipping sample")
                continue

            velocity = d2 / np.sqrt(d2**2 - DIST_TO_PATH**2) * dd / dt * 3.6
            velocities.append(velocity)

        if np.std(velocities) > 5:
            print(f"WARNING: High velocity standard deviation: " f"{np.mean(velocities)} +- {np.std(velocities)} kmh")

        return abs(sum(velocities) / len(velocities))


def split_to_non_zero_monotonic_series(samples: list[Tuple[int, int]], min_samples=1) -> list[list[Tuple[int, int]]]:

    def skip_to_next_motion(i) -> int:
        while i < len(samples) and samples[i][1] == -1:
            i += 1

        return i

    def flush(result: list[list[Tuple[int, int]]], start: int, end: int) -> None:
        series = samples[start:end]
        if len(series) >= min_samples:
            result.append(series)

    result = []
    prev_direction = None
    i = skip_to_next_motion(0)
    j = i + 1

    while j < len(samples):
        if samples[j][1] != -1:
            direction = samples[j][1] > samples[j - 1][1]

            if prev_direction == None:
                prev_direction = direction

            elif prev_direction != direction:
                flush(result, i, j)
                prev_direction = None
                i = j

            j += 1

        elif samples[j][1] == -1:
            flush(result, i, j)
            prev_direction = None
            i = skip_to_next_motion(j)
            j = i + 1

    flush(result, i, j)

    return result


def partition_center_zone_distance_measurements(df: pd.DataFrame, min_samples: int = 2) -> list[MonotonicSeries]:
    samples = df[["timestamp_ms", f"zone{CENTER_ZONE_IDX}_distance"]].values.tolist()
    series = split_to_non_zero_monotonic_series(samples, min_samples=min_samples)
    return [MonotonicSeries(s) for s in series]


# ------------ MERGE ADJECENT MONOTONIC SERIES INTO MOTION OBJECTS ----------- #


class Motion:
    def __init__(self, series: list[MonotonicSeries], max_time_delta_ms: int = 100) -> None:
        self._monotonic_series = series
        self._max_time_delta_ms = max_time_delta_ms
        self._validate_series()

        self.num_series = len(series)
        self.num_samples_total = sum(len(series) for series in series)

        self.time_start = series[0].time_start
        self.time_end = series[-1].time_end
        self.time_total = self.time_end - self.time_start

        self.dist_start = series[0].dist_start
        self.dist_end = series[-1].dist_end
        self.dist_avg = sum(series.dist_avg for series in series) / len(series)

        self.direction = series[0].direction
        self.velocity = sum(series.velocity for series in series) / len(series)

    def _validate_series(self) -> None:
        if len(self._monotonic_series) < 1:
            raise ValueError("Empty list of series")

        if not all(s.direction == self._monotonic_series[0].direction for s in self._monotonic_series):
            print("WARNING: Series must have the same direction")

        for i in range(1, len(self._monotonic_series)):
            if (
                self._monotonic_series[i].time_start - self._monotonic_series[i - 1].time_end
            ) > self._max_time_delta_ms:
                raise ValueError("Series must be adjacent")


def merge_adjecent_series(series: list[MonotonicSeries], max_time_delta_ms: int = 100) -> list[Motion]:
    results: list[Motion] = []
    temp: list[MonotonicSeries] = []

    for s in series:
        if len(temp) != 0:
            if abs(s.time_start - temp[-1].time_end) > max_time_delta_ms:
                results.append(Motion(temp, max_time_delta_ms))
                temp = []

        temp.append(s)

    return results


# --------------------------- PREPARE TRAINING DATA -------------------------- #


def extract_motions(
    tmf8828_data: pd.DataFrame,
    distStrategy: DistanceSelectionStrategy = confidence_strategy,
    min_samples=2,
    max_series_delta_time_ms=100,
) -> list[Motion]:
    zone_distance = select_center_zone_distance(tmf8828_data, strategy=distStrategy)
    partitioned_data = partition_center_zone_distance_measurements(zone_distance, min_samples=min_samples)
    motions = merge_adjecent_series(partitioned_data, max_time_delta_ms=max_series_delta_time_ms)

    return motions


# Maps gps, video velocities to single velocity
VelocityLabelStrategy = Callable[[float, float], float]

gps_strategy = lambda gps_v, _: gps_v
video_strategy = lambda _, video_v: video_v
average_strategy = lambda gps_v, video_v: (gps_v + video_v) / 2


def find_matching_velocity_label(motion: Motion, velocity_labels: pd.DataFrame) -> Optional[Tuple[int, float, float]]:
    idx = (velocity_labels["timestamp_ms"] - motion.time_start).abs().idxmin()
    row = velocity_labels.loc[idx, ["timestamp_ms", "gps_velocity_kmh", "video_velocity_kmh"]]
    if abs(row["timestamp_ms"] - motion.time_start) > 5000:
        print("WARNING: No matching velocity label found")
        return None

    return tuple(row.values)


def prepare_labeled_data(
    tmf8828_data: pd.DataFrame,
    velocity_labels: pd.DataFrame,
    distStrategy: DistanceSelectionStrategy = confidence_strategy,
    velocityLabelStrategy: VelocityLabelStrategy = video_strategy,
    min_samples=2,
    max_series_delta_time_ms=100,
) -> Tuple[list[Motion], list[float]]:

    motions = extract_motions(
        tmf8828_data,
        distStrategy=distStrategy,
        min_samples=min_samples,
        max_series_delta_time_ms=max_series_delta_time_ms,
    )

    labels = [find_matching_velocity_label(motion, velocity_labels) for motion in motions]
    labels = [velocityLabelStrategy(label[1], label[2]) if label is not None else None for label in labels]

    filtered_motions = []
    filtered_labels = []

    for motion, label in zip(motions, labels):
        if label is not None:
            filtered_motions.append(motion)
            filtered_labels.append(label)
        else:
            print(f"WARNING: Skipping motion with no matching velocity label: {motion.time_start}")

    return filtered_motions, filtered_labels


# ----------------------------------- PLOT ----------------------------------- #

from matplotlib import pyplot as plt


def plot(X: list[Motion], y: list[float]) -> None:

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

    for motion in X:
        for series in motion._monotonic_series:
            timestamps = [sample[0] for sample in series._samples]
            distances = [sample[1] for sample in series._samples]

            color = "red" if series.direction == 1 else "blue"
            label = "Approaching" if color == "red" else "Moving away"

            ax1.scatter(timestamps, distances, color="black", s=5)
            ax1.plot(timestamps, distances, color=color, label=label)

        ax2.scatter(series.time_end, motion.velocity, color="green", s=5, label="Estimated motion velocity")
        ax2.set_ylim([0, 30])

    ax3.scatter([motion.time_end for motion in X], y, color="purple", s=5, label="Real motion velocity")
    ax3.set_ylim([0, 30])

    # Collect labels and handles and remove duplicates
    handles, labels = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    handles3, labels3 = ax3.get_legend_handles_labels()
    by_label = dict(zip(labels + labels2 + labels3, handles + handles2 + handles3))
    fig.legend(by_label.values(), by_label.keys())

    plt.show()


# ----------------------------------- MAIN ----------------------------------- #


def main():
    args = parse_args()
    tmf8828_data = load_tmf8828_data(args.data)
    print(tmf8828_data.head())

    velocity_labels = load_velocity_labels(args.labels)
    print(velocity_labels.head())

    X, y = prepare_labeled_data(tmf8828_data, velocity_labels, min_samples=5, velocityLabelStrategy=gps_strategy)
    assert len(X) == len(y)
    print("Data set size:", len(X))

    plot(X, y)


if __name__ == "__main__":
    main()
