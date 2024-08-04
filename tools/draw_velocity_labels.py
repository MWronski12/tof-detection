from matplotlib import pyplot as plt

import pandas as pd
import numpy as np

import argparse


def parse_args() -> None:
    parser = argparse.ArgumentParser(
        description="Script for visualizing velocity labels from GPS and video.",
    )
    parser.add_argument(
        "file",
        type=str,
        help="Path of the velocity labels CSV file",
    )
    return parser.parse_args()


def load_data(file: str) -> pd.DataFrame:
    df = pd.read_csv(file, names=["timestamp_ms", "gps_velocity_kmh", "video_velocity_kmh"], skiprows=1)
    print(df.describe())
    return df


def plot_velocity_labels(df: pd.DataFrame) -> None:
    bar_width = 0.35
    indices = np.arange(len(df))
    gps_positions = indices - bar_width / 2
    video_positions = indices + bar_width / 2

    # Plot bars
    plt.bar(gps_positions, df["gps_velocity_kmh"], width=bar_width, color="red", label="GPS Velocity")
    plt.bar(video_positions, df["video_velocity_kmh"], width=bar_width, color="blue", label="Video Velocity")

    # Add labels, title, and legend
    plt.xlabel("Sample index")
    plt.ylabel("Velocity (km/h)")
    plt.title("Velocity Comparison")
    plt.legend()

    # Show plot
    plt.tight_layout()  # Adjust layout to make room for the rotated x-axis labels
    plt.show()


def main() -> None:
    args = parse_args()
    df = load_data(args.file)
    plot_velocity_labels(df)


if __name__ == "__main__":
    main()
