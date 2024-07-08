import numpy as np
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


from sklearn.model_selection import KFold
from sklearn.linear_model import LinearRegression


def extract_features(X: list[Motion]) -> np.ndarray:
    return np.array([[m.time_total, m.dist_avg, m.direction, m.velocity] for m in X])


def train_linear_regression(X: list[Motion], y: list[float]) -> Any:
    X, y = extract_features(X), np.array(y)

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
        mae = sum(abs(y_pred - y_test)) / len(y_pred)
        mae_scores.append(mae)

    # Calculate and print the average MAE across all folds
    average_mae = sum(mae_scores) / n_splits
    average_velocity = sum(y) / len(y)
    print(f"Average velocity: {average_velocity}")
    print(f"Average MAE across {n_splits} folds: {average_mae}")

    # Train on the whole dataset and return
    model = LinearRegression()
    model.fit(X, y)

    return model


def main() -> None:
    args = parse_args()
    tmf8828_data = load_tmf8828_data(args.data)
    velocity_labels = load_velocity_labels(args.labels)

    X, y = prepare_labeled_data(
        tmf8828_data,
        velocity_labels,
        distStrategy=confidence_strategy,
        velocityLabelStrategy=video_strategy,
        min_samples=2,
        max_dd=200,
        max_series_delta_time_ms=200,
        max_label_delta_time_ms=2000,
    )

    # Apply calibration offset
    y = [velocity - 4 for velocity in y]

    print("Detection percentage:", len(y) / len(velocity_labels) * 100, "%")

    model = train_linear_regression(X, y)
    y_pred = model.predict(extract_features(X))

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    plot_samples_partitioning(X, ax1)
    plot_real_velocity(X, y, ax2)
    plot_estimated_velocity(X, y_pred, ax2)
    plot_legend(fig, ax1, ax2)
    plt.show()

    if args.test_data:
        test_data = load_tmf8828_data(args.test_data)
        X = prepare_unlabeled_data(
            test_data,
            distStrategy=confidence_strategy,
            min_samples=2,
            max_dd=200,
            max_series_delta_time_ms=200,
        )

        y_pred = model.predict(extract_features(X))

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        plot_samples_partitioning(X, ax1)
        plot_estimated_velocity(X, y_pred, ax2)
        plot_legend(fig, ax1, ax2)
        plt.show()


if __name__ == "__main__":
    main()
