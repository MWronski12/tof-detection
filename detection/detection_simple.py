from config import COLUMNS, CENTER_ZONE_IDX

from typing import Callable

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
        index_col="timestamp",
    )


def load_velocity_labels(file: str) -> pd.DataFrame:
    return pd.read_csv(file, names=["timestamp_ms", "gps_velocity_kmh", "video_velocity_kmh"], skiprows=1)


# ------------------------------ TRANSFORM DATA ------------------------------ #


def confidence_strategy(zone_data: pd.Series) -> pd.Int64Dtype:
    conf0, dist0, conf1, dist1 = zone_data
    return dist0 if conf0 >= conf1 else dist1


def normalize_confidence(df: pd.DataFrame) -> pd.Int64Dtype:
    confidence_columns = df.filter(regex="zone[0-9]*_conf[0-9]*").columns
    return df[confidence_columns].apply(lambda confidence: confidence / 255.0)


def get_center_zone_distance_data(df: pd.DataFrame, strategy: Callable[[pd.Series], pd.Int64Dtype]) -> pd.DataFrame:
    zone_data = lambda zone_idx: df.filter(like=f"zone{zone_idx}")
    center_zone_data = zone_data(CENTER_ZONE_IDX)
    return center_zone_data.apply(strategy, axis=1)


# -------------------------- APPLY SPEED ESTIMATION -------------------------- #


# ----------------------------------- MAIN ----------------------------------- #


def main():
    args = parse_args()
    tmf8828_data = load_tmf8828_data(args.data)
    velocity_labels = load_velocity_labels(args.labels)

    df = get_center_zone_distance_data(tmf8828_data, confidence_strategy)
    print(df.info())
    print(df.describe())
    print(df.head())


if __name__ == "__main__":
    main()
