
import argparse
from utils import *

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
    parser.add_argument(
        "--test_data",
        required=False,
        type=str,
        help="Path of the test tmf8828 data CSV file",
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
        distStrategy=confidence_strategy,
        velocityLabelStrategy=average_strategy,
        min_samples=3,
        max_dd=200,
        max_series_delta_time_ms=200,
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

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    plot_samples_partitioning(X, ax1)
    plot_real_velocity(X, y, ax2)
    plot_calculated_velocity(X, ax2)
    plot_legend(fig, ax1, ax2)
    plt.show()

    # TEST ON NON-BIKE DATA
    if args.test_data:
        test_data = load_tmf8828_data(args.test_data)
        X = prepare_unlabeled_data(
            test_data,
            distStrategy=confidence_strategy,
            min_samples=2,
            max_dd=200,
            max_series_delta_time_ms=200,
        )

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        plot_samples_partitioning(X, ax1)
        plot_calculated_velocity(X, ax2)
        plot_legend(fig, ax1, ax2)
        plt.show()


if __name__ == "__main__":
    main()
