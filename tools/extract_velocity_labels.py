import pandas as pd
import cv2

import sys
import argparse

from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Script for automating collected velocity data from GPS and video recording at a given timestamp",
    )
    parser.add_argument(
        "--video",
        type=str,
        help="MP4 video file path",
    )
    parser.add_argument(
        "--gps",
        type=str,
        help="GPS CSV file path",
    )
    args = parser.parse_args()

    if not args.gps and args.video:
        parser.error("Please provide at least one of: video or GPS file paths")

    return args


def load_gps_data(gps_path):
    df = pd.read_csv(
        gps_path,
        names=[
            "type",
            "date time",
            "latitude",
            "longitude",
            "accuracy(m)",
            "altitude(m)",
            "geoid_height(m)",
            "speed(m/s)",
            "bearing(deg)",
            "sat_used",
            "sat_inview",
            "name",
            "desc",
        ],
        skiprows=1,
    )

    df["timestamp"] = pd.to_datetime(df["date time"], format="%Y-%m-%d %H:%M:%S").values.astype("int64") // 10**9
    df["velocity"] = df["speed(m/s)"].apply(lambda x: x * 3.6)
    df = df[["timestamp", "velocity"]]

    return df


def get_gps_velocity(df, timestamp):
    closest_idx = df["timestamp"].sub(timestamp).abs().idxmin()
    closest_row = df.loc[closest_idx]
    velocity = closest_row["velocity"]
    closest_timestamp_value = closest_row["timestamp"]

    if abs(timestamp - closest_timestamp_value) > 1:
        raise ValueError("No GPS data found for the given timestamp")

    return velocity


def show_frame_at_offset(video_path, offset_seconds):
    # Read frame from video at offset
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        sys.exit()

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration_seconds = total_frames / fps
    if offset_seconds < 0 or offset_seconds > duration_seconds:
        cap.release()
        raise ValueError(
            f"The offset {offset_seconds} seconds is outside the video duration of {duration_seconds} seconds."
        )

    frame_number = int(round(offset_seconds * fps))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        cap.release()
        sys.exit()

    # Display frame
    desired_height = 720
    aspect_ratio = frame.shape[1] / frame.shape[0]
    desired_width = int(desired_height * aspect_ratio)
    resized_frame = cv2.resize(frame, (desired_width, desired_height))

    cv2.imshow(f"Frame at {offset_seconds} seconds", resized_frame)

    # Cleanup
    cv2.waitKey(0)
    cap.release()
    cv2.destroyAllWindows()


def video_path_to_timestamp(path):
    filename = Path(path).name
    date_time_str = filename.split(".")[0]

    date_time_obj = datetime.strptime(date_time_str, "%Y%m%d_%H%M%S")
    epoch_timestamp = date_time_obj.timestamp()

    return epoch_timestamp


if __name__ == "__main__":
    args = parse_args()
    video_path = args.video
    gps_path = args.gps

    if gps_path:
        df = load_gps_data(gps_path)
        print(f"Loaded GPS data from {gps_path}:")
        print(df.describe())
        print("====================================")

    if video_path:
        video_start = video_path_to_timestamp(video_path) + 0.5
        print(f"Loaded video {video_path}, start timestamp: {video_start} s")
        print("====================================")

    while True:
        try:
            timestamp_input = input("Enter timestamp in milliseconds (ctrl+c to quit): ")
            if timestamp_input.lower() == "exit":
                break

            timestamp = int(timestamp_input) / 1000.0
            offset = timestamp - video_start

            if gps_path:
                print(f"Speed at timestamp {int(timestamp*1000)} ms: {get_gps_velocity(df, timestamp):.2f} km/h")

            if video_path:
                print(f"Displaying frame at video time: {int(offset // 60)}:{offset % 60:.2f}")
                show_frame_at_offset(video_path, offset)

            print("====================================")

        except ValueError as e:
            print(f"Error: {e}")
            continue

        except KeyboardInterrupt:
            print("\nExiting...")
            break

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break
