import numpy as np
import math


def get_optimal_beta(
    max_dist: float,
    max_range: float,
    alpha: float = math.radians(9.428),
    margin: float = 0.1,
) -> float:
    """Calculates optimal beta angle considering sensor fov, sensor max range and max distance between sensor and bike path"""
    return np.arccos((max_dist + margin) / max_range) - alpha


def get_range_covered(
    beta: float, max_dist: float, alpha: float = math.radians(9.428)
) -> float:
    """Calculates range of the bike path that will be covered by sensor fov"""
    return max_dist * (np.tan(alpha + beta) - np.tan(beta))


if __name__ == "__main__":
    margin = 0.1
    alpha = math.radians(9.428)

    max_dist = 2
    max_range = 4
    beta = get_optimal_beta(
        max_dist=max_dist, max_range=max_range, alpha=alpha, margin=margin
    )
    sensor_placement_angle = np.degrees(beta + alpha / 2)
    max_range_covered = get_range_covered(beta=beta, max_dist=max_dist, alpha=alpha)

    print(
        f"max_dist == {max_dist} m\n"
        f"max_range == {max_range} m\n"
        f"beta = {round(np.degrees(beta), 2)} deg\n"
        f"max_range_covered == {max_range_covered:.2f} m\n"
    )

    period = 0.022
    for speed in [10, 15, 20, 25, 30]:
        for dist in [1, 1.5]:
            range = max_range_covered * dist / max_dist
            speed_ms = speed / 3.6
            meters_per_period = speed_ms * period
            print(
                f"For bike riding {speed} kmh/h, {dist} m from the sensor, we should catch him at least {math.floor(range / meters_per_period)}"
                f", meters_per_period == {round(meters_per_period, 2)}"
            )
