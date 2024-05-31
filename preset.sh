#!/usr/bin/bash

ITERATIONS=300000
SPAD_MAP_ID=1
REPORT_PERIOD_MS=5000

echo -n "Powering on the sensor: "
echo 1 | sudo tee sysfs/chip_enable
echo -n "mode_8x8: "
echo 0 | sudo tee sysfs/app/mode_8x8
echo -n "spad_map_id: "
echo $SPAD_MAP_ID | sudo tee sysfs/app/spad_map_id
echo -n "iterations: "
echo $ITERATIONS | sudo tee sysfs/app/iterations
echo -n "report_perios_ms: "
echo $REPORT_PERIOD_MS | sudo tee sysfs/app/report_period_ms
sudo cat sysfs/app/factory_calibration > calib.bin

echo -n "short_range_mode: "
echo 0 | sudo tee sysfs/app/short_range_mode

echo -n "sysfs/app/conf_threshold: "
echo 5 | sudo tee sysfs/app/conf_threshold
