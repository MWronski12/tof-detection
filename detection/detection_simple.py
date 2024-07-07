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


def split_to_non_zero_monotonic_series(
    samples: list[Tuple[int, int]],
    min_samples: int,
    max_dd: int,
) -> list[list[Tuple[int, int]]]:

    def skip_to_next_motion(i) -> int:
        while i < len(samples) and samples[i][1] == -1:
            i += 1

        return i

    def flush(result: list[list[Tuple[int, int]]], start: int, end: int) -> None:
        series = samples[start:end]
        if (
            all(abs(series[i][1] - series[i - 1][1]) < max_dd for i in range(1, len(series)))
            and len(series) >= min_samples
        ):
            result.append(series)

    result = []
    prev_direction = None
    i = skip_to_next_motion(0)
    j = i + 1

    while j < len(samples):
        if samples[j][1] == -1:
            flush(result, i, j)
            prev_direction = None
            i = skip_to_next_motion(j)
            j = i + 1

        else:
            direction = samples[j][1] > samples[j - 1][1]

            if prev_direction == None:
                prev_direction = direction

            elif prev_direction != direction:
                flush(result, i, j)
                prev_direction = None
                i = j

            j += 1

    flush(result, i, j)

    return result


def partition_center_zone_distance_measurements(
    df: pd.DataFrame, min_samples: int, max_dd: int
) -> list[MonotonicSeries]:
    samples = df[["timestamp_ms", f"zone{CENTER_ZONE_IDX}_distance"]].values.tolist()
    series = split_to_non_zero_monotonic_series(samples, min_samples=min_samples, max_dd=max_dd)
    return [MonotonicSeries(s) for s in series]


# ------------ MERGE ADJECENT MONOTONIC SERIES INTO MOTION OBJECTS ----------- #


class Motion:
    def __init__(self, series: list[MonotonicSeries], max_time_delta_ms: int) -> None:
        self._validate_series(series, max_time_delta_ms)
        series = self._filter_opposite_directions(series)
        self._monotonic_series = series

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

    def _filter_opposite_directions(self, series: list[MonotonicSeries]) -> list[MonotonicSeries]:
        longest_series = max(series, key=lambda s: len(s))
        return [s for s in series if s.direction == longest_series.direction]

    def _validate_series(self, series: list[MonotonicSeries], max_time_delta_ms: int) -> None:
        if len(series) < 1:
            raise ValueError("Empty list of series")

        if not all(s.direction == series[0].direction for s in series):
            print("WARNING: Series must have the same direction")

        for i in range(1, len(series)):
            if (series[i].time_start - series[i - 1].time_end) > max_time_delta_ms:
                raise ValueError("Series must be adjacent")


def merge_adjecent_series(series: list[MonotonicSeries], max_time_delta_ms: int) -> list[Motion]:
    results: list[Motion] = []
    temp: list[MonotonicSeries] = []

    for s in series:
        if len(temp) != 0:
            if abs(s.time_start - temp[-1].time_end) > max_time_delta_ms:
                results.append(Motion(temp, max_time_delta_ms))
                temp = []

        temp.append(s)

    if len(temp) != 0:
        results.append(Motion(temp, max_time_delta_ms))

    return results


# --------------------------- PREPARE TRAINING DATA -------------------------- #


def extract_motions(
    tmf8828_data: pd.DataFrame,
    distStrategy: DistanceSelectionStrategy,
    min_samples: int,
    max_dd: int,
    max_series_delta_time_ms: int,
) -> list[Motion]:
    zone_distance = select_center_zone_distance(tmf8828_data, strategy=distStrategy)
    partitioned_data = partition_center_zone_distance_measurements(
        zone_distance, min_samples=min_samples, max_dd=max_dd
    )
    motions = merge_adjecent_series(partitioned_data, max_time_delta_ms=max_series_delta_time_ms)
    return motions


# Maps gps, video velocities to single velocity
VelocityLabelStrategy = Callable[[float, float], float]

gps_strategy = lambda gps_v, _: gps_v
video_strategy = lambda _, video_v: video_v
average_strategy = lambda gps_v, video_v: (gps_v + video_v) / 2


def find_matching_velocity_label(
    motion: Motion, velocity_labels: pd.DataFrame, max_delta_time_ms: int
) -> Optional[Tuple[int, float, float]]:
    idx = (velocity_labels["timestamp_ms"] - motion.time_start).abs().idxmin()
    row = velocity_labels.loc[idx, ["timestamp_ms", "gps_velocity_kmh", "video_velocity_kmh"]]
    if abs(row["timestamp_ms"] - motion.time_start) > max_delta_time_ms:
        print("WARNING: No matching velocity label found")
        return None

    return tuple(row.values)


def prepare_labeled_data(
    tmf8828_data: pd.DataFrame,
    velocity_labels: pd.DataFrame,
    distStrategy: DistanceSelectionStrategy = confidence_strategy,
    velocityLabelStrategy: VelocityLabelStrategy = video_strategy,
    min_samples=2,
    max_dd=200,
    max_series_delta_time_ms=500,
    max_label_delta_time_ms=1500,
) -> Tuple[list[Motion], list[float]]:

    motions = extract_motions(
        tmf8828_data,
        distStrategy=distStrategy,
        min_samples=min_samples,
        max_dd=max_dd,
        max_series_delta_time_ms=max_series_delta_time_ms,
    )

    labels = [find_matching_velocity_label(motion, velocity_labels, max_label_delta_time_ms) for motion in motions]
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

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    for motion in X:
        for series in motion._monotonic_series:
            timestamps = [sample[0] for sample in series._samples]
            distances = [sample[1] for sample in series._samples]

            color = "red" if series.direction == 1 else "blue"
            label = "Approaching" if color == "red" else "Moving away"

            ax1.scatter(timestamps, distances, color="black", s=5)
            ax1.plot(timestamps, distances, color=color, label=label)

    ax2.scatter(
        [motion.time_end for motion in X],
        [motion.velocity for motion in X],
        color="green",
        s=5,
        label="Real motion velocity",
    )
    ax2.plot([motion.time_end for motion in X], [motion.velocity for motion in X], color="green")

    ax2.scatter([motion.time_end for motion in X], y, color="purple", s=5, label="Estimated motion velocity")
    ax2.plot([motion.time_end for motion in X], y, color="purple")

    # Collect labels and handles and remove duplicates
    handles, labels = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    by_label = dict(zip(labels + labels2, handles + handles2))
    fig.legend(by_label.values(), by_label.keys())

    plt.show()


# ----------------------------------- MAIN ----------------------------------- #

from sklearn.model_selection import KFold
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split


def ml_solution():
    args = parse_args()
    tmf8828_data = load_tmf8828_data(args.data)
    print(tmf8828_data.head())

    velocity_labels = load_velocity_labels(args.labels)
    print(velocity_labels.head())

    X, y = prepare_labeled_data(
        tmf8828_data,
        velocity_labels,
        distStrategy=confidence_strategy,
        velocityLabelStrategy=video_strategy,
        min_samples=2,
        max_dd=200,
        max_series_delta_time_ms=1000,
        max_label_delta_time_ms=2000,
    )
    X = [[m.time_total, m.dist_avg, m.direction, m.velocity] for m in X]
    X, y = np.array(X), np.array(y)
    print("Detection percentage:", len(X) / len(velocity_labels) * 100, "%")

    n_splits = 5
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

    mae_scores = []
    for train_index, test_index in kf.split(X):
        # Splitting the data for this fold
        X_train, X_test = [X[i] for i in train_index], [X[i] for i in test_index]
        y_train, y_test = y[train_index], y[test_index]

        # Initialize and fit the model
        model = LinearRegression()
        # model = Lasso()
        # model = Ridge()
        # model = ElasticNet()
        # model = RandomForestRegressor()
        # model = SVR()
        model.fit(X_train, y_train)

        # Make predictions and evaluate
        y_pred = model.predict(X_test)
        mae = sum(abs((y_pred - y_test) / y_test)) / len(y_pred)
        mae_scores.append(mae)

    # Calculate and print the average MAE across all folds
    average_mae = sum(mae_scores) / n_splits
    average_velocity = sum(y) / len(y)
    print(f"Average velocity: {average_velocity}")
    print(f"Average MAE across {n_splits} folds: {average_mae}")


def algorithmic_solution():
    args = parse_args()
    tmf8828_data = load_tmf8828_data(args.data)
    print(tmf8828_data.head())

    velocity_labels = load_velocity_labels(args.labels)
    print(velocity_labels.head())

    X, y = prepare_labeled_data(
        tmf8828_data,
        velocity_labels,
        distStrategy=confidence_strategy,
        velocityLabelStrategy=gps_strategy,
        min_samples=2,
        max_dd=200,
        max_series_delta_time_ms=1000,
        max_label_delta_time_ms=2000,
    )

    X, y = np.array(X), np.array(y)

    print("Detection percentage:", len(X) / len(velocity_labels) * 100, "%")

    average_velocity = sum(y) / len(y)
    print(f"Average velocity: {average_velocity}")
    print(
        "MAE:",
        (
            sum([abs((motion.velocity - velocity_label) / velocity_label) for motion, velocity_label in zip(X, y)])
            / len(X)
        ),
    )

    plot(X, y)


def main():
    ml_solution()
    # algorithmic_solution()


if __name__ == "__main__":
    main()
