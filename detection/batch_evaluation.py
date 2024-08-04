import argparse
from utils import *
from config import THRESHOLD_KMH

# ----------------------------------- ARGS ----------------------------------- #


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Script for bicycle detection algorithm evaluation.",
    )
    parser.add_argument(
        "--data",
        required=True,
        type=str,
        help="Path of the tmf8828 data CSV file",
    )
    parser.add_argument(
        "--num-samples",
        required=True,
        type=int,
        help="Number of recorded bike samples",
    )
    parser.add_argument(
        "--labels",
        required=True,
        type=str,
        help="Path of the velocity labels CSV file",
    )
    parser.add_argument(
        "--validation-data",
        required=False,
        type=str,
        help="Path of the test tmf8828 data CSV file, without labels",
    )
    parser.add_argument(
        "--min-samples",
        "-m",
        required=False,
        type=int,
        default=3,
        help="Minimum number of samples in a series",
    )
    parser.add_argument(
        "--max-dd",
        "-d",
        required=False,
        type=int,
        default=200,
        help="Maximum distance delta between samples in a series",
    )
    parser.add_argument(
        "--max-dt",
        "-t",
        required=False,
        type=int,
        default=500,
        help="Maximum time delta between series in a motion",
    )
    parser.add_argument(
        "--dist-strategy",
        required=False,
        type=str,
        choices=["confidence", "closest"],
        default="confidence",
    )
    parser.add_argument(
        "--velocity-strategy",
        required=False,
        type=str,
        choices=["video", "gps"],
        default="gps",
    )
    parser.add_argument(
        "--threshold",
        required=False,
        type=int,
        default=THRESHOLD_KMH,
        help="Velocity threshold for bike detection",
    )

    return parser.parse_args()


# ----------------------------------- MAIN ----------------------------------- #


def main() -> None:
    # LOAD DATA
    args = parse_args()
    tmf8828_data = load_tmf8828_data(args.data)
    velocity_labels = load_velocity_labels(args.labels)

    # PREPARE DATA
    X, y = prepare_labeled_data(
        tmf8828_data,
        velocity_labels,
        distStrategy=confidence_strategy if args.dist_strategy == "confidence" else target_0_strategy,
        velocityLabelStrategy=video_strategy if args.velocity_strategy == "video" else gps_strategy,
        min_samples=args.min_samples,
        max_dd=args.max_dd,
        max_series_delta_time_ms=args.max_dt,
        max_label_delta_time_ms=2000,
    )

    # Apply calibration offset
    # y = [velocity - 4 for velocity in y]

    # TEST BIKE VELOCITY CALCULATION ACCURACY
    average_velocity = sum(y) / len(y)
    print(len(X))
    print(f"Data average velocity: {average_velocity}")
    print("Detection percentage:", len(X) / float(len(velocity_labels)) * 100)
    print(
        "MAE:",
        (sum([abs(motion.velocity - velocity_label) for motion, velocity_label in zip(X, y)]) / len(X)),
    )

    print(f"Bicycle classification accuracy: {(sum([motion.velocity >= args.threshold for motion in X])) / args.num_samples * 100:.2f}%")

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    ax1.set_ylim(0, 5500)
    ax2.set_ylim(0, 35)
    # plot_raw_data(tmf8828_data, ax1)
    plot_samples_partitioning(X, ax1)
    plot_real_velocity(X, y, ax2)
    plot_calculated_velocity(X, ax2)
    plot_velocity_threshold(args.threshold, ax2)
    plot_legend(fig, ax1, ax2)
    plt.show()

    # TEST ON NON-BIKE DATA
    if args.validation_data:
        validation_data = load_tmf8828_data(args.validation_data)
        X = prepare_unlabeled_data(
            validation_data,
            distStrategy=confidence_strategy if args.dist_strategy == "confidence" else target_0_strategy,
            min_samples=args.min_samples,
            max_dd=args.max_dd,
            max_series_delta_time_ms=args.max_dt,
        )

        print(f"Pedestrian classification accuracy: {(sum([motion.velocity < args.threshold for motion in X]) / len(X)) * 100:.2f}%")

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        ax1.set_ylim(0, 5500)
        ax2.set_ylim(0, 35)
        plot_samples_partitioning(X, ax1)
        plot_calculated_velocity(X, ax2)
        plot_velocity_threshold(args.threshold, ax2)
        plot_legend(fig, ax1, ax2)
        plt.show()


if __name__ == "__main__":
    main()
