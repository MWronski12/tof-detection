import pandas as pd
import sys

if len(sys.argv) != 2:
    print("Usage python3 evaluate_performance.py <csv file>")
    sys.exit(1)

file = sys.argv[1]
print("Data file:", file, end="\n\n")

# Read CSV data into a DataFrame

column_names = [
    "timestamp",
    "ambient_light",
    "confidence_target_0",
    "distance_mm_target_0",
    "confidence_target_1",
    "distance_mm_target_1",
]
df = pd.read_csv(file, names=column_names)


def choose_min_distance(row):
    return min(row["distance_mm_target_0"], row["distance_mm_target_1"])


def choose_max_distance(row):
    return max(row["distance_mm_target_0"], row["distance_mm_target_1"])


def choose_max_confidence_distance(row):
    if row["confidence_target_0"] >= row["confidence_target_1"]:
        return row["distance_mm_target_0"]
    else:
        return row["distance_mm_target_1"]


def choose_mean_distance(row):
    if row["distance_mm_target_0"] == -1 or row["distance_mm_target_0"] != -1:
        return choose_max_distance(row)

    return (row["distance_mm_target_0"] + row["distance_mm_target_1"]) / 2


def choose_confidence_weighted_mean_distance(row):
    if row["distance_mm_target_0"] == -1 or row["distance_mm_target_0"] != -1:
        return choose_max_distance(row)

    confidence_sum = row["confidence_target_0"] + row["confidence_target_1"]

    return (
        row["confidence_target_0"] * row["distance_mm_target_0"]
        + row["confidence_target_1"] * row["distance_mm_target_1"]
    ) / confidence_sum


def choose_confidence(row):
    if row["distance_mm"] == row["distance_mm_target_0"]:
        return row["confidence_target_0"]
    else:
        return row["confidence_target_1"]


df["distance_mm"] = df.apply(choose_max_distance, axis=1)
df["confidence"] = df.apply(choose_confidence, axis=1)

distance = df.loc[df["distance_mm"] != -1, "distance_mm"]
confidence = df.loc[df["confidence"] != -1, "confidence"]

period = df["timestamp"].diff()
ambient_light = df["ambient_light"]

print(f"Data present: {len(distance) / len(df):.2%}")
print(f"Mean ambient light: {ambient_light.mean():.0f} +- {ambient_light.std():.0f}")
print(f"Mean period: {period.mean():.2f} +- {period.std():.2f} ms")
print(f"Max period: {period.max()} mm")
print(f"Mean confidence: {confidence.mean():.2f} +- {confidence.std():.2f}")
print(f"Mean dist: {distance.mean():.0f} +- {distance.std():.0f} mm")
print(f"Min dist: {distance.min()} mm")
print(f"Max dist: {distance.max()} mm")
