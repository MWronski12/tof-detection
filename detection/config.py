NUM_ZONES = 9
NUM_TARGETS = 2
CENTER_ZONE_IDX = 4
SENSOR_ANGLE_DEG = 60
DIST_TO_PATH = 1.5

ZONE_DISTANCE_COLUMNS = [
    f"zone{zone_idx}_dist{target_idx}" for zone_idx in range(NUM_ZONES) for target_idx in range(NUM_TARGETS)
]

ZONE_CONFIDENCE_COLUMNS = [
    f"zone{zone_idx}_conf{target_idx}" for zone_idx in range(NUM_ZONES) for target_idx in range(NUM_TARGETS)
]

ZONE_COLUMNS = [item for pair in zip(ZONE_CONFIDENCE_COLUMNS, ZONE_DISTANCE_COLUMNS) for item in pair]

COLUMNS = ["timestamp_ms", "ambient_light"] + ZONE_COLUMNS
